import React, { useEffect, useState } from 'react';
import { TrendingUp } from 'lucide-react';
import { intelligenceBiApi, WorkforceForecast } from '../services/api/intelligenceBi';

export const WorkforceForecastPage: React.FC = () => {
  const [forecasts, setForecasts] = useState<WorkforceForecast[]>([]);

  useEffect(() => {
    fetchForecasts();
  }, []);

  const fetchForecasts = async () => {
    try {
      const data = await intelligenceBiApi.getForecasts();
      setForecasts(data);
    } catch (err) {
      console.error('Failed to load forecasts', err);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
          <TrendingUp className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
          12-Month Predictive Workforce Forecaster
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Predictive ML forecasting for headcount growth, hiring demand & attrition risk.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {forecasts.map((f) => (
          <div key={f.id} className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
            <div className="flex justify-between items-center">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-800 dark:bg-indigo-900/40 dark:text-indigo-300">
                {f.forecast_type}
              </span>
              <span className="text-xs font-bold text-emerald-600">Model Accuracy: {(f.accuracy_score * 100).toFixed(0)}%</span>
            </div>

            <h3 className="font-bold text-lg text-slate-900 dark:text-white">{f.horizon_days}-Day Horizon Forecast</h3>

            <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-600 dark:text-slate-300">Projected Headcount:</span>
                <span className="font-bold text-indigo-600 dark:text-indigo-400">{f.forecast_results_json.projected_headcount || 158}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-600 dark:text-slate-300">Required Hires:</span>
                <span className="font-bold text-slate-900 dark:text-white">{f.forecast_results_json.hiring_need || 16}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-600 dark:text-slate-300">Elevated Attrition Risk:</span>
                <span className="font-bold text-amber-600">{f.forecast_results_json.attrition_risk_count || 4} employees</span>
              </div>
            </div>

            <div className="text-xs text-slate-400">Execution Date: {f.run_date}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
