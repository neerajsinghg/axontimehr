import React, { useEffect, useState } from 'react';
import { Sliders, Plus } from 'lucide-react';
import { intelligenceBiApi, ScenarioModel } from '../services/api/intelligenceBi';

export const ScenarioPlannerPage: React.FC = () => {
  const [scenarios, setScenarios] = useState<ScenarioModel[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState('');
  const [hires, setHires] = useState(10);
  const [avgSalary, setAvgSalary] = useState(1500000);

  useEffect(() => {
    fetchScenarios();
  }, []);

  const fetchScenarios = async () => {
    try {
      const data = await intelligenceBiApi.getScenarios();
      setScenarios(data);
    } catch (err) {
      console.error('Failed to load scenarios', err);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await intelligenceBiApi.createScenario({
        scenario_name: name || 'Q4 Expansion Scenario',
        input_parameters: { additional_hires: Number(hires), average_salary_inr: Number(avgSalary) }
      });
      setShowModal(false);
      fetchScenarios();
    } catch (err) {
      console.error('Failed to create scenario', err);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
            <Sliders className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
            "What-If" Workforce Scenario Analysis Tool
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Simulate hiring plans, salary budget adjustments & headcount expansions safely.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition"
        >
          <Plus className="w-4 h-4" />
          Create What-If Scenario
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {scenarios.map((s) => (
          <div key={s.id} className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
            <h3 className="font-bold text-lg text-slate-900 dark:text-white">{s.scenario_name}</h3>
            <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-600 dark:text-slate-300">Additional Hires:</span>
                <span className="font-bold text-indigo-600 dark:text-indigo-400">+{s.input_parameters_json.additional_hires}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-600 dark:text-slate-300">Annual Payroll Increase:</span>
                <span className="font-bold text-emerald-600">₹{s.projected_results_json.annual_payroll_increase_inr?.toLocaleString()}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 max-w-md w-full space-y-4">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">New What-If Scenario</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Scenario Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded dark:bg-slate-700 dark:text-white text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Additional Hires</label>
                <input
                  type="number"
                  value={hires}
                  onChange={(e) => setHires(Number(e.target.value))}
                  className="w-full p-2 border border-slate-300 rounded dark:bg-slate-700 dark:text-white text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1">Average Gross Salary (INR)</label>
                <input
                  type="number"
                  value={avgSalary}
                  onChange={(e) => setAvgSalary(Number(e.target.value))}
                  className="w-full p-2 border border-slate-300 rounded dark:bg-slate-700 dark:text-white text-sm"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-sm text-slate-500">
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 bg-indigo-600 text-white font-semibold text-sm rounded">
                  Run Simulation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
