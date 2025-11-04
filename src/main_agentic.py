"""
Main CLI interface using Agentic Router Architecture
"""
import sys
import os
from pathlib import Path
from colorama import init, Fore, Style
from typing import Dict, Any

# Initialize colorama for Windows
init()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import config
from src.agents.router_agent import router_agent

class AgenticCustomerSupportCLI:
    """Command-line interface using agentic router architecture"""
    
    def __init__(self):
        self.running = True
        self.interactive = sys.stdin.isatty()
        self.session_id = f"session_{id(self)}"
        self.current_agent = None
    
    def print_header(self):
        """Print welcome header"""
        if self.interactive:
            print("\n" + "=" * 60)
            print(Fore.CYAN + "🤖 Agentic Customer Support Assistant" + Style.RESET_ALL)
            print("=" * 60)
            print("\nPowered by intelligent router agent with full context awareness")
            print("Ask me about orders, shipping, returns, products, and more!")
            print("\nCommands:")
            print("  'quit' or 'exit' - End the conversation")
            print("  'summary' - View conversation summary")
            print("  'clear' - Clear screen")
            print("=" * 60 + "\n")
    
    def process_query(self, user_query: str) -> None:
        """
        Process query through agentic router
        
        Args:
            user_query: User's question
        """
        # Check for special commands
        query_lower = user_query.lower().strip()
        
        if query_lower in ['quit', 'exit', 'bye', 'goodbye']:
            if self.interactive:
                print(Fore.GREEN + "\n👋 Thank you for contacting support. Have a great day!" + Style.RESET_ALL)
            self.running = False
            return
        
        if query_lower == 'summary':
            self.print_conversation_summary()
            return
        
        if query_lower == 'clear' and self.interactive:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.print_header()
            return
        
        try:
            if self.interactive:
                print(Fore.YELLOW + "\n🔍 Analyzing query and routing..." + Style.RESET_ALL)
            
            # Route through agentic system
            routing_result = router_agent.route_query(self.session_id, user_query)
            
            # Extract routing information
            routing_decision = routing_result["routing_decision"]
            target_agent = routing_decision["target_agent"]
            reason = routing_decision["reason"]
            
            # Display routing decision
            if self.interactive:
                print(Fore.MAGENTA + f"\n🎯 Routing: {target_agent.upper()}" + Style.RESET_ALL)
                print(Fore.MAGENTA + f"   └─ {reason}" + Style.RESET_ALL)
            
            # Check for agent switch
            agent_switched = target_agent != self.current_agent
            if agent_switched and self.current_agent is not None:
                if self.interactive:
                    print(Fore.YELLOW + f"🤖 Agent switched from {self.current_agent} to {target_agent}" + Style.RESET_ALL)
            
            self.current_agent = target_agent
            
            # Display extracted order numbers
            entities = routing_result.get("entities", [])
            order_numbers = [e["value"] for e in entities if e["type"] == "order_number"]
            if order_numbers:
                if self.interactive:
                    print(Fore.GREEN + f"📦 Order ID(s): {', '.join(order_numbers)}" + Style.RESET_ALL)
                else:
                    print(f"[📦 Order ID(s): {', '.join(order_numbers)}]")
            
            # Get agent response based on routing
            response = self._get_agent_response(target_agent, user_query, routing_result)
            
            # Record response
            router_agent.handle_response(self.session_id, response, target_agent)
            
            # Display response
            if self.interactive:
                print("\n" + Fore.GREEN + "💬 Assistant:" + Style.RESET_ALL)
            print(response)
            
            # Display metadata
            intent = routing_result.get("intent", "unknown")
            confidence = routing_result.get("confidence", 0)
            meta_info = f"Intent: {intent} (Confidence: {confidence:.1%})"
            if self.interactive:
                print("\n" + Fore.CYAN + f"📊 {meta_info}" + Style.RESET_ALL)
            else:
                print(f"\n[{meta_info}]")
            
            # Display escalation level if applicable
            escalation_level = routing_decision.get("context", {}).get("escalation_level")
            if escalation_level and escalation_level == "high":
                if self.interactive:
                    print(Fore.YELLOW + f"⚠️  HIGH PRIORITY - Escalation initiated" + Style.RESET_ALL)
                else:
                    print("[⚠️  HIGH PRIORITY - Escalation initiated]")
            
            if self.interactive:
                print("\n" + Fore.MAGENTA + "Was this helpful? (y/n): " + Style.RESET_ALL, end='')
            
        except Exception as e:
            print(Fore.RED + f"\n❌ Error: {e}" + Style.RESET_ALL)
            import traceback
            traceback.print_exc()

    def _get_agent_response(self, agent_type: str, query: str, routing_result: Dict) -> str:
        """Execute appropriate agent handler"""
        context = routing_result.get("routing_decision", {}).get("context", {})
        
        if agent_type == "faq_agent":
            return self._handle_faq(query, context)
        elif agent_type == "order_handler":
            return self._handle_order(query, context)
        elif agent_type == "escalation_agent":
            return self._handle_escalation(query, context)
        else:
            return "I'm not sure how to help with that. Let me connect you with a human agent."

    def _handle_faq(self, query: str, context: Dict) -> str:
        """Handle FAQ queries"""
        from src.rag.pipeline import rag_pipeline
        
        result = rag_pipeline._search_faqs(user_query=query)
        return result.get("response", "I couldn't find an answer to that question. Let me connect you with support.")

    def _handle_order(self, query: str, context: Dict) -> str:
        """Handle order-related queries"""
        from src.database import db_service
        
        order_number = context.get("order_number")
        
        if not order_number:
            return "I'd be happy to help with your order! Could you please provide your order number? You can find it in your confirmation email."
        
        try:
            result = db_service.lookup_order(order_number)
            if result.found:
                return f"✅ Found order {order_number}!\n\n{db_service.format_order_summary(result.order)}"
            else:
                return result.message
        except Exception as e:
            return f"I'm having trouble accessing that order. Please verify the order number: {order_number}"

    def _handle_escalation(self, query: str, context: Dict) -> str:
        """Handle escalation/complaint queries"""
        escalation_level = context.get("escalation_level", "normal")
        
        if escalation_level == "high":
            return "🔴 PRIORITY SUPPORT INITIATED\n\nI understand this is urgent. A senior support specialist will be with you shortly to assist with your concern."
        else:
            return "Thank you for bringing this to our attention. A support specialist is being assigned to help you with your issue."

    def print_conversation_summary(self):
        """Print conversation summary"""
        summary = router_agent.get_conversation_summary(self.session_id)
        if not summary:
            print("No conversation history yet.")
            return
        
        print("\n" + Fore.CYAN + "=== Conversation Summary ===" + Style.RESET_ALL)
        print(f"Total messages: {summary.get('message_count', 0)}")
        
        if summary.get("order_numbers_mentioned"):
            print(f"Order numbers: {', '.join(summary['order_numbers_mentioned'])}")
        
        if summary.get("topics_discussed"):
            print(f"Topics: {', '.join(summary['topics_discussed'])}")
        
        print(Fore.CYAN + "\nRecent conversation:" + Style.RESET_ALL)
        for msg in summary.get("recent_messages", []):
            role = "You" if msg["role"] == "user" else "Agent"
            print(f"  {role}: {msg['content']}")
        print()

    def run(self):
        """Main conversation loop"""
        self.print_header()
        
        # Check if input is piped
        if not sys.stdin.isatty():
            piped_input = []
            try:
                for line in sys.stdin:
                    piped_input.append(line.strip())
            except:
                pass
            
            for query in piped_input:
                if query:
                    self.process_query(query)
                    if not self.running:
                        break
            return
        
        # Interactive mode
        while self.running:
            try:
                user_input = input(Fore.BLUE + "You: " + Style.RESET_ALL).strip()
                
                if not user_input:
                    continue
                
                self.process_query(user_input)
                
                if self.running:
                    try:
                        feedback = input().strip().lower()
                        if feedback == 'y':
                            print(Fore.GREEN + "😊 Great! Glad I could help!\n" + Style.RESET_ALL)
                        elif feedback == 'n':
                            print(Fore.YELLOW + "😔 Sorry about that. Let me try a different approach.\n" + Style.RESET_ALL)
                    except:
                        pass
                
            except KeyboardInterrupt:
                print(Fore.GREEN + "\n\n👋 Goodbye!" + Style.RESET_ALL)
                break
            except Exception as e:
                print(Fore.RED + f"\n❌ Unexpected error: {e}" + Style.RESET_ALL)

def main():
    """Entry point"""
    try:
        print("Validating configuration...")
        config.validate()
        print("✓ Configuration valid\n")
        
        print("Connecting to database...")
        from src.database import db_service
        if not db_service.connect():
            print("⚠️  Database connection failed - order lookups will use fallback responses")
        else:
            print("✓ Database connected\n")
        
        # Start CLI
        cli = AgenticCustomerSupportCLI()
        cli.run()
        
    except ValueError as e:
        print(Fore.RED + f"\n❌ Configuration Error: {e}" + Style.RESET_ALL)
        sys.exit(1)
    except Exception as e:
        print(Fore.RED + f"\n❌ Error: {e}" + Style.RESET_ALL)
        sys.exit(1)

if __name__ == "__main__":
    main()
