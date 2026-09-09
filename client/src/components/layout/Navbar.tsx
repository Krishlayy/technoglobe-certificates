import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Award, ShieldCheck, User, Building2, ExternalLink } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface NavbarProps {
  centreName?: string;
  centreCode?: string;
}

export const Navbar: React.FC<NavbarProps> = ({ 
  centreName = "TECHNOGLOBE – BHARATPUR CENTRE",
  centreCode = "BPT-01" 
}) => {
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="no-print sticky top-0 z-40 bg-brand-700 text-white border-b border-brand-800 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & Centre Title */}
          <div className="flex items-center space-x-3">
            <Link to="/" className="flex items-center space-x-3 group">
              <div className="h-10 px-2 bg-white rounded-lg flex items-center justify-center shadow-xs group-hover:opacity-95 transition-opacity">
                <img src="/technoglobe_logo.png" alt="TechnoGlobe Logo" className="h-7 w-auto object-contain" />
              </div>
              <div className="flex flex-col">
                <span className="font-serif font-bold text-base tracking-wider text-white">
                  TECHNOGLOBE
                </span>
                <span className="text-[10px] uppercase tracking-widest text-gold-300 font-semibold">
                  Internship & Certificate Management
                </span>
              </div>
            </Link>

            <div className="hidden md:flex items-center space-x-2 pl-4 border-l border-brand-600">
              <Building2 className="w-4 h-4 text-gold-300" />
              <span className="text-xs font-medium text-slate-200">
                {centreName}
              </span>
              <span className="px-1.5 py-0.5 rounded bg-brand-800 text-[10px] font-mono text-gold-200 border border-brand-600">
                {centreCode}
              </span>
            </div>
          </div>

          {/* Right actions: Verify, User Profile, Quick Link */}
          <div className="flex items-center space-x-4">
            <Link
              to="/verify"
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-brand-800 hover:bg-brand-600 text-gold-200 text-xs font-medium border border-gold-500/30 transition-colors shadow-sm"
            >
              <ShieldCheck className="w-3.5 h-3.5 text-gold-400" />
              <span>Public Verification Portal</span>
              <ExternalLink className="w-3 h-3 ml-0.5 opacity-70" />
            </Link>

            <div className="flex items-center space-x-2 pl-2 border-l border-brand-600">
              <div className="w-8 h-8 rounded-full bg-brand-800 border border-brand-500 flex items-center justify-center text-slate-200">
                <User className="w-4 h-4 text-gold-300" />
              </div>
              <div className="hidden sm:flex flex-col text-left mr-3">
                <span className="text-xs font-semibold text-white">{user?.name || "Faculty / Admin"}</span>
                <span className="text-[10px] text-gold-300 font-medium">{user?.role || "SUPER_ADMIN"}</span>
              </div>
              
              <button 
                onClick={() => {
                  logout();
                  navigate('/login');
                }}
                className="text-xs px-2.5 py-1 rounded bg-red-900/60 hover:bg-red-800 text-red-200 border border-red-700/50 transition-colors"
                title="Sign out of system"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
