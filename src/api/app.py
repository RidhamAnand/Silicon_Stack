"""
Flask API for AI Customer Support Agent
Provides REST endpoints for the React frontend
Uses the CLI backend directly for consistency
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path
from datetime import datetime
import uuid
import io
from contextlib import redirect_stdout

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import config
from src.utils.conversation_context import conversation_manager, ConversationMessage
from src.database import db_service

# Import the CLI class to reuse its logic
from src.main import CustomerSupportCLI

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Store active CLI instances for each session (in production, use Redis or database)
active_sessions = {}


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'AI Customer Support API'
    })


@app.route('/api/chat/start', methods=['POST'])
def start_conversation():
    """Start a new conversation session with a CLI instance"""
    session_id = str(uuid.uuid4())
    
    # Create a new CLI instance for this session
    cli = CustomerSupportCLI()
    cli.interactive = False  # Disable interactive prompts for API
    
    active_sessions[session_id] = {
        'cli': cli,
        'created_at': datetime.utcnow(),
        'message_count': 0
    }
    
    return jsonify({
        'session_id': session_id,
        'message': 'Conversation started successfully',
        'welcome_message': 'Welcome! I\'m your AI Customer Support Assistant. How can I help you today?'
    })


@app.route('/api/chat/message', methods=['POST'])
def send_message():
    """
    Process a chat message using the CLI backend
    
    Expected JSON:
    {
        "session_id": "uuid",
        "message": "user message text"
    }
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        user_message = data.get('message', '').strip()
        
        if not session_id or not user_message:
            return jsonify({
                'error': 'Missing session_id or message'
            }), 400
        
        # Get or create CLI session
        if session_id not in active_sessions:
            cli = CustomerSupportCLI()
            cli.interactive = False
            active_sessions[session_id] = {
                'cli': cli,
                'created_at': datetime.utcnow(),
                'message_count': 0
            }
        
        session = active_sessions[session_id]
        cli = session['cli']
        
        # Process the query using CLI's process_query method
        # This ensures 100% consistency with CLI behavior
        result = cli.process_query(user_message)
        
        session['message_count'] += 2
        
        # Extract response data from CLI's conversation
        conversation = cli.conversation
        last_assistant_msg = None
        for msg in reversed(conversation.messages):
            if msg.role == "assistant":
                last_assistant_msg = msg
                break
        
        if not last_assistant_msg:
            return jsonify({
                'error': 'No response generated'
            }), 500
        
        # Check if conversation was closed
        conversation_closed = not cli.running
        
        # Check if the response suggests creating a ticket
        # This is set by the RAG pipeline when FAQ confidence is low
        should_create_ticket = False
        if result and isinstance(result, dict):
            should_create_ticket = result.get('should_create_ticket', False)
        
        # Prepare response (matching the expected format)
        response_data = {
            'session_id': session_id,
            'response': last_assistant_msg.content,
            'intent': last_assistant_msg.intent,
            'intent_confidence': last_assistant_msg.confidence,
            'entities': last_assistant_msg.entities or [],
            'routing_path': last_assistant_msg.metadata.get('routing_path', []) if last_assistant_msg.metadata else [],
            'needs_escalation': last_assistant_msg.metadata.get('needs_escalation', False) if last_assistant_msg.metadata else False,
            'should_create_ticket': should_create_ticket,  # Pass this to UI for confirmation prompt
            'conversation_closed': conversation_closed,
            'metadata': {
                'current_agent': conversation.current_agent,
                'message_count': session['message_count'],
                'agent_state': conversation.agent_state,
                'pending_action': conversation.pending_action,
                'collected_details': conversation.collected_details
            }
        }
        
        # Add agent-specific info
        if conversation.current_agent:
            response_data['agent'] = conversation.current_agent
        
        if conversation.pending_action:
            response_data['escalation_status'] = conversation.pending_action
        
        # Add followup question if appropriate
        if conversation.should_ask_followup():
            followup = conversation.generate_followup_question()
            if followup:
                response_data['followup_question'] = followup
        
        # If conversation closed, clean up session
        if conversation_closed:
            print(f"[API] Session {session_id} closed, cleaning up")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"[API ERROR] {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'message': 'An error occurred processing your message'
        }), 500


