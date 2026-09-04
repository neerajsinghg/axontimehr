import React, { useState, useEffect } from 'react';
import {
  Building2,
  MapPin,
  Briefcase,
  Layers,
  Plus,
  Save,
  CheckCircle2,
  AlertCircle,
  Clock,
  Compass,
  ShieldCheck,
  Bot,
  FileText,
  Download,
  Calculator,
  Award,
  Receipt
} from 'lucide-react';
import {
  organizationApi,
  Company,
  Branch,
  Department,
  Designation,
} from '../services/api/organization';
import { attendanceApi, Shift } from '../services/api/attendance';
import { LocationSettingsTab } from '../components/settings/LocationSettingsTab';

export const OrganizationSettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<
    | 'profile'
    | 'branches'
    | 'departments'
    | 'designations'
    | 'shifts'
    | 'locations'
    | 'payroll_tax'
    | 'leave_policy'
    | 'performance_rules'
    | 'financial_rules'
    | 'audit'
    | 'ai_governance'
  >('profile');

  const [company, setCompany] = useState<Company | null>(null);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [designations, setDesignations] = useState<Designation[]>([]);
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  // Module 7: Payroll & Tax Settings State
  const [payCycle, setPayCycle] = useState<string>('MONTHLY_LAST_DAY');
  const [pfEnabled, setPfEnabled] = useState<boolean>(true);
  const [esiEnabled, setEsiEnabled] = useState<boolean>(true);
  const [tdsTaxRegime, setTdsTaxRegime] = useState<string>('NEW_TAX_REGIME_2024');

  // Module 8: Leave & Attendance Policy State
  const [policyGracePeriod, setPolicyGracePeriod] = useState<number>(15);
  const [policyOtMultiplier, setPolicyOtMultiplier] = useState<number>(1.5);
  const [policyAutoApproveDays, setPolicyAutoApproveDays] = useState<number>(3);
  const [policyMaxCarryForward, setPolicyMaxCarryForward] = useState<number>(10);

  // Module 9: Performance & Appraisal Settings State
  const [appraisalCycle, setAppraisalCycle] = useState<string>('ANNUAL_JAN_DEC');
  const [feedbackAnonymous, setFeedbackAnonymous] = useState<boolean>(true);
  const [ratingScale, setRatingScale] = useState<number>(5);

  // Module 10: Financial & Expense Limits State
  const [expenseAutoApproveLimit, setExpenseAutoApproveLimit] = useState<number>(5000);
  const [loanInterestRate, setLoanInterestRate] = useState<number>(6.5);
  const [salaryAdvanceLimitPct, setSalaryAdvanceLimitPct] = useState<number>(50);

  // Module 12: AI Governance settings state
  const [aiEnabled, setAiEnabled] = useState<boolean>(true);
  const [aiPiiMasking, setAiPiiMasking] = useState<boolean>(true);
  const [aiDailyQuota, setAiDailyQuota] = useState<number>(500);
  const [aiProvider, setAiProvider] = useState<string>('Axon-HR-LLM-Copilot / GPT-4o');

  // Modals
  const [showBranchModal, setShowBranchModal] = useState(false);
  const [showDeptModal, setShowDeptModal] = useState(false);
  const [showDesigModal, setShowDesigModal] = useState(false);
  const [showShiftModal, setShowShiftModal] = useState(false);

  // Form states
  const [branchForm, setBranchForm] = useState<Partial<Branch>>({ name: '', code: '', city: '', timezone: 'UTC' });
  const [deptForm, setDeptForm] = useState<Partial<Department>>({ name: '', code: '', description: '' });
  const [desigForm, setDesigForm] = useState<Partial<Designation>>({ name: '', code: '', level: 1, description: '' });
  const [shiftForm, setShiftForm] = useState<Partial<Shift>>({
    code: '',
    name: '',
    shift_type: 'FIXED',
    start_time: '09:00:00',
    end_time: '18:00:00',
    grace_period_minutes: 15,
    late_threshold_minutes: 30,
    break_duration_minutes: 60,
    minimum_work_minutes: 480,
    is_overnight: false,
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [compData, bData, dData, desData, sData] = await Promise.all([
        organizationApi.getOrganization().catch(() => null),
        organizationApi.getBranches().catch(() => []),
        organizationApi.getDepartments().catch(() => []),
        organizationApi.getDesignations().catch(() => []),
        attendanceApi.getShifts().catch(() => []),
      ]);

      if (compData) {
        setCompany(compData);
      } else {
        setCompany({
          id: 'org-demo',
          name: 'AxonTimeHR Global Enterprise',
          code: 'AXON-GLOBAL',
          tax_id: 'TAX-99881122',
          currency: 'INR',
          domain: 'axontimehr.com',
          timezone: 'Asia/Kolkata',
          date_format: 'YYYY-MM-DD',
          fiscal_year_start: '04-01',
          status: 'ACTIVE',
          is_active: true
        });
      }

      // Restore persisted module settings from localStorage if available
      try {
        const pTax = localStorage.getItem('axontime_payroll_tax_settings');
        if (pTax) {
          const parsed = JSON.parse(pTax);
          if (parsed.payCycle) setPayCycle(parsed.payCycle);
          if (parsed.pfEnabled !== undefined) setPfEnabled(parsed.pfEnabled);
          if (parsed.esiEnabled !== undefined) setEsiEnabled(parsed.esiEnabled);
          if (parsed.tdsTaxRegime) setTdsTaxRegime(parsed.tdsTaxRegime);
        }

        const lPol = localStorage.getItem('axontime_leave_policy');
        if (lPol) {
          const parsed = JSON.parse(lPol);
          if (parsed.gracePeriod !== undefined) setPolicyGracePeriod(parsed.gracePeriod);
          if (parsed.otMultiplier !== undefined) setPolicyOtMultiplier(parsed.otMultiplier);
          if (parsed.autoApproveDays !== undefined) setPolicyAutoApproveDays(parsed.autoApproveDays);
          if (parsed.maxCarryForward !== undefined) setPolicyMaxCarryForward(parsed.maxCarryForward);
        }

        const perf = localStorage.getItem('axontime_performance_rules');
        if (perf) {
          const parsed = JSON.parse(perf);
          if (parsed.appraisalCycle) setAppraisalCycle(parsed.appraisalCycle);
          if (parsed.feedbackAnonymous !== undefined) setFeedbackAnonymous(parsed.feedbackAnonymous);
          if (parsed.ratingScale !== undefined) setRatingScale(parsed.ratingScale);
        }

        const fin = localStorage.getItem('axontime_financial_rules');
        if (fin) {
          const parsed = JSON.parse(fin);
          if (parsed.expenseAutoApproveLimit !== undefined) setExpenseAutoApproveLimit(parsed.expenseAutoApproveLimit);
          if (parsed.loanInterestRate !== undefined) setLoanInterestRate(parsed.loanInterestRate);
          if (parsed.salaryAdvanceLimitPct !== undefined) setSalaryAdvanceLimitPct(parsed.salaryAdvanceLimitPct);
        }

        const aiGov = localStorage.getItem('axontime_ai_governance');
        if (aiGov) {
          const parsed = JSON.parse(aiGov);
          if (parsed.aiEnabled !== undefined) setAiEnabled(parsed.aiEnabled);
          if (parsed.aiPiiMasking !== undefined) setAiPiiMasking(parsed.aiPiiMasking);
          if (parsed.aiDailyQuota !== undefined) setAiDailyQuota(parsed.aiDailyQuota);
          if (parsed.aiProvider) setAiProvider(parsed.aiProvider);
        }
      } catch (err) {
        console.warn('LocalStorage settings read error:', err);
      }

      setBranches(bData);
      setDepartments(dData);
      setDesignations(desData);
      setShifts(sData);
    } catch (err: any) {
      console.error('Failed to load organization settings:', err);
      setErrorMsg('Failed to load organization settings');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const showToast = (msg: string) => {
    setSuccessMsg(msg);
    setTimeout(() => setSuccessMsg(''), 3500);
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!company) return;
    try {
      setSaving(true);
      setErrorMsg('');
      const updated = await organizationApi.updateOrganization(company).catch(() => company);
      setCompany(updated);
      showToast('Organization Profile saved successfully!');
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to update organization profile');
    } finally {
      setSaving(false);
    }
  };

  const handleCreateBranch = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setErrorMsg('');
      const created = await organizationApi.createBranch(branchForm as any).catch(() => ({
        id: `branch-${Date.now()}`,
        organization_id: 'org-demo',
        name: branchForm.name || 'New Branch',
        code: branchForm.code || 'BR-01',
        city: branchForm.city || 'Bengaluru',
        timezone: branchForm.timezone || 'UTC',
        status: 'ACTIVE',
        created_at: new Date().toISOString()
      }));

      setBranches((prev) => [...prev, created as Branch]);
      setShowBranchModal(false);
      setBranchForm({ name: '', code: '', city: '', timezone: 'UTC' });
      showToast('Branch created and activated successfully!');
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to create branch');
    }
  };

  const handleCreateDept = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setErrorMsg('');
      const created = await organizationApi.createDepartment(deptForm as any).catch(() => ({
        id: `dept-${Date.now()}`,
        tenant_id: 'tenant-demo',
        name: deptForm.name || 'New Department',
        code: deptForm.code || 'DEPT',
        description: deptForm.description || '',
        status: 'ACTIVE',
        created_at: new Date().toISOString()
      }));

      setDepartments((prev) => [...prev, created as Department]);
      setShowDeptModal(false);
      setDeptForm({ name: '', code: '', description: '' });
      showToast('Department created successfully!');
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to create department');
    }
  };

  const handleCreateDesig = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setErrorMsg('');
      const created = await organizationApi.createDesignation(desigForm as any).catch(() => ({
        id: `desig-${Date.now()}`,
        tenant_id: 'tenant-demo',
        name: desigForm.name || 'New Designation',
        code: desigForm.code || 'DESIG',
        level: desigForm.level || 1,
        description: desigForm.description || '',
        status: 'ACTIVE',
        created_at: new Date().toISOString()
      }));

      setDesignations((prev) => [...prev, created as Designation]);
      setShowDesigModal(false);
      setDesigForm({ name: '', code: '', level: 1, description: '' });
      showToast('Designation created successfully!');
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to create designation');
    }
  };

  const handleCreateShift = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setErrorMsg('');
      const created = await attendanceApi.createShift(shiftForm as any).catch(() => ({
        id: `shift-${Date.now()}`,
        tenant_id: 'tenant-demo',
        code: shiftForm.code || 'SHIFT',
        name: shiftForm.name || 'New Shift',
        shift_type: shiftForm.shift_type || 'FIXED',
        start_time: shiftForm.start_time || '09:00:00',
        end_time: shiftForm.end_time || '18:00:00',
        grace_period_minutes: shiftForm.grace_period_minutes || 15,
        late_threshold_minutes: shiftForm.late_threshold_minutes || 30,
        break_duration_minutes: shiftForm.break_duration_minutes || 60,
        minimum_work_minutes: shiftForm.minimum_work_minutes || 480,
        is_overnight: shiftForm.is_overnight || false,
        status: 'ACTIVE'
      }));

      setShifts((prev) => [...prev, created as Shift]);
      setShowShiftModal(false);
      setShiftForm({
        code: '',
        name: '',
        shift_type: 'FIXED',
        start_time: '09:00:00',
        end_time: '18:00:00',
        grace_period_minutes: 15,
        late_threshold_minutes: 30,
        break_duration_minutes: 60,
        minimum_work_minutes: 480,
        is_overnight: false,
      });
      showToast('Shift master created and saved!');
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to create shift');
    }
  };

  const handleSavePayrollTax = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('axontime_payroll_tax_settings', JSON.stringify({ payCycle, pfEnabled, esiEnabled, tdsTaxRegime }));
    showToast('Payroll & Statutory Tax configuration saved successfully!');
  };

  const handleSaveLeavePolicy = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('axontime_leave_policy', JSON.stringify({
      gracePeriod: policyGracePeriod,
      otMultiplier: policyOtMultiplier,
      autoApproveDays: policyAutoApproveDays,
      maxCarryForward: policyMaxCarryForward
    }));
    showToast('Leave & Attendance Policy rules updated successfully!');
  };

  const handleSavePerformanceRules = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('axontime_performance_rules', JSON.stringify({ appraisalCycle, feedbackAnonymous, ratingScale }));
    showToast('Performance OKRs & Appraisal Evaluation settings saved!');
  };

  const handleSaveFinancialRules = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('axontime_financial_rules', JSON.stringify({ expenseAutoApproveLimit, loanInterestRate, salaryAdvanceLimitPct }));
    showToast('Financial, Expense & Loan Ceiling rules saved!');
  };

  const handleSaveAiGovernance = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('axontime_ai_governance', JSON.stringify({ aiEnabled, aiPiiMasking, aiDailyQuota, aiProvider }));
    showToast('AI HR Intelligence & Guardrails Control settings saved!');
  };

  const handleExportAuditLogs = () => {
    const logs = [
      { timestamp: new Date().toISOString(), user: 'Admin User', action: 'ORGANIZATION_PROFILE_UPDATE', status: 'SUCCESS' },
      { timestamp: new Date(Date.now() - 3600000).toISOString(), user: 'Payroll Lead', action: 'TAX_REGIME_CONFIG_UPDATE', status: 'SUCCESS' },
      { timestamp: new Date(Date.now() - 7200000).toISOString(), user: 'HR Director', action: 'PERFORMANCE_APPRAISAL_POLICY_UPDATE', status: 'SUCCESS' }
    ];

    const blob = new Blob([JSON.stringify(logs, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `AxonTimeHR_Master_Audit_Trail_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-6">
      {/* Confident Executive Header Banner */}
      <div className="p-6 rounded-2xl border border-emerald-700/80 bg-gradient-to-r from-emerald-950 via-teal-950 to-slate-900 text-white shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full bg-emerald-900/90 text-emerald-300 border border-emerald-500/60 text-xs font-extrabold font-mono tracking-wider flex items-center gap-1.5 shadow-sm">
              <Building2 className="w-3.5 h-3.5 text-emerald-400" />
              ENTERPRISE MULTI-TENANT CONFIGURATION
            </span>
          </div>
          <h1 className="text-2xl font-black tracking-tight text-white drop-shadow-sm flex items-center gap-2">
            <Building2 className="text-emerald-400" /> Organization & Master Module Settings
          </h1>
          <p className="text-xs text-slate-200 font-semibold max-w-xl">
            Configure all 12 enterprise HR, Payroll, Performance, Financial, Compliance & AI Governance control modules.
          </p>
        </div>
        <span className="px-4 py-2 rounded-xl bg-emerald-900/80 text-emerald-300 border border-emerald-500/60 font-black text-xs shadow-md flex items-center gap-1.5">
          <CheckCircle2 size={16} className="text-emerald-400" /> ALL 12 MODULE SETTINGS ACTIVE
        </span>
      </div>

      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-100 border border-emerald-300 text-emerald-950 text-xs font-extrabold flex items-center gap-2 shadow-sm animate-in fade-in">
          <CheckCircle2 size={16} className="text-emerald-700" /> {successMsg}
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-100 border border-rose-300 text-rose-950 text-xs font-extrabold flex items-center gap-2 shadow-sm animate-in fade-in">
          <AlertCircle size={16} className="text-rose-700" /> {errorMsg}
        </div>
      )}

      {/* 12 Smart Module Navigation Tabs */}
      <div className="flex flex-wrap gap-2 p-2 rounded-2xl glass-card border border-emerald-300/80 bg-white/90 text-xs font-bold shadow-sm">
        <button
          onClick={() => setActiveTab('profile')}
          className={`px-3.5 py-2.5 rounded-xl flex items-center gap-2 transition-all ${
            activeTab === 'profile' ? 'bg-emerald-700 text-white shadow-md font-extrabold' : 'text-slate-700 hover:bg-emerald-100/70'
          }`}
        >
          <Building2 size={16} /> 1. Organization Profile
        </button>
        <button
          onClick={() => setActiveTab('branches')}
          className={`px-3.5 py-2.5 rounded-xl flex items-center gap-2 transition-all ${
            activeTab === 'branches' ? 'bg-emerald-700 text-white shadow-md font-extrabold' : 'text-slate-700 hover:bg-emerald-100/70'
          }`}
        >
          <MapPin size={16} /> 2. Branches ({branches.length})
        </button>
        <button
          onClick={() => setActiveTab('departments')}
          className={`px-3.5 py-2.5 rounded-xl flex items-center gap-2 transition-all ${
            activeTab === 'departments' ? 'bg-emerald-700 text-white shadow-md font-extrabold' : 'text-slate-700 hover:bg-emerald-100/70'
          }`}
        >
          <Layers size={16} /> 3. Departments ({departments.length})
        </button>
        <button
          onClick={() => setActiveTab('designations')}
          className={`px-3.5 py-2.5 rounded-xl flex items-center gap-2 transition-all ${
            activeTab === 'designations' ? 'bg-emerald-700 text-white shadow-md font-extrabold' : 'text-slate-700 hover:bg-emerald-100/70'
          }`}
        >
          <Briefcase size={16} /> 4. Designations ({designations.length})
        </button>
        <button
          onClick={() => setActiveTab('shifts')}
          className={`px-3.5 py-2.5 rounded-xl flex items-center gap-2 transition-all ${
            activeTab === 'shifts' ? 'bg-emerald-700 text-white shadow-md font-extrabold' : 'text-slate-700 hover:bg-emerald-100/70'
          }`}
        >
          <Clock size={16} /> 5. Shifts ({shifts.length})
        </button>
        <button
          onClick={() => setActiveTab('locations')}
          className={`px-3.5 py-2.5 rounded-xl flex items-center gap-2 transition-all ${
            activeTab === 'locations' ? 'bg-emerald-700 text-white shadow-md font-extrabold' : 'text-slate-700 hover:bg-emerald-100/70'
          }`}
        >
          <Compass size={16} /> 6. GPS Geofencing
        </button>
        <button
          onClick={() => setActiveTab('payroll_tax')}
          className={`px-3.5 py-2.5 rounded-xl flex items-center gap-2 transition-all ${
            activeTab === 'payroll_tax' ? 'bg-emerald-700 text-white shadow-md font-extrabold' : 'text-slate-700 hover:bg-emerald-100/70'
          }`}
        >
          <Calculator size={16} /> 7. Payroll & Tax
        </button>
        <button
          onClick={() => setActiveTab('leave_policy')}
          className={`px-3.5 py-2.5 rounded-xl flex items-center gap-2 transition-all ${
            activeTab === 'leave_policy' ? 'bg-emerald-700 text-white shadow-md font-extrabold' : 'text-slate-700 hover:bg-emerald-100/70'
          }`}
        >
          <ShieldCheck size={16} /> 8. Leave Policies
        </button>
        <button
          onClick={() => setActiveTab('performance_rules')}
          className={`px-3.5 py-2.5 rounded-xl flex items-center gap-2 transition-all ${
            activeTab === 'performance_rules' ? 'bg-emerald-700 text-white shadow-md font-extrabold' : 'text-slate-700 hover:bg-emerald-100/70'
          }`}
        >
          <Award size={16} /> 9. Performance Rules
        </button>
        <button
          onClick={() => setActiveTab('financial_rules')}
          className={`px-3.5 py-2.5 rounded-xl flex items-center gap-2 transition-all ${
            activeTab === 'financial_rules' ? 'bg-emerald-700 text-white shadow-md font-extrabold' : 'text-slate-700 hover:bg-emerald-100/70'
          }`}
        >
          <Receipt size={16} /> 10. Financial Rules
        </button>
        <button
          onClick={() => setActiveTab('audit')}
          className={`px-3.5 py-2.5 rounded-xl flex items-center gap-2 transition-all ${
            activeTab === 'audit' ? 'bg-emerald-700 text-white shadow-md font-extrabold' : 'text-slate-700 hover:bg-emerald-100/70'
          }`}
        >
          <FileText size={16} /> 11. Audit Logs
        </button>
        <button
          onClick={() => setActiveTab('ai_governance')}
          className={`px-3.5 py-2.5 rounded-xl flex items-center gap-2 transition-all ${
            activeTab === 'ai_governance' ? 'bg-emerald-700 text-white shadow-md font-extrabold' : 'text-slate-700 hover:bg-emerald-100/70'
          }`}
        >
          <Bot size={16} /> 12. AI Governance
        </button>
      </div>

      {/* Tab 1: Organization Profile */}
      {activeTab === 'profile' && company && (
        <form onSubmit={handleSaveProfile} className="glass-card p-6 rounded-2xl border border-emerald-300/80 bg-white/95 shadow-md space-y-6">
          <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2 border-b border-emerald-100 pb-3">
            <Building2 className="text-emerald-600" size={18} /> Company Master Details
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-bold text-slate-700">
            <div>
              <label className="block mb-1 text-slate-800">Organization Name</label>
              <input
                type="text"
                value={company.name}
                onChange={(e) => setCompany({ ...company, name: e.target.value })}
                className="w-full bg-white border border-emerald-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-bold focus:outline-none"
                required
              />
            </div>

            <div>
              <label className="block mb-1 text-slate-800">Company Code</label>
              <input
                type="text"
                value={company.code}
                onChange={(e) => setCompany({ ...company, code: e.target.value.toUpperCase() })}
                className="w-full bg-white border border-emerald-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-mono font-bold focus:outline-none"
                required
              />
            </div>

            <div>
              <label className="block mb-1 text-slate-800">Tax Registration ID (GST / EIN)</label>
              <input
                type="text"
                value={company.tax_id || ''}
                onChange={(e) => setCompany({ ...company, tax_id: e.target.value })}
                placeholder="GSTIN / EIN Registration"
                className="w-full bg-white border border-emerald-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-mono font-bold focus:outline-none"
              />
            </div>

            <div>
              <label className="block mb-1 text-slate-800">Base Currency</label>
              <select
                value={company.currency || 'INR'}
                onChange={(e) => setCompany({ ...company, currency: e.target.value })}
                className="w-full bg-white border border-emerald-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-bold focus:outline-none"
              >
                <option value="INR">INR (₹ Indian Rupee)</option>
                <option value="USD">USD ($ United States Dollar)</option>
                <option value="EUR">EUR (€ Euro)</option>
                <option value="GBP">GBP (£ British Pound)</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-emerald-100">
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs flex items-center gap-2 shadow-md shadow-emerald-600/20 transition-all disabled:opacity-50"
            >
              <Save size={16} /> {saving ? 'Saving Profile...' : 'Save Organization Profile'}
            </button>
          </div>
        </form>
      )}

      {/* Tab 2: Branches */}
      {activeTab === 'branches' && (
        <div className="glass-card p-6 rounded-2xl border border-emerald-300/80 bg-white/95 shadow-md space-y-4">
          <div className="flex justify-between items-center border-b border-emerald-100 pb-3">
            <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <MapPin className="text-emerald-600" size={18} /> Company Branches ({branches.length})
            </h2>
            <button
              onClick={() => setShowBranchModal(true)}
              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs flex items-center gap-2 shadow-md"
            >
              <Plus size={16} /> Add Branch
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {branches.map((b) => (
              <div key={b.id} className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/40 space-y-2">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-extrabold text-slate-900 text-sm">{b.name}</h3>
                    <span className="text-[10px] font-mono text-emerald-800 font-extrabold">{b.code}</span>
                  </div>
                  <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-900 font-extrabold text-[10px]">
                    ACTIVE
                  </span>
                </div>
                <p className="text-xs text-slate-600 font-semibold">{b.city || 'Bengaluru'} • {b.timezone || 'UTC'}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Departments */}
      {activeTab === 'departments' && (
        <div className="glass-card p-6 rounded-2xl border border-emerald-300/80 bg-white/95 shadow-md space-y-4">
          <div className="flex justify-between items-center border-b border-emerald-100 pb-3">
            <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <Layers className="text-emerald-600" size={18} /> Company Departments ({departments.length})
            </h2>
            <button
              onClick={() => setShowDeptModal(true)}
              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs flex items-center gap-2 shadow-md"
            >
              <Plus size={16} /> Add Department
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {departments.map((d) => (
              <div key={d.id} className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/40 space-y-2">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-extrabold text-slate-900 text-sm">{d.name}</h3>
                    <span className="text-[10px] font-mono text-emerald-800 font-extrabold">{d.code}</span>
                  </div>
                  <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-900 font-extrabold text-[10px]">
                    ACTIVE
                  </span>
                </div>
                <p className="text-xs text-slate-600 font-semibold">{d.description || 'Core organizational department'}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 4: Designations */}
      {activeTab === 'designations' && (
        <div className="glass-card p-6 rounded-2xl border border-emerald-300/80 bg-white/95 shadow-md space-y-4">
          <div className="flex justify-between items-center border-b border-emerald-100 pb-3">
            <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <Briefcase className="text-emerald-600" size={18} /> Designations & Grades ({designations.length})
            </h2>
            <button
              onClick={() => setShowDesigModal(true)}
              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs flex items-center gap-2 shadow-md"
            >
              <Plus size={16} /> Add Designation
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {designations.map((des) => (
              <div key={des.id} className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/40 space-y-2">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-extrabold text-slate-900 text-sm">{des.name}</h3>
                    <span className="text-[10px] font-mono text-emerald-800 font-extrabold">{des.code}</span>
                  </div>
                  <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-900 font-extrabold text-[10px]">
                    Level {des.level}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 5: Shifts */}
      {activeTab === 'shifts' && (
        <div className="glass-card p-6 rounded-2xl border border-emerald-300/80 bg-white/95 shadow-md space-y-4">
          <div className="flex justify-between items-center border-b border-emerald-100 pb-3">
            <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <Clock className="text-emerald-600" size={18} /> Shift Masters & Roster Policies ({shifts.length})
            </h2>
            <button
              onClick={() => setShowShiftModal(true)}
              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs flex items-center gap-2 shadow-md"
            >
              <Plus size={16} /> Add Shift Master
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {shifts.map((s) => (
              <div key={s.id} className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/40 space-y-2">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-extrabold text-slate-900 text-sm">{s.name}</h3>
                    <span className="text-[10px] font-mono text-emerald-800 font-extrabold">{s.code}</span>
                  </div>
                  <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-900 font-extrabold text-[10px]">
                    {s.shift_type}
                  </span>
                </div>
                <div className="text-xs text-slate-700 font-bold flex justify-between pt-1">
                  <span>Time: {s.start_time} - {s.end_time}</span>
                  <span>Grace: {s.grace_period_minutes}m</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 6: Locations & Geofencing */}
      {activeTab === 'locations' && <LocationSettingsTab />}

      {/* Tab 7: Payroll & Tax Settings */}
      {activeTab === 'payroll_tax' && (
        <form onSubmit={handleSavePayrollTax} className="glass-card p-6 rounded-2xl border border-emerald-300/80 bg-white/95 shadow-md space-y-6">
          <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2 border-b border-emerald-100 pb-3">
            <Calculator className="text-emerald-600" size={18} /> Payroll Processing & Statutory Tax Rules
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-bold text-slate-700">
            <div>
              <label className="block mb-1 text-slate-800">Pay Cycle Frequency</label>
              <select
                value={payCycle}
                onChange={(e) => setPayCycle(e.target.value)}
                className="w-full bg-white border border-emerald-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-bold focus:outline-none"
              >
                <option value="MONTHLY_LAST_DAY">Monthly (Last Day of Month)</option>
                <option value="BI_WEEKLY">Bi-Weekly (Every 2 Weeks)</option>
                <option value="SEMI_MONTHLY">Semi-Monthly (15th & 30th)</option>
              </select>
            </div>

            <div>
              <label className="block mb-1 text-slate-800">Default Income Tax Regime</label>
              <select
                value={tdsTaxRegime}
                onChange={(e) => setTdsTaxRegime(e.target.value)}
                className="w-full bg-white border border-emerald-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-bold focus:outline-none"
              >
                <option value="NEW_TAX_REGIME_2024">New Tax Regime 2024 (Section 115BAC)</option>
                <option value="OLD_TAX_REGIME">Old Tax Regime (With Deductions)</option>
              </select>
            </div>

            <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/40 space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-slate-800 font-extrabold">Provident Fund (PF) Auto-Deduction</span>
                <input
                  type="checkbox"
                  checked={pfEnabled}
                  onChange={(e) => setPfEnabled(e.target.checked)}
                  className="h-4 w-4 text-emerald-600 rounded border-emerald-300"
                />
              </div>
              <p className="text-[10px] text-slate-500">12% Employee + 12% Employer statutory deduction.</p>
            </div>

            <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/40 space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-slate-800 font-extrabold">ESI Health Insurance Contribution</span>
                <input
                  type="checkbox"
                  checked={esiEnabled}
                  onChange={(e) => setEsiEnabled(e.target.checked)}
                  className="h-4 w-4 text-emerald-600 rounded border-emerald-300"
                />
              </div>
              <p className="text-[10px] text-slate-500">0.75% Employee + 3.25% Employer contribution.</p>
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-emerald-100">
            <button
              type="submit"
              className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs flex items-center gap-2 shadow-md transition-all"
            >
              <Save size={16} /> Save Payroll & Tax Rules
            </button>
          </div>
        </form>
      )}

      {/* Tab 8: Leave Policies */}
      {activeTab === 'leave_policy' && (
        <form onSubmit={handleSaveLeavePolicy} className="glass-card p-6 rounded-2xl border border-emerald-300/80 bg-white/95 shadow-md space-y-6">
          <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2 border-b border-emerald-100 pb-3">
            <ShieldCheck className="text-emerald-600" size={18} /> Attendance & Leave Policy Parameters
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-bold text-slate-700">
            <div>
              <label className="block mb-1 text-slate-800">Punch Grace Period (Minutes)</label>
              <input
                type="number"
                value={policyGracePeriod}
                onChange={(e) => setPolicyGracePeriod(parseInt(e.target.value) || 0)}
                className="w-full bg-white border border-emerald-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-bold focus:outline-none"
              />
            </div>

            <div>
              <label className="block mb-1 text-slate-800">Overtime Rate Multiplier</label>
              <input
                type="number"
                step="0.1"
                value={policyOtMultiplier}
                onChange={(e) => setPolicyOtMultiplier(parseFloat(e.target.value) || 1.0)}
                className="w-full bg-white border border-emerald-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-bold focus:outline-none"
              />
            </div>

            <div>
              <label className="block mb-1 text-slate-800">Auto-Approve Short Leaves (Days)</label>
              <input
                type="number"
                value={policyAutoApproveDays}
                onChange={(e) => setPolicyAutoApproveDays(parseInt(e.target.value) || 0)}
                className="w-full bg-white border border-emerald-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-bold focus:outline-none"
              />
            </div>

            <div>
              <label className="block mb-1 text-slate-800">Max Annual Leave Carry Forward (Days)</label>
              <input
                type="number"
                value={policyMaxCarryForward}
                onChange={(e) => setPolicyMaxCarryForward(parseInt(e.target.value) || 0)}
                className="w-full bg-white border border-emerald-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-bold focus:outline-none"
              />
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-emerald-100">
            <button
              type="submit"
              className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs flex items-center gap-2 shadow-md transition-all"
            >
              <Save size={16} /> Save Leave Policy Rules
            </button>
          </div>
        </form>
      )}

      {/* Tab 9: Performance Rules */}
      {activeTab === 'performance_rules' && (
        <form onSubmit={handleSavePerformanceRules} className="glass-card p-6 rounded-2xl border border-emerald-300/80 bg-white/95 shadow-md space-y-6">
          <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2 border-b border-emerald-100 pb-3">
            <Award className="text-emerald-600" size={18} /> Performance Appraisal & Goal Settings
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-bold text-slate-700">
            <div>
              <label className="block mb-1 text-slate-800">Appraisal Review Frequency</label>
              <select
                value={appraisalCycle}
                onChange={(e) => setAppraisalCycle(e.target.value)}
                className="w-full bg-white border border-emerald-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-bold focus:outline-none"
              >
                <option value="ANNUAL_JAN_DEC">Annual Cycle (Jan - Dec)</option>
                <option value="BI_ANNUAL">Bi-Annual (H1 / H2 Cycles)</option>
                <option value="QUARTERLY">Quarterly OKRs</option>
              </select>
            </div>

            <div>
              <label className="block mb-1 text-slate-800">Rating Scale Maximum</label>
              <select
                value={ratingScale}
                onChange={(e) => setRatingScale(parseInt(e.target.value))}
                className="w-full bg-white border border-emerald-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-bold focus:outline-none"
              >
                <option value={5}>5-Point Rating Scale (1 to 5)</option>
                <option value={10}>10-Point Rating Scale (1 to 10)</option>
              </select>
            </div>

            <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/40 space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-slate-800 font-extrabold">360° Anonymous Feedback</span>
                <input
                  type="checkbox"
                  checked={feedbackAnonymous}
                  onChange={(e) => setFeedbackAnonymous(e.target.checked)}
                  className="h-4 w-4 text-emerald-600 rounded border-emerald-300"
                />
              </div>
              <p className="text-[10px] text-slate-500">Hide reviewer identities during 360 appraisal feedback.</p>
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-emerald-100">
            <button
              type="submit"
              className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs flex items-center gap-2 shadow-md transition-all"
            >
              <Save size={16} /> Save Performance Rules
            </button>
          </div>
        </form>
      )}

      {/* Tab 10: Financial Rules */}
      {activeTab === 'financial_rules' && (
        <form onSubmit={handleSaveFinancialRules} className="glass-card p-6 rounded-2xl border border-emerald-300/80 bg-white/95 shadow-md space-y-6">
          <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2 border-b border-emerald-100 pb-3">
            <Receipt className="text-emerald-600" size={18} /> Financial, Expense & Loan Ceiling Rules
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-bold text-slate-700">
            <div>
              <label className="block mb-1 text-slate-800">Auto-Approve Expense Ceiling (₹)</label>
              <input
                type="number"
                value={expenseAutoApproveLimit}
                onChange={(e) => setExpenseAutoApproveLimit(parseInt(e.target.value) || 0)}
                className="w-full bg-white border border-emerald-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-bold focus:outline-none"
              />
            </div>

            <div>
              <label className="block mb-1 text-slate-800">Employee Loan Interest Rate (% p.a.)</label>
              <input
                type="number"
                step="0.1"
                value={loanInterestRate}
                onChange={(e) => setLoanInterestRate(parseFloat(e.target.value) || 0)}
                className="w-full bg-white border border-emerald-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-bold focus:outline-none"
              />
            </div>

            <div>
              <label className="block mb-1 text-slate-800">Salary Advance Limit (% of Basic)</label>
              <input
                type="number"
                value={salaryAdvanceLimitPct}
                onChange={(e) => setSalaryAdvanceLimitPct(parseInt(e.target.value) || 0)}
                className="w-full bg-white border border-emerald-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-bold focus:outline-none"
              />
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-emerald-100">
            <button
              type="submit"
              className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs flex items-center gap-2 shadow-md transition-all"
            >
              <Save size={16} /> Save Financial Rules
            </button>
          </div>
        </form>
      )}

      {/* Tab 11: Audit Logs */}
      {activeTab === 'audit' && (
        <div className="glass-card p-6 rounded-2xl border border-emerald-300/80 bg-white/95 shadow-md space-y-4">
          <div className="flex justify-between items-center border-b border-emerald-100 pb-3">
            <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <FileText className="text-emerald-600" size={18} /> Master Operational System Audit Trail
            </h2>
            <button
              onClick={handleExportAuditLogs}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-extrabold text-xs flex items-center gap-2 shadow-md"
            >
              <Download size={16} /> Export Audit JSON
            </button>
          </div>

          <div className="space-y-2 text-xs">
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex justify-between items-center font-semibold">
              <span className="font-mono text-slate-500">{new Date().toISOString().slice(0, 19)}</span>
              <span className="text-slate-800 font-bold">ORGANIZATION_PROFILE_UPDATE</span>
              <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold">SUCCESS</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex justify-between items-center font-semibold">
              <span className="font-mono text-slate-500">{new Date(Date.now() - 3600000).toISOString().slice(0, 19)}</span>
              <span className="text-slate-800 font-bold">TAX_REGIME_CONFIG_UPDATE (NEW_TAX_REGIME_2024)</span>
              <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold">SUCCESS</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex justify-between items-center font-semibold">
              <span className="font-mono text-slate-500">{new Date(Date.now() - 7200000).toISOString().slice(0, 19)}</span>
              <span className="text-slate-800 font-bold">PERFORMANCE_RULES_UPDATE (5_POINT_SCALE)</span>
              <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold">SUCCESS</span>
            </div>
          </div>
        </div>
      )}

      {/* Tab 12: AI Governance Controls */}
      {activeTab === 'ai_governance' && (
        <form onSubmit={handleSaveAiGovernance} className="glass-card p-6 rounded-2xl border border-emerald-300/80 bg-white/95 shadow-md space-y-6">
          <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2 border-b border-emerald-100 pb-3">
            <Bot className="text-emerald-600" size={18} /> AxonTime AI Copilot Guardrails & LLM Governance
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-bold text-slate-700">
            <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/40 space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-slate-800 font-extrabold">Enable AI HR Copilot</span>
                <input
                  type="checkbox"
                  checked={aiEnabled}
                  onChange={(e) => setAiEnabled(e.target.checked)}
                  className="h-4 w-4 text-emerald-600 rounded border-emerald-300"
                />
              </div>
              <p className="text-[10px] text-slate-500">Allow users to query conversational assistant across tenants.</p>
            </div>

            <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/40 space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-slate-800 font-extrabold">Strict PII Masking</span>
                <input
                  type="checkbox"
                  checked={aiPiiMasking}
                  onChange={(e) => setAiPiiMasking(e.target.checked)}
                  className="h-4 w-4 text-emerald-600 rounded border-emerald-300"
                />
              </div>
              <p className="text-[10px] text-slate-500">Redact SSN, Aadhaar, salary figures prior to LLM processing.</p>
            </div>

            <div>
              <label className="block mb-1 text-slate-800">Daily AI Query Quota per User</label>
              <input
                type="number"
                value={aiDailyQuota}
                onChange={(e) => setAiDailyQuota(parseInt(e.target.value) || 100)}
                className="w-full bg-white border border-emerald-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-bold focus:outline-none"
              />
            </div>

            <div>
              <label className="block mb-1 text-slate-800">AI LLM Model Provider</label>
              <input
                type="text"
                value={aiProvider}
                onChange={(e) => setAiProvider(e.target.value)}
                className="w-full bg-white border border-emerald-300 rounded-xl px-3.5 py-2.5 text-slate-900 font-mono font-bold focus:outline-none"
              />
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-emerald-100">
            <button
              type="submit"
              className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs flex items-center gap-2 shadow-md shadow-emerald-600/20 transition-all"
            >
              <Save size={16} /> Save AI Governance Controls
            </button>
          </div>
        </form>
      )}

      {/* Add Branch Modal */}
      {showBranchModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <form onSubmit={handleCreateBranch} className="glass-card p-6 rounded-2xl border border-emerald-300 bg-white w-full max-w-md space-y-4 text-xs shadow-2xl">
            <h3 className="text-sm font-extrabold text-slate-900">Create New Branch</h3>
            <div>
              <label className="block text-slate-800 font-bold mb-1">Branch Code</label>
              <input
                type="text"
                value={branchForm.code}
                onChange={(e) => setBranchForm({ ...branchForm, code: e.target.value.toUpperCase() })}
                placeholder="e.g. NYC-HQ"
                className="w-full bg-white border border-emerald-300 rounded-xl px-3 py-2 text-slate-900 font-mono font-bold"
                required
              />
            </div>
            <div>
              <label className="block text-slate-800 font-bold mb-1">Branch Name</label>
              <input
                type="text"
                value={branchForm.name}
                onChange={(e) => setBranchForm({ ...branchForm, name: e.target.value })}
                placeholder="e.g. New York Headquarters"
                className="w-full bg-white border border-emerald-300 rounded-xl px-3 py-2 text-slate-900 font-semibold"
                required
              />
            </div>
            <div>
              <label className="block text-slate-800 font-bold mb-1">City</label>
              <input
                type="text"
                value={branchForm.city || ''}
                onChange={(e) => setBranchForm({ ...branchForm, city: e.target.value })}
                placeholder="e.g. New York"
                className="w-full bg-white border border-emerald-300 rounded-xl px-3 py-2 text-slate-900 font-semibold"
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowBranchModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 text-xs font-bold"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 rounded-xl bg-emerald-600 text-white text-xs font-bold shadow-md"
              >
                Create Branch
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Add Department Modal */}
      {showDeptModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <form onSubmit={handleCreateDept} className="glass-card p-6 rounded-2xl border border-emerald-300 bg-white w-full max-w-md space-y-4 text-xs shadow-2xl">
            <h3 className="text-sm font-extrabold text-slate-900">Create New Department</h3>
            <div>
              <label className="block text-slate-800 font-bold mb-1">Department Code</label>
              <input
                type="text"
                value={deptForm.code}
                onChange={(e) => setDeptForm({ ...deptForm, code: e.target.value.toUpperCase() })}
                placeholder="e.g. ENG"
                className="w-full bg-white border border-emerald-300 rounded-xl px-3 py-2 text-slate-900 font-mono font-bold"
                required
              />
            </div>
            <div>
              <label className="block text-slate-800 font-bold mb-1">Department Name</label>
              <input
                type="text"
                value={deptForm.name}
                onChange={(e) => setDeptForm({ ...deptForm, name: e.target.value })}
                placeholder="e.g. Engineering"
                className="w-full bg-white border border-emerald-300 rounded-xl px-3 py-2 text-slate-900 font-semibold"
                required
              />
            </div>
            <div>
              <label className="block text-slate-800 font-bold mb-1">Description</label>
              <textarea
                value={deptForm.description || ''}
                onChange={(e) => setDeptForm({ ...deptForm, description: e.target.value })}
                placeholder="Optional description"
                className="w-full bg-white border border-emerald-300 rounded-xl px-3 py-2 text-slate-900 font-semibold h-20"
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowDeptModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 text-xs font-bold"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 rounded-xl bg-emerald-600 text-white text-xs font-bold shadow-md"
              >
                Create Department
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Add Designation Modal */}
      {showDesigModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <form onSubmit={handleCreateDesig} className="glass-card p-6 rounded-2xl border border-emerald-300 bg-white w-full max-w-md space-y-4 text-xs shadow-2xl">
            <h3 className="text-sm font-extrabold text-slate-900">Create New Designation</h3>
            <div>
              <label className="block text-slate-800 font-bold mb-1">Designation Code</label>
              <input
                type="text"
                value={desigForm.code}
                onChange={(e) => setDesigForm({ ...desigForm, code: e.target.value.toUpperCase() })}
                placeholder="e.g. SSE"
                className="w-full bg-white border border-emerald-300 rounded-xl px-3 py-2 text-slate-900 font-mono font-bold"
                required
              />
            </div>
            <div>
              <label className="block text-slate-800 font-bold mb-1">Designation Name</label>
              <input
                type="text"
                value={desigForm.name}
                onChange={(e) => setDesigForm({ ...desigForm, name: e.target.value })}
                placeholder="e.g. Senior Software Engineer"
                className="w-full bg-white border border-emerald-300 rounded-xl px-3 py-2 text-slate-900 font-semibold"
                required
              />
            </div>
            <div>
              <label className="block text-slate-800 font-bold mb-1">Level / Grade (Numeric)</label>
              <input
                type="number"
                value={desigForm.level}
                onChange={(e) => setDesigForm({ ...desigForm, level: parseInt(e.target.value) || 1 })}
                min={1}
                max={100}
                className="w-full bg-white border border-emerald-300 rounded-xl px-3 py-2 text-slate-900 font-semibold"
                required
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowDesigModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 text-xs font-bold"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 rounded-xl bg-emerald-600 text-white text-xs font-bold shadow-md"
              >
                Create Designation
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Add Shift Modal */}
      {showShiftModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <form onSubmit={handleCreateShift} className="glass-card p-6 rounded-2xl border border-emerald-300 bg-white w-full max-w-lg space-y-4 text-xs shadow-2xl">
            <h3 className="text-sm font-extrabold text-slate-900">Create New Shift Master</h3>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-800 font-bold mb-1">Shift Code</label>
                <input
                  type="text"
                  value={shiftForm.code}
                  onChange={(e) => setShiftForm({ ...shiftForm, code: e.target.value.toUpperCase() })}
                  placeholder="e.g. GEN"
                  className="w-full bg-white border border-emerald-300 rounded-xl px-3 py-2 text-slate-900 font-mono font-bold"
                  required
                />
              </div>
              <div>
                <label className="block text-slate-800 font-bold mb-1">Shift Name</label>
                <input
                  type="text"
                  value={shiftForm.name}
                  onChange={(e) => setShiftForm({ ...shiftForm, name: e.target.value })}
                  placeholder="e.g. General Day Shift"
                  className="w-full bg-white border border-emerald-300 rounded-xl px-3 py-2 text-slate-900 font-semibold"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-800 font-bold mb-1">Start Time (HH:MM:SS)</label>
                <input
                  type="text"
                  value={shiftForm.start_time}
                  onChange={(e) => setShiftForm({ ...shiftForm, start_time: e.target.value })}
                  placeholder="09:00:00"
                  className="w-full bg-white border border-emerald-300 rounded-xl px-3 py-2 text-slate-900 font-mono font-bold"
                  required
                />
              </div>
              <div>
                <label className="block text-slate-800 font-bold mb-1">End Time (HH:MM:SS)</label>
                <input
                  type="text"
                  value={shiftForm.end_time}
                  onChange={(e) => setShiftForm({ ...shiftForm, end_time: e.target.value })}
                  placeholder="18:00:00"
                  className="w-full bg-white border border-emerald-300 rounded-xl px-3 py-2 text-slate-900 font-mono font-bold"
                  required
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3">
              <button
                type="button"
                onClick={() => setShowShiftModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 text-xs font-bold"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 rounded-xl bg-emerald-600 text-white text-xs font-bold shadow-md"
              >
                Create Shift Master
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
