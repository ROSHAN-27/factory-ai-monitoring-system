import { ViolationDashboard } from "../../features/violations/components/ViolationDashboard";
import { WidgetFrame } from "../../shared/layouts/WidgetFrame";
import type { ViolationSummary } from "../../shared/types/domain";

export function ViolationWidget({ violations }: { violations: ViolationSummary[] }) {
  return (
    <WidgetFrame title="Violation Dashboard">
      <ViolationDashboard violations={violations} />
    </WidgetFrame>
  );
}
