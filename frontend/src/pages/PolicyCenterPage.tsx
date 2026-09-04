import React, { useEffect, useState } from 'react';
import { CheckCircle2, ShieldCheck } from 'lucide-react';
import { employeeExperienceApi, HRPolicy } from '../services/api/employeeExperience';

export const PolicyCenterPage: React.FC = () => {
  const [policies, setPolicies] = useState<HRPolicy[]>([]);

  useEffect(() => {
    fetchPolicies();
  }, []);

  const fetchPolicies = async () => {
    try {
      const data = await employeeExperienceApi.getHrPolicies();
      setPolicies(data);
    } catch (err) {
      console.error('Failed to load policies', err);
    }
  };

  const handleAcknowledge = async (id: string) => {
    try {
      await employeeExperienceApi.acknowledgePolicy(id);
      alert('Policy acknowledged successfully!');
      fetchPolicies();
    } catch (err) {
      alert('Error acknowledging policy');
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
          📜 Company Policies & Compliance Handbook
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Review official organizational policies, code of conduct, and sign electronic compliance acknowledgements.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
        {policies.map(policy => (
          <div key={policy.id} className="glass-card p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <span className="px-2.5 py-0.5 rounded-md bg-emerald-100 text-emerald-800 font-extrabold text-[10px] uppercase">
                  {policy.category} • V{policy.current_version}
                </span>
                <h3 className="font-extrabold text-base text-slate-900 mt-2">{policy.title}</h3>
              </div>
              {policy.is_acknowledged_by_me ? (
                <span className="flex items-center gap-1 text-emerald-600 font-extrabold text-xs">
                  <CheckCircle2 size={16} /> Signed
                </span>
              ) : (
                <span className="px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 font-bold text-[10px]">
                  Pending Signature
                </span>
              )}
            </div>

            <p className="text-slate-600 text-xs bg-slate-50 p-4 rounded-xl border border-slate-200 font-medium leading-relaxed">
              {policy.policy_body}
            </p>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => handleAcknowledge(policy.id)}
                className="px-5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-extrabold text-xs flex items-center gap-1.5 shadow-md"
              >
                <ShieldCheck size={16} /> Acknowledge & Sign Policy
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
