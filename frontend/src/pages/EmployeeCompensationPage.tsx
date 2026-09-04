import React, { useState, useEffect } from 'react';
import { UserCheck, Award, Plus } from 'lucide-react';
import { payrollApi, SalaryStructure, EmployeeSalaryAssignment } from '../services/api/payroll';

export const EmployeeCompensationPage: React.FC = () => {
  const [structures, setStructures] = useState<SalaryStructure[]>([]);

  // Assignment Form State
  const [employeeId, setEmployeeId] = useState<string>('');
  const [selectedStructureId, setSelectedStructureId] = useState<string>('');
  const [annualCtc, setAnnualCtc] = useState<string>('840000');
  const [effectiveFrom, setEffectiveFrom] = useState<string>(new Date().toISOString().split('T')[0]);
  const [assigning, setAssigning] = useState<boolean>(false);
  const [recentAssignment, setRecentAssignment] = useState<EmployeeSalaryAssignment | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const structs = await payrollApi.getStructures();
      setStructures(structs);
      if (structs.length > 0) {
        setSelectedStructureId(structs[0].id);
      }
    } catch (err) {
      console.error('Error fetching compensation structures:', err);
    }
  };

  const handleAssignSalary = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!employeeId || !selectedStructureId || !annualCtc) return;

    try {
      setAssigning(true);
      const res = await payrollApi.assignSalary({
        employee_id: employeeId,
        salary_structure_id: selectedStructureId,
        annual_ctc: parseFloat(annualCtc),
        effective_from: effectiveFrom
      });
      setRecentAssignment(res);
    } catch (err) {
      console.error('Error assigning salary structure:', err);
    } finally {
      setAssigning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white/60 backdrop-blur-md p-6 rounded-2xl border border-emerald-100 shadow-sm">
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <UserCheck className="w-7 h-7 text-emerald-600" />
          Employee Compensation & Salary Assignments
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          Assign salary structures, version CTC updates, and manage effective dates.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Assignment Form */}
        <div className="bg-white/70 backdrop-blur-md p-6 rounded-2xl border border-emerald-100/80 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
            <Plus className="w-5 h-5 text-emerald-600" />
            Assign Salary Structure to Employee
          </h2>

          <form onSubmit={handleAssignSalary} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 uppercase mb-1">Employee UUID</label>
              <input
                type="text"
                value={employeeId}
                onChange={(e) => setEmployeeId(e.target.value)}
                placeholder="Paste Employee ID UUID..."
                required
                className="w-full px-3.5 py-2.5 bg-slate-50/80 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 font-mono text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 uppercase mb-1">Salary Structure</label>
              <select
                value={selectedStructureId}
                onChange={(e) => setSelectedStructureId(e.target.value)}
                required
                className="w-full px-3.5 py-2.5 bg-slate-50/80 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 text-sm"
              >
                {structures.map((s) => (
                  <option key={s.id} value={s.id}>{s.name} ({s.code})</option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-600 uppercase mb-1">Annual CTC (₹)</label>
                <input
                  type="number"
                  value={annualCtc}
                  onChange={(e) => setAnnualCtc(e.target.value)}
                  placeholder="840000"
                  required
                  className="w-full px-3.5 py-2.5 bg-slate-50/80 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 uppercase mb-1">Effective From</label>
                <input
                  type="date"
                  value={effectiveFrom}
                  onChange={(e) => setEffectiveFrom(e.target.value)}
                  required
                  className="w-full px-3.5 py-2.5 bg-slate-50/80 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 text-sm"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={assigning || structures.length === 0}
              className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl shadow-md shadow-emerald-600/20 transition disabled:opacity-50"
            >
              {assigning ? 'Assigning...' : 'Assign Compensation Structure'}
            </button>
          </form>
        </div>

        {/* Assignment Result Card */}
        <div className="bg-white/70 backdrop-blur-md p-6 rounded-2xl border border-emerald-100/80 shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
              <Award className="w-5 h-5 text-emerald-600" />
              Active Assignment Breakdown
            </h2>

            {recentAssignment ? (
              <div className="space-y-4 bg-emerald-50/40 p-4 rounded-xl border border-emerald-100">
                <div className="flex justify-between items-center pb-2 border-b border-emerald-200/60">
                  <span className="text-xs text-slate-500 uppercase font-semibold">Status</span>
                  <span className="text-xs font-bold bg-emerald-100 text-emerald-800 px-2.5 py-0.5 rounded-full">
                    {recentAssignment.status} (v{recentAssignment.version})
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-xs text-slate-400 block">Annual CTC</span>
                    <span className="font-bold text-slate-800 text-base">₹{recentAssignment.annual_ctc.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-xs text-slate-400 block">Monthly Gross Base</span>
                    <span className="font-bold text-emerald-600 text-base">₹{recentAssignment.gross_salary.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-xs text-slate-400 block">Effective From</span>
                    <span className="font-medium text-slate-700">{recentAssignment.effective_from}</span>
                  </div>
                  <div>
                    <span className="text-xs text-slate-400 block">Structure</span>
                    <span className="font-medium text-slate-700">{recentAssignment.structure_name || 'Standard'}</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-slate-500 bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
                Assign a salary structure on the left to preview effective breakdown.
              </div>
            )}
          </div>

          <div className="text-xs text-slate-400 mt-4 text-center">
            Salary structure versioning preserves historical payroll calculations automatically.
          </div>
        </div>
      </div>
    </div>
  );
};