@app.route('/api/chat/escalate', methods=['POST'])
def escalate_conversation():
    """
    Manually escalate conversation to create a ticket
    
    Expected JSON:
    {
        "session_id": "uuid",
        "user_query": "original issue description"
    }
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        user_query = data.get('user_query', '')
        
        if not session_id:
            return jsonify({'error': 'Missing session_id'}), 400
        
        if session_id not in active_sessions:
            return jsonify({'error': 'Invalid session_id'}), 404
        
        session = active_sessions[session_id]
        cli = session['cli']
        conversation = cli.conversation
        
        # Activate escalation agent
        from src.agents.escalation_agent import escalation_agent
        conversation.set_active_agent("escalation_agent")
        
        # Process with escalation agent
        response = escalation_agent.process_message(
            conversation_context=conversation,
            user_query=user_query,
            chat_history=None
        )
        
        # Store escalation message
        assistant_msg = ConversationMessage(
            role="assistant",
            content=response,
            metadata={
                "agent": "escalation_agent",
                "current_agent": conversation.current_agent,
                "pending_action": conversation.pending_action,
                "collected_details": conversation.collected_details,
                "agent_state": conversation.agent_state
            }
        )
        conversation.add_message(assistant_msg)
        
        # Check if ticket was created
        conversation_closed = False
        if isinstance(response, str) and ("Ticket ID:" in response or "SUPPORT TICKET CREATED" in response.upper()):
            conversation_closed = True
            cli.running = False
        
        return jsonify({
            'session_id': session_id,
            'response': response,
            'escalation_status': conversation.pending_action or 'Processing',
            'conversation_closed': conversation_closed,
            'metadata': {
                'current_agent': conversation.current_agent,
                'pending_action': conversation.pending_action
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'An error occurred during escalation'
        }), 500


@app.route('/api/chat/history/<session_id>', methods=['GET'])
def get_conversation_history(session_id):
    """Get conversation history for a session"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = active_sessions[session_id]
    cli = session['cli']
    conversation = cli.conversation
    
    messages = []
    for msg in conversation.messages:
        messages.append({
            'role': msg.role,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat() if msg.timestamp else None,
            'intent': msg.intent,
            'confidence': msg.confidence,
            'entities': msg.entities
        })
    
    return jsonify({
        'session_id': session_id,
        'messages': messages,
        'message_count': len(messages),
        'current_agent': conversation.current_agent
    })


@app.route('/api/topics', methods=['GET'])
def get_topics():
    """Get available FAQ topics"""
    topics = [
        {"id": "shipping", "name": "Shipping & Delivery", "icon": "🚚"},
        {"id": "returns", "name": "Returns & Refunds", "icon": "↩️"},
        {"id": "billing", "name": "Billing & Payment", "icon": "💳"},
        {"id": "account", "name": "Account Management", "icon": "👤"},
        {"id": "products", "name": "Products & Inventory", "icon": "📦"},
        {"id": "orders", "name": "Orders & Tracking", "icon": "📋"},
        {"id": "promotions", "name": "Promotions & Discounts", "icon": "🎁"},
        {"id": "support", "name": "Customer Service", "icon": "💬"},
        {"id": "privacy", "name": "Privacy & Security", "icon": "🔒"},
        {"id": "technical", "name": "Technical Issues", "icon": "⚙️"}
    ]
    
    return jsonify({'topics': topics})


def init_app():
    """Initialize the application"""
    try:
        # Validate configuration
        print("Validating configuration...")
        config.validate()
        print("✅ Configuration valid")
        
        # Initialize database connection
        print("Connecting to database...")
        if not db_service.connect():
            print("⚠️  Database connection failed - order lookups will fallback to general responses")
        else:
            print("✅ Database connected")
        
        return True
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False


if __name__ == '__main__':
    if init_app():
        print("\n🚀 Starting Flask API server...")
        print(f"Server running on http://localhost:{config.FLASK_PORT}")
        print("Press CTRL+C to stop\n")
        
        app.run(
            host='0.0.0.0',
            port=config.FLASK_PORT,
            debug=config.FLASK_DEBUG
        )
    else:
        print("Failed to initialize application")
        sys.exit(1)
