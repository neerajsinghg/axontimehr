import React, { useEffect, useState } from 'react';
import { AlertTriangle, Plus } from 'lucide-react';
import { complianceApi, ComplianceViolation } from '../services/api/compliance';

export const ViolationsCapaPage: React.FC = () => {
  const [violations, setViolations] = useState<ComplianceViolation[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [code, setCode] = useState('');
  const [category, setCategory] = useState('MINIMUM_WAGE');
  const [desc, setDesc] = useState('');

  useEffect(() => {
    fetchViolations();
  }, []);

  const fetchViolations = async () => {
    try {
      const data = await complianceApi.getViolations();
      setViolations(data);
    } catch (err) {
      console.error('Failed to load violations', err);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await complianceApi.createViolation({
        violation_code: code || 'VIOL-001',
        category,
        description: desc
      });
      setShowModal(false);
      fetchViolations();
    } catch (err) {
      console.error('Failed to create violation', err);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
            <AlertTriangle className="w-7 h-7 text-amber-500" />
            Compliance Violations & CAPA Manager
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Corrective Action & Preventive Action (CAPA) tracking engine.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-amber-600 text-white font-semibold rounded-lg hover:bg-amber-700 transition"
        >
          <Plus className="w-4 h-4" />
          Log Compliance Violation
        </button>
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden shadow-sm">
        <table className="w-full text-left border-collapse text-sm">
          <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400">
            <tr>
              <th className="p-4 font-semibold">Violation Code</th>
              <th className="p-4 font-semibold">Category</th>
              <th className="p-4 font-semibold">Severity</th>
              <th className="p-4 font-semibold">Description</th>
              <th className="p-4 font-semibold">Detected Date</th>
              <th className="p-4 font-semibold">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
            {violations.map((v) => (
              <tr key={v.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/30">
                <td className="p-4 font-mono font-semibold text-slate-800 dark:text-slate-200">{v.violation_code}</td>
                <td className="p-4 font-semibold text-indigo-600 dark:text-indigo-400">{v.category}</td>
                <td className="p-4">
                  <span className="px-2 py-0.5 rounded text-xs font-bold bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400">
                    {v.severity}
                  </span>
                </td>
                <td className="p-4 text-slate-700 dark:text-slate-300">{v.description}</td>
                <td className="p-4 text-slate-500">{new Date(v.detected_date).toLocaleDateString()}</td>
                <td className="p-4">
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400">
                    {v.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 max-w-md w-full space-y-4">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">Log Violation</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Violation Code</label>
                <input
                  type="text"
                  required
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded dark:bg-slate-700 dark:text-white text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded dark:bg-slate-700 dark:text-white text-sm"
                >
                  <option value="MINIMUM_WAGE">Minimum Wage</option>
                  <option value="OVERTIME">Overtime Threshold</option>
                  <option value="PF_ESI">PF / ESI Withholding</option>
                  <option value="SAFETY">Occupational Safety</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Description</label>
                <textarea
                  required
                  value={desc}
                  onChange={(e) => setDesc(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded dark:bg-slate-700 dark:text-white text-sm"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-sm text-slate-500">
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 bg-amber-600 text-white font-semibold text-sm rounded">
                  Log Violation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
