import React, { useEffect, useState } from 'react';
import { ArrowRight, AlertCircle } from 'lucide-react';
import { employeeExperienceApi, UnifiedTaskItem } from '../services/api/employeeExperience';

export const UnifiedTasksPage: React.FC = () => {
  const [tasks, setTasks] = useState<UnifiedTaskItem[]>([]);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const data = await employeeExperienceApi.getUnifiedTasks();
      setTasks(data);
    } catch (err) {
      console.error('Failed to load unified tasks', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
          📋 Unified Task Inbox & Action Center
        </h1>
        <p className="text-xs text-slate-500 mt-1">Aggregated task presentation layer consolidating pending approvals, policy acknowledgements, goal self-reviews, and assigned training.</p>
      </div>

      <div className="glass-card p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-4">
        <div className="space-y-3 text-xs">
          {tasks.map(task => (
            <div key={task.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100/80 flex items-center justify-between transition-all">
              <div className="flex items-center gap-4">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold ${task.priority === 'HIGH' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}`}>
                  <AlertCircle size={20} />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-slate-900 text-white font-extrabold text-[10px]">{task.module}</span>
                    <span className="font-extrabold text-slate-900 text-sm">{task.title}</span>
                  </div>
                  <p className="text-slate-500 text-xs mt-0.5">{task.description}</p>
                </div>
              </div>

              <a
                href={task.action_url}
                className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs flex items-center gap-1.5 shadow-md shadow-emerald-600/20"
              >
                Complete Task <ArrowRight size={14} />
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
