import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { authApi } from '../../services/api/auth';
import { Mail, Lock, Eye, EyeOff, LogIn, AlertCircle, ShieldCheck, Phone, KeyRound, Send, CheckCircle2 } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [authMode, setAuthMode] = useState<'email' | 'mobile'>('email');

  // Email form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // Mobile OTP form state
  const [phone, setPhone] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [otpSending, setOtpSending] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const { login, loginWithOTP } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as any)?.from?.pathname || '/dashboard';

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;

    try {
      setLoading(true);
      setError(null);
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.message || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  const handleSendOTP = async () => {
    if (!phone) {
      setError('Please enter a valid mobile number');
      return;
    }
    try {
      setOtpSending(true);
      setError(null);
      setSuccessMessage(null);
      await authApi.sendOTP(phone);
      setOtpSent(true);
      setSuccessMessage(`OTP sent to ${phone}. Check console or test master OTP 123456.`);
    } catch (err: any) {
      setError(err.message || 'Failed to dispatch OTP code');
    } finally {
      setOtpSending(false);
    }
  };

  const handleMobileOTPSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phone || !otpCode) return;

    try {
      setLoading(true);
      setError(null);
      await loginWithOTP(phone, otpCode);
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.message || 'Invalid or expired OTP code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-emerald-50/40 flex items-center justify-center p-4 selection:bg-emerald-600 selection:text-white">
      <div className="w-full max-w-md space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="mx-auto h-12 w-12 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center font-extrabold text-xl text-white shadow-xl shadow-emerald-600/20">
            A
          </div>
          <h1 className="text-2xl font-extrabold bg-gradient-to-r from-emerald-900 via-emerald-800 to-teal-700 bg-clip-text text-transparent tracking-tight">
            AxonTime HR
          </h1>
          <p className="text-slate-600 text-xs font-semibold">Sign in to access your enterprise SaaS workspace</p>
        </div>

        {/* Card Form */}
        <div className="p-8 rounded-3xl glass-card border border-emerald-200/80 bg-white/90 shadow-xl space-y-6">
          {/* Auth Mode Toggle Tabs */}
          <div className="grid grid-cols-2 gap-1 p-1 bg-emerald-100/60 rounded-xl border border-emerald-200 text-xs font-bold">
            <button
              type="button"
              onClick={() => {
                setAuthMode('email');
                setError(null);
                setSuccessMessage(null);
              }}
              className={`py-2 rounded-lg transition-all flex items-center justify-center gap-2 ${
                authMode === 'email'
                  ? 'bg-emerald-600 text-white shadow-md'
                  : 'text-slate-600 hover:text-emerald-900'
              }`}
            >
              <Mail size={14} /> Email & Password
            </button>
            <button
              type="button"
              onClick={() => {
                setAuthMode('mobile');
                setError(null);
                setSuccessMessage(null);
              }}
              className={`py-2 rounded-lg transition-all flex items-center justify-center gap-2 ${
                authMode === 'mobile'
                  ? 'bg-emerald-600 text-white shadow-md'
                  : 'text-slate-600 hover:text-emerald-900'
              }`}
            >
              <Phone size={14} /> Mobile & OTP
            </button>
          </div>

          {error && (
            <div className="p-3.5 rounded-xl bg-rose-100 border border-rose-300 text-rose-900 text-xs flex items-center gap-2 font-bold">
              <AlertCircle size={16} className="shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {successMessage && (
            <div className="p-3.5 rounded-xl bg-emerald-100 border border-emerald-300 text-emerald-900 text-xs flex items-center gap-2 font-bold">
              <CheckCircle2 size={16} className="shrink-0" />
              <span>{successMessage}</span>
            </div>
          )}

          {authMode === 'email' ? (
            /* Email + Password Form */
            <form onSubmit={handleEmailSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                  <input
                    type="email"
                    required
                    placeholder="admin@axontimehr.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-emerald-50/50 border border-emerald-200 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-emerald-500 font-medium transition-colors"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-bold text-slate-700">Password</label>
                  <Link to="/forgot-password" className="text-[11px] text-emerald-700 hover:underline font-bold">
                    Forgot Password?
                  </Link>
                </div>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-emerald-50/50 border border-emerald-200 rounded-xl pl-10 pr-10 py-2.5 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-emerald-500 font-medium transition-colors"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700"
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-lg shadow-emerald-600/20 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
              >
                {loading ? (
                  <span>Signing in...</span>
                ) : (
                  <>
                    <LogIn size={16} /> Sign In with Password
                  </>
                )}
              </button>
            </form>
          ) : (
            /* Mobile + OTP Form */
            <form onSubmit={handleMobileOTPSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Mobile Number</label>
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <Phone className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                    <input
                      type="tel"
                      required
                      placeholder="+919876543210"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      className="w-full bg-emerald-50/50 border border-emerald-200 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-emerald-500 font-medium"
                    />
                  </div>
                  <button
                    type="button"
                    onClick={handleSendOTP}
                    disabled={otpSending || !phone}
                    className="px-4 py-2.5 rounded-xl bg-emerald-100 hover:bg-emerald-200 border border-emerald-300 text-xs font-bold text-emerald-800 flex items-center gap-1.5 shrink-0 disabled:opacity-50"
                  >
                    <Send size={14} />
                    {otpSending ? 'Sending...' : otpSent ? 'Resend' : 'Send OTP'}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">6-Digit OTP Code</label>
                <div className="relative">
                  <KeyRound className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                  <input
                    type="text"
                    required
                    maxLength={6}
                    placeholder="Enter OTP (e.g. 123456)"
                    value={otpCode}
                    onChange={(e) => setOtpCode(e.target.value)}
                    className="w-full bg-emerald-50/50 border border-emerald-200 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-emerald-500 font-mono tracking-widest text-center font-bold"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading || !otpCode}
                className="w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-lg shadow-emerald-600/20 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
              >
                {loading ? (
                  <span>Verifying OTP...</span>
                ) : (
                  <>
                    <LogIn size={16} /> Verify OTP & Sign In
                  </>
                )}
              </button>
            </form>
          )}

          <div className="pt-2 text-center text-xs text-slate-500 border-t border-emerald-100">
            Don't have an account?{' '}
            <Link to="/register" className="text-emerald-700 font-bold hover:underline">
              Create Account
            </Link>
          </div>
        </div>

        {/* Security badge */}
        <div className="flex items-center justify-center gap-2 text-[11px] text-slate-500 font-medium">
          <ShieldCheck size={14} className="text-emerald-600" />
          <span>256-bit JWT & Mobile OTP Security Active</span>
        </div>
      </div>
    </div>
  );
};
