import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { DashboardLayout } from './layouts/DashboardLayout';
import { DashboardPage } from './pages/DashboardPage';
import { EmployeesPage } from './pages/EmployeesPage';

import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { ForgotPasswordPage } from './pages/auth/ForgotPasswordPage';
import { ResetPasswordPage } from './pages/auth/ResetPasswordPage';
import { VerifyEmailPage } from './pages/auth/VerifyEmailPage';

import { OrganizationSettingsPage } from './pages/OrganizationSettingsPage';
import { AttendancePage } from './pages/AttendancePage';
import { LeaveDashboardPage } from './pages/LeaveDashboardPage';
import { ApprovalInboxPage } from './pages/ApprovalInboxPage';
import { HolidayCalendarPage } from './pages/HolidayCalendarPage';
import { PayrollProcessingPage } from './pages/PayrollProcessingPage';
import { SalaryStructuresPage } from './pages/SalaryStructuresPage';
import { EmployeeCompensationPage } from './pages/EmployeeCompensationPage';
import { MyPayslipsPage } from './pages/MyPayslipsPage';
import { ExpensesPage } from './pages/ExpensesPage';
import { LoansPage } from './pages/LoansPage';
import { SalaryAdvancesPage } from './pages/SalaryAdvancesPage';
import { FinancialReportsPage } from './pages/FinancialReportsPage';
import { PerformanceDashboardPage } from './pages/PerformanceDashboardPage';
import { GoalsPage } from './pages/GoalsPage';
import { PerformanceReviewsPage } from './pages/PerformanceReviewsPage';
import { CalibrationPage } from './pages/CalibrationPage';
import { PeerFeedbackPage } from './pages/PeerFeedbackPage';
import { PipPage } from './pages/PipPage';
import { PromotionsPage } from './pages/PromotionsPage';
import { TrainingPage } from './pages/TrainingPage';
import { SkillsMatrixPage } from './pages/SkillsMatrixPage';
import { EngagementSurveysPage } from './pages/EngagementSurveysPage';
import { RequisitionsPage } from './pages/RequisitionsPage';
import { CandidatePipelinePage } from './pages/CandidatePipelinePage';
import { InterviewsPage } from './pages/InterviewsPage';
import { OffersPage } from './pages/OffersPage';
import { HeadcountPlanningPage } from './pages/HeadcountPlanningPage';
import { ExecutiveAnalyticsPage } from './pages/ExecutiveAnalyticsPage';
import { AiAssistantPage } from './pages/AiAssistantPage';
import { EmployeeDashboardPage } from './pages/EmployeeDashboardPage';
import { ManagerDashboardPage } from './pages/ManagerDashboardPage';
import { DocumentCenterPage } from './pages/DocumentCenterPage';
import { PolicyCenterPage } from './pages/PolicyCenterPage';
import { HrHelpdeskPage } from './pages/HrHelpdeskPage';
import { AnnouncementsFeedPage } from './pages/AnnouncementsFeedPage';
import { UnifiedTasksPage } from './pages/UnifiedTasksPage';

import { ComplianceDashboardPage } from './pages/ComplianceDashboardPage';
import { ComplianceRulesPage } from './pages/ComplianceRulesPage';
import { ComplianceCalendarTasksPage } from './pages/ComplianceCalendarTasksPage';
import { ViolationsCapaPage } from './pages/ViolationsCapaPage';
import { InternalAuditsPage } from './pages/InternalAuditsPage';
import { PrivacyRetentionPage } from './pages/PrivacyRetentionPage';
import { ComplianceReportsPage } from './pages/ComplianceReportsPage';

