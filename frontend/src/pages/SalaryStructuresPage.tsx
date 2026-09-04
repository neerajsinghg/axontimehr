import React, { useState, useEffect } from 'react';
import { DollarSign, Layers, Plus, Sparkles, CheckCircle, ShieldCheck } from 'lucide-react';
import { payrollApi, SalaryComponent, SalaryStructure } from '../services/api/payroll';

export const SalaryStructuresPage: React.FC = () => {
  const [components, setComponents] = useState<SalaryComponent[]>([]);
  const [structures, setStructures] = useState<SalaryStructure[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [seeding, setSeeding] = useState<boolean>(false);

  // Form State
  const [code, setCode] = useState<string>('');
  const [name, setName] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [creating, setCreating] = useState<boolean>(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [comps, structs] = await Promise.all([
        payrollApi.getComponents(),
        payrollApi.getStructures()
      ]);
      setComponents(comps);
      setStructures(structs);
    } catch (err) {
      console.error('Error fetching salary structure data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSeedDefaults = async () => {
    try {
      setSeeding(true);
      const comps = await payrollApi.seedComponents();
      setComponents(comps);
    } catch (err) {
      console.error('Error seeding default salary components:', err);
    } finally {
      setSeeding(false);
    }
  };

  const handleCreateStructure = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!code || !name) return;
    try {
      setCreating(true);
      await payrollApi.createStructure({
        code,
        name,
        description,
        components: []
      });
      setCode('');
      setName('');
      setDescription('');
      fetchData();
    } catch (err) {
      console.error('Error creating salary structure:', err);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white/60 backdrop-blur-md p-6 rounded-2xl border border-emerald-100 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <DollarSign className="w-7 h-7 text-emerald-600" />
            Salary Structures & Component Master
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Configure enterprise salary components, statutory formulas, and structure templates.
          </p>
        </div>

        <button
          onClick={handleSeedDefaults}
          disabled={seeding}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-xl font-medium shadow-md shadow-emerald-500/20 hover:from-emerald-600 hover:to-teal-700 transition disabled:opacity-50"
        >
          <Sparkles className="w-4 h-4" />
          {seeding ? 'Seeding Defaults...' : 'Seed Standard Components'}
        </button>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Create Structure Form */}
        <div className="bg-white/70 backdrop-blur-md p-6 rounded-2xl border border-emerald-100/80 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
            <Plus className="w-5 h-5 text-emerald-600" />
            Create Salary Structure
          </h2>

          <form onSubmit={handleCreateStructure} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 uppercase mb-1">Structure Code</label>
              <input
                type="text"
                value={code}
                onChange={(e) => setCode(e.target.value.toUpperCase())}
                placeholder="e.g. EXEC_FULL_TIME"
                required
                className="w-full px-3.5 py-2.5 bg-slate-50/80 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 font-mono text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 uppercase mb-1">Structure Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Full-Time Software Engineer"
                required
                className="w-full px-3.5 py-2.5 bg-slate-50/80 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 uppercase mb-1">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                placeholder="Details about component distribution..."
                className="w-full px-3.5 py-2.5 bg-slate-50/80 border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 text-sm"
              />
            </div>

            <button
              type="submit"
              disabled={creating}
              className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl shadow-md shadow-emerald-600/20 transition disabled:opacity-50"
            >
              {creating ? 'Saving...' : 'Save Salary Structure'}
            </button>
          </form>
        </div>

        {/* Existing Structures & Components List */}
        <div className="lg:col-span-2 space-y-6">
          {/* Component Master Cards */}
          <div className="bg-white/70 backdrop-blur-md p-6 rounded-2xl border border-emerald-100/80 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
              <Layers className="w-5 h-5 text-emerald-600" />
              Active Salary Components Master ({components.length})
            </h2>

            {loading ? (
              <div className="py-8 text-center text-slate-400">Loading components...</div>
            ) : components.length === 0 ? (
              <div className="py-8 text-center text-slate-500 bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
                No salary components found. Click "Seed Standard Components" to initialize.
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {components.map((comp) => (
                  <div key={comp.id} className="p-3.5 bg-slate-50/80 rounded-xl border border-slate-200/80 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-800 text-sm">{comp.name}</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        comp.component_type === 'EARNING' ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'
                      }`}>
                        {comp.component_type}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 font-mono">{comp.code} • {comp.calculation_type}</p>
                    {comp.formula && (
                      <p className="text-[11px] text-emerald-600 font-mono bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200/60 inline-block">
                        {comp.formula}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Structures List */}
          <div className="bg-white/70 backdrop-blur-md p-6 rounded-2xl border border-emerald-100/80 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-600" />
              Configured Salary Structures ({structures.length})
            </h2>

            {structures.length === 0 ? (
              <div className="py-8 text-center text-slate-500 bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
                No salary structures configured yet. Create one using the form on the left.
              </div>
            ) : (
              <div className="space-y-3">
                {structures.map((st) => (
                  <div key={st.id} className="p-4 bg-emerald-50/30 rounded-xl border border-emerald-100 flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-slate-800">{st.name}</h3>
                      <p className="text-xs text-slate-500 font-mono">{st.code} • {st.status}</p>
                    </div>
                    <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 bg-emerald-100 px-3 py-1 rounded-full">
                      <CheckCircle className="w-3.5 h-3.5" />
                      Active Structure
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
