import React from 'react';
import { Layout, Plus, BarChart, PieChart, LineChart } from 'lucide-react';

export const CustomDashboardBuilderPage: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
            <Layout className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
            Custom Drag & Drop BI Dashboard Builder
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Build custom Executive, HR, and Manager boards with metric widget grids.
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition">
          <Plus className="w-4 h-4" />
          Add Metric Widget
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-700 flex flex-col items-center justify-center text-center py-12 space-y-2">
          <BarChart className="w-8 h-8 text-indigo-500" />
          <h3 className="font-bold text-slate-800 dark:text-white">Headcount Trend Widget</h3>
          <p className="text-xs text-slate-400">Bar Chart Widget</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-700 flex flex-col items-center justify-center text-center py-12 space-y-2">
          <PieChart className="w-8 h-8 text-emerald-500" />
          <h3 className="font-bold text-slate-800 dark:text-white">Department Ratio Widget</h3>
          <p className="text-xs text-slate-400">Pie Chart Widget</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-700 flex flex-col items-center justify-center text-center py-12 space-y-2">
          <LineChart className="w-8 h-8 text-blue-500" />
          <h3 className="font-bold text-slate-800 dark:text-white">Overtime Growth Widget</h3>
          <p className="text-xs text-slate-400">Line Chart Widget</p>
        </div>
      </div>
    </div>
  );
};
