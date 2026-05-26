import { Download, FileBarChart } from "lucide-react";

const reports = [
  "Daily movement report",
  "Compliance report",
  "Supervisor exception report",
  "Repeat offender report"
];

export function ReportsPanel() {
  return (
    <div className="grid gap-2">
      {reports.map((report) => (
        <div key={report} className="flex items-center justify-between gap-3 rounded-lg border border-white/8 bg-white/[0.035] p-3">
          <div className="flex items-center gap-3">
            <FileBarChart className="h-4 w-4 text-signal-cyan" />
            <span className="text-sm text-slate-200">{report}</span>
          </div>
          <button
            type="button"
            className="grid h-8 w-8 place-items-center rounded-md border border-white/10 text-slate-400 transition hover:bg-white/8 hover:text-white"
            title={`Export ${report}`}
          >
            <Download className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  );
}
