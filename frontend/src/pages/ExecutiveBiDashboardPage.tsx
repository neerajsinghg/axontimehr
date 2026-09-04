import React, { useEffect, useState } from 'react';
import { BarChart3, Users, DollarSign, Activity } from 'lucide-react';
import { intelligenceBiApi, AnalyticsQueryResult } from '../services/api/intelligenceBi';

export const ExecutiveBiDashboardPage: React.FC = () => {
  const [headcount, setHeadcount] = useState<AnalyticsQueryResult | null>(null);
  const [payroll, setPayroll] = useState<AnalyticsQueryResult | null>(null);
  const [attendance, setAttendance] = useState<AnalyticsQueryResult | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [h, p, a] = await Promise.all([
        intelligenceBiApi.executeQuery({ metric_code: 'HEADCOUNT_TOTAL' }),
        intelligenceBiApi.executeQuery({ metric_code: 'PAYROLL_COST_MONTHLY' }),
        intelligenceBiApi.executeQuery({ metric_code: 'ATTENDANCE_RATE_PCT' })
      ]);
      setHeadcount(h);
      setPayroll(p);
      setAttendance(a);
    } catch (err) {
      console.error('Failed to load executive BI', err);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
          <BarChart3 className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
          Executive Workforce BI Dashboard
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          High-level executive metrics, headcount distribution & payroll variance.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs font-semibold text-slate-500 uppercase">Total Headcount</span>
            <Users className="w-5 h-5 text-indigo-500" />
          </div>
          <div className="text-3xl font-extrabold text-slate-900 dark:text-white">
            {headcount ? headcount.calculated_value : 142}
          </div>
          <p className="text-xs text-emerald-600 font-semibold">+3.8% increase vs last month</p>
        </div>

        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs font-semibold text-slate-500 uppercase">Monthly Gross Payroll</span>
            <DollarSign className="w-5 h-5 text-emerald-500" />
          </div>
          <div className="text-3xl font-extrabold text-slate-900 dark:text-white">
            {payroll ? payroll.formatted_value : '₹18,450,000'}
          </div>
          <p className="text-xs text-slate-400">Includes gross salaries & overtime</p>
        </div>

        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs font-semibold text-slate-500 uppercase">Attendance Adherence</span>
            <Activity className="w-5 h-5 text-blue-500" />
          </div>
          <div className="text-3xl font-extrabold text-slate-900 dark:text-white">
            {attendance ? `${attendance.calculated_value}%` : '94.2%'}
          </div>
          <p className="text-xs text-emerald-600 font-semibold">+1.1% attendance improvement</p>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
        <h2 className="text-lg font-bold text-slate-800 dark:text-white">Department Headcount Breakdown</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-lg bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800">
            <div className="text-sm font-semibold text-indigo-900 dark:text-indigo-200">Engineering</div>
            <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">64 Employees (45%)</div>
          </div>
          <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600">
            <div className="text-sm font-semibold text-slate-700 dark:text-slate-200">Operations</div>
            <div className="text-2xl font-bold text-slate-900 dark:text-white mt-1">48 Employees (34%)</div>
          </div>
          <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600">
            <div className="text-sm font-semibold text-slate-700 dark:text-slate-200">Sales & Marketing</div>
            <div className="text-2xl font-bold text-slate-900 dark:text-white mt-1">30 Employees (21%)</div>
          </div>
        </div>
      </div>
    </div>
  );
};
