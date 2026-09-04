import React from 'react';
import { FileSpreadsheet, Download } from 'lucide-react';

export const ComplianceReportsPage: React.FC = () => {
  const reportsList = [
    { title: 'Compliance Summary Report', code: 'REP-COMP-001', cat: 'Executive Summary' },
    { title: 'Statutory Registration Status', code: 'REP-COMP-002', cat: 'Registrations' },
    { title: 'Employee Statutory Profiles', code: 'REP-COMP-003', cat: 'Employee Data' },
    { title: 'Minimum Wage Safety Report', code: 'REP-COMP-004', cat: 'Payroll Compliance' },
    { title: 'Overtime & Rest Period Audit', code: 'REP-COMP-005', cat: 'Attendance Compliance' },
    { title: 'Policy Acknowledgement Audit', code: 'REP-COMP-006', cat: 'Governance' },
    { title: 'CAPA Violations Ledger', code: 'REP-COMP-007', cat: 'Violations' },
    { title: 'Internal Audit Summary', code: 'REP-COMP-008', cat: 'Audits' },
    { title: 'Data Privacy & Consent Register', code: 'REP-COMP-009', cat: 'Privacy' },
    { title: 'Legal Hold Retention Audit', code: 'REP-COMP-010', cat: 'Data Retention' }
  ];

  const handleExport = (reportCode: string) => {
    alert(`Exporting regulatory report [${reportCode}] in CSV/PDF format...`);
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
          <FileSpreadsheet className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
          18 Regulatory Compliance Reports Exporter
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Export certified compliance audit reports in CSV, XLSX, and PDF formats.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {reportsList.map((r) => (
          <div key={r.code} className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex justify-between items-center">
            <div>
              <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 uppercase">{r.cat}</span>
              <h3 className="font-bold text-slate-900 dark:text-white mt-0.5">{r.title}</h3>
              <p className="text-xs font-mono text-slate-400 mt-0.5">{r.code}</p>
            </div>
            <button
              onClick={() => handleExport(r.code)}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded hover:bg-indigo-50 hover:text-indigo-600 transition"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
