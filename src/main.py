"""
Main CLI interface for the AI Customer Support Agent
"""
import sys
import os
from pathlib import Path
from colorama import init, Fore, Style

# Initialize colorama for Windows
init()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import config
from src.rag.pipeline import rag_pipeline
from src.utils.conversation_context import conversation_manager, ConversationMessage
from src.agents.router_agent import router_agent

class CustomerSupportCLI:
    """Command-line interface for customer support bot"""
    
    def __init__(self):
        self.rag = rag_pipeline
        self.running = True
        self.interactive = sys.stdin.isatty()  # Check if running interactively
        self.conversation = conversation_manager.create_conversation()
        self.current_agent = None  # Track current agent for change detection
        self.router = router_agent  # Use agentic router
        self.session_id = f"session_{id(self)}"  # Unique session ID
    
    def print_header(self):
        """Print welcome header"""
        if self.interactive:
            print("\n" + "=" * 60)
            print(Fore.CYAN + "🤖 AI Customer Support Assistant" + Style.RESET_ALL)
            print("=" * 60)
            print("\nWelcome! I'm here to help answer your questions.")
            print("Ask me about shipping, returns, billing, accounts, and more!")
            print("\nCommands:")
            print("  'quit' or 'exit' - End the conversation")
            print("  'help' - Show available topics")
            print("  'clear' - Clear screen")
            print("=" * 60 + "\n")
    
    def print_topics(self):
        """Print available FAQ topics"""
        topics = [
            "Shipping & Delivery",
            "Returns & Refunds",
            "Billing & Payment",
            "Account Management",
            "Products & Inventory",
            "Orders & Tracking",
            "Promotions & Discounts",
            "Customer Service",
            "Privacy & Security",
            "Technical Issues"
        ]
        print("\n" + Fore.YELLOW + "📚 Available Topics:" + Style.RESET_ALL)
        for topic in topics:
            print(f"  • {topic}")
        print()
    
    def process_query(self, query: str) -> None:
        """
        Process user query and display response
        
        Args:
            query: User's question
        """
        
        # Store user message in conversation
        user_message = ConversationMessage(
            role="user",
            content=query
        )
        self.conversation.add_message(user_message)
        
        # **CRITICAL**: Check if escalation agent is active - ONE WAY ROUTE
        # Once in escalation, stay there until ticket is created
        print(f"[DEBUG] Checking escalation bypass: current_agent = '{self.conversation.current_agent}'")
        if self.conversation.current_agent == "escalation_agent":
            from src.agents.escalation_agent import escalation_agent
            
            print(f"[DEBUG] ✅ ESCALATION BYPASS ACTIVATED - Calling escalation_agent directly")
            if self.interactive:
                print(Fore.YELLOW + "\n🎫 Escalation in progress..." + Style.RESET_ALL)
            
            # Call escalation agent directly - NO ROUTER
            response = escalation_agent.process_message(
                conversation_context=self.conversation,
                user_query=query,
                chat_history=None  # It will extract from conversation_context
            )
            
            # Store assistant message
            assistant_message = ConversationMessage(
                role="assistant",
                content=response,
                metadata={
                    "agent": "escalation_agent",
                    "current_agent": self.conversation.current_agent,
                    "pending_action": self.conversation.pending_action,
                    "collected_details": self.conversation.collected_details,
                    "agent_state": self.conversation.agent_state
                }
            )
            self.conversation.add_message(assistant_message)
            
            # Display response
            if self.interactive:
                print("\n" + Fore.GREEN + "💬 Assistant:" + Style.RESET_ALL)
            print(response)
            
            # Show status
            if self.interactive:
                print("\n" + Fore.CYAN + f"🎫 Escalation Status: {self.conversation.pending_action or 'Processing'}" + Style.RESET_ALL)

            # Auto-close chat if ticket created
            if isinstance(response, str) and ("Ticket ID:" in response or "SUPPORT TICKET CREATED" in response.upper()):
                if self.interactive:
                    print(Fore.GREEN + "\n👋 Ticket created and conversation closed. Thank you!" + Style.RESET_ALL)
                self.running = False
                return
            
            return
        
        # Check for special commands
        query_lower = query.lower().strip()
        
        if query_lower in ['quit', 'exit', 'bye', 'goodbye']:
            if self.interactive:
                print(Fore.GREEN + "\n👋 Thank you for contacting support. Have a great day!" + Style.RESET_ALL)
            self.running = False
            return
        
        if query_lower in ['help', 'topics']:
            self.print_topics()
            return
        
        if query_lower == 'clear' and self.interactive:
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
            self.print_header()
            return
        
        # Process actual query
        try:
            if self.interactive:
                print(Fore.YELLOW + "\n🔍 Searching knowledge base..." + Style.RESET_ALL)
            
            # Pass the actual ConversationContext object (not just messages)
            # This allows the router and agents to modify the state
            result = self.rag.query(
                user_query=query,
                include_sources=True,
                conversation_context=self.conversation  # Pass the actual object!
            )
            
            # Update the user message with intent and entities from the result
            user_message.intent = result.get('intent')
            user_message.confidence = result.get('intent_confidence')
            user_message.entities = result.get('entities', [])
            
            # Update conversation state based on the processed result
            self.conversation._update_state_from_user_message(user_message)
            
            # Store assistant message in conversation
            assistant_message = ConversationMessage(
                role="assistant",
                content=result["response"],
                intent=result.get('intent'),
                confidence=result.get('intent_confidence'),
                entities=result.get('entities', []),
                metadata={
                    "routing_path": result.get('routing_path', []),
                    "needs_escalation": result.get('needs_escalation', False),
                    "escalation_reason": result.get('escalation_reason'),
                    # **CRITICAL**: Save conversation state for context continuity
                    "current_agent": self.conversation.current_agent,
                    "pending_action": self.conversation.pending_action,
                    "collected_details": self.conversation.collected_details,
                    "agent_state": self.conversation.agent_state
                }
            )
            self.conversation.add_message(assistant_message)
            
            # Display response
            if self.interactive:
                print("\n" + Fore.GREEN + "💬 Assistant:" + Style.RESET_ALL)
            print(result["response"])

            # If the response shows a ticket was created (edge case), close chat
            if isinstance(result.get("response"), str) and ("Ticket ID:" in result["response"] or "SUPPORT TICKET CREATED" in result["response"].upper()):
                if self.interactive:
                    print(Fore.GREEN + "\n👋 Ticket created and conversation closed. Thank you!" + Style.RESET_ALL)
                self.running = False
                return result
            
            # Check if system suggests creating a ticket (no/low-confidence FAQ match)
            should_create_ticket = result.get("should_create_ticket", False)
            if should_create_ticket and self.interactive:
                print("\n" + Fore.YELLOW + "📋 Would you like me to create a support ticket? (yes/no): " + Style.RESET_ALL, end='')
                try:
                    ticket_response = input().strip().lower()
                    if ticket_response in ['yes', 'y']:
                        # Activate one-way escalation and hand off immediately
                        from src.agents.escalation_agent import escalation_agent
                        self.conversation.set_active_agent("escalation_agent")

                        if self.interactive:
                            print(Fore.YELLOW + "\n🎫 Escalating and creating a ticket..." + Style.RESET_ALL)

                        escalation_reply = escalation_agent.process_message(
                            conversation_context=self.conversation,
                            user_query="Please create a support ticket for this issue.",
                            chat_history=None
                        )

                        # Store escalation assistant message with state
                        assistant_message_escalation = ConversationMessage(
                            role="assistant",
                            content=escalation_reply,
                            metadata={
                                "agent": "escalation_agent",
                                "current_agent": self.conversation.current_agent,
                                "pending_action": self.conversation.pending_action,
                                "collected_details": self.conversation.collected_details,
                                "agent_state": self.conversation.agent_state
                            }
                        )
                        self.conversation.add_message(assistant_message_escalation)

                        # Show escalation reply
                        if self.interactive:
                            print("\n" + Fore.GREEN + "� Assistant:" + Style.RESET_ALL)
                        print(escalation_reply)

                        # If ticket created, close chat
                        if isinstance(escalation_reply, str) and ("Ticket ID:" in escalation_reply or "SUPPORT TICKET CREATED" in escalation_reply.upper()):
                            if self.interactive:
                                print(Fore.GREEN + "\n👋 Ticket created and conversation closed. Thank you!" + Style.RESET_ALL)
                            self.running = False
                        return result
                except Exception as _:
                    pass
            
            # Display metadata (always show for transparency)
            intent_info = f"Intent: {result.get('intent', 'unknown')} (Confidence: {result.get('intent_confidence', 0):.1%})"
            if self.interactive:
                print("\n" + Fore.CYAN + f"📊 {intent_info}" + Style.RESET_ALL)
            else:
                print(f"\n[{intent_info}]")
            
            # Show entities if found
            entities = result.get('entities', [])
            if entities:
                entity_summary = f"Found {len(entities)} entities: "
                entity_summary += ", ".join([f"{e['type']}: {e['value']}" for e in entities[:3]])
                if len(entities) > 3:
                    entity_summary += f" (+{len(entities) - 3} more)"
                if self.interactive:
                    print(Fore.CYAN + f"🔍 {entity_summary}" + Style.RESET_ALL)
                else:
                    print(f"[{entity_summary}]")
                
                # Highlight order numbers specifically
                order_entities = [e for e in entities if e['type'] == 'order_number']
                if order_entities:
                    order_info = f"📦 Order ID(s) extracted: {', '.join([e['value'] for e in order_entities])}"
                    if self.interactive:
                        print(Fore.GREEN + f"{order_info}" + Style.RESET_ALL)
                    else:
                        print(f"[{order_info}]")
            
            # Show routing path
            routing_path = result.get('routing_path', [])
            if routing_path:
                route_info = f"Route: {' → '.join(routing_path)}"
                if self.interactive:
                    print(Fore.CYAN + f"🔀 {route_info}" + Style.RESET_ALL)
                else:
                    print(f"[{route_info}]")
                
                # Check for agent changes
                agent_names = ['faq_agent', 'order_query_agent', 'escalation_agent', 'order_return_agent']
                route_indicators = {
                    'route_faq': 'faq_agent',
                    'route_order': 'order_query_agent', 
                    'route_complaint': 'escalation_agent',
                    'route_escalation': 'escalation_agent'
                }
                
                current_agent_in_path = None
                agent_reason = ""
                
                # First check for explicit agent names in path
                for agent in agent_names:
                    if agent in routing_path:
                        current_agent_in_path = agent
                        agent_reason = f"Direct agent call: {agent}"
                        break
                
                # Then check for route indicators
                if not current_agent_in_path:
                    for route, agent in route_indicators.items():
                        if any(r.startswith(route) for r in routing_path):
                            current_agent_in_path = agent
                            agent_reason = f"Route-based agent selection: {route} → {agent}"
                            break
                
                # Print agent information
                if current_agent_in_path:
                    agent_display_name = {
                        'faq_agent': 'FAQ Agent',
                        'order_query_agent': 'Order Query Agent', 
                        'escalation_agent': 'Escalation Agent',
                        'order_return_agent': 'Order Return Agent'
                    }.get(current_agent_in_path, current_agent_in_path)
                    
                    if current_agent_in_path != self.current_agent:
                        # Agent switch
                        if self.interactive:
                            print(Fore.MAGENTA + f"🤖 Agent SWITCHED to: {agent_display_name}" + Style.RESET_ALL)
                            print(Fore.MAGENTA + f"   └─ Reason: {agent_reason}" + Style.RESET_ALL)
                        else:
                            print(f"[🤖 Agent SWITCHED to: {agent_display_name}]")
                            print(f"[   └─ Reason: {agent_reason}]")
                    else:
                        # Same agent continued
                        if self.interactive:
                            print(Fore.BLUE + f"🤖 Agent CONTINUED: {agent_display_name}" + Style.RESET_ALL)
                            print(Fore.BLUE + f"   └─ Reason: {agent_reason}" + Style.RESET_ALL)
                        else:
                            print(f"[🤖 Agent CONTINUED: {agent_display_name}]")
                            print(f"[   └─ Reason: {agent_reason}]")
                    
                    self.current_agent = current_agent_in_path

                    # If escalation agent is selected, lock-in one-way escalation
                    if current_agent_in_path == 'escalation_agent':
                        self.conversation.set_active_agent('escalation_agent')
            
            # Show agent selection details if available
            agent_details = result.get("agent_selection_details", {})
            if agent_details:
                if agent_details.get("agents_checked"):
                    checked_info = f"Agents checked: {len(agent_details['agents_checked'])}"
                    if self.interactive:
                        print(Fore.CYAN + f"🔍 {checked_info}" + Style.RESET_ALL)
                    else:
                        print(f"[{checked_info}]")
                    
                    # Show which agents were considered
                    for agent_check in agent_details["agents_checked"]:
                        status = "✅" if agent_check["can_handle"] else "❌"
                        agent_info = f"  {status} {agent_check['agent']}: {agent_check['reason']}"
                        if self.interactive:
                            color = Fore.GREEN if agent_check["can_handle"] else Fore.RED
                            print(color + agent_info + Style.RESET_ALL)
                        else:
                            print(f"[{agent_info}]")
                
                if agent_details.get("agent_selected"):
                    selected_info = f"Selected agent: {agent_details['agent_selected']} - {agent_details['selection_reason']}"
                    if self.interactive:
                        print(Fore.YELLOW + f"🎯 {selected_info}" + Style.RESET_ALL)
                    else:
                        print(f"[🎯 {selected_info}]")
            
            # Ask follow-up question if appropriate
            if self.interactive and self.conversation.should_ask_followup():
                followup = self.conversation.generate_followup_question()
                if followup:
                    print("\n" + Fore.BLUE + f"💭 {followup}" + Style.RESET_ALL)
            
            return result
            
        except Exception as e:
            print(Fore.RED + f"\n❌ Error: {e}" + Style.RESET_ALL)
            print("Please try rephrasing your question or contact human support.")
            return None
    
    def run(self):
        """Main conversation loop"""
        self.print_header()
        
        # Check if input is piped (non-interactive)
        if not sys.stdin.isatty():
            # Read piped input
            piped_input = []
            try:
                for line in sys.stdin:
                    piped_input.append(line.strip())
            except:
                pass
            
            # Process piped input in non-interactive mode
            for query in piped_input:
                if query:
                    self.process_query(query)
                    if not self.running:
                        break
            return
        
        # Interactive mode
        while self.running:
            try:
                # Get user input
                user_input = input(Fore.BLUE + "You: " + Style.RESET_ALL).strip()
                
                if not user_input:
                    continue
                
                # Process query
                self.process_query(user_input)
                
            except KeyboardInterrupt:
                print(Fore.GREEN + "\n\n👋 Goodbye!" + Style.RESET_ALL)
                break
            except Exception as e:
                print(Fore.RED + f"\n❌ Unexpected error: {e}" + Style.RESET_ALL)

def main():
    """Entry point"""
    try:
        # Validate configuration
        print("Validating configuration...")
        config.validate()
        print("✓ Configuration valid")
        
        # Initialize database connection
        print("Connecting to database...")
        from src.database import db_service
        if not db_service.connect():
            print("⚠️  Database connection failed - order lookups will fallback to general responses")
        else:
            print("✓ Database connected")
        print()
        
        # Start CLI
        cli = CustomerSupportCLI()
        cli.run()
        
    except ValueError as e:
        print(Fore.RED + f"\n❌ Configuration Error: {e}" + Style.RESET_ALL)
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your API keys")
        print("3. Run 'python scripts/setup_faqs.py' to initialize the FAQ database")
        print("4. Run 'python scripts/setup_database.py' to initialize the order database")
        sys.exit(1)
    except Exception as e:
        print(Fore.RED + f"\n❌ Error: {e}" + Style.RESET_ALL)
        sys.exit(1)

if __name__ == "__main__":
    main()
