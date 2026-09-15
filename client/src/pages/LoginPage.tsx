import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useInstitution } from '../contexts/InstitutionContext';
import { ShieldCheck, Sun, GraduationCap, Building2, CheckCircle, ArrowRight, Lock, Mail } from 'lucide-react';

export default function LoginPage() {
  const [selectedPortal, setSelectedPortal] = useState<'poddar' | 'poswal'>('poddar');
  const [email, setEmail] = useState('nitin@pctm');
  const [password, setPassword] = useState('nitin321');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { login } = useAuth();
  const { selectInstitution } = useInstitution();
  const navigate = useNavigate();

  const handlePortalSwitch = (portal: 'poddar' | 'poswal') => {
    setSelectedPortal(portal);
    setError('');
    if (portal === 'poddar') {
      setEmail('nitin@pctm');
      setPassword('nitin321');
    } else {
      setEmail('madhuvangurjar19@gmail.com');
      setPassword('poswal123');
    }
  };

  const executeLogin = async (loginEmail: string, loginPass: string, instId: number) => {
    setError('');
    setIsSubmitting(true);
    const result = await login(loginEmail, loginPass);
    if (result.success) {
      selectInstitution(instId);
      navigate('/');
    } else {
      setError(result.error || 'Failed to login');
      setIsSubmitting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const instId = selectedPortal === 'poddar' ? 1 : 2;
    await executeLogin(email, password, instId);
  };

  const isPoddar = selectedPortal === 'poddar';

  return (
    <div className={`min-h-screen flex items-center justify-center p-4 transition-colors duration-500 ${
      isPoddar 
        ? 'bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950' 
        : 'bg-gradient-to-br from-stone-950 via-neutral-900 to-amber-950'
    }`}>
      <div className="max-w-4xl w-full">
        {/* Top Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-white/10 text-white border border-white/15 text-xs font-semibold backdrop-blur-md mb-3">
            <ShieldCheck className="w-4 h-4 text-amber-400" />
            <span>Official Academic & Industrial Certification System</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            Select Issuing Organization / Portal
          </h1>
          <p className="text-slate-400 text-xs md:text-sm mt-1">
            Two distinct, independent certification engines. Choose your operational portal to continue.
          </p>
        </div>

        {/* 2 Dedicated Option Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Option 1: Poddar College */}
          <div
            onClick={() => handlePortalSwitch('poddar')}
            className={`relative p-5 rounded-2xl border-2 cursor-pointer transition-all duration-300 text-left ${
              isPoddar
                ? 'bg-blue-950/80 border-blue-500 ring-2 ring-blue-500/40 shadow-xl shadow-blue-950/50'
                : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 opacity-75 hover:opacity-100'
            }`}
          >
            {isPoddar && (
              <div className="absolute -top-3 right-4 px-2.5 py-0.5 rounded-full bg-blue-600 text-white text-[10px] font-bold uppercase tracking-wider flex items-center space-x-1 shadow-md">
                <CheckCircle className="w-3 h-3" />
                <span>Active Option</span>
              </div>
            )}
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 rounded-xl bg-white p-1.5 flex items-center justify-center shrink-0 shadow-md">
                <img src="/poddar_logo.png" alt="Poddar Logo" className="max-h-full max-w-full object-contain" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-1.5 text-blue-400 text-[11px] font-bold uppercase tracking-wider">
                  <GraduationCap className="w-3.5 h-3.5" />
                  <span>Option 1 • Academic Institution</span>
                </div>
                <h3 className="text-lg font-bold text-white mt-0.5 leading-snug">
                  Poddar College
                </h3>
                <p className="text-[11px] text-slate-300 mt-1 line-clamp-2">
                  Technical Degree Internships (Data Analytics, MERN Stack, AI/ML, Cyber Security, Java, Cloud).
                </p>
                <div className="mt-3 pt-2.5 border-t border-slate-800 text-[10px] text-slate-400 space-y-0.5">
                  <div><b>Authority:</b> Nitin Agarwal</div>
                  <div><b>Faculty:</b> Krishlay, Rahul</div>
                  <div><b>Contact:</b> 9414293370 | nitin@pctm</div>
                </div>
              </div>
            </div>
          </div>

          {/* Option 2: Poswal Developers */}
          <div
            onClick={() => handlePortalSwitch('poswal')}
            className={`relative p-5 rounded-2xl border-2 cursor-pointer transition-all duration-300 text-left ${
              !isPoddar
                ? 'bg-amber-950/80 border-amber-500 ring-2 ring-amber-500/40 shadow-xl shadow-amber-950/50'
                : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 opacity-75 hover:opacity-100'
            }`}
          >
            {!isPoddar && (
              <div className="absolute -top-3 right-4 px-2.5 py-0.5 rounded-full bg-amber-600 text-white text-[10px] font-bold uppercase tracking-wider flex items-center space-x-1 shadow-md">
                <CheckCircle className="w-3 h-3" />
                <span>Active Option</span>
              </div>
            )}
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 rounded-xl bg-white p-1.5 flex items-center justify-center shrink-0 shadow-md">
                <img src="/poswal_logo.png" alt="Poswal Logo" className="max-h-full max-w-full object-contain" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-1.5 text-amber-400 text-[11px] font-bold uppercase tracking-wider">
                  <Sun className="w-3.5 h-3.5" />
                  <span>Option 2 • Industrial Partner</span>
                </div>
                <h3 className="text-lg font-bold text-white mt-0.5 leading-snug">
                  Poswal Developers
                </h3>
                <p className="text-[11px] text-slate-300 mt-1 line-clamp-2">
                  Solar Energy & Industrial Certifications (Rooftop Solar PV, Inverter Tech, Panel Mounting, O&M).
                </p>
                <div className="mt-3 pt-2.5 border-t border-slate-800 text-[10px] text-slate-400 space-y-0.5">
                  <div><b>Authority:</b> Madhuvan Singh Gurjar</div>
                  <div><b>Trainer:</b> Mahesh Chand Saini</div>
                  <div><b>Reg:</b> GST: 08ABIFP2454N1ZQ | MSME: UDYAM-RJ-06-0052498</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Login Box */}
        <div className="bg-slate-900/90 rounded-2xl shadow-2xl p-6 md:p-8 border border-slate-800 backdrop-blur-md">
          <div className="flex flex-col md:flex-row md:items-center justify-between pb-5 mb-5 border-b border-slate-800 gap-3">
            <div className="flex items-center space-x-3">
              <div className={`p-2.5 rounded-xl ${isPoddar ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30' : 'bg-amber-600/20 text-amber-400 border border-amber-500/30'}`}>
                {isPoddar ? <GraduationCap className="w-6 h-6" /> : <Sun className="w-6 h-6" />}
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">
                  Sign in to {isPoddar ? 'Poddar College Portal' : 'Poswal Developers Portal'}
                </h2>
                <p className="text-xs text-slate-400">
                  {isPoddar ? 'Authorized Academic Degree Management System' : 'Authorized Solar & Industrial Training System'}
                </p>
              </div>
            </div>

            {/* Quick 1-Click Role Login Shortcuts */}
            <div className="flex items-center flex-wrap gap-2">
              {isPoddar ? (
                <>
                  <button
                    type="button"
                    onClick={() => executeLogin('nitin@pctm', 'nitin321', 1)}
                    className="text-[11px] px-3 py-1.5 rounded-lg bg-blue-900/50 hover:bg-blue-800 text-blue-200 border border-blue-700/50 transition-colors font-medium"
                  >
                    Quick: Nitin Agarwal (Authority)
                  </button>
                  <button
                    type="button"
                    onClick={() => executeLogin('krishlay@pctm', 'krishlay321', 1)}
                    className="text-[11px] px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors font-medium"
                  >
                    Quick: Krishlay (Faculty)
                  </button>
                </>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={() => executeLogin('madhuvangurjar19@gmail.com', 'poswal123', 2)}
                    className="text-[11px] px-3 py-1.5 rounded-lg bg-amber-900/50 hover:bg-amber-800 text-amber-200 border border-amber-700/50 transition-colors font-medium"
                  >
                    Quick: Madhuvan Gurjar (Authority)
                  </button>
                  <button
                    type="button"
                    onClick={() => executeLogin('trainer@poswal.com', 'trainer123', 2)}
                    className="text-[11px] px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors font-medium"
                  >
                    Quick: Mahesh Chand Saini (Trainer)
                  </button>
                </>
              )}
            </div>
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-3 rounded-xl mb-5 text-sm text-center font-medium">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                  <Mail className="w-3.5 h-3.5 text-slate-400" />
                  <span>Email / Login ID</span>
                </label>
                <input
                  type="text"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="username"
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-700 rounded-xl text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none text-sm"
                  placeholder="e.g. email@organization.com"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                  <Lock className="w-3.5 h-3.5 text-slate-400" />
                  <span>Password</span>
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-700 rounded-xl text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none text-sm"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className={`w-full font-bold py-3.5 px-4 rounded-xl transition-all shadow-lg flex items-center justify-center space-x-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed ${
                isPoddar
                  ? 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-900/30'
                  : 'bg-amber-600 hover:bg-amber-500 text-white shadow-amber-900/30'
              }`}
            >
              <span>{isSubmitting ? 'Authenticating...' : `Enter ${isPoddar ? 'Poddar College Portal' : 'Poswal Developers Portal'}`}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

