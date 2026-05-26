import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore, type UserRole } from "../store/authStore";

type ProtectedRouteProps = {
  allowedRoles: UserRole[];
};

export function ProtectedRoute({ allowedRoles }: ProtectedRouteProps) {
  const user = useAuthStore((state) => state.user);

  if (!user) {
    return <Navigate to="/" replace />;
  }

  if (!allowedRoles.includes(user.role)) {
    return (
      <div className="mx-auto max-w-2xl rounded-lg border border-signal-red/30 bg-signal-red/10 p-6 text-sm text-red-100">
        You do not have permission to view this monitoring workspace.
      </div>
    );
  }

  return <Outlet />;
}
