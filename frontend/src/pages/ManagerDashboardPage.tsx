import React from 'react';
import { 
  Users, CheckCircle2, FileCheck, ArrowRight,
  TrendingUp
} from 'lucide-react';

export const ManagerDashboardPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 p-8 text-white shadow-xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <span className="text-indigo-400 text-xs font-bold uppercase tracking-wider">Manager Self-Service (MSS)</span>
            <h1 className="text-3xl font-black tracking-tight mt-1">Team Overview & Approval Inbox</h1>
            <p className="text-slate-300 text-sm mt-1">Monitor direct report attendance, pending team leaves, expense claims, and performance goals.</p>
          </div>
          <div className="px-4 py-2 rounded-2xl bg-white/10 border border-white/20 text-xs font-extrabold text-indigo-300">
            📊 Scope: Engineering Department (8 Direct Reports)
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="glass-card p-5 rounded-2xl border border-slate-200 bg-white shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-extrabold text-slate-500 uppercase">Team Headcount</div>
            <div className="text-2xl font-black text-slate-900 mt-1">8 Members</div>
            <div className="text-[11px] text-emerald-600 font-bold mt-1">100% Active</div>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold">
            <Users size={24} />
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-200 bg-white shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-extrabold text-slate-500 uppercase">Present Today</div>
            <div className="text-2xl font-black text-emerald-600 mt-1">7 Present</div>
            <div className="text-[11px] text-slate-500 font-bold mt-1">1 On Planned Leave</div>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
            <CheckCircle2 size={24} />
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-200 bg-white shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-extrabold text-slate-500 uppercase">Pending Approvals</div>
            <div className="text-2xl font-black text-amber-600 mt-1">4 Pending</div>
            <div className="text-[11px] text-amber-600 font-bold mt-1">Requires Your Action</div>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-amber-100 text-amber-700 flex items-center justify-center font-bold">
            <FileCheck size={24} />
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-200 bg-white shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-extrabold text-slate-500 uppercase">Avg Team Review</div>
            <div className="text-2xl font-black text-slate-900 mt-1">4.6 / 5.0</div>
            <div className="text-[11px] text-emerald-600 font-bold mt-1">High Performance</div>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-purple-100 text-purple-700 flex items-center justify-center font-bold">
            <TrendingUp size={24} />
          </div>
        </div>
      </div>

      {/* Centralized Approval Inbox Table */}
      <div className="glass-card p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <h3 className="font-extrabold text-base text-slate-900 flex items-center gap-2">
              📥 Centralized Manager Approval Inbox
            </h3>
            <p className="text-xs text-slate-500">Approve or reject pending leave requests, expense claims, and attendance regularizations.</p>
          </div>
          <a href="/approvals" className="px-3 py-1.5 rounded-xl bg-slate-900 text-white font-extrabold text-xs flex items-center gap-1">
            Open Full Inbox <ArrowRight size={14} />
          </a>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 text-slate-500 font-extrabold uppercase bg-slate-50">
                <th className="p-3">Module</th>
                <th className="p-3">Employee</th>
                <th className="p-3">Request Details</th>
                <th className="p-3">Submitted Date</th>
                <th className="p-3 text-right">Quick Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              <tr className="hover:bg-slate-50/80">
                <td className="p-3">
                  <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-extrabold text-[10px]">LEAVE</span>
                </td>
                <td className="p-3 font-bold text-slate-900">Rohan Verma (EMP-104)</td>
                <td className="p-3">Casual Leave (2 Days: Oct 12 - Oct 13)</td>
                <td className="p-3 text-slate-500">Yesterday, 4:30 PM</td>
                <td className="p-3 text-right space-x-2">
                  <button onClick={() => alert('Leave approved successfully!')} className="px-3 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-[11px]">Approve</button>
                  <button onClick={() => alert('Leave rejected.')} className="px-3 py-1 rounded-lg bg-slate-200 hover:bg-slate-300 text-slate-700 font-extrabold text-[11px]">Reject</button>
                </td>
              </tr>

              <tr className="hover:bg-slate-50/80">
                <td className="p-3">
                  <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-extrabold text-[10px]">EXPENSE</span>
                </td>
                <td className="p-3 font-bold text-slate-900">Priya Sharma (EMP-108)</td>
                <td className="p-3">Client Meeting Dinner & Cab Reimbursement (₹4,500)</td>
                <td className="p-3 text-slate-500">Today, 10:15 AM</td>
                <td className="p-3 text-right space-x-2">
                  <button onClick={() => alert('Expense claim approved!')} className="px-3 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-[11px]">Approve</button>
                  <button onClick={() => alert('Expense rejected.')} className="px-3 py-1 rounded-lg bg-slate-200 hover:bg-slate-300 text-slate-700 font-extrabold text-[11px]">Reject</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
