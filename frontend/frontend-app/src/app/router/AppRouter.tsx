import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "../layouts/AppShell";
import { ProtectedRoute } from "./ProtectedRoute";
import { PageLoader } from "../../shared/ui/PageLoader";

const DashboardPage = lazy(() =>
  import("../../pages/dashboard/DashboardPage").then((module) => ({
    default: module.DashboardPage
  }))
);
const LiveMonitoringPage = lazy(() =>
  import("../../pages/live/LiveMonitoringPage").then((module) => ({
    default: module.LiveMonitoringPage
  }))
);
const FactoryPage = lazy(() =>
  import("../../pages/factory/FactoryPage").then((module) => ({
    default: module.FactoryPage
  }))
);
const ViolationsPage = lazy(() =>
  import("../../pages/violations/ViolationsPage").then((module) => ({
    default: module.ViolationsPage
  }))
);
const CamerasPage = lazy(() =>
  import("../../pages/cameras/CamerasPage").then((module) => ({
    default: module.CamerasPage
  }))
);
const AlertsPage = lazy(() =>
  import("../../pages/alerts/AlertsPage").then((module) => ({
    default: module.AlertsPage
  }))
);
const ReportsPage = lazy(() =>
  import("../../pages/reports/ReportsPage").then((module) => ({
    default: module.ReportsPage
  }))
);

export function AppRouter() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route element={<ProtectedRoute allowedRoles={["admin", "supervisor", "security"]} />}>
          <Route
            path="/"
            element={
              <Suspense fallback={<PageLoader label="Loading monitoring console" />}>
                <DashboardPage />
              </Suspense>
            }
          />
          <Route
            path="/live"
            element={
              <Suspense fallback={<PageLoader label="Loading live monitoring" />}>
                <LiveMonitoringPage />
              </Suspense>
            }
          />
          <Route
            path="/factory"
            element={
              <Suspense fallback={<PageLoader label="Loading factory overview" />}>
                <FactoryPage />
              </Suspense>
            }
          />
          <Route
            path="/violations"
            element={
              <Suspense fallback={<PageLoader label="Loading violations" />}>
                <ViolationsPage />
              </Suspense>
            }
          />
          <Route
            path="/cameras"
            element={
              <Suspense fallback={<PageLoader label="Loading camera health" />}>
                <CamerasPage />
              </Suspense>
            }
          />
          <Route
            path="/alerts"
            element={
              <Suspense fallback={<PageLoader label="Loading alert center" />}>
                <AlertsPage />
              </Suspense>
            }
          />
          <Route
            path="/reports"
            element={
              <Suspense fallback={<PageLoader label="Loading reports" />}>
                <ReportsPage />
              </Suspense>
            }
          />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
