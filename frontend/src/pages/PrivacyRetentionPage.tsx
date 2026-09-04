import React, { useEffect, useState } from 'react';
import { Lock, FileText } from 'lucide-react';
import { complianceApi, DataSubjectRequest, LegalHold } from '../services/api/compliance';

export const PrivacyRetentionPage: React.FC = () => {
  const [dsrRequests, setDsrRequests] = useState<DataSubjectRequest[]>([]);
  const [holds, setHolds] = useState<LegalHold[]>([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [dData, hData] = await Promise.all([
        complianceApi.getDsrRequests(),
        complianceApi.getLegalHolds()
      ]);
      setDsrRequests(dData);
      setHolds(hData);
    } catch (err) {
      console.error('Failed to load privacy data', err);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
          <Lock className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
          Data Privacy, Consent & Legal Hold Center
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Data Subject Requests (DSR), retention rules & legal hold deletion overrides.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Data Subject Requests */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
          <h2 className="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-500" />
            Data Subject Requests (DSR)
          </h2>
          <div className="space-y-3">
            {dsrRequests.map((r) => (
              <div key={r.id} className="p-3 rounded-lg bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 flex justify-between items-center">
                <div>
                  <div className="font-mono text-xs font-bold text-slate-800 dark:text-white">{r.request_number}</div>
                  <div className="text-xs text-indigo-600 font-semibold">{r.request_type}</div>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">
                  {r.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Legal Holds */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
          <h2 className="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
            <Lock className="w-5 h-5 text-indigo-500" />
            Active Legal Holds (Purge Overrides)
          </h2>
          <div className="space-y-3">
            {holds.map((h) => (
              <div key={h.id} className="p-3 rounded-lg bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 space-y-1">
                <div className="font-bold text-sm text-slate-900 dark:text-white">{h.hold_name}</div>
                <p className="text-xs text-slate-500">{h.reason}</p>
                <div className="text-xs font-semibold text-emerald-600 pt-1">Active from {h.start_date}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