import { AiCopilotPage } from './pages/AiCopilotPage';
import { ExecutiveBiDashboardPage } from './pages/ExecutiveBiDashboardPage';
import { AnomalyDetectionPage } from './pages/AnomalyDetectionPage';
import { WorkforceForecastPage } from './pages/WorkforceForecastPage';
import { ScenarioPlannerPage } from './pages/ScenarioPlannerPage';
import { CustomDashboardBuilderPage } from './pages/CustomDashboardBuilderPage';
import { DataQualityAuditPage } from './pages/DataQualityAuditPage';

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />

          {/* Protected Application Routes */}
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <Routes>
                    <Route path="/" element={<DashboardPage />} />
                    <Route path="/dashboard" element={<DashboardPage />} />
                    <Route path="/me/dashboard" element={<EmployeeDashboardPage />} />
                    <Route path="/team/dashboard" element={<ManagerDashboardPage />} />
                    <Route path="/me/documents" element={<DocumentCenterPage />} />
                    <Route path="/policies" element={<PolicyCenterPage />} />
                    <Route path="/me/helpdesk" element={<HrHelpdeskPage />} />
                    <Route path="/announcements" element={<AnnouncementsFeedPage />} />
                    <Route path="/me/tasks" element={<UnifiedTasksPage />} />
                    <Route path="/employees" element={<EmployeesPage />} />
                    <Route path="/attendance" element={<AttendancePage />} />
                    <Route path="/leaves" element={<LeaveDashboardPage />} />
                    <Route path="/approvals" element={<ApprovalInboxPage />} />
                    <Route path="/holidays" element={<HolidayCalendarPage />} />
                    <Route path="/payroll/processing" element={<PayrollProcessingPage />} />
                    <Route path="/salary-structures" element={<SalaryStructuresPage />} />
                    <Route path="/employee-compensation" element={<EmployeeCompensationPage />} />
                    <Route path="/payslips" element={<MyPayslipsPage />} />
                    <Route path="/expenses" element={<ExpensesPage />} />
                    <Route path="/loans" element={<LoansPage />} />
                    <Route path="/salary-advances" element={<SalaryAdvancesPage />} />
                    <Route path="/financial-reports" element={<FinancialReportsPage />} />
                    <Route path="/performance" element={<PerformanceDashboardPage />} />
                    <Route path="/performance/goals" element={<GoalsPage />} />
                    <Route path="/performance/reviews" element={<PerformanceReviewsPage />} />
                    <Route path="/performance/calibration" element={<CalibrationPage />} />
                    <Route path="/performance/360-feedback" element={<PeerFeedbackPage />} />
                    <Route path="/performance/pip" element={<PipPage />} />
                    <Route path="/performance/promotions" element={<PromotionsPage />} />
                    <Route path="/training" element={<TrainingPage />} />
                    <Route path="/skills/matrix" element={<SkillsMatrixPage />} />
                    <Route path="/engagement" element={<EngagementSurveysPage />} />
                    <Route path="/recruitment/requisitions" element={<RequisitionsPage />} />
                    <Route path="/recruitment/pipeline" element={<CandidatePipelinePage />} />
                    <Route path="/recruitment/interviews" element={<InterviewsPage />} />
                    <Route path="/recruitment/offers" element={<OffersPage />} />
                    <Route path="/workforce/planning" element={<HeadcountPlanningPage />} />
                    <Route path="/analytics/executive" element={<ExecutiveAnalyticsPage />} />
                    <Route path="/ai/assistant" element={<AiAssistantPage />} />

                    {/* Phase 12 Compliance & Governance */}
                    <Route path="/compliance/dashboard" element={<ComplianceDashboardPage />} />
                    <Route path="/compliance/rules" element={<ComplianceRulesPage />} />
                    <Route path="/compliance/calendar-tasks" element={<ComplianceCalendarTasksPage />} />
                    <Route path="/compliance/violations" element={<ViolationsCapaPage />} />
                    <Route path="/compliance/audits" element={<InternalAuditsPage />} />
                    <Route path="/compliance/privacy" element={<PrivacyRetentionPage />} />
                    <Route path="/compliance/reports" element={<ComplianceReportsPage />} />

                    {/* Phase 13 AI Intelligence & BI Platform */}
                    <Route path="/ai/copilot" element={<AiCopilotPage />} />
                    <Route path="/intelligence/executive-bi" element={<ExecutiveBiDashboardPage />} />
                    <Route path="/intelligence/anomalies" element={<AnomalyDetectionPage />} />
                    <Route path="/intelligence/forecasts" element={<WorkforceForecastPage />} />
                    <Route path="/intelligence/scenarios" element={<ScenarioPlannerPage />} />
                    <Route path="/intelligence/dashboard-builder" element={<CustomDashboardBuilderPage />} />
                    <Route path="/intelligence/data-quality" element={<DataQualityAuditPage />} />

                    <Route path="/settings" element={<OrganizationSettingsPage />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </DashboardLayout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
};
