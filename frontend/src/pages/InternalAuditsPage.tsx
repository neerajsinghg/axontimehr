import React, { useEffect, useState } from 'react';
import { ClipboardCheck, Plus } from 'lucide-react';
import { complianceApi, InternalAudit } from '../services/api/compliance';

export const InternalAuditsPage: React.FC = () => {
  const [audits, setAudits] = useState<InternalAudit[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState('');
  const [auditType, setAuditType] = useState('LABOUR_LAW');
  const [auditor, setAuditor] = useState('');

  useEffect(() => {
    fetchAudits();
  }, []);

  const fetchAudits = async () => {
    try {
      const data = await complianceApi.getAudits();
      setAudits(data);
    } catch (err) {
      console.error('Failed to load audits', err);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await complianceApi.createAudit({
        audit_title: title,
        audit_type: auditType,
        auditor_name: auditor || 'Internal Audit Committee',
        start_date: '2026-10-01',
        end_date: '2026-10-15'
      });
      setShowModal(false);
      fetchAudits();
    } catch (err) {
      console.error('Failed to create audit', err);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
            <ClipboardCheck className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
            Internal Audit Planner & Checklist Engine
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Enterprise audit scope, auditor assignments & compliance checklist templates.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition"
        >
          <Plus className="w-4 h-4" />
          Plan Internal Audit
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {audits.map((a) => (
          <div key={a.id} className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
            <div className="flex justify-between items-center">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-800 dark:bg-indigo-900/40 dark:text-indigo-300">
                {a.audit_type}
              </span>
              <span className="text-xs font-bold text-emerald-600">Score: {a.checklist_score}%</span>
            </div>
            <h3 className="font-bold text-slate-900 dark:text-white">{a.audit_title}</h3>
            <p className="text-xs text-slate-500">Auditor: {a.auditor_name}</p>
            <div className="flex justify-between items-center text-xs text-slate-400 pt-2 border-t border-slate-100 dark:border-slate-700">
              <span>Period: {a.start_date} to {a.end_date}</span>
              <span className="font-semibold text-indigo-600">{a.status}</span>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 max-w-md w-full space-y-4">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">Plan Audit</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Audit Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded dark:bg-slate-700 dark:text-white text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Audit Type</label>
                <select
                  value={auditType}
                  onChange={(e) => setAuditType(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded dark:bg-slate-700 dark:text-white text-sm"
                >
                  <option value="LABOUR_LAW">Labour Law Audit</option>
                  <option value="PAYROLL">Payroll & Tax Audit</option>
                  <option value="PRIVACY">Data Privacy Audit</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Auditor Name</label>
                <input
                  type="text"
                  value={auditor}
                  onChange={(e) => setAuditor(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded dark:bg-slate-700 dark:text-white text-sm"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-sm text-slate-500">
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 bg-indigo-600 text-white font-semibold text-sm rounded">
                  Save Audit
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
