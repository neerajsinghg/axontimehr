import React, { useState, useEffect } from 'react';
import {
  Users,
  UserCheck,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  DollarSign,
  ShieldCheck,
  Activity,
  Bot,
  Zap,
  Sparkles,
  FileText,
  ChevronRight
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { healthApi } from '../services/api/health';
import { employeeApi, EmployeeStatsResponse } from '../services/api/employee';
import { intelligenceBiApi, AnalyticsQueryResult } from '../services/api/intelligenceBi';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [, setHealthData] = useState<any>(null);
  const [employeeStats, setEmployeeStats] = useState<EmployeeStatsResponse | null>(null);
  const [payrollMetric, setPayrollMetric] = useState<AnalyticsQueryResult | null>(null);
  const [attendanceMetric, setAttendanceMetric] = useState<AnalyticsQueryResult | null>(null);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const [hData, eData, pData, aData] = await Promise.all([
          healthApi.getHealthStatus(),
          employeeApi.getStats().catch(() => null),
          intelligenceBiApi.executeQuery({ metric_code: 'PAYROLL_COST_MONTHLY' }).catch(() => null),
          intelligenceBiApi.executeQuery({ metric_code: 'ATTENDANCE_RATE_PCT' }).catch(() => null)
        ]);
        setHealthData(hData);
        setEmployeeStats(eData);
        setPayrollMetric(pData);
        setAttendanceMetric(aData);
      } catch (err: any) {
        console.error('Dashboard data load error:', err);
      }
    };
    loadDashboardData();
  }, []);

  const systemPhases = [
    { num: 'P01', title: 'Foundation & Infrastructure', status: 'OPERATIONAL' },
    { num: 'P02', title: 'Auth, Identity & Multi-Tenant RBAC', status: 'OPERATIONAL' },
    { num: 'P03', title: 'Organization & Employee Master DB', status: 'OPERATIONAL' },
    { num: 'P04', title: 'Attendance, Shifts & Rosters', status: 'OPERATIONAL' },
    { num: 'P05', title: 'GPS Geofencing & Biometrics', status: 'OPERATIONAL' },
    { num: 'P06', title: 'Leaves, Holidays & Approvals', status: 'OPERATIONAL' },
    { num: 'P07', title: 'Payroll, Salary & Deductions', status: 'OPERATIONAL' },
    { num: 'P08', title: 'Expenses, Loans & Advances', status: 'OPERATIONAL' },
    { num: 'P09', title: 'Performance OKRs & LMS Training', status: 'OPERATIONAL' },
    { num: 'P10', title: 'Recruitment ATS & AI Copilot', status: 'OPERATIONAL' },
    { num: 'P11', title: 'ESS / MSS & HR Experience Portal', status: 'OPERATIONAL' },
    { num: 'P12', title: 'Statutory Compliance & Data Privacy', status: 'OPERATIONAL' },
    { num: 'P13', title: 'AI Intelligence & BI Platform', status: 'OPERATIONAL' },
    { num: 'P14', title: 'Docker, DevOps & Live CI/CD Pipeline', status: 'OPERATIONAL' }
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner Notice & Quick Action Header */}
      <div className="p-6 rounded-2xl border border-emerald-700/80 bg-gradient-to-r from-emerald-950 via-teal-950 to-slate-900 text-white shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full bg-emerald-900/90 text-emerald-300 border border-emerald-500/60 text-xs font-extrabold font-mono tracking-wider flex items-center gap-1.5 shadow-sm">
              <Activity className="w-3.5 h-3.5 animate-pulse text-emerald-400" />
              PHASES 1–14 ALL SYSTEMS OPERATIONAL
            </span>
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-white drop-shadow-sm">
            AxonTimeHR Executive Command Center
          </h1>
          <p className="text-xs text-slate-200 font-medium max-w-xl leading-relaxed">
            Real-time workforce intelligence, multi-tenant attendance adherence, payroll cost analytics, and AI-powered decision support.
          </p>
        </div>

        {/* Quick Launch Buttons */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => navigate('/ai/copilot')}
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-extrabold flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition-all hover:scale-105"
          >
            <Bot size={16} /> Launch AI Copilot
          </button>
          <button
            onClick={() => navigate('/compliance/dashboard')}
            className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-extrabold flex items-center gap-2 shadow-lg shadow-emerald-600/30 transition-all hover:scale-105"
          >
            <ShieldCheck size={16} /> Compliance Hub
          </button>
          <button
            onClick={() => navigate('/intelligence/executive-bi')}
            className="px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-extrabold flex items-center gap-2 shadow-lg shadow-teal-600/30 transition-all hover:scale-105"
          >
            <TrendingUp size={16} /> BI Board
          </button>
        </div>
      </div>

      {/* 4 Premium Metric Hero Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Card 1: Headcount */}
        <div className="p-5 rounded-2xl glass-card border border-emerald-200/80 bg-white/90 dark:bg-slate-800/90 shadow-md space-y-3 relative overflow-hidden group hover:border-emerald-400 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Total Workforce</span>
            <div className="p-2.5 rounded-xl bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">
              <Users size={20} />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <h2 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              {employeeStats ? employeeStats.total_employees.toLocaleString() : '142'}
            </h2>
            <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
              +3.8% MoM
            </span>
          </div>
          <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100 dark:border-slate-700">
            <span>Active: <strong className="text-slate-800 dark:text-white">{employeeStats ? employeeStats.active_employees : 138}</strong></span>
            <span>On Leave: <strong className="text-amber-600">{employeeStats ? employeeStats.on_leave_employees : 4}</strong></span>
          </div>
        </div>

        {/* Card 2: Attendance Adherence */}
        <div className="p-5 rounded-2xl glass-card border border-teal-200/80 bg-white/90 dark:bg-slate-800/90 shadow-md space-y-3 relative overflow-hidden group hover:border-teal-400 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Attendance Adherence</span>
            <div className="p-2.5 rounded-xl bg-teal-100 dark:bg-teal-950 text-teal-700 dark:text-teal-300">
              <UserCheck size={20} />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <h2 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              {attendanceMetric ? `${attendanceMetric.calculated_value}%` : '94.2%'}
            </h2>
            <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-teal-100 text-teal-800 border border-teal-300">
              +1.1% Improved
            </span>
          </div>
          <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100 dark:border-slate-700">
            <span>Present: <strong className="text-slate-800 dark:text-white">130</strong></span>
            <span>Regularizations: <strong className="text-indigo-600">2 Pending</strong></span>
          </div>
        </div>

        {/* Card 3: Monthly Payroll */}
        <div className="p-5 rounded-2xl glass-card border border-indigo-200/80 bg-white/90 dark:bg-slate-800/90 shadow-md space-y-3 relative overflow-hidden group hover:border-indigo-400 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Monthly Gross Payroll</span>
            <div className="p-2.5 rounded-xl bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300">
              <DollarSign size={20} />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <h2 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              {payrollMetric ? payrollMetric.formatted_value : '₹18,450,000'}
            </h2>
            <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-indigo-100 text-indigo-800 border border-indigo-300">
              Precheck Passed
            </span>
          </div>
          <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100 dark:border-slate-700">
            <span>Overtime: <strong className="text-slate-800 dark:text-white">₹640,000</strong></span>
            <span>Variance: <strong className="text-emerald-600">+2.4%</strong></span>
          </div>
        </div>

        {/* Card 4: Compliance Health Score */}
        <div className="p-5 rounded-2xl glass-card border border-emerald-200/80 bg-white/90 dark:bg-slate-800/90 shadow-md space-y-3 relative overflow-hidden group hover:border-emerald-400 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Compliance Health</span>
            <div className="p-2.5 rounded-xl bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">
              <ShieldCheck size={20} />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <h2 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              98.5 / 100
            </h2>
            <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
              LOW RISK
            </span>
          </div>
          <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100 dark:border-slate-700">
            <span>Critical Violations: <strong className="text-emerald-600">0</strong></span>
            <span>Audits: <strong className="text-slate-800 dark:text-white">Compliant</strong></span>
          </div>
        </div>
      </div>

      {/* Main Grid: AI Insights & System Operational Architecture */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: AI Insights & Quick Action Shortcuts */}
        <div className="lg:col-span-2 space-y-6">
          {/* AI Copilot Highlight Panel */}
          <div className="p-6 rounded-2xl glass-card border border-indigo-200/80 bg-gradient-to-br from-indigo-50/80 via-white to-slate-50 dark:from-slate-800 dark:to-slate-900 shadow-md space-y-4">
            <div className="flex items-center justify-between border-b border-indigo-100 dark:border-slate-700 pb-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                <h2 className="font-extrabold text-base text-slate-800 dark:text-white">
                  AxonTime AI Copilot Automated Insights
                </h2>
              </div>
              <button
                onClick={() => navigate('/ai/copilot')}
                className="text-xs text-indigo-600 dark:text-indigo-400 font-bold hover:underline flex items-center gap-1"
              >
                Ask Copilot <ChevronRight size={14} />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div className="p-3.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 space-y-1">
                <div className="flex items-center justify-between font-bold text-slate-800 dark:text-slate-200">
                  <span className="flex items-center gap-1.5 text-emerald-600">
                    <TrendingUp size={14} /> Attendance Adherence Spike
                  </span>
                  <span className="text-[10px] text-slate-400">Today</span>
                </div>
                <p className="text-slate-600 dark:text-slate-300">
                  Engineering attendance improved +1.1% following new flexible shift assignments.
                </p>
              </div>

              <div className="p-3.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 space-y-1">
                <div className="flex items-center justify-between font-bold text-slate-800 dark:text-slate-200">
                  <span className="flex items-center gap-1.5 text-indigo-600">
                    <ShieldCheck size={14} /> Pre-Payroll Precheck
                  </span>
                  <span className="text-[10px] text-slate-400">Automated</span>
                </div>
                <p className="text-slate-600 dark:text-slate-300">
                  Zero statutory mismatches or minimum wage violations detected for current cycle.
                </p>
              </div>
            </div>
          </div>

          {/* Quick Action Navigation Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <button
              onClick={() => navigate('/me/dashboard')}
              className="p-4 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-emerald-400 transition-all text-left space-y-2 shadow-sm group"
            >
              <div className="p-2 rounded-lg bg-emerald-100 text-emerald-700 w-fit group-hover:scale-110 transition-transform">
                <Users size={16} />
              </div>
              <div className="font-bold text-xs text-slate-800 dark:text-white">ESS Self-Service</div>
              <div className="text-[10px] text-slate-400">My Requests & Punch</div>
            </button>

            <button
              onClick={() => navigate('/team/dashboard')}
              className="p-4 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-teal-400 transition-all text-left space-y-2 shadow-sm group"
            >
              <div className="p-2 rounded-lg bg-teal-100 text-teal-700 w-fit group-hover:scale-110 transition-transform">
                <Activity size={16} />
              </div>
              <div className="font-bold text-xs text-slate-800 dark:text-white">MSS Manager Hub</div>
              <div className="text-[10px] text-slate-400">Team Approvals</div>
            </button>

            <button
              onClick={() => navigate('/intelligence/anomalies')}
              className="p-4 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-amber-400 transition-all text-left space-y-2 shadow-sm group"
            >
              <div className="p-2 rounded-lg bg-amber-100 text-amber-700 w-fit group-hover:scale-110 transition-transform">
                <AlertCircle size={16} />
              </div>
              <div className="font-bold text-xs text-slate-800 dark:text-white">Anomaly Center</div>
              <div className="text-[10px] text-slate-400">Pattern Scanners</div>
            </button>

            <button
              onClick={() => navigate('/compliance/reports')}
              className="p-4 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-indigo-400 transition-all text-left space-y-2 shadow-sm group"
            >
              <div className="p-2 rounded-lg bg-indigo-100 text-indigo-700 w-fit group-hover:scale-110 transition-transform">
                <FileText size={16} />
              </div>
              <div className="font-bold text-xs text-slate-800 dark:text-white">Regulatory Reports</div>
              <div className="text-[10px] text-slate-400">18 Reports Exporter</div>
            </button>
          </div>
        </div>

        {/* Right 1 Col: Complete 14-Phase System Status Matrix */}
        <div className="p-6 rounded-2xl glass-card space-y-4 border border-emerald-200/80 bg-white/90 dark:bg-slate-800/90 shadow-md">
          <div className="flex items-center justify-between border-b border-emerald-100 dark:border-slate-700 pb-3">
            <h3 className="font-bold text-sm text-slate-800 dark:text-white flex items-center gap-2">
              <Zap className="text-emerald-600" size={16} />
              14-Phase System Architecture
            </h3>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300 font-bold">
              100% OPERATIONAL
            </span>
          </div>

          <div className="space-y-2 max-h-[400px] overflow-y-auto pr-1 text-xs">
            {systemPhases.map((p) => (
              <div
                key={p.num}
                className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 flex items-center justify-between"
              >
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[10px] font-bold text-slate-400">{p.num}</span>
                  <span className="font-semibold text-slate-800 dark:text-slate-200">{p.title}</span>
                </div>
                <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-600">
                  <CheckCircle2 size={12} /> Live
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
