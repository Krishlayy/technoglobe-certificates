import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, Lock, Mail, AlertCircle, ArrowRight, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useInstitution } from '../contexts/InstitutionContext';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('nitin@technoglobe.co.in');
  const [password, setPassword] = useState('nitin321');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const { selectInstitution } = useInstitution();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      selectInstitution(1);
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const executeQuickLogin = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    selectInstitution(1);
    login(demoEmail, demoPass)
      .then(() => navigate('/'))
      .catch((err) => setError(err.response?.data?.detail || 'Login failed'));
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background Graphic Accents */}
      <div className="absolute inset-0 z-0 opacity-15">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-blue-500 rounded-full filter blur-3xl"></div>
        <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-amber-500 rounded-full filter blur-3xl"></div>
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md z-10 text-center">
        {/* TechnoGlobe Logo */}
        <div className="inline-flex items-center justify-center p-3 bg-white rounded-2xl shadow-xl mb-4">
          <img 
            src="/technoglobe_logo.png" 
            alt="TechnoGlobe Bharatpur" 
            className="h-12 w-auto object-contain" 
          />
        </div>

        <h2 className="text-2xl sm:text-3xl font-serif font-black tracking-wide text-white">
          TECHNOGLOBE
        </h2>
        <p className="mt-1 text-xs text-amber-300 font-bold tracking-widest uppercase">
          Certification & Training Management Portal • Bharatpur
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md z-10 px-4 sm:px-0">
        <div className="bg-slate-800/90 backdrop-blur-md py-8 px-6 shadow-2xl rounded-3xl sm:px-10 border border-slate-700/80">
          <form className="space-y-5" onSubmit={handleSubmit}>
            {error && (
              <div className="p-3 bg-rose-500/20 border border-rose-500/40 rounded-xl flex items-center space-x-2 text-rose-300 text-xs font-medium">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
                <span>{error}</span>
              </div>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                Authorized Email Address
              </label>
              <div className="relative rounded-xl shadow-xs">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Mail className="h-4 w-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full pl-10 pr-4 py-2.5 bg-slate-900/80 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm transition-all"
                  placeholder="nitin@technoglobe.co.in"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                Administrative Password
              </label>
              <div className="relative rounded-xl shadow-xs">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="h-4 w-4" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-10 pr-4 py-2.5 bg-slate-900/80 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm transition-all"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-xl shadow-lg text-sm font-black text-white bg-blue-600 hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-all cursor-pointer"
            >
              {loading ? (
                <span>Authenticating Credentials...</span>
              ) : (
                <>
                  <span>Sign In to Admin Portal</span>
                  <ArrowRight className="ml-2 w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick Demo Login Preset */}
          <div className="mt-6 pt-6 border-t border-slate-700/80">
            <div className="text-[11px] font-bold text-slate-400 mb-2 uppercase tracking-wider text-center">
              Quick Administrative Access
            </div>
            <button
              type="button"
              onClick={() => executeQuickLogin('nitin@technoglobe.co.in', 'nitin321')}
              className="w-full py-2 px-3 bg-slate-700/60 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-bold border border-slate-600/80 flex items-center justify-between transition-colors cursor-pointer"
            >
              <span>Nitin Agarwal (Director / Center Head)</span>
              <span className="text-[10px] px-2 py-0.5 bg-blue-500/30 text-blue-300 rounded font-black">1-Click</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
