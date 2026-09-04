import React, { useEffect, useState } from 'react';
import { 
  Calendar, DollarSign, FileText, Bell, CheckCircle2, 
  Clock, ArrowRight, ShieldAlert, Sparkles, BookOpen, AlertCircle
} from 'lucide-react';
import { employeeExperienceApi, EmployeeDashboardSummary } from '../services/api/employeeExperience';

export const EmployeeDashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<EmployeeDashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const data = await employeeExperienceApi.getMyDashboard();
      setSummary(data);
    } catch (err) {
      console.error('Failed to load employee dashboard', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-emerald-700 via-teal-800 to-slate-900 p-8 text-white shadow-xl">
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 text-emerald-300 text-xs font-bold uppercase tracking-wider mb-2">
              <Sparkles size={16} /> Employee Self-Service Portal
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight">
              Welcome Back, {summary?.first_name} {summary?.last_name}! 👋
            </h1>
            <p className="text-slate-300 text-sm mt-1 max-w-2xl">
              {summary?.designation_name} • {summary?.department_name}
            </p>
          </div>

          <div className="flex items-center gap-3 bg-white/10 backdrop-blur-md p-3 rounded-2xl border border-white/20">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/30 flex items-center justify-center text-emerald-300 font-bold">
              <Clock size={20} />
            </div>
            <div>
              <div className="text-[11px] text-slate-300 uppercase font-extrabold">Today's Check-in</div>
              <div className="text-sm font-extrabold text-emerald-300 flex items-center gap-1.5">
                <CheckCircle2 size={14} /> {summary?.today_status} ({summary?.check_in_time})
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="glass-card p-5 rounded-2xl border border-slate-200/80 bg-white shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-extrabold text-slate-500 uppercase tracking-wider">Leave Balance</div>
            <div className="text-2xl font-black text-slate-900 mt-1">{summary?.leave_balance_days} Days</div>
            <div className="text-[11px] text-emerald-600 font-bold mt-1">Available Paid Leaves</div>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
            <Calendar size={24} />
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-200/80 bg-white shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-extrabold text-slate-500 uppercase tracking-wider">Latest Net Pay</div>
            <div className="text-2xl font-black text-slate-900 mt-1">₹{summary?.latest_net_pay_inr?.toLocaleString()}</div>
            <div className="text-[11px] text-slate-500 font-bold mt-1">{summary?.latest_payslip_month}</div>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-teal-100 text-teal-700 flex items-center justify-center font-bold">
            <DollarSign size={24} />
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-200/80 bg-white shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-extrabold text-slate-500 uppercase tracking-wider">Action Items</div>
            <div className="text-2xl font-black text-slate-900 mt-1">{summary?.pending_tasks_count} Tasks</div>
            <div className="text-[11px] text-amber-600 font-bold mt-1">Pending Approvals/Reviews</div>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-amber-100 text-amber-700 flex items-center justify-center font-bold">
            <FileText size={24} />
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-200/80 bg-white shadow-sm flex items-center justify-between">
          <div>
            <div className="text-xs font-extrabold text-slate-500 uppercase tracking-wider">Announcements</div>
            <div className="text-2xl font-black text-slate-900 mt-1">{summary?.unread_announcements_count} Unread</div>
            <div className="text-[11px] text-indigo-600 font-bold mt-1">Company Notices</div>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold">
            <Bell size={24} />
          </div>
        </div>
      </div>

      {/* Main Grid Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Self-Service Actions */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-card p-6 rounded-2xl border border-slate-200/80 bg-white shadow-sm">
            <h3 className="font-extrabold text-base text-slate-900 mb-4 flex items-center gap-2">
              ⚡ Quick Self-Service Operations
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              <a href="/leaves" className="p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-emerald-50 hover:border-emerald-300 transition-all text-center group">
                <div className="w-10 h-10 mx-auto rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Calendar size={20} />
                </div>
                <div className="font-extrabold text-xs text-slate-900 mt-2">Apply Leave</div>
              </a>

              <a href="/payslips" className="p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-teal-50 hover:border-teal-300 transition-all text-center group">
                <div className="w-10 h-10 mx-auto rounded-xl bg-teal-100 text-teal-700 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <DollarSign size={20} />
                </div>
                <div className="font-extrabold text-xs text-slate-900 mt-2">View Payslips</div>
              </a>

              <a href="/me/requests" className="p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-indigo-50 hover:border-indigo-300 transition-all text-center group">
                <div className="w-10 h-10 mx-auto rounded-xl bg-indigo-100 text-indigo-700 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <FileText size={20} />
                </div>
                <div className="font-extrabold text-xs text-slate-900 mt-2">HR Request</div>
              </a>

              <a href="/me/helpdesk" className="p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-rose-50 hover:border-rose-300 transition-all text-center group">
                <div className="w-10 h-10 mx-auto rounded-xl bg-rose-100 text-rose-700 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <ShieldAlert size={20} />
                </div>
                <div className="font-extrabold text-xs text-slate-900 mt-2">Raise Ticket</div>
              </a>

              <a href="/me/documents" className="p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-blue-50 hover:border-blue-300 transition-all text-center group">
                <div className="w-10 h-10 mx-auto rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <BookOpen size={20} />
                </div>
                <div className="font-extrabold text-xs text-slate-900 mt-2">HR Letters</div>
              </a>

              <a href="/policies" className="p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-purple-50 hover:border-purple-300 transition-all text-center group">
                <div className="w-10 h-10 mx-auto rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <CheckCircle2 size={20} />
                </div>
                <div className="font-extrabold text-xs text-slate-900 mt-2">Policies</div>
              </a>
            </div>
          </div>

          {/* Pending Tasks List */}
          <div className="glass-card p-6 rounded-2xl border border-slate-200/80 bg-white shadow-sm space-y-3">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-extrabold text-base text-slate-900 flex items-center gap-2">
                📋 Unified Action Tasks & Pending Reviews
              </h3>
              <a href="/me/tasks" className="text-xs font-bold text-emerald-600 hover:text-emerald-700 flex items-center gap-1">
                View All <ArrowRight size={14} />
              </a>
            </div>

            <div className="space-y-2 text-xs">
              <div className="p-3.5 rounded-xl border border-amber-200 bg-amber-50 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-amber-200 text-amber-900 flex items-center justify-center font-bold">
                    <AlertCircle size={16} />
                  </div>
                  <div>
                    <div className="font-extrabold text-slate-900">Acknowledge Remote Work Code of Conduct Policy (V2.1)</div>
                    <div className="text-[11px] text-slate-500">Mandatory HR compliance policy acknowledgement required.</div>
                  </div>
                </div>
                <a href="/policies" className="px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-700 text-white font-extrabold text-[11px]">
                  Review & Sign
                </a>
              </div>

              <div className="p-3.5 rounded-xl border border-slate-200 bg-slate-50 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold">
                    <Sparkles size={16} />
                  </div>
                  <div>
                    <div className="font-extrabold text-slate-900">Complete Q3 Performance Self-Assessment</div>
                    <div className="text-[11px] text-slate-500">Submit accomplishments and self-assessment for review.</div>
                  </div>
                </div>
                <a href="/performance/reviews" className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-extrabold text-[11px]">
                  Open Goal Review
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Right Sidebar: Announcements & Kudos */}
        <div className="space-y-6">
          <div className="glass-card p-6 rounded-2xl border border-slate-200/80 bg-white shadow-sm space-y-4">
            <h3 className="font-extrabold text-base text-slate-900 flex items-center gap-2">
              📢 Company Announcements
            </h3>
            <div className="space-y-3 text-xs">
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="px-2 py-0.5 rounded bg-indigo-100 text-indigo-800 font-extrabold text-[10px]">EVENT</span>
                  <span className="text-[10px] text-slate-400 font-bold">Today</span>
                </div>
                <div className="font-extrabold text-slate-900">🎉 Q3 AxonTimeHR All-Hands Enterprise Townhall</div>
                <p className="text-slate-600 text-[11px]">Join us this Friday at 4:00 PM IST for our quarterly product milestone launch.</p>
              </div>
            </div>
          </div>

          <div className="glass-card p-6 rounded-2xl border border-slate-200/80 bg-white shadow-sm space-y-4">
            <h3 className="font-extrabold text-base text-slate-900 flex items-center gap-2">
              🏆 Peer Recognition & Kudos
            </h3>
            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-full bg-emerald-600 text-white font-extrabold flex items-center justify-center text-[10px]">
                  AK
                </div>
                <div>
                  <div className="font-extrabold text-slate-900">Ananya Kapoor recognized you!</div>
                  <div className="text-[10px] text-emerald-700 font-bold">Badge: Great Work 🌟</div>
                </div>
              </div>
              <p className="text-slate-600 text-[11px] italic">"Awesome effort delivering Phase 10 HR Analytics ahead of schedule!"</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
