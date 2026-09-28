import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  ShieldCheck, BookOpen, User, ExternalLink, RefreshCw, 
  GraduationCap, Award, Wand2, Layers, Check, ArrowLeftRight, LogOut, CheckCircle2
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useInstitution } from '../../contexts/InstitutionContext';

export const Navbar: React.FC = () => {
  const { logout, user } = useAuth();
  const { activeInstitution } = useInstitution();
  const navigate = useNavigate();

  return (
    <header className="no-print sticky top-0 z-40 text-white border-b shadow-md bg-[#0A2540] border-[#1E3A8A]">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & Organization Identity */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            <Link to="/" className="flex items-center space-x-2.5 sm:space-x-3.5 group">
              <div className="h-10 px-2.5 bg-white rounded-xl flex items-center justify-center shadow-xs group-hover:opacity-95 transition-opacity">
                <img 
                  src="/technoglobe_logo.png" 
                  alt="TechnoGlobe Bharatpur" 
                  className="h-8 w-auto object-contain" 
                />
              </div>
              <div className="flex flex-col text-left">
                <div className="flex items-center space-x-1.5">
                  <span className="font-serif font-black text-sm sm:text-base tracking-wider text-white">
                    TECHNOGLOBE
                  </span>
                  <span className="text-[10px] px-1.5 py-0.2 bg-amber-400/20 text-amber-300 font-bold rounded-md border border-amber-400/30">
                    BHARATPUR
                  </span>
                </div>
                <span className="text-[9px] sm:text-[10px] tracking-wide text-slate-300 font-medium truncate max-w-[280px] sm:max-w-none">
                  Advanced IT Training & Development • Near SP Office
                </span>
              </div>
            </Link>
          </div>

          {/* Quick Action Navigation Buttons */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            {/* 15-Doc Dossier Wizard Button */}
            <Link
              to="/wizard"
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white border border-blue-400/40 text-xs font-black transition-all shadow-xs cursor-pointer"
              title="15-Document Dossier & Completion Certificate Wizard"
            >
              <Wand2 className="w-3.5 h-3.5 text-blue-200" />
              <span className="hidden sm:inline">15-Doc Wizard</span>
            </Link>

            {/* Appreciation Studio Button */}
            <Link
              to="/appreciation"
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-amber-400/20 hover:bg-amber-400/30 text-amber-300 border border-amber-400/40 text-xs font-black transition-all shadow-xs cursor-pointer"
              title="Custom Certificate of Appreciation & Excellence Studio"
            >
              <Award className="w-3.5 h-3.5 text-amber-400" />
              <span className="hidden sm:inline">Appreciation Studio</span>
            </Link>

            {/* Bulk Batch Register Button */}
            <Link
              to="/bulk-attendance"
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-400/40 text-xs font-black transition-all shadow-xs cursor-pointer"
              title="Batch Master Attendance Register (50+ Students)"
            >
              <Layers className="w-3.5 h-3.5 text-emerald-300" />
              <span className="hidden md:inline">Batch Register</span>
            </Link>

            {/* Public Verification Link */}
            <Link
              to="/verify"
              target="_blank"
              className="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-slate-200 text-xs font-bold transition-all border border-white/10"
              title="Public Verification Portal"
            >
              <ShieldCheck className="w-3.5 h-3.5 text-amber-300" />
              <span className="hidden lg:inline">Verify</span>
              <ExternalLink className="w-2.5 h-2.5 opacity-60 ml-0.5" />
            </Link>

            {/* Authority Signatory Pill */}
            <div className="hidden sm:flex items-center space-x-2 pl-2 border-l border-white/15">
              <div className="w-8 h-8 rounded-full bg-amber-400/20 border border-amber-400/40 flex items-center justify-center text-amber-300 font-black text-xs">
                NA
              </div>
              <div className="flex flex-col text-left">
                <span className="text-xs font-bold text-white">Nitin Agarwal</span>
                <span className="text-[10px] text-amber-300 font-bold">Director / Center Head</span>
              </div>
            </div>

            {/* Logout Button */}
            <button
              onClick={logout}
              className="p-1.5 rounded-xl text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
