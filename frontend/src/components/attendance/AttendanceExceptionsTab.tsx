import React, { useState, useEffect } from 'react';
import { AlertTriangle, RefreshCw, CheckCircle2, Image as ImageIcon } from 'lucide-react';
import { locationApi, AttendanceExceptionItem } from '../../services/api/location';

export const AttendanceExceptionsTab: React.FC = () => {
  const [exceptions, setExceptions] = useState<AttendanceExceptionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [selectedSelfieId, setSelectedSelfieId] = useState<string | null>(null);

  const fetchExceptions = async () => {
    setLoading(true);
    try {
      const res = await locationApi.getExceptions(1, 20);
      setExceptions(res.data);
      setTotal(res.total);
    } catch (err) {
      console.error('Failed to load attendance exceptions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExceptions();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header Stat & Actions */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-amber-50 text-amber-600 rounded-xl border border-amber-100">
            <AlertTriangle className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-800">Attendance Exception Dashboard</h3>
            <p className="text-xs text-slate-500">Monitor outside-geofence punches, low accuracy GPS, and failed identity verifications.</p>
          </div>
        </div>
        <button
          onClick={fetchExceptions}
          className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-sm font-medium flex items-center space-x-2 transition"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Exceptions</span>
        </button>
      </div>

      {/* Exception Records Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">
            Flagged Punch Records ({total})
          </span>
        </div>

        {loading ? (
          <div className="p-12 text-center">
            <RefreshCw className="animate-spin h-8 w-8 text-emerald-600 mx-auto" />
            <p className="text-xs text-slate-500 mt-2">Loading exception records...</p>
          </div>
        ) : exceptions.length === 0 ? (
          <div className="p-12 text-center">
            <CheckCircle2 className="h-10 w-10 text-emerald-500 mx-auto mb-2" />
            <p className="text-sm font-bold text-slate-700">All Punches Validated!</p>
            <p className="text-xs text-slate-400">No outside-geofence or failed identity verification exceptions found.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-xs uppercase font-semibold text-slate-500 border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3">Employee</th>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">Geofence Status</th>
                  <th className="px-4 py-3">Selfie Verification</th>
                  <th className="px-4 py-3">GPS Coordinates</th>
                  <th className="px-4 py-3">Distance</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {exceptions.map((exc) => (
                  <tr key={exc.attendance_id} className="hover:bg-slate-50/50">
                    <td className="px-4 py-3 font-semibold text-slate-800">{exc.employee_name}</td>
                    <td className="px-4 py-3 text-xs font-mono text-slate-600">{exc.attendance_date}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                        exc.location_status === 'INSIDE'
                          ? 'bg-emerald-100 text-emerald-800'
                          : exc.location_status === 'OUTSIDE'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-slate-100 text-slate-700'
                      }`}>
                        {exc.location_status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                        exc.verification_status === 'VERIFIED'
                          ? 'bg-emerald-100 text-emerald-800'
                          : exc.verification_status === 'FAILED'
                          ? 'bg-rose-100 text-rose-800'
                          : 'bg-slate-100 text-slate-700'
                      }`}>
                        {exc.verification_status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs font-mono text-slate-600">
                      {exc.latitude && exc.longitude ? `${exc.latitude.toFixed(4)}, ${exc.longitude.toFixed(4)}` : 'N/A'}
                    </td>
                    <td className="px-4 py-3 text-xs font-medium">
                      {exc.distance_meters !== undefined && exc.distance_meters !== null ? `${exc.distance_meters}m` : 'N/A'}
                    </td>
                    <td className="px-4 py-3">
                      {exc.verification_id ? (
                        <button
                          onClick={() => setSelectedSelfieId(exc.verification_id || null)}
                          className="px-2.5 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded text-xs font-semibold flex items-center space-x-1 border border-emerald-200"
                        >
                          <ImageIcon className="h-3.5 w-3.5" />
                          <span>View Selfie</span>
                        </button>
                      ) : (
                        <span className="text-xs text-slate-400">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Selfie Preview Modal */}
      {selectedSelfieId && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-sm w-full p-5 shadow-xl border border-slate-200 text-center space-y-4">
            <div className="flex justify-between items-center border-b pb-2">
              <h4 className="font-bold text-slate-800 text-sm">Verified Selfie Preview</h4>
              <button onClick={() => setSelectedSelfieId(null)} className="text-slate-400 hover:text-slate-600 text-sm">✕</button>
            </div>
            <div className="aspect-square bg-slate-100 rounded-lg overflow-hidden border border-slate-200 flex items-center justify-center">
              <img
                src={`/api/v1/attendance/verification/selfie/${selectedSelfieId}`}
                alt="Selfie Preview"
                className="w-full h-full object-cover"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = 'https://via.placeholder.com/300?text=Selfie+Image+Preview';
                }}
              />
            </div>
            <button
              onClick={() => setSelectedSelfieId(null)}
              className="w-full py-2 bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold rounded-lg"
            >
              Close Preview
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
