import { create } from "zustand";

export type UserRole = "admin" | "supervisor" | "security" | "viewer";

type AuthState = {
  user: {
    id: string;
    name: string;
    role: UserRole;
  } | null;
};

export const useAuthStore = create<AuthState>(() => ({
  user: {
    id: "local-supervisor",
    name: "Factory Supervisor",
    role: "supervisor"
  }
}));
