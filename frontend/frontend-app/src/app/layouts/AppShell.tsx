import { NavLink, Outlet } from "react-router-dom";
import { Activity, Bell, Camera, Factory, FileBarChart, LayoutDashboard, ShieldAlert } from "lucide-react";
import { ConnectionStatus } from "../../features/live-monitoring/components/ConnectionStatus";
import { cn } from "../../shared/lib/cn";

const navigation = [
  { label: "Overview", href: "/", icon: LayoutDashboard, end: true },
  { label: "Live", href: "/live", icon: Activity },
  { label: "Factory", href: "/factory", icon: Factory },
  { label: "Violations", href: "/violations", icon: ShieldAlert },
  { label: "Cameras", href: "/cameras", icon: Camera },
  { label: "Alerts", href: "/alerts", icon: Bell },
  { label: "Reports", href: "/reports", icon: FileBarChart }
];

export function AppShell() {
  return (
    <div className="min-h-screen bg-industrial-950 text-slate-100">
      <aside className="fixed inset-y-0 left-0 hidden w-20 border-r border-white/8 bg-industrial-900/95 px-3 py-5 lg:block">
        <NavLink
          to="/"
          className="mb-8 grid h-11 place-items-center rounded-lg border border-signal-cyan/25 bg-signal-cyan/10 text-sm font-black text-signal-cyan"
          title="Overview"
        >
          AI
        </NavLink>
        <nav className="space-y-3">
          {navigation.map((item) => (
            <NavLink
              key={item.label}
              to={item.href}
              end={item.end}
              className={({ isActive }) =>
                cn(
                  "group grid h-12 w-full place-items-center rounded-lg border transition",
                  isActive
                    ? "border-signal-cyan/25 bg-signal-cyan/12 text-signal-cyan"
                    : "border-transparent text-slate-400 hover:bg-white/7 hover:text-white"
                )
              }
              title={item.label}
            >
              <item.icon className="h-5 w-5" />
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="lg:pl-20">
        <header className="sticky top-0 z-30 border-b border-white/8 bg-industrial-950/86 px-4 py-3 backdrop-blur md:px-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-signal-cyan">
                Factory AI Command Center
              </p>
              <h1 className="text-lg font-semibold text-white md:text-2xl">
                Operator Movement Compliance
              </h1>
            </div>
            <ConnectionStatus />
          </div>
        </header>
        <main className="px-4 py-5 md:px-6">
          <Outlet />
        </main>
        <nav className="fixed inset-x-0 bottom-0 z-40 grid grid-cols-6 border-t border-white/10 bg-industrial-900/95 px-2 py-2 backdrop-blur lg:hidden">
          {navigation.slice(1).map((item) => (
            <NavLink
              key={item.label}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  "grid place-items-center gap-1 rounded-md px-1 py-2 text-[10px] transition",
                  isActive ? "bg-signal-cyan/12 text-signal-cyan" : "text-slate-400"
                )
              }
            >
              <item.icon className="h-4 w-4" />
              <span className="truncate">{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
    </div>
  );
}
