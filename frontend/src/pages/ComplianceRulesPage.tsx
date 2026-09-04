import React, { useEffect, useState } from 'react';
import { Sliders, Play, CheckCircle2 } from 'lucide-react';
import { complianceApi, ComplianceRule, PrePayrollPrecheckResponse } from '../services/api/compliance';

export const ComplianceRulesPage: React.FC = () => {
  const [rules, setRules] = useState<ComplianceRule[]>([]);
  const [precheck, setPrecheck] = useState<PrePayrollPrecheckResponse | null>(null);

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      const data = await complianceApi.getRules();
      setRules(data);
    } catch (err) {
      console.error('Failed to load rules', err);
    }
  };

  const handleRunPrecheck = async () => {
    try {
      const res = await complianceApi.runPayrollPrecheck();
      setPrecheck(res);
    } catch (err) {
      console.error('Failed to run precheck', err);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
            <Sliders className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
            Effective-Dated Compliance Rules & Payroll Precheck
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Versioned statutory tax rulesets & pre-payroll compliance pre-check engine.
          </p>
        </div>
        <button
          onClick={handleRunPrecheck}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition"
        >
          <Play className="w-4 h-4" />
          Run Pre-Payroll Precheck
        </button>
      </div>

      {precheck && (
        <div className="bg-indigo-50 dark:bg-indigo-950/40 p-4 rounded-xl border border-indigo-200 dark:border-indigo-800 space-y-2">
          <div className="flex justify-between items-center">
            <h3 className="font-bold text-indigo-900 dark:text-indigo-200 flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-indigo-600" />
              Precheck Result: {precheck.status}
            </h3>
            <span className="text-xs font-semibold text-indigo-700 dark:text-indigo-300">
              Employees Checked: {precheck.total_employees_checked}
            </span>
          </div>
          <p className="text-xs text-indigo-700 dark:text-indigo-300">
            Detected Issues: {precheck.issues_count}
          </p>
        </div>
      )}

      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden shadow-sm">
        <table className="w-full text-left border-collapse text-sm">
          <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400">
            <tr>
              <th className="p-4 font-semibold">Rule Code</th>
              <th className="p-4 font-semibold">Rule Name</th>
              <th className="p-4 font-semibold">Category</th>
              <th className="p-4 font-semibold">Jurisdiction</th>
              <th className="p-4 font-semibold">Effective From</th>
              <th className="p-4 font-semibold">Version</th>
              <th className="p-4 font-semibold">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
            {rules.map((rule) => (
              <tr key={rule.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/30">
                <td className="p-4 font-mono font-semibold text-slate-800 dark:text-slate-200">{rule.rule_code}</td>
                <td className="p-4 text-slate-700 dark:text-slate-300">{rule.rule_name}</td>
                <td className="p-4 font-semibold text-indigo-600 dark:text-indigo-400">{rule.category}</td>
                <td className="p-4 text-slate-600 dark:text-slate-400">{rule.country_code} ({rule.state_code})</td>
                <td className="p-4 text-slate-600 dark:text-slate-400">{rule.effective_from}</td>
                <td className="p-4 font-semibold">v{rule.version}</td>
                <td className="p-4">
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400">
                    {rule.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
