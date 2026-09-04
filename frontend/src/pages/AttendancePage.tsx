import React, { useState, useEffect } from 'react';
import {
  Clock,
  LogIn,
  LogOut,
  CheckCircle2,
  AlertCircle,
  Calendar,
  Users,
  FileCheck,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Camera,
  AlertTriangle,
  Compass
} from 'lucide-react';
import {
  attendanceApi,
  DailyAttendanceStatus,
  AttendanceRecord,
  AttendanceDashboardMetrics,
} from '../services/api/attendance';
import { locationApi, LocationValidateResponse } from '../services/api/location';
import { AttendanceExceptionsTab } from '../components/attendance/AttendanceExceptionsTab';

export const AttendancePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'punch' | 'exceptions'>('punch');
  const [todayStatus, setTodayStatus] = useState<DailyAttendanceStatus | null>(null);
  const [dashboardMetrics, setDashboardMetrics] = useState<AttendanceDashboardMetrics | null>(null);
  const [history, setHistory] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [punching, setPunching] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // GPS & Geofence State
  const [gpsLocation, setGpsLocation] = useState<{ latitude: number; longitude: number; accuracy: number } | null>(null);
  const [gettingGps, setGettingGps] = useState(false);
  const [geofencePrecheck, setGeofencePrecheck] = useState<LocationValidateResponse | null>(null);

  // Selfie Verification State
  const [selfieFile, setSelfieFile] = useState<File | null>(null);
  const [selfiePreview, setSelfiePreview] = useState<string | null>(null);
  const [verificationId, setVerificationId] = useState<string | null>(null);
  const [showSelfieModal, setShowSelfieModal] = useState(false);

  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);

  // Filters
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // Regularization Modal
  const [showRegModal, setShowRegModal] = useState(false);
  const [regDate, setRegDate] = useState(new Date().toISOString().split('T')[0]);
  const [regReason, setRegReason] = useState('');
  const [regCheckIn, setRegCheckIn] = useState('');
  const [regCheckOut, setRegCheckOut] = useState('');
  const [regSubmitting, setRegSubmitting] = useState(false);

  // Live Work Duration Counter
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const fetchTodayAndMetrics = async () => {
    try {
      const [todayData, metrics] = await Promise.all([
        attendanceApi.getTodayStatus(),
        attendanceApi.getDashboardMetrics().catch(() => null),
      ]);
      setTodayStatus(todayData);
      setDashboardMetrics(metrics);
    } catch (err) {
      console.error('Failed to load today status:', err);
    }
  };

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const res = await attendanceApi.getMyHistory(page, 10, startDate || undefined, endDate || undefined);
      setHistory(res.data);
      setTotalPages(res.total_pages);
      setTotalRecords(res.total);
    } catch (err) {
      console.error('Failed to load attendance history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTodayAndMetrics();
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [page, startDate, endDate]);

  // Live ticker for checked-in status
  useEffect(() => {
    let interval: any = null;
    if (todayStatus?.is_checked_in && todayStatus.first_check_in) {
      const startTime = new Date(todayStatus.first_check_in).getTime();
      const updateTimer = () => {
        const now = new Date().getTime();
        setElapsedSeconds(Math.max(0, Math.floor((now - startTime) / 1000)));
      };
      updateTimer();
      interval = setInterval(updateTimer, 1000);
    } else {
      setElapsedSeconds(0);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [todayStatus]);

  // Capture Live GPS Coordinates via HTML5 Geolocation API
  const handleCaptureGPS = () => {
    if (!navigator.geolocation) {
      setErrorMsg('Geolocation is not supported by your browser.');
      return;
    }
    setGettingGps(true);
    setErrorMsg('');
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const coords = {
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
          accuracy: pos.coords.accuracy
        };
        setGpsLocation(coords);
        setGettingGps(false);
        try {
          const precheck = await locationApi.validateLocation({
            latitude: coords.latitude,
            longitude: coords.longitude,
            accuracy: coords.accuracy
          });
          setGeofencePrecheck(precheck);
        } catch (err) {
          console.error('Location precheck failed:', err);
        }
      },
      (err) => {
        setGettingGps(false);
        setErrorMsg(`GPS Capture failed: ${err.message}. Please enable location permissions.`);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  };

  const handleSelfieFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelfieFile(file);
      setSelfiePreview(URL.createObjectURL(file));
    }
  };

  const handleUploadSelfie = async () => {
    if (!selfieFile) return;
    try {
      const res = await locationApi.uploadSelfie(selfieFile);
      setVerificationId(res.verification_id);
      setShowSelfieModal(false);
      setSuccessMsg(`Selfie verified (${res.status})`);
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to upload selfie');
    }
  };

  const handlePunchCheckIn = async () => {
    try {
      setPunching(true);
      setErrorMsg('');
      await attendanceApi.checkIn('WEB', 'Web Check-In Punch');
      setSuccessMsg('Check-In recorded successfully!');
      setTimeout(() => setSuccessMsg(''), 4000);
      await fetchTodayAndMetrics();
      await fetchHistory();
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setErrorMsg(typeof detail === 'object' ? detail.message : detail || 'Failed to check in.');
    } finally {
      setPunching(false);
    }
  };

  const handlePunchCheckOut = async () => {
    try {
      setPunching(true);
      setErrorMsg('');
      await attendanceApi.checkOut('WEB', 'Web Check-Out Punch');
      setSuccessMsg('Check-Out recorded successfully!');
      setTimeout(() => setSuccessMsg(''), 4000);
      await fetchTodayAndMetrics();
      await fetchHistory();
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setErrorMsg(typeof detail === 'object' ? detail.message : detail || 'Failed to check out.');
    } finally {
      setPunching(false);
    }
  };

  const handleRegSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setRegSubmitting(true);
      await attendanceApi.requestRegularization(regDate, regReason, regCheckIn || undefined, regCheckOut || undefined);
      setShowRegModal(false);
      setRegReason('');
      setRegCheckIn('');
      setRegCheckOut('');
      setSuccessMsg('Attendance regularization requested successfully.');
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to submit regularization request');
    } finally {
      setRegSubmitting(false);
    }
  };

  const formatSeconds = (sec: number) => {
    const hrs = Math.floor(sec / 3600);
    const mins = Math.floor((sec % 3600) / 60);
    const secs = sec % 60;
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusBadge = (statusStr: string) => {
    switch (statusStr) {
      case 'PRESENT':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-emerald-100 text-emerald-900 border border-emerald-300">PRESENT</span>;
      case 'LATE':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-amber-100 text-amber-900 border border-amber-300">LATE</span>;
      case 'EARLY_EXIT':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-orange-100 text-orange-900 border border-orange-300">EARLY EXIT</span>;
      case 'HALF_DAY':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-blue-100 text-blue-900 border border-blue-300">HALF DAY</span>;
      case 'REGULARIZED':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-teal-100 text-teal-900 border border-teal-300">REGULARIZED</span>;
      case 'ABSENT':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-rose-100 text-rose-900 border border-rose-300">ABSENT</span>;
      case 'WEEK_OFF':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-slate-100 text-slate-700 border border-slate-300">WEEK OFF</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-slate-100 text-slate-800 border border-slate-300">{statusStr}</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 flex items-center gap-2.5 tracking-tight">
            <Clock className="text-emerald-600" size={26} />
            Attendance Punch Engine
          </h1>
          <p className="text-slate-700 text-xs mt-1 font-semibold">
            Real-time shift punches, GPS geofencing, selfie identity verification, and exceptions.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowRegModal(true)}
            className="px-4 py-2 rounded-xl bg-white border border-emerald-300 text-emerald-900 font-extrabold text-xs flex items-center gap-2 shadow-sm hover:bg-emerald-50 transition-all"
          >
            <FileCheck size={16} className="text-emerald-600" /> Request Regularization
          </button>
        </div>
      </div>

      {/* Tabs Bar */}
      <div className="flex gap-2 p-1.5 rounded-2xl glass-card border border-emerald-300/80 bg-white/90 text-xs font-bold shadow-sm">
        <button
          onClick={() => setActiveTab('punch')}
          className={`px-4 py-2 rounded-xl flex items-center gap-2 transition-all ${
            activeTab === 'punch'
              ? 'bg-emerald-600 text-white shadow-md font-extrabold'
              : 'text-slate-700 hover:text-emerald-900 hover:bg-emerald-100/70 font-bold'
          }`}
        >
          <Clock size={16} /> Live Punch Card
        </button>
        <button
          onClick={() => setActiveTab('exceptions')}
          className={`px-4 py-2 rounded-xl flex items-center gap-2 transition-all ${
            activeTab === 'exceptions'
              ? 'bg-emerald-600 text-white shadow-md font-extrabold'
              : 'text-slate-700 hover:text-emerald-900 hover:bg-emerald-100/70 font-bold'
          }`}
        >
          <AlertTriangle size={16} /> Exception Dashboard
        </button>
      </div>

      {activeTab === 'exceptions' ? (
        <AttendanceExceptionsTab />
      ) : (
        <>
          {/* Notifications */}
          {successMsg && (
            <div className="p-3.5 rounded-xl bg-emerald-100 border border-emerald-400 text-emerald-950 text-xs flex items-center gap-2 font-bold shadow-sm">
              <CheckCircle2 size={16} className="text-emerald-700" /> {successMsg}
            </div>
          )}
          {errorMsg && (
            <div className="p-3.5 rounded-xl bg-rose-100 border border-rose-400 text-rose-950 text-xs flex items-center gap-2 font-bold shadow-sm">
              <AlertCircle size={16} className="text-rose-700" /> {errorMsg}
            </div>
          )}

          {/* Main Grid: Interactive Punch Widget & Today's Summary */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Interactive Check-In / Check-Out Card */}
            <div className="lg:col-span-1 glass-card p-6 rounded-2xl border border-emerald-300/80 bg-white/95 shadow-md flex flex-col justify-between space-y-6">
              <div>
                <div className="flex items-center justify-between border-b border-emerald-100 pb-3">
                  <span className="text-xs font-extrabold text-slate-800 uppercase tracking-wider">Today's Punch Status</span>
                  <span className="text-[11px] font-mono font-extrabold text-emerald-800 bg-emerald-100 px-2.5 py-0.5 rounded-full border border-emerald-300">
                    {todayStatus?.today_date || new Date().toISOString().split('T')[0]}
                  </span>
                </div>

                <div className="mt-4 space-y-3">
                  <div className="p-3.5 rounded-xl bg-emerald-50/80 border border-emerald-200 flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-700">Assigned Shift</span>
                    <span className="text-xs font-extrabold text-emerald-900 font-mono">
                      {todayStatus?.shift ? `${todayStatus.shift.name} (${todayStatus.shift.start_time.slice(0,5)} - ${todayStatus.shift.end_time.slice(0,5)})` : 'General Shift (09:00 - 18:00)'}
                    </span>
                  </div>

                  {/* GPS Live Geofence Status Indicator Widget */}
                  <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                        <Compass className="h-4 w-4 text-emerald-600" /> GPS Geofence Check
                      </span>
                      <button
                        onClick={handleCaptureGPS}
                        disabled={gettingGps}
                        className="text-[10px] px-2 py-0.5 bg-emerald-600 text-white rounded font-bold hover:bg-emerald-700"
                      >
                        {gettingGps ? 'Locating...' : 'Get GPS Location'}
                      </button>
                    </div>

                    {gpsLocation ? (
                      <div className="text-[11px] font-mono text-slate-600 flex justify-between items-center">
                        <span>{gpsLocation.latitude.toFixed(4)}, {gpsLocation.longitude.toFixed(4)}</span>
                        <span className="text-emerald-700 font-bold">Accuracy: ±{gpsLocation.accuracy.toFixed(1)}m</span>
                      </div>
                    ) : (
                      <p className="text-[10px] text-slate-400">Click "Get GPS Location" to verify office geofence distance.</p>
                    )}

                    {geofencePrecheck && (
                      <div className={`p-2 rounded text-[11px] font-bold flex items-center justify-between ${
                        geofencePrecheck.status_code === 'INSIDE' ? 'bg-emerald-100 text-emerald-900' : 'bg-amber-100 text-amber-900'
                      }`}>
                        <span>Geofence: {geofencePrecheck.status_code}</span>
                        <span>{geofencePrecheck.distance_meters}m from center</span>
                      </div>
                    )}
                  </div>

                  {/* Selfie Verification Widget */}
                  <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Camera className="h-4 w-4 text-emerald-600" />
                      <span className="text-xs font-bold text-slate-700">Selfie Verification</span>
                    </div>
                    <button
                      onClick={() => setShowSelfieModal(true)}
                      className={`text-[10px] px-2.5 py-1 rounded font-bold border ${
                        verificationId ? 'bg-emerald-100 text-emerald-800 border-emerald-300' : 'bg-slate-100 text-slate-700 border-slate-300'
                      }`}
                    >
                      {verificationId ? '✓ Verified' : 'Capture Selfie'}
                    </button>
                  </div>
                </div>
              </div>

              {/* Live Work Ticker & Dynamic Punch Button */}
              <div className="space-y-4 pt-4 border-t border-emerald-100">
                {todayStatus?.is_checked_in && (
                  <div className="text-center">
                    <span className="text-[10px] uppercase tracking-wider font-extrabold text-slate-500">Live Worked Duration</span>
                    <p className="text-3xl font-extrabold font-mono text-emerald-800 tracking-tight mt-0.5">
                      {formatSeconds(elapsedSeconds)}
                    </p>
                  </div>
                )}

                {!todayStatus?.is_checked_in ? (
                  <button
                    onClick={handlePunchCheckIn}
                    disabled={punching || todayStatus?.is_checked_out}
                    className="w-full py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs shadow-md shadow-emerald-600/20 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                  >
                    <LogIn size={18} /> {punching ? 'Punching...' : todayStatus?.is_checked_out ? 'Completed for Today' : 'CHECK IN NOW'}
                  </button>
                ) : (
                  <button
                    onClick={handlePunchCheckOut}
                    disabled={punching}
                    className="w-full py-3 px-4 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-extrabold text-xs shadow-md shadow-rose-600/20 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                  >
                    <LogOut size={18} /> {punching ? 'Punching...' : 'CHECK OUT NOW'}
                  </button>
                )}
              </div>
            </div>

            {/* Attendance Dashboard Summary Bar */}
            <div className="lg:col-span-2 glass-card p-6 rounded-2xl border border-emerald-300/80 bg-white/95 shadow-md space-y-4">
              <div className="flex items-center justify-between border-b border-emerald-100 pb-3">
                <h3 className="font-extrabold text-base text-slate-900 flex items-center gap-2">
                  <Users className="text-emerald-600" size={20} />
                  Organization Daily Summary
                </h3>
                <span className="text-xs text-emerald-800 font-mono font-bold">Real-time Aggregation</span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200">
                  <span className="text-[10px] font-extrabold uppercase text-emerald-800">Present</span>
                  <p className="text-2xl font-extrabold text-emerald-950 mt-1">{dashboardMetrics?.present_count || 0}</p>
                </div>

                <div className="p-4 rounded-xl bg-amber-50 border border-amber-200">
                  <span className="text-[10px] font-extrabold uppercase text-amber-800">Late Arrival</span>
                  <p className="text-2xl font-extrabold text-amber-950 mt-1">{dashboardMetrics?.late_count || 0}</p>
                </div>

                <div className="p-4 rounded-xl bg-rose-50 border border-rose-200">
                  <span className="text-[10px] font-extrabold uppercase text-rose-800">Absent</span>
                  <p className="text-2xl font-extrabold text-rose-950 mt-1">{dashboardMetrics?.absent_count || 0}</p>
                </div>

                <div className="p-4 rounded-xl bg-blue-50 border border-blue-200">
                  <span className="text-[10px] font-extrabold uppercase text-blue-800">On Leave / WFH</span>
                  <p className="text-2xl font-extrabold text-blue-950 mt-1">{(dashboardMetrics?.on_leave_count || 0) + (dashboardMetrics?.wfh_count || 0)}</p>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-emerald-50/50 border border-emerald-200 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 text-slate-700 font-semibold">
                  <ShieldCheck size={16} className="text-emerald-600" />
                  <span>GPS Geofence & Facial Verification Pipeline Enabled</span>
                </div>
                <span className="font-mono text-[10px] font-bold text-slate-500">Haversine Verified</span>
              </div>
            </div>
          </div>

          {/* Attendance History Table */}
          <div className="glass-card rounded-2xl border border-emerald-300/80 overflow-hidden bg-white/95 shadow-md space-y-4 p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-emerald-100 pb-4">
              <h3 className="font-extrabold text-base text-slate-900 flex items-center gap-2">
                <Calendar className="text-emerald-600" size={20} />
                My Attendance Records
              </h3>

              <div className="flex items-center gap-3 text-xs">
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => { setStartDate(e.target.value); setPage(1); }}
                  className="bg-white border border-emerald-300 rounded-xl px-3 py-1.5 text-slate-800 font-semibold"
                />
                <span className="text-slate-500 font-bold">to</span>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => { setEndDate(e.target.value); setPage(1); }}
                  className="bg-white border border-emerald-300 rounded-xl px-3 py-1.5 text-slate-800 font-semibold"
                />
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-800">
                <thead className="bg-emerald-100/90 text-emerald-950 uppercase tracking-wider font-extrabold border-b border-emerald-300">
                  <tr>
                    <th className="px-5 py-3.5">Date</th>
                    <th className="px-4 py-3.5">Check In</th>
                    <th className="px-4 py-3.5">Check Out</th>
                    <th className="px-4 py-3.5">Worked Hours</th>
                    <th className="px-4 py-3.5">Late Mins</th>
                    <th className="px-4 py-3.5">Geofence</th>
                    <th className="px-4 py-3.5">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-emerald-100">
                  {loading ? (
                    <tr>
                      <td colSpan={7} className="px-5 py-10 text-center text-slate-600 font-bold">Loading records...</td>
                    </tr>
                  ) : history.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="px-5 py-10 text-center text-slate-600 font-bold">No attendance records found for selected period.</td>
                    </tr>
                  ) : (
                    history.map((rec) => (
                      <tr key={rec.id} className="hover:bg-emerald-50/60 transition-colors font-semibold">
                        <td className="px-5 py-3.5 font-mono text-slate-900 font-extrabold">{rec.attendance_date}</td>
                        <td className="px-4 py-3.5 font-mono text-slate-800">
                          {rec.first_check_in ? new Date(rec.first_check_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—'}
                        </td>
                        <td className="px-4 py-3.5 font-mono text-slate-800">
                          {rec.last_check_out ? new Date(rec.last_check_out).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—'}
                        </td>
                        <td className="px-4 py-3.5 font-mono text-slate-900 font-bold">
                          {Math.floor(rec.worked_minutes / 60)}h {rec.worked_minutes % 60}m
                        </td>
                        <td className="px-4 py-3.5 font-mono text-amber-800 font-bold">
                          {rec.late_minutes > 0 ? `${rec.late_minutes}m` : '0m'}
                        </td>
                        <td className="px-4 py-3.5">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            rec.location_status === 'INSIDE' ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-600'
                          }`}>
                            {rec.location_status || 'NOT_REQUIRED'}
                          </span>
                        </td>
                        <td className="px-4 py-3.5">{getStatusBadge(rec.status)}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Footer */}
            <div className="pt-3 border-t border-emerald-100 flex items-center justify-between text-xs">
              <span className="text-slate-700 font-semibold">
                Page {page} of {totalPages} ({totalRecords} records)
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="p-2 rounded-xl bg-white border border-emerald-300 text-slate-800 disabled:opacity-40"
                >
                  <ChevronLeft size={16} />
                </button>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="p-2 rounded-xl bg-white border border-emerald-300 text-slate-800 disabled:opacity-40"
                >
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Selfie Photo Upload Modal */}
      {showSelfieModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-sm w-full p-5 shadow-xl border border-slate-200 text-center space-y-4">
            <div className="flex justify-between items-center border-b pb-2">
              <h4 className="font-bold text-slate-800 text-sm">Selfie Verification Upload</h4>
              <button onClick={() => setShowSelfieModal(false)} className="text-slate-400 hover:text-slate-600 text-sm">✕</button>
            </div>
            
            {selfiePreview ? (
              <div className="aspect-square bg-slate-100 rounded-lg overflow-hidden border border-slate-200">
                <img src={selfiePreview} alt="Selfie Preview" className="w-full h-full object-cover" />
              </div>
            ) : (
              <div className="aspect-square bg-slate-50 rounded-lg border-2 border-dashed border-slate-300 flex flex-col items-center justify-center p-4">
                <Camera className="h-10 w-10 text-slate-400 mb-2" />
                <p className="text-xs text-slate-500">Upload or capture photo for identity verification.</p>
              </div>
            )}

            <input
              type="file"
              accept="image/*"
              capture="user"
              onChange={handleSelfieFileSelect}
              className="block w-full text-xs text-slate-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100"
            />

            <div className="flex justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={() => setShowSelfieModal(false)}
                className="px-3 py-1.5 border rounded-lg text-xs font-semibold text-slate-700"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleUploadSelfie}
                disabled={!selfieFile}
                className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold disabled:opacity-50"
              >
                Verify & Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Regularization Modal */}
      {showRegModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <form onSubmit={handleRegSubmit} className="glass-card p-6 rounded-2xl border border-emerald-300 bg-white w-full max-w-md space-y-4 text-xs shadow-2xl">
            <h3 className="text-sm font-extrabold text-slate-900">Request Attendance Regularization</h3>
            <div>
              <label className="block text-slate-800 font-bold mb-1">Target Attendance Date</label>
              <input
                type="date"
                value={regDate}
                onChange={(e) => setRegDate(e.target.value)}
                className="w-full bg-white border border-emerald-300 rounded-xl px-3 py-2 text-slate-900 font-bold"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-slate-800 font-bold mb-1">Requested Check-In</label>
                <input
                  type="datetime-local"
                  value={regCheckIn}
                  onChange={(e) => setRegCheckIn(e.target.value)}
                  className="w-full bg-white border border-emerald-300 rounded-xl px-3 py-2 text-slate-900 font-semibold"
                />
              </div>
              <div>
                <label className="block text-slate-800 font-bold mb-1">Requested Check-Out</label>
                <input
                  type="datetime-local"
                  value={regCheckOut}
                  onChange={(e) => setRegCheckOut(e.target.value)}
                  className="w-full bg-white border border-emerald-300 rounded-xl px-3 py-2 text-slate-900 font-semibold"
                />
              </div>
            </div>

            <div>
              <label className="block text-slate-800 font-bold mb-1">Reason for Regularization</label>
              <textarea
                value={regReason}
                onChange={(e) => setRegReason(e.target.value)}
                placeholder="e.g. Forgot check-in punch due to official client visit"
                className="w-full bg-white border border-emerald-300 rounded-xl px-3 py-2 text-slate-900 font-semibold h-20"
                required
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowRegModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 text-xs font-bold"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={regSubmitting}
                className="px-4 py-2 rounded-xl bg-emerald-600 text-white text-xs font-bold shadow-md"
              >
                {regSubmitting ? 'Submitting...' : 'Submit Request'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
