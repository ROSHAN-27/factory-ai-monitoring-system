import { memo } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { DailyTrendPoint } from "../types/domain";

export const OperationsBarChart = memo(function OperationsBarChart({
  data
}: {
  data: DailyTrendPoint[];
}) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data}>
        <CartesianGrid stroke="rgba(255,255,255,.08)" vertical={false} />
        <XAxis dataKey="label" stroke="#64748b" tickLine={false} axisLine={false} />
        <YAxis stroke="#64748b" tickLine={false} axisLine={false} />
        <Tooltip
          cursor={{ fill: "rgba(255,255,255,.05)" }}
          contentStyle={{ background: "#0b1718", border: "1px solid rgba(255,255,255,.12)", borderRadius: 8 }}
        />
        <Bar dataKey="events" fill="#5bd8ff" radius={[4, 4, 0, 0]} />
        <Bar dataKey="violations" fill="#ff6b6b" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
});
