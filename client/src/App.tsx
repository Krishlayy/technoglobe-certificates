import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { DashboardPage } from './pages/DashboardPage';
import { StudentsPage } from './pages/StudentsPage';
import { StepByStepWizardPage } from './pages/StepByStepWizardPage';
import { NewStudentPage } from './pages/NewStudentPage';
import { StudentDetailPage } from './pages/StudentDetailPage';
import { CoursesPage } from './pages/CoursesPage';
import { AttendancePage } from './pages/AttendancePage';
import { DailyLogsPage } from './pages/DailyLogsPage';
import { ProjectsPage } from './pages/ProjectsPage';
import { CertificatesPage } from './pages/CertificatesPage';
import { DocumentEditorPage } from './pages/DocumentEditorPage';
import { TemplatesPage } from './pages/TemplatesPage';
import { BackupRestorePage } from './pages/BackupRestorePage';
import { CentreSettingsPage } from './pages/CentreSettingsPage';
import { AuditLogsPage } from './pages/AuditLogsPage';
import { PublicVerifyPage } from './pages/PublicVerifyPage';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Standalone Public Verification Portal (Scannable from any phone) */}
        <Route path="/verify" element={<PublicVerifyPage />} />

        {/* Protected App Layout */}
        <Route path="/" element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="wizard" element={<StepByStepWizardPage />} />
          <Route path="students" element={<StudentsPage />} />
          <Route path="students/new" element={<NewStudentPage />} />
          <Route path="students/:id" element={<StudentDetailPage />} />
          <Route path="courses" element={<CoursesPage />} />
          <Route path="attendance" element={<AttendancePage />} />
          <Route path="daily-logs" element={<DailyLogsPage />} />
          <Route path="projects" element={<ProjectsPage />} />
          <Route path="certificates" element={<CertificatesPage />} />
          <Route path="document-editor" element={<DocumentEditorPage />} />
          <Route path="templates" element={<TemplatesPage />} />
          <Route path="backup-restore" element={<BackupRestorePage />} />
          <Route path="centre-settings" element={<CentreSettingsPage />} />
          <Route path="audit-logs" element={<AuditLogsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
