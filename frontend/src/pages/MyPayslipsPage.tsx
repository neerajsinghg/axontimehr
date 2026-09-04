import React, { useState, useEffect } from 'react';
import { FileText, Download, Calendar } from 'lucide-react';
import { payrollApi, Payslip } from '../services/api/payroll';

export const MyPayslipsPage: React.FC = () => {
  const [payslips, setPayslips] = useState<Payslip[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const data = await payrollApi.getPayslips();
      setPayslips(data);
    } catch (err) {
      console.error('Error fetching employee payslips:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (token: string) => {
    const url = payrollApi.downloadPayslipUrl(token);
    window.open(url, '_blank');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white/60 backdrop-blur-md p-6 rounded-2xl border border-emerald-100 shadow-sm">
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <FileText className="w-7 h-7 text-emerald-600" />
          My Salary & Payslips
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          View historical monthly payslips, salary breakdowns, and download official PDF statements.
        </p>
      </div>

      {/* Payslips Table */}
      <div className="bg-white/70 backdrop-blur-md p-6 rounded-2xl border border-emerald-100/80 shadow-sm space-y-4">
        <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-emerald-600" />
          Historical Payslips ({payslips.length})
        </h2>

        {loading ? (
          <div className="py-8 text-center text-slate-400">Loading your payslips...</div>
        ) : payslips.length === 0 ? (
          <div className="py-12 text-center text-slate-500 bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
            No payslips available yet. Once payroll is locked by HR, your payslips will appear here.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="bg-slate-50/80 border-b border-slate-200/80 text-xs font-semibold uppercase text-slate-500">
                  <th className="py-3 px-4">Payroll Period</th>
                  <th className="py-3 px-4">Generated Date</th>
                  <th className="py-3 px-4 text-center">Downloads</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {payslips.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-50/60 transition">
                    <td className="py-3.5 px-4 font-semibold text-slate-800">{p.period_name}</td>
                    <td className="py-3.5 px-4 text-slate-600 text-xs">
                      {new Date(p.generated_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
                    </td>
                    <td className="py-3.5 px-4 text-center text-xs font-mono text-slate-500">
                      {p.download_count} views
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => handleDownload(p.download_token)}
                        className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-medium shadow-sm transition"
                      >
                        <Download className="w-3.5 h-3.5" />
                        Download PDF Payslip
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
