import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import TypingIndicator from './components/TypingIndicator';
import TicketsView from './components/TicketsView';
import { chatAPI } from './api/client';
import { AlertCircle, RefreshCw } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const [conversationClosed, setConversationClosed] = useState(false);
  const [showTicketPrompt, setShowTicketPrompt] = useState(false); // New state for ticket confirmation
  const [lastUserMessage, setLastUserMessage] = useState(''); // Store last message for ticket creation
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Auto-start conversation
  useEffect(() => {
    startConversation();
  }, []);

  const startConversation = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const data = await chatAPI.startConversation();
      setSessionId(data.session_id);
      
      setMessages([
        {
          content: data.welcome_message,
          isUser: false,
          metadata: {},
        },
      ]);
    } catch (err) {
      setError('Failed to start conversation. Please refresh the page.');
      console.error('Error starting conversation:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (messageText) => {
    if (!sessionId || conversationClosed) return;

    const userMessage = {
      content: messageText,
      isUser: true,
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);
    setError(null);
    setLastUserMessage(messageText); // Store for potential ticket creation

    try {
      const response = await chatAPI.sendMessage(sessionId, messageText);

      const assistantMessage = {
        content: response.response,
        isUser: false,
        intent: response.intent,
        intent_confidence: response.intent_confidence,
        entities: response.entities,
        routing_path: response.routing_path,
        metadata: response.metadata,
        agent: response.metadata?.current_agent,
        escalation_status: response.metadata?.pending_action || response.escalation_status,
        followup_question: response.followup_question,
      };

      // Only replace default order number in TICKET SUMMARY, not in conversation prompts
      if (assistantMessage.content && 
          assistantMessage.content.includes('SUPPORT TICKET CREATED') &&
          assistantMessage.content.includes('Order: ORD-1234-5678')) {
        assistantMessage.content = assistantMessage.content.replace(/Order: ORD-1234-5678/g, '');
      }

      setMessages((prev) => [...prev, assistantMessage]);

      console.log('[Frontend] Conversation state:', {
        current_agent: response.metadata?.current_agent,
        pending_action: response.metadata?.pending_action,
        collected_details: response.metadata?.collected_details,
        should_create_ticket: response.should_create_ticket
      });

      // Check if system suggests creating a ticket
      if (response.should_create_ticket && !response.metadata?.current_agent) {
        console.log('[Frontend] Showing ticket confirmation prompt');
        setShowTicketPrompt(true); // Show confirmation prompt
      }

      // Check if ticket was created
      if (response.conversation_closed) {
        setConversationClosed(true);
        
        // Save ticket to localStorage
        if (response.response.includes('Ticket ID:')) {
          const ticketMatch = response.response.match(/Ticket ID:\s*([A-Z0-9-]+)/);
          if (ticketMatch) {
            const ticketId = ticketMatch[1];
            
            // Get order number and clean it if it's the default
            let orderNumber = response.metadata?.collected_details?.order_number;
            if (orderNumber === 'ORD-1234-5678') {
              orderNumber = null;
            }
            
            const ticket = {
              ticket_id: ticketId,
              reason: response.metadata?.collected_details?.reason || messageText,
              email: response.metadata?.collected_details?.email,
              order_number: orderNumber || 'No related order',
              priority: response.metadata?.collected_details?.priority || 'medium',
              status: 'open',
              created_at: new Date().toISOString(),
            };
            
            const existingTickets = JSON.parse(localStorage.getItem('support_tickets') || '[]');
            existingTickets.push(ticket);
            localStorage.setItem('support_tickets', JSON.stringify(existingTickets));
          }
        }
        
        console.log('[Frontend] Conversation closed');
      }
    } catch (err) {
      setError('Failed to send message. Please try again.');
      console.error('Error sending message:', err);
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsTyping(false);
    }
  };

  const handleRestart = () => {
    setSessionId(null);
    setMessages([]);
    setConversationClosed(false);
    setError(null);
    setShowTicketPrompt(false);
    setLastUserMessage('');
    startConversation();
  };

  // Handle ticket creation confirmation
  const handleCreateTicket = async (confirm) => {
    setShowTicketPrompt(false);
    
    if (!confirm) {
      // User declined - send a message to continue conversation
      const userMessage = {
        content: 'No, I\'ll try rephrasing',
        isUser: true,
      };
      setMessages((prev) => [...prev, userMessage]);
      return;
    }
    
    // User confirmed - use escalate endpoint to activate escalation agent
    const userMessage = {
      content: 'Yes, create a support ticket',
      isUser: true,
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    try {
      // Use the escalate endpoint instead of regular message
      const response = await chatAPI.escalateConversation(sessionId, lastUserMessage);

      const assistantMessage = {
        content: response.response,
        isUser: false,
        agent: 'escalation_agent',
        escalation_status: response.escalation_status,
        metadata: response.metadata,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      console.log('[Frontend] Escalation activated:', {
        escalation_status: response.escalation_status,
        conversation_closed: response.conversation_closed,
      });

      // Check if conversation closed after creating ticket
      if (response.conversation_closed) {
        setConversationClosed(true);
        
        // Save ticket if created
        if (response.response.includes('Ticket ID:')) {
          const ticketMatch = response.response.match(/Ticket ID:\s*([A-Z0-9-]+)/);
          if (ticketMatch) {
            const ticketId = ticketMatch[1];
            
            // Get order number and clean it if it's the default
            let orderNumber = response.metadata?.collected_details?.order_number;
            if (orderNumber === 'ORD-1234-5678') {
              orderNumber = null;
            }
            
            const ticket = {
              ticket_id: ticketId,
              reason: response.metadata?.collected_details?.reason || lastUserMessage,
              email: response.metadata?.collected_details?.email,
              order_number: orderNumber || 'No related order',
              priority: response.metadata?.collected_details?.priority || 'medium',
              status: 'open',
              created_at: new Date().toISOString(),
            };
            
            const existingTickets = JSON.parse(localStorage.getItem('support_tickets') || '[]');
            existingTickets.push(ticket);
            localStorage.setItem('support_tickets', JSON.stringify(existingTickets));
          }
        }
      }
    } catch (err) {
      setError('Failed to create ticket. Please try again.');
      console.error('Error creating ticket:', err);
    } finally {
      setIsTyping(false);
    }
  };

  // Chat Interface
  return (
    <div className="min-h-screen bg-white flex flex-col">
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />

      {activeTab === 'tickets' ? (
        <TicketsView />
      ) : (
        <main className="flex-1 flex flex-col max-w-4xl w-full mx-auto">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto custom-scrollbar px-6 py-8">
            {messages.map((msg, idx) => (
              <ChatMessage key={idx} message={msg} isUser={msg.isUser} />
            ))}
            
            {isTyping && <TypingIndicator />}
            
            {/* Ticket Creation Prompt */}
            {showTicketPrompt && !conversationClosed && (
              <div className="flex justify-center mb-6 animate-fade-in">
                <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6 max-w-md">
                  <div className="text-amber-600 text-2xl mb-3">📋</div>
                  <h3 className="font-heading font-semibold text-gray-900 mb-2">
                    Create a Support Ticket?
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    I couldn't find a clear answer in our FAQ. Would you like me to create a support ticket for personalized assistance?
                  </p>
                  <div className="flex gap-3">
                    <button
                      onClick={() => handleCreateTicket(true)}
                      className="flex-1 bg-gray-900 text-white py-2.5 px-4 rounded-full text-sm font-medium hover:bg-gray-800 transition-colors"
                    >
                      Yes, Create Ticket
                    </button>
                    <button
                      onClick={() => handleCreateTicket(false)}
                      className="flex-1 bg-white border border-gray-300 text-gray-700 py-2.5 px-4 rounded-full text-sm font-medium hover:bg-gray-50 transition-colors"
                    >
                      No Thanks
                    </button>
                  </div>
                </div>
              </div>
            )}
            
            {conversationClosed && (
              <div className="text-center py-8">
                <div className="inline-block bg-green-50 border border-green-200 rounded-2xl p-8 max-w-md">
                  <div className="text-green-600 text-4xl mb-3">✓</div>
                  <h3 className="text-lg font-heading font-semibold text-gray-900 mb-2">
                    Ticket Created
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Your support ticket has been created. Check the Tickets tab to view it.
                  </p>
                  <button
                    onClick={handleRestart}
                    className="btn-primary flex items-center gap-2 mx-auto"
                  >
                    <RefreshCw className="w-4 h-4" />
                    New Conversation
                  </button>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Error Display */}
          {error && (
            <div className="mx-6 mb-4 bg-red-50 border border-red-200 rounded-2xl p-4 flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
              <p className="text-red-800 flex-1 text-sm">{error}</p>
              <button
                onClick={() => setError(null)}
                className="text-red-600 hover:text-red-800"
              >
                ×
              </button>
            </div>
          )}

          {/* Input Area */}
          {!conversationClosed && (
            <div className="border-t border-gray-100 px-6 py-4 bg-white">
              <ChatInput
                onSendMessage={handleSendMessage}
                disabled={isTyping || !sessionId}
                placeholder={
                  isTyping
                    ? 'AI is thinking...'
                    : 'Message AI Support...'
                }
              />
            </div>
          )}
        </main>
      )}
    </div>
  );
}

export default App;
