import React, { useState, useEffect } from 'react';
import { Plus, Layers, Sparkles } from 'lucide-react';
import { leaveApi, LeaveType } from '../../services/api/leave';

interface LeaveCategoryPreset {
  code: string;
  name: string;
  color_code: string;
  paid: boolean;
  requires_document: boolean;
  allow_half_day: boolean;
  allow_backdated: boolean;
  allow_future: boolean;
  minimum_notice_days: number;
  description: string;
}

const PRESET_CATEGORIES: LeaveCategoryPreset[] = [
  {
    code: 'CASUAL_LEAVE',
    name: 'Casual Leave (CL)',
    color_code: '#3B82F6',
    paid: true,
    requires_document: false,
    allow_half_day: true,
    allow_backdated: false,
    allow_future: true,
    minimum_notice_days: 1,
    description: 'Short notice personal leave for routine tasks and emergencies.'
  },
  {
    code: 'SICK_LEAVE',
    name: 'Sick Leave (SL)',
    color_code: '#EF4444',
    paid: true,
    requires_document: true,
    allow_half_day: true,
    allow_backdated: true,
    allow_future: false,
    minimum_notice_days: 0,
    description: 'Medical and health recovery leave. Requires medical certificate.'
  },
  {
    code: 'PRIVILEGE_LEAVE',
    name: 'Privilege Leave (PL)',
    color_code: '#059669',
    paid: true,
    requires_document: false,
    allow_half_day: true,
    allow_backdated: false,
    allow_future: true,
    minimum_notice_days: 7,
    description: 'Privilege accrued annual leave for scheduled vacations and planned time off.'
  },
  {
    code: 'EARNED_LEAVE',
    name: 'Earned Leave (EL / AL)',
    color_code: '#10B981',
    paid: true,
    requires_document: false,
    allow_half_day: true,
    allow_backdated: false,
    allow_future: true,
    minimum_notice_days: 7,
    description: 'Annual accrued leave for vacations and planned extended time off.'
  },
  {
    code: 'MATERNITY_LEAVE',
    name: 'Maternity Leave (ML)',
    color_code: '#EC4899',
    paid: true,
    requires_document: true,
    allow_half_day: false,
    allow_backdated: false,
    allow_future: true,
    minimum_notice_days: 30,
    description: 'Statutory maternity entitlement for female employees.'
  },
  {
    code: 'PATERNITY_LEAVE',
    name: 'Paternity Leave (PL)',
    color_code: '#8B5CF6',
    paid: true,
    requires_document: true,
    allow_half_day: false,
    allow_backdated: false,
    allow_future: true,
    minimum_notice_days: 7,
    description: 'Paternity entitlement for new fathers.'
  },
  {
    code: 'COMP_OFF',
    name: 'Compensatory Off (Comp-Off)',
    color_code: '#F59E0B',
    paid: true,
    requires_document: false,
    allow_half_day: true,
    allow_backdated: false,
    allow_future: true,
    minimum_notice_days: 1,
    description: 'Leave earned against working on weekends or official holidays.'
  },
  {
    code: 'BEREAVEMENT_LEAVE',
    name: 'Bereavement Leave (BL)',
    color_code: '#6B7280',
    paid: true,
    requires_document: false,
    allow_half_day: true,
    allow_backdated: true,
    allow_future: false,
    minimum_notice_days: 0,
    description: 'Compassionate leave granted in the event of family bereavement.'
  },
  {
    code: 'MARRIAGE_LEAVE',
    name: 'Marriage Leave',
    color_code: '#F43F5E',
    paid: true,
    requires_document: true,
    allow_half_day: false,
    allow_backdated: false,
    allow_future: true,
    minimum_notice_days: 15,
    description: 'Special leave granted for employee marriage.'
  },
  {
    code: 'UNPAID_LEAVE',
    name: 'Loss of Pay (LOP / Unpaid)',
    color_code: '#64748B',
    paid: false,
    requires_document: false,
    allow_half_day: true,
    allow_backdated: true,
    allow_future: true,
    minimum_notice_days: 0,
    description: 'Leave without pay when paid balance is exhausted.'
  }
];

