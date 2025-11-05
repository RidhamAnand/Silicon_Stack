import React, { useState, useEffect } from 'react';
import { Ticket, Clock, Mail, Package, AlertCircle, CheckCircle2, X } from 'lucide-react';

const TicketsView = () => {
  const [tickets, setTickets] = useState([]);
  
  // Load tickets from localStorage
  useEffect(() => {
    const storedTickets = localStorage.getItem('support_tickets');
    if (storedTickets) {
      try {
        const parsed = JSON.parse(storedTickets);
        setTickets(parsed);
      } catch (e) {
        console.error('Failed to parse tickets:', e);
      }
    }
  }, []);

  const getPriorityColor = (priority) => {
    const colors = {
      urgent: 'text-red-700 bg-red-50 border-red-200',
      high: 'text-orange-700 bg-orange-50 border-orange-200',
      medium: 'text-yellow-700 bg-yellow-50 border-yellow-200',
      low: 'text-green-700 bg-green-50 border-green-200',
    };
    return colors[priority?.toLowerCase()] || colors.medium;
  };

  const getStatusColor = (status) => {
    const colors = {
      open: 'text-blue-700 bg-blue-50 border-blue-200',
      in_progress: 'text-purple-700 bg-purple-50 border-purple-200',
      resolved: 'text-green-700 bg-green-50 border-green-200',
      closed: 'text-gray-700 bg-gray-50 border-gray-200',
    };
    return colors[status] || colors.open;
  };

  if (tickets.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-20">
        <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mb-4">
          <Ticket className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-heading font-semibold text-gray-900 mb-2">
          No tickets yet
        </h3>
        <p className="text-sm text-gray-500 text-center max-w-sm">
          When you escalate a conversation or create a support ticket, it will appear here.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <div className="mb-6">
        <h2 className="text-2xl font-heading font-semibold text-gray-900 mb-2">
          Support Tickets
        </h2>
        <p className="text-sm text-gray-500">
          Track and manage your support requests
        </p>
      </div>

      <div className="space-y-4">
        {tickets.map((ticket, idx) => (
          <div
            key={idx}
            className="card hover:shadow-md transition-shadow duration-200"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0 mt-1">
                  <Ticket className="w-5 h-5 text-gray-600" />
                </div>
                <div>
                  <h3 className="font-heading font-semibold text-gray-900 mb-1">
                    {ticket.ticket_id}
                  </h3>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      className={`px-2.5 py-1 rounded-full text-xs font-medium border ${getPriorityColor(
                        ticket.priority
                      )}`}
                    >
                      {ticket.priority?.toUpperCase() || 'MEDIUM'}
                    </span>
                    <span
                      className={`px-2.5 py-1 rounded-full text-xs font-medium border ${getStatusColor(
                        ticket.status || 'open'
                      )}`}
                    >
                      {ticket.status?.replace('_', ' ').toUpperCase() || 'OPEN'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-3 mb-4">
              <div className="flex items-start gap-2 text-sm">
                <AlertCircle className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                <div>
                  <span className="text-gray-500">Issue:</span>
                  <p className="text-gray-900 mt-0.5">{ticket.reason || ticket.issue || 'N/A'}</p>
                </div>
              </div>

              {ticket.order_number && ticket.order_number !== 'No related order' && (
                <div className="flex items-center gap-2 text-sm">
                  <Package className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  <span className="text-gray-500">Order:</span>
                  <span className="text-gray-900 font-medium">{ticket.order_number}</span>
                </div>
              )}

              {ticket.email && (
                <div className="flex items-center gap-2 text-sm">
                  <Mail className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  <span className="text-gray-500">Contact:</span>
                  <span className="text-gray-900">{ticket.email}</span>
                </div>
              )}

              {ticket.created_at && (
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Clock className="w-4 h-4 flex-shrink-0" />
                  <span>
                    Created {new Date(ticket.created_at).toLocaleDateString()} at{' '}
                    {new Date(ticket.created_at).toLocaleTimeString()}
                  </span>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-gray-100">
              <p className="text-xs text-gray-500">
                Our team will contact you at {ticket.email} within 24 hours.
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TicketsView;
