import React, { useState, useEffect } from 'react';
import { Inbox, CheckCircle, XCircle, User } from 'lucide-react';
import { workflowApi, ApprovalItem } from '../services/api/workflow';

export const ApprovalInboxPage: React.FC = () => {
  const [items, setItems] = useState<ApprovalItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeFilter, setActiveFilter] = useState<'ALL' | 'LEAVE_REQUEST' | 'REGULARIZATION'>('ALL');
  const [selectedItem, setSelectedItem] = useState<ApprovalItem | null>(null);
  const [comments, setComments] = useState<string>('');
  const [actionLoading, setActionLoading] = useState<boolean>(false);

  useEffect(() => {
    loadInbox();
  }, []);

  const loadInbox = async () => {
    try {
      setLoading(true);
      const data = await workflowApi.getInbox();
      setItems(data);
    } catch (err) {
      console.error('Error loading approval inbox:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (action: 'APPROVE' | 'REJECT') => {
    if (!selectedItem) return;
    if (action === 'REJECT' && !comments.trim()) {
      alert('Please provide a comment explaining the rejection.');
      return;
    }

    try {
      setActionLoading(true);
      await workflowApi.processAction(selectedItem.instance_id, {
        action,
        comments
      });
      setSelectedItem(null);
      setComments('');
      loadInbox();
    } catch (err: any) {
      alert(err.response?.data?.detail || `Failed to ${action.toLowerCase()} request.`);
    } finally {
      setActionLoading(false);
    }
  };

  const filteredItems = items.filter((i) => {
    if (activeFilter === 'ALL') return true;
    return i.entity_type === activeFilter;
  });

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <Inbox className="text-emerald-600" /> My Approval Inbox
          </h1>
          <p className="text-sm text-slate-600">Review and action pending team requests (Leaves & Attendance Regularizations).</p>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-2 bg-slate-200/50 p-1.5 rounded-xl text-xs font-medium w-fit">
          <button
            onClick={() => setActiveFilter('ALL')}
            className={`px-3 py-1.5 rounded-lg transition-all ${activeFilter === 'ALL' ? 'bg-white text-emerald-800 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'}`}
          >
            All Requests ({items.length})
          </button>
          <button
            onClick={() => setActiveFilter('LEAVE_REQUEST')}
            className={`px-3 py-1.5 rounded-lg transition-all ${activeFilter === 'LEAVE_REQUEST' ? 'bg-white text-emerald-800 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'}`}
          >
            Leaves ({items.filter(i => i.entity_type === 'LEAVE_REQUEST').length})
          </button>
          <button
            onClick={() => setActiveFilter('REGULARIZATION')}
            className={`px-3 py-1.5 rounded-lg transition-all ${activeFilter === 'REGULARIZATION' ? 'bg-white text-emerald-800 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'}`}
          >
            Regularizations ({items.filter(i => i.entity_type === 'REGULARIZATION').length})
          </button>
        </div>
      </div>

      {/* Inbox List */}
      <div className="glass-card rounded-2xl p-6">
        {loading ? (
          <div className="text-center py-12 text-slate-500">Loading inbox requests...</div>
        ) : filteredItems.length === 0 ? (
          <div className="text-center py-12 text-slate-500 space-y-2">
            <CheckCircle className="mx-auto text-emerald-500" size={36} />
            <p className="font-semibold text-slate-700">Inbox is empty!</p>
            <p className="text-xs text-slate-400">All pending requests have been processed.</p>
          </div>
        ) : (
          <div className="divide-y divide-emerald-50">
            {filteredItems.map((item) => (
              <div
                key={item.instance_id}
                className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-emerald-50/40 p-3 rounded-xl transition-colors cursor-pointer"
                onClick={() => setSelectedItem(item)}
              >
                <div className="flex items-start gap-3">
                  <div className="p-2.5 bg-emerald-100/80 text-emerald-700 rounded-xl mt-0.5">
                    <User size={20} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-bold text-slate-800 text-sm">{item.requester_name}</h4>
                      <span className="px-2 py-0.5 text-[10px] font-semibold uppercase rounded-md bg-slate-100 text-slate-700">
                        {item.entity_type.replace('_', ' ')}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Workflow Step: <strong>{item.current_step_name}</strong> • Submitted: {new Date(item.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-center">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedItem(item);
                    }}
                    className="px-3 py-1.5 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 font-semibold text-xs rounded-lg transition-all"
                  >
                    Review Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Review Modal */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-card bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-5 animate-in fade-in zoom-in-95">
            <div className="flex justify-between items-center border-b border-emerald-100 pb-3">
              <h3 className="text-lg font-bold text-slate-800">Review Request</h3>
              <button onClick={() => setSelectedItem(null)} className="text-slate-400 hover:text-slate-600">✕</button>
            </div>

            <div className="space-y-3 text-sm">
              <div className="p-3 bg-emerald-50/50 rounded-xl space-y-1 text-xs">
                <p><strong>Employee:</strong> {selectedItem.requester_name}</p>
                <p><strong>Type:</strong> {selectedItem.entity_type}</p>
                <p><strong>Step:</strong> {selectedItem.current_step_name}</p>
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">Approver Comments / Remarks</label>
                <textarea
                  value={comments}
                  onChange={(e) => setComments(e.target.value)}
                  rows={3}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-emerald-200 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none text-xs"
                  placeholder="Enter comments (required for rejection)..."
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-3 border-t border-emerald-100">
              <button
                type="button"
                disabled={actionLoading}
                onClick={() => handleAction('REJECT')}
                className="px-4 py-2 bg-rose-50 text-rose-700 hover:bg-rose-100 font-semibold text-xs rounded-xl flex items-center gap-1"
              >
                <XCircle size={14} /> Reject Request
              </button>
              <button
                type="button"
                disabled={actionLoading}
                onClick={() => handleAction('APPROVE')}
                className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-xl shadow-md flex items-center gap-1"
              >
                <CheckCircle size={14} /> Approve Request
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
