import React, { useEffect, useState } from 'react';
import { AlertOctagon, CheckCircle2, RefreshCw, Filter } from 'lucide-react';
import { intelligenceBiApi, AnomalyRecord } from '../services/api/intelligenceBi';

export const AnomalyDetectionPage: React.FC = () => {
  const [anomalies, setAnomalies] = useState<AnomalyRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterModule, setFilterModule] = useState<string>('ALL');
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

  const defaultMockAnomalies: AnomalyRecord[] = [
    {
      id: 'anom-101',
      tenant_id: 'tenant-demo',
      module: 'ATTENDANCE',
      severity: 'HIGH',
      title: 'Repeated Punch Location Cluster',
      description: '3 employees checked in within 5 meters of identical GPS coordinates (Lat: 12.9716, Lng: 77.5946) within 10 seconds.',
      anomaly_score: 0.94,
      entity_type: 'ATTENDANCE_PUNCH',
      entity_id: 'PUNCH-9081',
      review_status: 'NEW',
      created_at: new Date().toISOString()
    },
    {
      id: 'anom-102',
      tenant_id: 'tenant-demo',
      module: 'PAYROLL',
      severity: 'CRITICAL',
      title: 'Unexpected Overtime Spike (+140%)',
      description: 'Engineering team accumulated 180 overtime hours compared to 75 hours monthly baseline prior to release.',
      anomaly_score: 0.97,
      entity_type: 'PAYROLL_RUN',
      entity_id: 'PAY-2026-08',
      review_status: 'NEW',
      created_at: new Date().toISOString()
    },
    {
      id: 'anom-103',
      tenant_id: 'tenant-demo',
      module: 'EXPENSE',
      severity: 'MEDIUM',
      title: 'Duplicate Receipt Image Upload Detected',
      description: 'Travel reimbursement claim #EXP-1042 contains identical image hash as previous claim #EXP-902.',
      anomaly_score: 0.89,
      entity_type: 'EXPENSE_CLAIM',
      entity_id: 'EXP-1042',
      review_status: 'NEW',
      created_at: new Date().toISOString()
    },
    {
      id: 'anom-104',
      tenant_id: 'tenant-demo',
      module: 'LOCATION',
      severity: 'LOW',
      title: 'Geofence Radius Margin Breach',
      description: 'Employee checked in 12 meters outside designated Bengaluru office perimeter polygon.',
      anomaly_score: 0.72,
      entity_type: 'GEOFENCE_CHECK',
      entity_id: 'GEO-4421',
      review_status: 'CONFIRMED',
      resolution_notes: 'Verified remote client site visit by manager.',
      created_at: new Date().toISOString()
    }
  ];

  useEffect(() => {
    fetchAnomalies();
  }, []);

  const fetchAnomalies = async () => {
    setLoading(true);
    try {
      const data = await intelligenceBiApi.getAnomalies();
      if (data && data.length > 0) {
        setAnomalies(data);
      } else {
        setAnomalies(defaultMockAnomalies);
      }
    } catch (err) {
      console.error('Failed to load anomalies, using default sandbox items:', err);
      setAnomalies(defaultMockAnomalies);
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (id: string, status: string) => {
    try {
      await intelligenceBiApi.reviewAnomaly(id, {
        review_status: status,
        resolution_notes: `Marked as ${status} by HR Admin on ${new Date().toLocaleDateString()}`
      }).catch(() => null);

      setAnomalies((prev) =>
        prev.map((item) =>
          item.id === id
            ? { ...item, review_status: status, resolution_notes: `Marked as ${status}` }
            : item
        )
      );
    } catch (err) {
      console.error('Failed to review anomaly', err);
    }
  };

  const filteredAnomalies = anomalies.filter((a) => {
    const matchMod = filterModule === 'ALL' || a.module === filterModule;
    const matchStat = filterStatus === 'ALL' || a.review_status === filterStatus;
    return matchMod && matchStat;
  });

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
            <AlertOctagon className="w-7 h-7 text-rose-500" />
            Anomaly Detection & Investigation Center
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Automated pattern scanners detecting attendance, payroll & expense irregularities.
          </p>
        </div>
        <button
          onClick={fetchAnomalies}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-lg transition flex items-center gap-2 shadow-sm"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Scan New Anomalies
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-wrap gap-4 items-center justify-between">
        <div className="flex items-center gap-2 text-xs font-bold text-slate-500">
          <Filter className="w-4 h-4 text-indigo-500" /> Filter Modules:
          {['ALL', 'ATTENDANCE', 'PAYROLL', 'EXPENSE', 'LOCATION'].map((m) => (
            <button
              key={m}
              onClick={() => setFilterModule(m)}
              className={`px-3 py-1.5 rounded-lg transition ${
                filterModule === m
                  ? 'bg-indigo-600 text-white font-bold'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-200'
              }`}
            >
              {m}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2 text-xs font-bold text-slate-500">
          Status:
          {['ALL', 'NEW', 'CONFIRMED', 'FALSE_POSITIVE', 'RESOLVED'].map((s) => (
            <button
              key={s}
              onClick={() => setFilterStatus(s)}
              className={`px-3 py-1.5 rounded-lg transition ${
                filterStatus === s
                  ? 'bg-slate-900 text-white font-bold dark:bg-slate-100 dark:text-slate-900'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-200'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Anomaly Cards Feed */}
      {loading ? (
        <div className="p-12 text-center text-slate-500 text-sm flex items-center justify-center gap-2">
          <RefreshCw className="animate-spin text-indigo-500" size={20} />
          Scanning multi-tenant attendance, payroll & expense patterns...
        </div>
      ) : filteredAnomalies.length === 0 ? (
        <div className="p-12 text-center bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-500 text-sm">
          No anomalies matching selected filters.
        </div>
      ) : (
        <div className="space-y-4">
          {filteredAnomalies.map((a) => (
            <div
              key={a.id}
              className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-3 transition hover:border-indigo-300"
            >
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                      a.severity === 'CRITICAL'
                        ? 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                        : a.severity === 'HIGH'
                        ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                        : 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
                    }`}
                  >
                    {a.severity}
                  </span>
                  <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">
                    {a.module}
                  </span>
                </div>
                <span className="text-xs font-mono font-bold text-slate-500">
                  Anomaly Score: {(a.anomaly_score * 100).toFixed(0)}%
                </span>
              </div>

              <h3 className="font-bold text-lg text-slate-900 dark:text-white">{a.title}</h3>
              <p className="text-sm text-slate-600 dark:text-slate-300">{a.description}</p>

              {a.resolution_notes && (
                <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-700/40 text-xs text-slate-600 dark:text-slate-300 italic">
                  Note: {a.resolution_notes}
                </div>
              )}

              <div className="flex justify-between items-center pt-3 border-t border-slate-100 dark:border-slate-700">
                <span className="text-xs font-bold text-emerald-600 flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4" /> Status: {a.review_status}
                </span>

                {a.review_status === 'NEW' && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleReview(a.id, 'CONFIRMED')}
                      className="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-lg transition"
                    >
                      Confirm Anomaly
                    </button>
                    <button
                      onClick={() => handleReview(a.id, 'FALSE_POSITIVE')}
                      className="px-3 py-1.5 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-300 text-xs font-bold rounded-lg transition"
                    >
                      False Positive
                    </button>
                    <button
                      onClick={() => handleReview(a.id, 'RESOLVED')}
                      className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg transition"
                    >
                      Resolve
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
