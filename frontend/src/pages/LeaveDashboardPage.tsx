import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  FileText, 
  Umbrella
} from 'lucide-react';
import { leaveApi, LeaveBalance, LeaveRequest } from '../services/api/leave';

export const LeaveDashboardPage: React.FC = () => {
  const [balances, setBalances] = useState<LeaveBalance[]>([]);
  const [requests, setRequests] = useState<LeaveRequest[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  // Form State
  const [leaveTypeId, setLeaveTypeId] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [durationType, setDurationType] = useState<'FULL_DAY' | 'HALF_DAY'>('FULL_DAY');
  const [halfDayPos, setHalfDayPos] = useState<'FIRST_HALF' | 'SECOND_HALF'>('FIRST_HALF');
  const [reason, setReason] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string>('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [balData, reqData] = await Promise.all([
        leaveApi.getBalances(),
        leaveApi.getLeaveRequests()
      ]);
      setBalances(balData);
      setRequests(reqData);
      if (balData.length > 0 && !leaveTypeId) {
        setLeaveTypeId(balData[0].leave_type_id);
      }
    } catch (err: any) {
      console.error('Error loading leave data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyLeave = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');

    if (!startDate || !endDate) {
      setErrorMsg('Please select both start and end dates.');
      return;
    }

    try {
      setSubmitting(true);
      await leaveApi.createLeaveRequest({
        leave_type_id: leaveTypeId,
        start_date: startDate,
        end_date: endDate,
        duration_type: durationType,
        half_day_position: durationType === 'HALF_DAY' ? halfDayPos : undefined,
        reason
      });
      setIsModalOpen(false);
      setReason('');
      loadData();
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to submit leave request.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancelLeave = async (id: string) => {
    if (!window.confirm('Are you sure you want to cancel this leave request?')) return;
    try {
      await leaveApi.cancelLeaveRequest(id);
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to cancel leave request.');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 flex items-center gap-1 w-fit"><CheckCircle size={12} /> Approved</span>;
      case 'PENDING':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-100 text-amber-800 flex items-center gap-1 w-fit"><Clock size={12} /> Pending</span>;
      case 'REJECTED':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-rose-100 text-rose-800 flex items-center gap-1 w-fit"><XCircle size={12} /> Rejected</span>;
      case 'CANCELLED':
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-slate-100 text-slate-700 flex items-center gap-1 w-fit"><AlertCircle size={12} /> Cancelled</span>;
      default:
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-slate-100 text-slate-700 w-fit">{status}</span>;
    }
  };

  return (
    <div className="space-y-6 p-6">
      {/* Top Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <Umbrella className="text-emerald-600" /> My Leave Dashboard
          </h1>
          <p className="text-sm text-slate-600">Track leave balances, apply for leave, and view request history.</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl shadow-lg shadow-emerald-600/20 transition-all flex items-center gap-2 w-fit"
        >
          <Plus size={18} /> Apply Leave
        </button>
      </div>

      {/* Leave Balance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-3 text-center py-8 text-slate-500">Loading leave balances...</div>
        ) : balances.length === 0 ? (
          <div className="col-span-3 glass-card p-6 rounded-2xl text-center text-slate-500">No leave policies assigned yet.</div>
        ) : (
          balances.map((b) => (
            <div key={b.id} className="glass-card p-6 rounded-2xl relative overflow-hidden">
              <div 
                className="absolute top-0 left-0 right-0 h-1.5" 
                style={{ backgroundColor: b.color_code || '#10B981' }} 
              />
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="font-semibold text-slate-800 text-lg">{b.leave_type_name}</h3>
                  <span className="text-xs font-mono text-slate-500 uppercase">{b.leave_type_code}</span>
                </div>
                <span className="text-2xl font-bold text-slate-900">{b.available} <span className="text-xs font-normal text-slate-500">Days</span></span>
              </div>
              <div className="space-y-2 text-xs text-slate-600">
                <div className="flex justify-between">
                  <span>Allocated: <strong>{b.allocated}</strong></span>
                  <span>Used: <strong>{b.used}</strong></span>
                  <span>Pending: <strong>{b.pending}</strong></span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-emerald-500 transition-all" 
                    style={{ width: `${Math.min(100, (b.used / (b.allocated || 1)) * 100)}%` }} 
                  />
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Leave History Table */}
      <div className="glass-card rounded-2xl p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <FileText size={18} className="text-emerald-600" /> Leave Application History
        </h2>
        {requests.length === 0 ? (
          <p className="text-slate-500 text-center py-6 text-sm">No leave applications found.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse">
              <thead>
                <tr className="border-b border-emerald-100 text-slate-500 text-xs font-semibold uppercase">
                  <th className="py-3 px-4">Leave Type</th>
                  <th className="py-3 px-4">Dates</th>
                  <th className="py-3 px-4">Duration</th>
                  <th className="py-3 px-4">Reason</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-emerald-50">
                {requests.map((r) => (
                  <tr key={r.id} className="hover:bg-emerald-50/40 transition-colors">
                    <td className="py-3.5 px-4">
                      <span className="font-semibold text-slate-800">{r.leave_type_name}</span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs text-slate-600">
                      {r.start_date} → {r.end_date}
                    </td>
                    <td className="py-3.5 px-4 text-slate-700 font-medium">
                      {r.working_days_count} Working Days {r.holiday_days_count > 0 && <span className="text-xs text-amber-600">({r.holiday_days_count} Holiday)</span>}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 max-w-xs truncate">{r.reason}</td>
                    <td className="py-3.5 px-4">{getStatusBadge(r.status)}</td>
                    <td className="py-3.5 px-4 text-right">
                      {(r.status === 'PENDING' || r.status === 'APPROVED') && (
                        <button
                          onClick={() => handleCancelLeave(r.id)}
                          className="text-xs text-rose-600 hover:text-rose-800 font-semibold underline"
                        >
                          Cancel
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Apply Leave Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-card bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-5 animate-in fade-in zoom-in-95">
            <div className="flex justify-between items-center border-b border-emerald-100 pb-3">
              <h3 className="text-lg font-bold text-slate-800">Apply for Leave</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-600">✕</button>
            </div>

            {errorMsg && (
              <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl flex items-center gap-2">
                <AlertCircle size={14} /> {errorMsg}
              </div>
            )}

            <form onSubmit={handleApplyLeave} className="space-y-4 text-sm">
              <div>
                <label className="block font-medium text-slate-700 mb-1">Leave Category</label>
                <select
                  value={leaveTypeId}
                  onChange={(e) => setLeaveTypeId(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-emerald-200 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none"
                >
                  {balances.map((b) => (
                    <option key={b.leave_type_id} value={b.leave_type_id}>
                      {b.leave_type_name} (Available: {b.available} Days)
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-slate-700 mb-1">Start Date</label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-emerald-200 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="block font-medium text-slate-700 mb-1">End Date</label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-emerald-200 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">Duration Type</label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="duration"
                      value="FULL_DAY"
                      checked={durationType === 'FULL_DAY'}
                      onChange={() => setDurationType('FULL_DAY')}
                      className="text-emerald-600"
                    />
                    Full Day
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="duration"
                      value="HALF_DAY"
                      checked={durationType === 'HALF_DAY'}
                      onChange={() => setDurationType('HALF_DAY')}
                      className="text-emerald-600"
                    />
                    Half Day
                  </label>
                </div>
              </div>

              {durationType === 'HALF_DAY' && (
                <div>
                  <label className="block font-medium text-slate-700 mb-1">Half Day Slot</label>
                  <select
                    value={halfDayPos}
                    onChange={(e) => setHalfDayPos(e.target.value as any)}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-emerald-200 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none"
                  >
                    <option value="FIRST_HALF">First Half (Morning)</option>
                    <option value="SECOND_HALF">Second Half (Afternoon)</option>
                  </select>
                </div>
              )}

              <div>
                <label className="block font-medium text-slate-700 mb-1">Reason for Leave</label>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  rows={3}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-emerald-200 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none"
                  placeholder="Provide brief reason..."
                  required
                />
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl shadow-md disabled:opacity-50"
                >
                  {submitting ? 'Submitting...' : 'Submit Request'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
