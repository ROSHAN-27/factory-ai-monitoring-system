import { useMemo } from "react";
import type { ColumnDef } from "@tanstack/react-table";
import { DataTable } from "../../shared/tables/DataTable";
import type { RecognitionEvent } from "../../shared/types/domain";
import { formatTime } from "../../shared/lib/date";
import { WidgetFrame } from "../../shared/layouts/WidgetFrame";

export function OperatorTrackingWidget({ events }: { events: RecognitionEvent[] }) {
  const latestByOperator = useMemo(() => {
    const map = new Map<string, RecognitionEvent>();

    for (const event of events) {
      if (!map.has(event.operatorId)) {
        map.set(event.operatorId, event);
      }
    }

    return Array.from(map.values()).slice(0, 8);
  }, [events]);

  const columns = useMemo<ColumnDef<RecognitionEvent>[]>(
    () => [
      { header: "Operator", accessorKey: "operatorName" },
      { header: "Zone", accessorKey: "zone" },
      { header: "Direction", accessorKey: "direction" },
      {
        header: "Last Seen",
        cell: ({ row }) => formatTime(row.original.timestamp)
      }
    ],
    []
  );

  return (
    <WidgetFrame title="Operator Tracking">
      <DataTable
        data={latestByOperator}
        columns={columns}
        emptyTitle="No operators tracked"
        emptyMessage="Operator positions appear after recognition events arrive."
      />
    </WidgetFrame>
  );
}
