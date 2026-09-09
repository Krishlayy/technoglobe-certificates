import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  color?: 'blue' | 'navy' | 'emerald' | 'amber' | 'purple' | 'gold';
  onClick?: () => void;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  color = 'navy',
  onClick
}) => {
  const colorStyles = {
    navy: "bg-brand-50 text-brand-700 border-brand-200",
    blue: "bg-blue-50 text-blue-700 border-blue-200",
    emerald: "bg-emerald-50 text-emerald-700 border-emerald-200",
    amber: "bg-amber-50 text-amber-700 border-amber-200",
    purple: "bg-purple-50 text-purple-700 border-purple-200",
    gold: "bg-amber-100/70 text-amber-900 border-amber-300",
  };

  const iconStyles = {
    navy: "text-brand-600 bg-brand-100",
    blue: "text-blue-600 bg-blue-100",
    emerald: "text-emerald-600 bg-emerald-100",
    amber: "text-amber-600 bg-amber-100",
    purple: "text-purple-600 bg-purple-100",
    gold: "text-amber-800 bg-amber-200/80",
  };

  return (
    <div 
      onClick={onClick}
      className={`p-5 rounded-xl bg-white border border-slate-200/90 shadow-xs hover:shadow-md transition-all flex items-start justify-between ${
        onClick ? "cursor-pointer hover:border-brand-300" : ""
      }`}
    >
      <div className="space-y-1">
        <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{title}</p>
        <p className="text-2xl font-bold text-slate-900 tracking-tight font-serif">{value}</p>
        {subtitle && (
          <p className="text-[11px] text-slate-400 font-medium">{subtitle}</p>
        )}
      </div>
      <div className={`p-2.5 rounded-lg shrink-0 ${iconStyles[color]}`}>
        <Icon className="w-5 h-5" />
      </div>
    </div>
  );
};
