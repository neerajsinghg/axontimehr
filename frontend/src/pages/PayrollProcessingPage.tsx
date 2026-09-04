import React, { useState, useEffect } from 'react';
import { Calculator, Play, Lock, CheckCircle2 } from 'lucide-react';
import { payrollApi, PayrollPeriod, PayrollRun, PayrollEmployee } from '../services/api/payroll';

export const PayrollProcessingPage: React.FC = () => {
  const [periods, setPeriods] = useState<PayrollPeriod[]>([]);
  const [selectedPeriodId, setSelectedPeriodId] = useState<string>('');
  const [activeRun, setActiveRun] = useState<PayrollRun | null>(null);
  const [processing, setProcessing] = useState<boolean>(false);
  const [selectedEmp, setSelectedEmp] = useState<PayrollEmployee | null>(null);

  // New Period State
  const [periodName, setPeriodName] = useState<string>('');
  const [year, setYear] = useState<number>(new Date().getFullYear());
  const [month, setMonth] = useState<number>(new Date().getMonth() + 1);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const periodList = await payrollApi.getPeriods();
      setPeriods(periodList);
      if (periodList.length > 0) {
        setSelectedPeriodId(periodList[0].id);
      }
    } catch (err) {
      console.error('Error fetching payroll periods:', err);
    }
  };

  const handleCreatePeriod = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!periodName) return;

    const startDate = `${year}-${month.toString().padStart(2, '0')}-01`;
    const lastDay = new Date(year, month, 0).getDate();
    const endDate = `${year}-${month.toString().padStart(2, '0')}-${lastDay}`;
    const payDate = endDate;

    try {
      setProcessing(true);
      await payrollApi.createPeriod({
        name: periodName,
        year,
        month,
        start_date: startDate,
        end_date: endDate,
        pay_date: payDate
      });
      setPeriodName('');
      fetchData();
    } catch (err) {
      console.error('Error creating payroll period:', err);
    } finally {
      setProcessing(false);
    }
  };

  const handleCreateRun = async () => {
    if (!selectedPeriodId) return;
    try {
      setProcessing(true);
      const run = await payrollApi.createRun(selectedPeriodId);
      setActiveRun(run);
    } catch (err) {
      console.error('Error initializing payroll run:', err);
    } finally {
      setProcessing(false);
    }
  };

  const handleCalculateRun = async () => {
    if (!activeRun) return;
    try {
      setProcessing(true);
      const run = await payrollApi.calculateRun(activeRun.id);
      setActiveRun(run);
    } catch (err) {
      console.error('Error calculating payroll run:', err);
    } finally {
      setProcessing(false);
    }
  };

  const handleLockRun = async () => {
    if (!activeRun) return;
    try {
      setProcessing(true);
      const run = await payrollApi.lockRun(activeRun.id);
      setActiveRun(run);
    } catch (err) {
      console.error('Error locking payroll run:', err);
    } finally {
      setProcessing(false);
    }
  };

  const handleMarkPaid = async () => {
    if (!activeRun) return;
    try {
      setProcessing(true);
      const run = await payrollApi.markRunPaid(activeRun.id);
      setActiveRun(run);
    } catch (err) {
      console.error('Error marking payroll run paid:', err);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white/60 backdrop-blur-md p-6 rounded-2xl border border-emerald-100 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <Calculator className="w-7 h-7 text-emerald-600" />
            Payroll Processing Workspace
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Calculate monthly salaries, verify statutory deductions, review exceptions, and lock payroll.
          </p>
        </div>

        {activeRun && (
          <div className="flex items-center gap-2">
            {activeRun.status === 'PROCESSING' && (
              <button
                onClick={handleCalculateRun}
                disabled={processing}
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-emerald-600 text-white rounded-xl font-medium shadow-md shadow-emerald-600/20 hover:bg-emerald-700 transition disabled:opacity-50"
              >
                <Play className="w-4 h-4" />
                {processing ? 'Calculating...' : 'Run Financial Calculation'}
              </button>
            )}

            {activeRun.status === 'PROCESSED' && (
              <button
                onClick={handleLockRun}
                disabled={processing}
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-amber-600 text-white rounded-xl font-medium shadow-md shadow-amber-600/20 hover:bg-amber-700 transition disabled:opacity-50"
              >
                <Lock className="w-4 h-4" />
                {processing ? 'Locking...' : 'Lock & Generate Payslips'}
              </button>
            )}

            {activeRun.status === 'LOCKED' && (
              <button
                onClick={handleMarkPaid}
                disabled={processing}
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-teal-600 text-white rounded-xl font-medium shadow-md shadow-teal-600/20 hover:bg-teal-700 transition disabled:opacity-50"
              >
                <CheckCircle2 className="w-4 h-4" />
                {processing ? 'Marking Paid...' : 'Mark Payroll Paid'}
              </button>
            )}
          </div>
        )}
      </div>

      {/* Period Selection & Run Setup */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Create Period Form */}
        <div className="bg-white/70 backdrop-blur-md p-6 rounded-2xl border border-emerald-100/80 shadow-sm space-y-4">
          <h2 className="text-base font-semibold text-slate-800">1. Initialize Payroll Period</h2>

          <form onSubmit={handleCreatePeriod} className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-slate-600 uppercase mb-1">Period Name</label>
              <input
                type="text"
                value={periodName}
                onChange={(e) => setPeriodName(e.target.value)}
                placeholder="e.g. September 2026 Payroll"
                required
                className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 text-sm"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-600 uppercase mb-1">Year</label>
                <input
                  type="number"
                  value={year}
                  onChange={(e) => setYear(parseInt(e.target.value))}
                  className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 uppercase mb-1">Month</label>
                <select
                  value={month}
                  onChange={(e) => setMonth(parseInt(e.target.value))}
                  className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 text-sm"
                >
                  {[...Array(12)].map((_, i) => (
                    <option key={i + 1} value={i + 1}>{new Date(2000, i, 1).toLocaleString('default', { month: 'long' })}</option>
                  ))}
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={processing}
              className="w-full py-2.5 bg-slate-800 hover:bg-slate-900 text-white font-medium rounded-xl text-sm transition"
            >
              Create Payroll Period
            </button>
          </form>
        </div>

        {/* Period Selector & Run Trigger */}
        <div className="lg:col-span-2 bg-white/70 backdrop-blur-md p-6 rounded-2xl border border-emerald-100/80 shadow-sm space-y-4 flex flex-col justify-between">
          <div>
            <h2 className="text-base font-semibold text-slate-800 mb-2">2. Active Payroll Run Target</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-600 uppercase mb-1">Select Period</label>
                <select
                  value={selectedPeriodId}
                  onChange={(e) => setSelectedPeriodId(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 text-sm"
                >
                  {periods.map((p) => (
                    <option key={p.id} value={p.id}>{p.name} ({p.status})</option>
                  ))}
                </select>
              </div>

              <div className="flex items-end">
                <button
                  onClick={handleCreateRun}
                  disabled={processing || !selectedPeriodId}
                  className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl text-sm transition disabled:opacity-50"
                >
                  Start New Calculation Run
                </button>
              </div>
            </div>
          </div>

          {activeRun && (
            <div className="p-4 bg-emerald-50/60 rounded-xl border border-emerald-100 grid grid-cols-4 gap-2 text-center text-sm">
              <div>
                <span className="text-xs text-slate-400 block">Employees</span>
                <span className="font-bold text-slate-800">{activeRun.total_employees}</span>
              </div>
              <div>
                <span className="text-xs text-slate-400 block">Total Gross</span>
                <span className="font-bold text-slate-800">₹{activeRun.total_gross.toLocaleString()}</span>
              </div>
              <div>
                <span className="text-xs text-slate-400 block">Deductions</span>
                <span className="font-bold text-rose-600">₹{activeRun.total_deductions.toLocaleString()}</span>
              </div>
              <div>
                <span className="text-xs text-slate-400 block">Net Payable</span>
                <span className="font-bold text-emerald-700">₹{activeRun.total_net.toLocaleString()}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Employees Table */}
      {activeRun && activeRun.employees && activeRun.employees.length > 0 && (
        <div className="bg-white/70 backdrop-blur-md p-6 rounded-2xl border border-emerald-100/80 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-800">Processed Employee Line Items</h2>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="bg-slate-50/80 border-b border-slate-200/80 text-xs font-semibold uppercase text-slate-500">
                  <th className="py-3 px-4">Employee</th>
                  <th className="py-3 px-4">Present / LOP</th>
                  <th className="py-3 px-4 text-right">Gross</th>
                  <th className="py-3 px-4 text-right">Deductions</th>
                  <th className="py-3 px-4 text-right">Net Payable</th>
                  <th className="py-3 px-4 text-center">Status</th>
                  <th className="py-3 px-4 text-center">Breakdown</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {activeRun.employees.map((emp) => (
                  <tr key={emp.id} className="hover:bg-slate-50/60 transition">
                    <td className="py-3.5 px-4 font-medium text-slate-800">
                      {emp.employee_name || emp.employee_code || 'Employee'}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 text-xs font-mono">
                      {emp.present_days}d Present • <span className="text-rose-600 font-bold">{emp.lop_days}d LOP</span>
                    </td>
                    <td className="py-3.5 px-4 text-right font-medium text-slate-700">₹{emp.gross_salary.toLocaleString()}</td>
                    <td className="py-3.5 px-4 text-right font-medium text-rose-600">₹{emp.total_deductions.toLocaleString()}</td>
                    <td className="py-3.5 px-4 text-right font-bold text-emerald-700">₹{emp.net_salary.toLocaleString()}</td>
                    <td className="py-3.5 px-4 text-center">
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold bg-emerald-100 text-emerald-800 px-2.5 py-0.5 rounded-full">
                        <CheckCircle2 className="w-3 h-3" />
                        {emp.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <button
                        onClick={() => setSelectedEmp(emp)}
                        className="px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium transition"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Breakdown Modal */}
      {selectedEmp && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-slate-800">
              Calculation Breakdown: {selectedEmp.employee_name}
            </h3>

            <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
              {selectedEmp.line_items.map((item) => (
                <div key={item.id} className="p-3 bg-slate-50 rounded-xl flex items-center justify-between text-xs">
                  <div>
                    <span className="font-semibold text-slate-800">{item.component_name}</span>
                    <p className="text-[11px] text-slate-500">{item.calculation_explanation}</p>
                  </div>
                  <span className={`font-bold ${item.line_type === 'EARNING' ? 'text-emerald-600' : 'text-rose-600'}`}>
                    ₹{item.amount.toLocaleString()}
                  </span>
                </div>
              ))}
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-between items-center text-sm font-bold">
              <span>NET SALARY PAYABLE</span>
              <span className="text-emerald-700 text-base">₹{selectedEmp.net_salary.toLocaleString()}</span>
            </div>

            <button
              onClick={() => setSelectedEmp(null)}
              className="w-full py-2.5 bg-slate-800 text-white rounded-xl text-sm font-medium hover:bg-slate-900 transition"
            >
              Close Breakdown
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
