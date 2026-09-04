import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Clock,
  Calendar,
  CalendarDays,
  FileText,
  Settings,
  Bell,
  Search,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  Activity,
  ShieldCheck,
  Building2,
  LogOut,
  Calculator,
  DollarSign,
  Wallet,
  Receipt,
  PiggyBank,
  Briefcase,
  LifeBuoy,
  Megaphone,
} from 'lucide-react';
import { healthApi, HealthResponse } from '../services/api/health';
import { useAuth } from '../context/AuthContext';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

interface SubMenuItem {
  label: string;
  path: string;
  icon: any;
  active: boolean;
  badge?: string;
}

interface MenuCategory {
  categoryLabel: string;
  icon: any;
  items: SubMenuItem[];
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [healthStatus, setHealthStatus] = useState<HealthResponse | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const location = useLocation();
  const { user, logout } = useAuth();

  const [openCategories, setOpenCategories] = useState<{ [key: string]: boolean }>({});

  const toggleCategory = (catLabel: string) => {
    setOpenCategories((prev) => ({ ...prev, [catLabel]: !prev[catLabel] }));
  };

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const data = await healthApi.getHealthStatus();
        setHealthStatus(data);
      } catch (err) {
        console.error('Failed to fetch health status:', err);
      } finally {
        setHealthLoading(false);
      }
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const menuCategories: MenuCategory[] = [
    {
      categoryLabel: 'CORE HR & WORKFORCE',
      icon: LayoutDashboard,
      items: [
        { label: 'Dashboard Overview', path: '/', icon: LayoutDashboard, active: location.pathname === '/' || location.pathname === '/dashboard' },
        { label: 'Employee Directory', path: '/employees', icon: Users, active: location.pathname === '/employees' },
        { label: 'Holiday Calendar', path: '/holidays', icon: Building2, active: location.pathname === '/holidays' },
        { label: 'Organization Settings', path: '/settings', icon: Settings, active: location.pathname === '/settings' },
      ]
    },
    {
      categoryLabel: 'ATTENDANCE & PAYROLL',
      icon: Clock,
      items: [
        { label: 'Attendance & Shifts', path: '/attendance', icon: Clock, active: location.pathname === '/attendance' },
        { label: 'Leaves & Balances', path: '/leaves', icon: CalendarDays, active: location.pathname === '/leaves' },
        { label: 'Approval Inbox', path: '/approvals', icon: FileText, active: location.pathname === '/approvals' },
        { label: 'Payroll Processing', path: '/payroll/processing', icon: Calculator, active: location.pathname === '/payroll/processing' },
        { label: 'Salary Structures', path: '/salary-structures', icon: DollarSign, active: location.pathname === '/salary-structures' },
        { label: 'My Payslips', path: '/payslips', icon: FileText, active: location.pathname === '/payslips' },
      ]
    },
    {
      categoryLabel: 'FINANCIAL & EXPENSES',
      icon: Wallet,
      items: [
        { label: 'Expense Claims', path: '/expenses', icon: Receipt, active: location.pathname === '/expenses' },
        { label: 'Employee Loans', path: '/loans', icon: PiggyBank, active: location.pathname === '/loans' },
        { label: 'Salary Advances', path: '/salary-advances', icon: DollarSign, active: location.pathname === '/salary-advances' },
        { label: 'Financial Ledger', path: '/financial-reports', icon: Activity, active: location.pathname === '/financial-reports' },
      ]
    },
    {
      categoryLabel: 'PERFORMANCE & LEARNING',
      icon: Activity,
      items: [
        { label: 'Performance Hub', path: '/performance', icon: Activity, active: location.pathname === '/performance' },
        { label: 'Goals & OKRs', path: '/performance/goals', icon: Briefcase, active: location.pathname === '/performance/goals' },
        { label: 'Appraisal Reviews', path: '/performance/reviews', icon: FileText, active: location.pathname === '/performance/reviews' },
        { label: 'Rating Calibration', path: '/performance/calibration', icon: Activity, active: location.pathname === '/performance/calibration' },
        { label: '360° Peer Feedback', path: '/performance/360-feedback', icon: Users, active: location.pathname === '/performance/360-feedback' },
        { label: 'PIP & Growth Plans', path: '/performance/pip', icon: Activity, active: location.pathname === '/performance/pip' },
        { label: 'Promotions & Succession', path: '/performance/promotions', icon: Briefcase, active: location.pathname === '/performance/promotions' },
        { label: 'L&D Training Courses', path: '/training', icon: Building2, active: location.pathname === '/training' },
        { label: 'Skills Matrix Gaps', path: '/skills/matrix', icon: Briefcase, active: location.pathname === '/skills/matrix' },
        { label: 'Pulse Surveys', path: '/engagement', icon: Activity, active: location.pathname === '/engagement' },
      ]
    },
    {
      categoryLabel: 'SELF SERVICE & RECRUITMENT',
      icon: Users,
      items: [
        { label: 'My ESS Portal', path: '/me/dashboard', icon: LayoutDashboard, active: location.pathname === '/me/dashboard' },
        { label: 'My Action Tasks', path: '/me/tasks', icon: FileText, active: location.pathname === '/me/tasks' },
        { label: 'HR Letters & Docs', path: '/me/documents', icon: FileText, active: location.pathname === '/me/documents' },
        { label: 'Company Policies', path: '/policies', icon: ShieldCheck, active: location.pathname === '/policies' },
        { label: 'HR Helpdesk & Requests', path: '/me/helpdesk', icon: LifeBuoy, active: location.pathname === '/me/helpdesk' },
        { label: 'Communications Feed', path: '/announcements', icon: Megaphone, active: location.pathname === '/announcements' },
        { label: 'Manager MSS Hub', path: '/team/dashboard', icon: LayoutDashboard, active: location.pathname === '/team/dashboard' },
        { label: 'Job Requisitions', path: '/recruitment/requisitions', icon: FileText, active: location.pathname === '/recruitment/requisitions' },
        { label: 'Candidate Pipeline', path: '/recruitment/pipeline', icon: Users, active: location.pathname === '/recruitment/pipeline' },
        { label: 'Panel Interviews', path: '/recruitment/interviews', icon: Calendar, active: location.pathname === '/recruitment/interviews' },
        { label: 'Offers & Conversion', path: '/recruitment/offers', icon: Receipt, active: location.pathname === '/recruitment/offers' },
      ]
    },
    {
      categoryLabel: 'AI INTELLIGENCE & COMPLIANCE',
      icon: ShieldCheck,
      items: [
        { label: 'AxonTime AI Copilot', path: '/ai/copilot', icon: Activity, active: location.pathname === '/ai/copilot' },
        { label: 'Executive BI Board', path: '/intelligence/executive-bi', icon: LayoutDashboard, active: location.pathname === '/intelligence/executive-bi' },
        { label: 'Anomaly Detection', path: '/intelligence/anomalies', icon: Activity, active: location.pathname === '/intelligence/anomalies' },
        { label: '12-Month Forecaster', path: '/intelligence/forecasts', icon: Activity, active: location.pathname === '/intelligence/forecasts' },
        { label: 'What-If Scenario Planner', path: '/intelligence/scenarios', icon: Settings, active: location.pathname === '/intelligence/scenarios' },
        { label: 'Custom Dashboard Builder', path: '/intelligence/dashboard-builder', icon: LayoutDashboard, active: location.pathname === '/intelligence/dashboard-builder' },
        { label: 'Data Quality Auditor', path: '/intelligence/data-quality', icon: ShieldCheck, active: location.pathname === '/intelligence/data-quality' },
        { label: 'Compliance Overview', path: '/compliance/dashboard', icon: ShieldCheck, active: location.pathname === '/compliance/dashboard' },
        { label: 'Rules & Payroll Precheck', path: '/compliance/rules', icon: Settings, active: location.pathname === '/compliance/rules' },
        { label: 'Calendar & Task Evidence', path: '/compliance/calendar-tasks', icon: Calendar, active: location.pathname === '/compliance/calendar-tasks' },
        { label: 'Violations & CAPA', path: '/compliance/violations', icon: Activity, active: location.pathname === '/compliance/violations' },
        { label: 'Internal Audits', path: '/compliance/audits', icon: FileText, active: location.pathname === '/compliance/audits' },
        { label: 'Data Privacy & Legal Hold', path: '/compliance/privacy', icon: ShieldCheck, active: location.pathname === '/compliance/privacy' },
        { label: '18 Regulatory Reports', path: '/compliance/reports', icon: FileText, active: location.pathname === '/compliance/reports' },
        { label: 'Headcount & Gap Plans', path: '/workforce/planning', icon: Briefcase, active: location.pathname === '/workforce/planning' },
        { label: 'Executive HR Dashboard', path: '/analytics/executive', icon: Activity, active: location.pathname === '/analytics/executive' },
        { label: 'AI HR Assistant', path: '/ai/assistant', icon: Activity, active: location.pathname === '/ai/assistant' },
      ]
    }
  ];



  return (
    <div className="min-h-screen flex bg-emerald-50/30 text-slate-800">
      {/* Sidebar */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-30 transition-all duration-300 glass-panel border-r border-emerald-200/60 flex flex-col ${
          collapsed ? 'w-20' : 'w-64'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 px-4 flex items-center justify-between border-b border-emerald-100">
          {!collapsed && (
            <div className="flex items-center gap-2.5">
              <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center font-bold text-white shadow-md shadow-emerald-600/20">
                A
              </div>
              <div>
                <h1 className="font-extrabold text-base leading-none bg-gradient-to-r from-emerald-900 via-emerald-800 to-teal-700 bg-clip-text text-transparent">
                  AxonTime HR
                </h1>
                <span className="text-[10px] text-emerald-600 tracking-wider font-semibold uppercase">Enterprise Portal</span>
              </div>
            </div>
          )}
          {collapsed && (
            <div className="mx-auto h-9 w-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center font-bold text-white shadow-md">
              A
            </div>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-emerald-700 hover:bg-emerald-100/60 transition-colors"
            title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>
        </div>

        {/* Categorized Navigation Menu & Sub-Menus */}
        <nav className="flex-1 px-3 py-3 space-y-3 overflow-y-auto">
          {menuCategories.map((category) => {
            const CategoryIcon = category.icon;
            const isOpen = !!openCategories[category.categoryLabel];
            const hasActiveItem = category.items.some((i) => i.active);

            if (collapsed) {
              // Collapsed Mode: Render centered sub-item icons with floating tooltips
              return (
                <div key={category.categoryLabel} className="space-y-1.5 py-1 border-b border-emerald-100/60 last:border-b-0">
                  {category.items.map((item) => {
                    const ItemIcon = item.icon;
                    return (
                      <div key={item.path} className="relative group flex justify-center">
                        <Link
                          to={item.path}
                          className={`p-2.5 rounded-xl transition-all flex items-center justify-center ${
                            item.active
                              ? 'bg-emerald-600/15 text-emerald-800 border border-emerald-300/80 shadow-sm'
                              : 'text-slate-500 hover:text-emerald-900 hover:bg-emerald-100/50'
                          }`}
                        >
                          <ItemIcon size={18} className={item.active ? 'text-emerald-600' : 'text-slate-500'} />
                        </Link>

                        {/* Hover Floating Tooltip */}
                        <div className="absolute left-full ml-3 top-1/2 -translate-y-1/2 hidden group-hover:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 text-white text-xs font-semibold whitespace-nowrap shadow-xl z-50 pointer-events-none">
                          <span className="text-[10px] text-emerald-400 font-mono font-normal">[{category.categoryLabel}]</span>
                          <span>{item.label}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              );
            }

            // Expanded Mode: Category Headers + Sub-Menu Links
            return (
              <div key={category.categoryLabel} className="space-y-1">
                <button
                  onClick={() => toggleCategory(category.categoryLabel)}
                  className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-[11px] font-extrabold tracking-wider uppercase transition-colors ${
                    hasActiveItem ? 'text-emerald-900 bg-emerald-100/60' : 'text-slate-700 hover:text-emerald-900 hover:bg-emerald-50'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <CategoryIcon size={14} className={hasActiveItem ? 'text-emerald-700' : 'text-emerald-600'} />
                    <span>{category.categoryLabel}</span>
                  </div>
                  {isOpen ? <ChevronUp size={14} className="text-slate-600" /> : <ChevronDown size={14} className="text-slate-600" />}
                </button>

                {isOpen && (
                  <div className="space-y-1 pl-2">
                    {category.items.map((item) => {
                      const ItemIcon = item.icon;
                      return (
                        <Link
                          key={item.path}
                          to={item.path}
                          className={`flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-bold transition-all ${
                            item.active
                              ? 'bg-emerald-600/20 text-emerald-950 border border-emerald-400 shadow-sm'
                              : 'text-slate-700 hover:text-emerald-950 hover:bg-emerald-100/60'
                          }`}
                        >
                          <ItemIcon size={16} className={item.active ? 'text-emerald-700' : 'text-slate-500'} />
                          <span>{item.label}</span>
                        </Link>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </nav>

        {/* Backend Connectivity Status */}
        <div className="p-3 border-t border-emerald-200">
          <div
            className={`p-2.5 rounded-xl border flex items-center gap-2.5 ${
              healthStatus?.success
                ? 'bg-emerald-100 border-emerald-300 text-emerald-900'
                : healthLoading
                ? 'bg-amber-100 border-amber-300 text-amber-900'
                : 'bg-rose-100 border-rose-300 text-rose-900'
            }`}
          >
            <Activity size={18} className="animate-pulse text-emerald-700" />
            {!collapsed && (
              <div className="flex-1 text-xs">
                <p className="font-extrabold leading-none">
                  {healthLoading ? 'Checking API...' : healthStatus?.success ? 'API Healthy' : 'API Offline'}
                </p>
                <p className="text-[10px] text-slate-700 font-medium mt-0.5">FastAPI + Auth JWT + Redis</p>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className={`flex-1 flex flex-col transition-all duration-300 ${collapsed ? 'ml-20' : 'ml-64'}`}>
        {/* Top Header */}
        <header className="h-16 px-6 glass-panel border-b border-emerald-300/80 sticky top-0 z-20 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-4 w-1/3">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
              <input
                type="text"
                placeholder="Search employees, departments, settings..."
                disabled
                className="w-full bg-white border border-emerald-300 rounded-xl pl-9 pr-4 py-1.5 text-xs text-slate-800 placeholder-slate-500 font-semibold focus:outline-none cursor-not-allowed shadow-inner"
              />
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-100 border border-emerald-300 text-emerald-900 text-xs shadow-sm">
              <ShieldCheck size={14} className="text-emerald-700" />
              <span className="font-extrabold">Phases 1–14 All Systems Operational</span>
            </div>

            <button className="relative p-2 rounded-xl text-slate-600 hover:text-emerald-900 hover:bg-emerald-100/60 transition-colors">
              <Bell size={18} />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-emerald-600"></span>
            </button>

            <div className="h-8 w-px bg-emerald-300/80"></div>

            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-emerald-700 to-teal-700 border border-emerald-500 flex items-center justify-center font-extrabold text-white text-xs shadow-md">
                {user ? `${user.first_name[0]}${user.last_name[0]}` : 'U'}
              </div>
              <div className="hidden md:block text-left">
                <p className="text-xs font-extrabold text-slate-900 leading-none">
                  {user ? `${user.first_name} ${user.last_name}` : 'Authenticated User'}
                </p>
                <p className="text-[10px] text-slate-600 font-medium mt-0.5">{user?.email || 'user@axontime.com'}</p>
              </div>

              <button
                onClick={logout}
                title="Log Out"
                className="p-2 rounded-xl text-slate-600 hover:text-rose-700 hover:bg-rose-100/80 transition-colors ml-1"
              >
                <LogOut size={16} />
              </button>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-6 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
};
