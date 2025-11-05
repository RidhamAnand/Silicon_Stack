import React from 'react';
import { User, CheckCircle, AlertCircle, Sparkles } from 'lucide-react';

const ChatMessage = ({ message, isUser }) => {
  const {
    content,
    intent,
    intent_confidence,
    entities = [],
    routing_path = [],
    metadata = {},
    agent,
    escalation_status,
    followup_question,
  } = message;

  // Determine agent info
  const getAgentInfo = () => {
    const currentAgent = agent || metadata?.current_agent;
    
    const agentConfig = {
      faq_agent: { name: 'FAQ', color: 'text-blue-600', bg: 'bg-blue-50' },
      order_query_agent: { name: 'Orders', color: 'text-purple-600', bg: 'bg-purple-50' },
      escalation_agent: { name: 'Support', color: 'text-red-600', bg: 'bg-red-50' },
      order_return_agent: { name: 'Returns', color: 'text-orange-600', bg: 'bg-orange-50' },
    };

    return agentConfig[currentAgent] || null;
  };

  const agentInfo = getAgentInfo();
  
  // Clean content
  const cleanContent = (text) => {
    if (!text) return text;
    const patterns = [/^🎫\s*$/m, /^📚\s*$/m, /^📦\s*$/m, /^↩️\s*$/m];
    let cleaned = text;
    patterns.forEach(pattern => {
      cleaned = cleaned.replace(pattern, '').trim();
    });
    return cleaned;
  };
  
  const displayContent = cleanContent(content);

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6 animate-fade-in`}>
      <div className={`flex max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-3`}>
        {/* Avatar - Only for assistant */}
        {!isUser && (
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center mt-1">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
        )}

        {/* Message Content */}
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} gap-2 w-full`}>
          {/* Agent Badge */}
          {!isUser && agentInfo && (
            <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${agentInfo.bg} ${agentInfo.color}`}>
              <span>{agentInfo.name}</span>
            </div>
          )}

          {/* Main Message */}
          <div
            className={`rounded-2xl px-5 py-3 max-w-full ${
              isUser
                ? 'bg-gray-900 text-white'
                : 'bg-gray-50 text-gray-900 border border-gray-100'
            }`}
          >
            <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{displayContent}</p>
          </div>

          {/* Escalation Status */}
          {escalation_status && !isUser && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-50 text-amber-700 rounded-full text-xs font-medium border border-amber-100">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>{escalation_status}</span>
            </div>
          )}

          {/* Metadata - Minimal display */}
          {!isUser && (intent || entities.length > 0) && (
            <div className="flex flex-wrap gap-2 text-xs text-gray-500">
              {intent && intent_confidence > 0.2 && (
                <span className="px-2 py-1 bg-gray-100 rounded-full">
                  {intent}
                </span>
              )}
              {entities.slice(0, 2).map((entity, idx) => (
                <span key={idx} className="px-2 py-1 bg-green-50 text-green-700 rounded-full border border-green-100">
                  {entity.value}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
