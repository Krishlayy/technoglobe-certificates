import React from 'react';
import { CheckCircle2, Circle, Clock } from 'lucide-react';

export interface StepItem {
  key: string;
  label: string;
  completed: boolean;
  current?: boolean;
}

interface ProgressStepperProps {
  currentStep?: string;
  status?: string;
  isLocked?: boolean;
}

export const ProgressStepper: React.FC<ProgressStepperProps> = ({ 
  currentStep = 'student',
  status = 'REGISTERED',
  isLocked = false
}) => {
  const steps: StepItem[] = [
    { key: 'student', label: '1. Student', completed: true },
    { key: 'enrollment', label: '2. Enrollment', completed: ['TRAINING', 'PROJECT_SUBMITTED', 'EVALUATED', 'COMPLETED', 'CERTIFIED'].includes(status) || status === 'REGISTERED' },
    { key: 'training', label: '3. Training Plan', completed: ['TRAINING', 'PROJECT_SUBMITTED', 'EVALUATED', 'COMPLETED', 'CERTIFIED'].includes(status) },
    { key: 'attendance', label: '4. Attendance', completed: ['PROJECT_SUBMITTED', 'EVALUATED', 'COMPLETED', 'CERTIFIED'].includes(status) },
    { key: 'daily_logs', label: '5. Daily Logs', completed: ['PROJECT_SUBMITTED', 'EVALUATED', 'COMPLETED', 'CERTIFIED'].includes(status) },
    { key: 'project', label: '6. Project', completed: ['PROJECT_SUBMITTED', 'EVALUATED', 'COMPLETED', 'CERTIFIED'].includes(status) },
    { key: 'evaluation', label: '7. Evaluation', completed: ['EVALUATED', 'COMPLETED', 'CERTIFIED'].includes(status) },
    { key: 'compliance', label: '8. Compliance', completed: ['COMPLETED', 'CERTIFIED'].includes(status) },
    { key: 'certificate', label: '9. Certificate', completed: isLocked || status === 'CERTIFIED' },
  ];

  return (
    <div className="w-full bg-white p-4 rounded-xl border border-slate-200 shadow-xs mb-6">
      <div className="flex items-center justify-between overflow-x-auto pb-2 scrollbar-none">
        {steps.map((step, idx) => {
          const isDone = step.completed;
          return (
            <React.Fragment key={step.key}>
              <div className="flex flex-col items-center min-w-[80px] text-center">
                <div 
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${
                    isDone 
                      ? "bg-emerald-600 text-white ring-4 ring-emerald-50" 
                      : "bg-slate-100 text-slate-400 border border-slate-300"
                  }`}
                >
                  {isDone ? <CheckCircle2 className="w-4 h-4" /> : <span>{idx + 1}</span>}
                </div>
                <span className={`text-[11px] mt-1.5 font-medium whitespace-nowrap ${
                  isDone ? "text-emerald-800 font-semibold" : "text-slate-500"
                }`}>
                  {step.label}
                </span>
              </div>
              {idx < steps.length - 1 && (
                <div 
                  className={`h-0.5 flex-1 min-w-[20px] mx-1 transition-colors ${
                    step.completed && steps[idx + 1].completed 
                      ? "bg-emerald-500" 
                      : "bg-slate-200"
                  }`} 
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
