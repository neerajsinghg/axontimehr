import React, { useEffect, useState } from 'react';
import { Calendar, Plus, Clock } from 'lucide-react';
import { complianceApi, ComplianceTask } from '../services/api/compliance';

export const ComplianceCalendarTasksPage: React.FC = () => {
  const [tasks, setTasks] = useState<ComplianceTask[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState('');
  const [complianceType, setComplianceType] = useState('TAX_FILING');
  const [dueDate, setDueDate] = useState('');
  const [priority] = useState('MEDIUM');

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const data = await complianceApi.getTasks();
      setTasks(data);
    } catch (err) {
      console.error('Failed to load tasks', err);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await complianceApi.createTask({
        title,
        compliance_type: complianceType,
        due_date: dueDate || '2026-10-15',
        priority
      });
      setShowModal(false);
      fetchTasks();
    } catch (err) {
      console.error('Failed to create task', err);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
            <Calendar className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
            Compliance Calendar & Task Evidence Inbox
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Filing deadlines, task assignments & document evidence repository.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition"
        >
          <Plus className="w-4 h-4" />
          Create Compliance Task
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {tasks.map((t) => (
          <div key={t.id} className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
            <div className="flex justify-between items-start">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-800 dark:bg-indigo-900/40 dark:text-indigo-300">
                {t.compliance_type}
              </span>
              <span className="px-2 py-0.5 rounded text-xs font-bold bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400">
                {t.priority}
              </span>
            </div>
            <h3 className="font-bold text-slate-900 dark:text-white">{t.title}</h3>
            {t.description && <p className="text-xs text-slate-500">{t.description}</p>}
            <div className="flex justify-between items-center text-xs text-slate-500 pt-2 border-t border-slate-100 dark:border-slate-700">
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" /> Due: {t.due_date}
              </span>
              <span className="font-semibold text-emerald-600">{t.status}</span>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 max-w-md w-full space-y-4">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">Create Compliance Task</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Task Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded dark:bg-slate-700 dark:text-white text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Compliance Type</label>
                <select
                  value={complianceType}
                  onChange={(e) => setComplianceType(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded dark:bg-slate-700 dark:text-white text-sm"
                >
                  <option value="TAX_FILING">Tax Filing</option>
                  <option value="PF_RETURNS">Provident Fund Returns</option>
                  <option value="LABOUR_AUDIT">Labour Audit</option>
                  <option value="SAFETY_INSPECTION">Safety Inspection</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Due Date</label>
                <input
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded dark:bg-slate-700 dark:text-white text-sm"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-sm text-slate-500"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 text-white font-semibold text-sm rounded"
                >
                  Save Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
