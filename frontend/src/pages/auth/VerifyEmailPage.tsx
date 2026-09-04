import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { authApi } from '../../services/api/auth';
import { ShieldCheck, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';

export const VerifyEmailPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const tokenFromUrl = searchParams.get('token') || '';

  const [token, setToken] = useState(tokenFromUrl);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const navigate = useNavigate();

  const handleVerify = async (tokenToUse: string) => {

    if (!tokenToUse) return;
    try {
      setLoading(true);
      setStatus('idle');
      const res = await authApi.verifyEmail(tokenToUse);
      if (res.success) {
        setStatus('success');
        setMessage('Your email address has been verified successfully!');
      } else {
        setStatus('error');
        setMessage(res.message || 'Verification failed');
      }
    } catch (err: any) {
      setStatus('error');
      setMessage(err.message || 'Verification token invalid or expired.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (tokenFromUrl) {
      handleVerify(tokenFromUrl);
    }
  }, [tokenFromUrl]);

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-extrabold text-white tracking-tight">Email Verification</h1>
          <p className="text-slate-400 text-xs">Verify your identity token to unlock full account features</p>
        </div>

        <div className="p-8 rounded-3xl glass-card border border-slate-800 space-y-6 text-center">
          {status === 'success' ? (
            <div className="space-y-4">
              <div className="mx-auto w-12 h-12 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <CheckCircle2 size={24} />
              </div>
              <h2 className="text-lg font-bold text-white">Email Verified!</h2>
              <p className="text-slate-400 text-xs leading-relaxed">{message}</p>
              <button
                onClick={() => navigate('/login')}
                className="w-full py-2.5 px-4 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs"
              >
                Proceed to Sign In
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {status === 'error' && (
                <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2 text-left">
                  <AlertCircle size={16} className="shrink-0" />
                  <span>{message}</span>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-300 text-left mb-1.5">Verification Token</label>
                <input
                  type="text"
                  required
                  placeholder="Paste verification token..."
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 font-mono"
                />
              </div>

              <button
                onClick={() => handleVerify(token)}
                disabled={loading || !token}
                className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 text-white font-semibold text-xs shadow-lg shadow-brand-500/25 flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? <RefreshCw className="animate-spin" size={16} /> : <ShieldCheck size={16} />}
                Verify Email Token
              </button>
            </div>
          )}

          <div className="pt-2 border-t border-slate-800">
            <Link to="/login" className="text-xs text-slate-400 hover:text-white">
              Back to Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
