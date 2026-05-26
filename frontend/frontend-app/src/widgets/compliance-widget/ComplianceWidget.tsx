import { FactoryOverview } from "../../features/factory-overview/components/FactoryOverview";
import { WidgetFrame } from "../../shared/layouts/WidgetFrame";
import type { DailyTrendPoint, DepartmentOccupancy } from "../../shared/types/domain";

export function ComplianceWidget({
  departments,
  trends
}: {
  departments: DepartmentOccupancy[];
  trends: DailyTrendPoint[];
}) {
  return (
    <WidgetFrame title="Factory Overview">
      <FactoryOverview departments={departments} trends={trends} />
    </WidgetFrame>
  );
}
