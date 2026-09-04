import React, { useEffect, useState } from 'react';
import { LifeBuoy, Plus, FileText } from 'lucide-react';
import { employeeExperienceApi, HRHelpdeskTicket, HRRequest } from '../services/api/employeeExperience';

export const HrHelpdeskPage: React.FC = () => {
  const [tickets, setTickets] = useState<HRHelpdeskTicket[]>([]);
  const [requests, setRequests] = useState<HRRequest[]>([]);
  const [activeTab, setActiveTab] = useState<'tickets' | 'requests'>('tickets');
  const [showModal, setShowModal] = useState(false);
  const [subject, setSubject] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('IT_HR');
  const [priority] = useState('MEDIUM');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [tData, rData] = await Promise.all([
        employeeExperienceApi.getHelpdeskTickets(),
        employeeExperienceApi.getHrRequests()
      ]);
      setTickets(tData);
      setRequests(rData);
    } catch (err) {
      console.error('Failed to load helpdesk data', err);
    }
  };

  const handleCreateTicket = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await employeeExperienceApi.createHelpdeskTicket({
        category,
        priority,
        subject,
        description
      });
      alert('Support ticket created successfully!');
      setShowModal(false);
      setSubject('');
      setDescription('');
      fetchData();
    } catch (err) {
      alert('Error creating ticket');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
            🛟 HR Request Center & Helpdesk Ticketing System
          </h1>
          <p className="text-xs text-slate-500 mt-1">Submit payroll queries, employment certificate requests, and IT/HR support tickets.</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs flex items-center gap-2 shadow-md shadow-emerald-600/20"
        >
          <Plus size={16} /> Raise HR Ticket / Request
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 text-xs font-extrabold gap-6">
        <button
          onClick={() => setActiveTab('tickets')}
          className={`pb-3 border-b-2 transition-all flex items-center gap-2 ${activeTab === 'tickets' ? 'border-emerald-600 text-emerald-600' : 'border-transparent text-slate-500'}`}
        >
          <LifeBuoy size={16} /> Support Tickets ({tickets.length})
        </button>
        <button
          onClick={() => setActiveTab('requests')}
          className={`pb-3 border-b-2 transition-all flex items-center gap-2 ${activeTab === 'requests' ? 'border-emerald-600 text-emerald-600' : 'border-transparent text-slate-500'}`}
        >
          <FileText size={16} /> HR Service Requests ({requests.length})
        </button>
      </div>

      {/* Tickets List */}
      {activeTab === 'tickets' && (
        <div className="space-y-4">
          {tickets.map(ticket => (
            <div key={ticket.id} className="glass-card p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-3 text-xs">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded bg-slate-900 text-white font-extrabold text-[10px]">{ticket.ticket_number}</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-extrabold text-[10px]">{ticket.category}</span>
                  <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-extrabold text-[10px]">{ticket.priority}</span>
                </div>
                <span className="px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800 font-bold text-[10px] uppercase">{ticket.status}</span>
              </div>

              <h3 className="font-extrabold text-sm text-slate-900">{ticket.subject}</h3>
              <p className="text-slate-600 bg-slate-50 p-3.5 rounded-xl border border-slate-200">{ticket.description}</p>
            </div>
          ))}
        </div>
      )}

      {/* New Ticket Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <form onSubmit={handleCreateTicket} className="bg-white rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <h3 className="font-extrabold text-base text-slate-900">Raise HR Support Ticket</h3>
              <button type="button" onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600 font-bold">✕</button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block font-extrabold text-slate-700 mb-1">Category</label>
                <select value={category} onChange={(e) => setCategory(e.target.value)} className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 font-bold">
                  <option value="PAYROLL">Payroll & Salary</option>
                  <option value="LEAVE">Leave & Attendance</option>
                  <option value="BENEFITS">Employee Benefits</option>
                  <option value="IT_HR">IT & HR Operations</option>
                </select>
              </div>

              <div>
                <label className="block font-extrabold text-slate-700 mb-1">Subject</label>
                <input type="text" value={subject} onChange={(e) => setSubject(e.target.value)} required className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 font-bold" />
              </div>

              <div>
                <label className="block font-extrabold text-slate-700 mb-1">Description</label>
                <textarea rows={4} value={description} onChange={(e) => setDescription(e.target.value)} required className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 font-bold" />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-slate-200">
              <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 rounded-xl border border-slate-300 text-slate-700 font-bold text-xs">Cancel</button>
              <button type="submit" className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs">Submit Ticket</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
