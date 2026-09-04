import React, { useEffect, useState } from 'react';
import { ShieldCheck } from 'lucide-react';
import { intelligenceBiApi, DataQualityIssue } from '../services/api/intelligenceBi';

export const DataQualityAuditPage: React.FC = () => {
  const [issues, setIssues] = useState<DataQualityIssue[]>([]);

  useEffect(() => {
    fetchIssues();
  }, []);

  const fetchIssues = async () => {
    try {
      const data = await intelligenceBiApi.getDataQualityIssues();
      setIssues(data);
    } catch (err) {
      console.error('Failed to load data quality issues', err);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
          <ShieldCheck className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
          Data Quality Audit & Diagnostics Center
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Automated data integrity checks detecting orphan records, missing managers & statutory gaps.
        </p>
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden shadow-sm">
        <table className="w-full text-left border-collapse text-sm">
          <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400">
            <tr>
              <th className="p-4 font-semibold">Issue Type</th>
              <th className="p-4 font-semibold">Severity</th>
              <th className="p-4 font-semibold">Description</th>
              <th className="p-4 font-semibold">Affected Entity</th>
              <th className="p-4 font-semibold">Detected At</th>
              <th className="p-4 font-semibold">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
            {issues.map((i) => (
              <tr key={i.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/30">
                <td className="p-4 font-mono font-semibold text-slate-800 dark:text-slate-200">{i.issue_type}</td>
                <td className="p-4">
                  <span className="px-2 py-0.5 rounded text-xs font-bold bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400">
                    {i.severity}
                  </span>
                </td>
                <td className="p-4 text-slate-700 dark:text-slate-300">{i.description}</td>
                <td className="p-4 text-slate-600 dark:text-slate-400">{i.affected_entity_type} ({i.affected_entity_id})</td>
                <td className="p-4 text-slate-500">{new Date(i.detected_at).toLocaleDateString()}</td>
                <td className="p-4">
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400">
                    {i.is_resolved ? 'RESOLVED' : 'ACTIVE'}
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
