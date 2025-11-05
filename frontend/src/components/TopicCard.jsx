import React from 'react';
import { Package, CreditCard, Truck, User, HelpCircle, Gift, Shield, Settings, MessageCircle, ShoppingBag } from 'lucide-react';

const TopicCard = ({ topic, onClick }) => {
  const iconMap = {
    '🚚': <Truck className="w-6 h-6" />,
    '↩️': <Package className="w-6 h-6" />,
    '💳': <CreditCard className="w-6 h-6" />,
    '👤': <User className="w-6 h-6" />,
    '📦': <ShoppingBag className="w-6 h-6" />,
    '📋': <HelpCircle className="w-6 h-6" />,
    '🎁': <Gift className="w-6 h-6" />,
    '💬': <MessageCircle className="w-6 h-6" />,
    '🔒': <Shield className="w-6 h-6" />,
    '⚙️': <Settings className="w-6 h-6" />,
  };

  return (
    <button
      onClick={() => onClick(topic)}
      className="group card hover:shadow-lg transition-all duration-300 hover:-translate-y-1 cursor-pointer border-2 border-transparent hover:border-primary-500"
    >
      <div className="flex flex-col items-center text-center gap-3">
        <div className="p-3 bg-primary-50 rounded-full group-hover:bg-primary-100 transition-colors">
          {iconMap[topic.icon] || <HelpCircle className="w-6 h-6" />}
        </div>
        <h3 className="font-semibold text-gray-800 group-hover:text-primary-600 transition-colors">
          {topic.name}
        </h3>
      </div>
    </button>
  );
};

export default TopicCard;