export const LeaveSettingsTab: React.FC = () => {
  const [types, setTypes] = useState<LeaveType[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [batchSeeding, setBatchSeeding] = useState<boolean>(false);

  // Form State
  const [selectedPreset, setSelectedPreset] = useState<string>('');
  const [code, setCode] = useState<string>('');
  const [name, setName] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [colorCode, setColorCode] = useState<string>('#10B981');
  const [paid, setPaid] = useState<boolean>(true);
  const [requiresDocument, setRequiresDocument] = useState<boolean>(false);
  const [allowHalfDay, setAllowHalfDay] = useState<boolean>(true);
  const [allowBackdated, setAllowBackdated] = useState<boolean>(false);
  const [allowFuture, setAllowFuture] = useState<boolean>(true);
  const [minimumNoticeDays, setMinimumNoticeDays] = useState<number>(0);
  const [submitting, setSubmitting] = useState<boolean>(false);

  useEffect(() => {
    loadTypes();
  }, []);

  const loadTypes = async () => {
    try {
      setLoading(true);
      const data = await leaveApi.getLeaveTypes();
      setTypes(data);
    } catch (err) {
      console.error('Error loading leave types:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPreset = (presetCode: string) => {
    setSelectedPreset(presetCode);
    if (!presetCode) return;
    const preset = PRESET_CATEGORIES.find((p) => p.code === presetCode);
    if (preset) {
      setCode(preset.code);
      setName(preset.name);
      setDescription(preset.description);
      setColorCode(preset.color_code);
      setPaid(preset.paid);
      setRequiresDocument(preset.requires_document);
      setAllowHalfDay(preset.allow_half_day);
      setAllowBackdated(preset.allow_backdated);
      setAllowFuture(preset.allow_future);
      setMinimumNoticeDays(preset.minimum_notice_days);
    }
  };

  const handleCreateType = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await leaveApi.createLeaveType({
        code,
        name,
        description,
        color_code: colorCode,
        paid,
        requires_document: requiresDocument,
        allow_half_day: allowHalfDay,
        allow_backdated: allowBackdated,
        allow_future: allowFuture,
        minimum_notice_days: minimumNoticeDays
      });
      setIsModalOpen(false);
      resetForm();
      loadTypes();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create leave type.');
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setSelectedPreset('');
    setCode('');
    setName('');
    setDescription('');
    setColorCode('#10B981');
    setPaid(true);
    setRequiresDocument(false);
    setAllowHalfDay(true);
    setAllowBackdated(false);
    setAllowFuture(true);
    setMinimumNoticeDays(0);
  };

  const handleSeedStandardCategories = async () => {
    if (!window.confirm('Seed standard HR leave categories (CL, SL, PL, EL, LOP, Comp-Off)?')) return;
    try {
      setBatchSeeding(true);
      const existingCodes = new Set(types.map((t) => t.code));
      for (const preset of PRESET_CATEGORIES.slice(0, 7)) {
        if (!existingCodes.has(preset.code)) {
          await leaveApi.createLeaveType({
            code: preset.code,
            name: preset.name,
            description: preset.description,
            color_code: preset.color_code,
            paid: preset.paid,
            requires_document: preset.requires_document,
            allow_half_day: preset.allow_half_day,
            allow_backdated: preset.allow_backdated,
            allow_future: preset.allow_future,
            minimum_notice_days: preset.minimum_notice_days
          });
        }
      }
      loadTypes();
    } catch (err: any) {
      alert('Failed to seed standard categories.');
    } finally {
      setBatchSeeding(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <Layers className="text-emerald-600" /> Leave Category Masters
          </h2>
          <p className="text-xs text-slate-500">Configure paid/unpaid leave categories, rules, and document requirements.</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleSeedStandardCategories}
            disabled={batchSeeding}
            className="px-3.5 py-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-semibold text-xs rounded-xl border border-emerald-200 transition-all flex items-center gap-1.5 disabled:opacity-50"
          >
            <Sparkles size={15} /> {batchSeeding ? 'Seeding...' : 'Auto-Seed Standard Types'}
          </button>
          <button
            onClick={() => {
              resetForm();
              setIsModalOpen(true);
            }}
            className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-xl shadow-md flex items-center gap-1.5 transition-all"
          >
            <Plus size={16} /> Add Leave Category
          </button>
        </div>
      </div>

      {/* Grid of Categories */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading ? (
          <div className="col-span-3 text-center py-8 text-slate-500 text-xs">Loading leave types...</div>
        ) : types.length === 0 ? (
          <div className="col-span-3 glass-card p-6 text-center space-y-3 rounded-2xl">
            <Layers className="mx-auto text-emerald-600" size={32} />
            <p className="text-slate-700 font-semibold text-sm">No leave categories configured yet.</p>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Click <strong>"Auto-Seed Standard Types"</strong> to instantly create standard Casual, Sick, and Earned Leave options.
            </p>
          </div>
        ) : (
          types.map((t) => (
            <div key={t.id} className="glass-card p-4 rounded-xl space-y-3 relative overflow-hidden">
              <div className="absolute top-0 left-0 bottom-0 w-1.5" style={{ backgroundColor: t.color_code || '#10B981' }} />
              
              <div className="flex justify-between items-start pl-2">
                <div>
                  <h4 className="font-bold text-slate-800 text-sm">{t.name}</h4>
                  <span className="text-[10px] font-mono text-slate-400 uppercase">{t.code}</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className={`px-2 py-0.5 text-[10px] font-bold rounded-md uppercase ${t.paid ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-200 text-slate-700'}`}>
                    {t.paid ? 'Paid' : 'Unpaid'}
                  </span>
                </div>
              </div>

              {t.description && (
                <p className="pl-2 text-xs text-slate-600 line-clamp-2">{t.description}</p>
              )}

              <div className="pl-2 pt-1 text-[11px] text-slate-500 space-y-1 border-t border-emerald-50">
                <div className="flex justify-between">
                  <span>Half Day: <strong>{t.allow_half_day ? 'Allowed' : 'Prohibited'}</strong></span>
                  <span>Document Req: <strong className={t.requires_document ? 'text-amber-600' : 'text-slate-500'}>{t.requires_document ? 'Yes' : 'No'}</strong></span>
                </div>
                <div className="flex justify-between">
                  <span>Backdated: <strong>{t.allow_backdated ? 'Allowed' : 'No'}</strong></span>
                  <span>Min Notice: <strong>{t.minimum_notice_days} Days</strong></span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Add / Custom Leave Category Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-card bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4 animate-in fade-in zoom-in-95 overflow-y-auto max-h-[90vh]">
            <div className="flex justify-between items-center border-b border-emerald-100 pb-3">
              <h3 className="text-base font-bold text-slate-800">Add / Configure Leave Category</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-600">✕</button>
            </div>

            {/* Quick Preset Selector */}
            <div className="p-3 bg-emerald-50/60 rounded-xl space-y-1.5 border border-emerald-100">
              <label className="block text-xs font-bold text-emerald-900 flex items-center gap-1">
                <Sparkles size={14} className="text-emerald-600" /> Choose Preset Leave Option (Fast Fill)
              </label>
              <select
                value={selectedPreset}
                onChange={(e) => handleSelectPreset(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-emerald-200 rounded-lg outline-none text-xs font-medium"
              >
                <option value="">-- Custom Category --</option>
                {PRESET_CATEGORIES.map((p) => (
                  <option key={p.code} value={p.code}>
                    {p.name} ({p.paid ? 'Paid' : 'Unpaid'})
                  </option>
                ))}
              </select>
            </div>

            <form onSubmit={handleCreateType} className="space-y-3.5 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-slate-700 mb-1">Category Code</label>
                  <input
                    type="text"
                    value={code}
                    onChange={(e) => setCode(e.target.value.toUpperCase().replace(/\s+/g, '_'))}
                    placeholder="e.g. CASUAL_LEAVE"
                    className="w-full px-3 py-2 bg-slate-50 border border-emerald-200 rounded-lg outline-none font-mono text-xs"
                    required
                  />
                </div>
                <div>
                  <label className="block font-medium text-slate-700 mb-1">Category Name</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Casual Leave"
                    className="w-full px-3 py-2 bg-slate-50 border border-emerald-200 rounded-lg outline-none text-xs"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">Description</label>
                <input
                  type="text"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Short description of entitlement rules..."
                  className="w-full px-3 py-2 bg-slate-50 border border-emerald-200 rounded-lg outline-none text-xs"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">Theme Color</label>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    value={colorCode}
                    onChange={(e) => setColorCode(e.target.value)}
                    className="h-8 w-14 p-0.5 bg-slate-50 border border-emerald-200 rounded-lg cursor-pointer"
                  />
                  <span className="font-mono text-xs text-slate-500">{colorCode}</span>
                </div>
              </div>

              {/* Checkbox Options */}
              <div className="p-3 bg-slate-50 rounded-xl space-y-2 border border-slate-200/60">
                <h4 className="font-bold text-slate-700 text-xs mb-1">Entitlement & Constraint Rules</h4>
                <div className="grid grid-cols-2 gap-2 text-slate-700">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={paid}
                      onChange={(e) => setPaid(e.target.checked)}
                      className="text-emerald-600 rounded"
                    />
                    Paid Leave
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={allowHalfDay}
                      onChange={(e) => setAllowHalfDay(e.target.checked)}
                      className="text-emerald-600 rounded"
                    />
                    Allow Half-Day
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={requiresDocument}
                      onChange={(e) => setRequiresDocument(e.target.checked)}
                      className="text-emerald-600 rounded"
                    />
                    Require Medical Doc
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={allowBackdated}
                      onChange={(e) => setAllowBackdated(e.target.checked)}
                      className="text-emerald-600 rounded"
                    />
                    Allow Backdated
                  </label>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-slate-700 mb-1">Minimum Advance Notice (Days)</label>
                  <input
                    type="number"
                    min="0"
                    value={minimumNoticeDays}
                    onChange={(e) => setMinimumNoticeDays(parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 bg-slate-50 border border-emerald-200 rounded-lg outline-none text-xs"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-emerald-100">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl shadow-md disabled:opacity-50"
                >
                  {submitting ? 'Saving...' : 'Save Category'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
