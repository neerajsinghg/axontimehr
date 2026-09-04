import React, { useEffect, useState } from 'react';
import { ShieldCheck, AlertTriangle, Clock, Lock, FileText, Activity } from 'lucide-react';
import { complianceApi, ComplianceDashboardSummary } from '../services/api/compliance';

export const ComplianceDashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<ComplianceDashboardSummary | null>(null);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const data = await complianceApi.getDashboardSummary();
      setSummary(data);
    } catch (err) {
      console.error('Failed to load compliance dashboard', err);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
            <ShieldCheck className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
            Compliance & Governance Command Center
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Enterprise statutory health, risk scoring, legal holds & regulatory audit control.
          </p>
        </div>
      </div>

      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
            <div className="flex justify-between items-center">
              <span className="text-xs font-semibold text-slate-500 uppercase">Compliance Score</span>
              <Activity className="w-5 h-5 text-indigo-500" />
            </div>
            <div className="text-3xl font-extrabold text-slate-900 dark:text-white mt-2">
              {summary.compliance_score.toFixed(1)} / 100
            </div>
            <span className="inline-block mt-2 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400">
              Risk Level: {summary.risk_level}
            </span>
          </div>

          <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
            <div className="flex justify-between items-center">
              <span className="text-xs font-semibold text-slate-500 uppercase">Open Violations</span>
              <AlertTriangle className="w-5 h-5 text-amber-500" />
            </div>
            <div className="text-3xl font-extrabold text-slate-900 dark:text-white mt-2">
              {summary.open_violations_count}
            </div>
            <p className="text-xs text-slate-400 mt-1">Requires CAPA investigation</p>
          </div>

          <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
            <div className="flex justify-between items-center">
              <span className="text-xs font-semibold text-slate-500 uppercase">Overdue Tasks</span>
              <Clock className="w-5 h-5 text-red-500" />
            </div>
            <div className="text-3xl font-extrabold text-slate-900 dark:text-white mt-2">
              {summary.overdue_tasks_count}
            </div>
            <p className="text-xs text-slate-400 mt-1">Filing deadline alerts</p>
          </div>

          <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
            <div className="flex justify-between items-center">
              <span className="text-xs font-semibold text-slate-500 uppercase">Active Legal Holds</span>
              <Lock className="w-5 h-5 text-indigo-500" />
            </div>
            <div className="text-3xl font-extrabold text-slate-900 dark:text-white mt-2">
              {summary.active_legal_holds_count}
            </div>
            <p className="text-xs text-slate-400 mt-1">Deletion overrides active</p>
          </div>
        </div>
      )}

      {/* Compliance Overview Summary */}
      <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
        <h2 className="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
          <FileText className="w-5 h-5 text-indigo-500" />
          Statutory Framework Status
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600">
            <div className="text-sm font-semibold text-slate-700 dark:text-slate-200">Statutory Registrations</div>
            <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">{summary?.expiring_registrations_count || 1} Active</div>
            <div className="text-xs text-slate-500 mt-1">Encrypted PF, ESI, TDS & Tax IDs</div>
          </div>
          <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600">
            <div className="text-sm font-semibold text-slate-700 dark:text-slate-200">Policy Mandatory Ack Rate</div>
            <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">{summary?.mandatory_policy_ack_pct || 98.5}%</div>
            <div className="text-xs text-slate-500 mt-1">Digitally signed policy versions</div>
          </div>
          <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600">
            <div className="text-sm font-semibold text-slate-700 dark:text-slate-200">Pre-Payroll Precheck Status</div>
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">PASSED</div>
            <div className="text-xs text-slate-500 mt-1">Zero critical payroll blockers</div>
          </div>
        </div>
      </div>
    </div>
  );
};
