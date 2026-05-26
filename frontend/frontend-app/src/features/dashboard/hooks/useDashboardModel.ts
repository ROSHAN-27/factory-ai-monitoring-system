import { useEffect, useMemo } from "react";
import { useLiveMonitoringStore } from "../../../app/store/liveMonitoringStore";
import type {
  CameraHealth,
  DailyTrendPoint,
  DepartmentOccupancy,
  FactoryMetric,
  RecognitionEvent,
  ViolationSummary
} from "../../../shared/types/domain";
import { useRecognitionEventsQuery } from "../api/dashboardQueries";
import { useRealtimeBridge } from "../../live-monitoring/hooks/useRealtimeBridge";

const violationLabels = [
  "Missing department entry",
  "Wrong department",
  "Long absence",
  "Early exit",
  "Dormitory alert",
  "Repeat offender"
];

export function useDashboardModel() {
  useRealtimeBridge();

  const query = useRecognitionEventsQuery();
  const ingestEvents = useLiveMonitoringStore((state) => state.ingestEvents);
  const storeEvents = useLiveMonitoringStore((state) => state.events);
  const alerts = useLiveMonitoringStore((state) => state.alerts);
  const connectionState = useLiveMonitoringStore((state) => state.connectionState);

  useEffect(() => {
    if (query.data) ingestEvents(query.data, "api");
  }, [ingestEvents, query.data]);

  return useMemo(() => {
    const events = storeEvents.length > 0 ? storeEvents : query.data ?? [];
    const departments = buildDepartmentOccupancy(events);
    const cameras = buildCameraHealth(events);
    const violations = buildViolationSummary(events);
    const trends = buildTrends(events);
    const compliance = Math.max(0, 100 - alerts.filter((alert) => alert.status === "open").length * 4);

    const metrics: FactoryMetric[] = [
      { label: "Operators Seen", value: String(new Set(events.map((event) => event.operatorId)).size), delta: "live shift", tone: "cyan" },
      { label: "Compliance", value: `${compliance}%`, delta: "policy score", tone: compliance >= 85 ? "green" : "amber" },
      { label: "Active Alerts", value: String(alerts.filter((alert) => alert.status === "open").length), delta: "needs action", tone: alerts.length > 0 ? "red" : "green" },
      { label: "Online Cameras", value: `${cameras.filter((camera) => camera.status === "online").length}/${cameras.length || 1}`, delta: "heartbeat", tone: "green" }
    ];

    return {
      query,
      events,
      alerts,
      cameras,
      departments,
      violations,
      trends,
      metrics,
      connectionState
    };
  }, [alerts, connectionState, query, storeEvents]);
}

function buildDepartmentOccupancy(events: RecognitionEvent[]): DepartmentOccupancy[] {
  const groups = new Map<string, Set<string>>();

  for (const event of events) {
    const department = event.department ?? "General";
    if (!groups.has(department)) groups.set(department, new Set());
    if (event.direction !== "OUT") groups.get(department)?.add(event.operatorId);
  }

  return Array.from(groups.entries()).map(([department, operators], index) => ({
    department,
    activeOperators: operators.size,
    compliance: Math.max(72, 98 - index * 7)
  }));
}

function buildCameraHealth(events: RecognitionEvent[]): CameraHealth[] {
  const cameraNames = Array.from(new Set(events.map((event) => event.cameraName))).slice(0, 6);
  const fallback = cameraNames.length > 0 ? cameraNames : ["ENTRY_CAMERA", "EXIT_CAMERA", "DEPT_CAMERA"];

  return fallback.map((name, index) => ({
    id: name,
    name,
    zone: events.find((event) => event.cameraName === name)?.zone ?? "Production Floor",
    status: index === 1 && events.length > 6 ? "degraded" : "online",
    fps: 24 - index * 2,
    heartbeatSecondsAgo: 3 + index * 8,
    accuracy: Math.max(84, 96 - index * 3)
  }));
}

function buildViolationSummary(events: RecognitionEvent[]): ViolationSummary[] {
  return violationLabels.map((type, index) => ({
    type,
    count: Math.max(0, Math.floor(events.length / (index + 5)) - index),
    severity: index < 2 ? "high" : index < 4 ? "medium" : "low"
  }));
}

function buildTrends(events: RecognitionEvent[]): DailyTrendPoint[] {
  const buckets = ["06:00", "08:00", "10:00", "12:00", "14:00", "16:00"];

  return buckets.map((label, index) => ({
    label,
    events: Math.max(2, Math.floor(events.length / 3) + index * 2),
    violations: Math.max(0, Math.floor(events.length / 12) + (index % 2))
  }));
}
