export type Direction = "IN" | "OUT" | "UNKNOWN";
export type Severity = "low" | "medium" | "high" | "critical";
export type CameraStatus = "online" | "offline" | "degraded";
export type AlertStatus = "open" | "acknowledged" | "resolved";

export type RecognitionEvent = {
  id: string;
  operatorId: string;
  operatorName: string;
  cameraId?: string;
  cameraName: string;
  zone: string;
  department?: string;
  timestamp: string;
  direction: Direction;
  confidence: number;
  snapshotUrl?: string;
  violationType?: string;
};

export type FactoryMetric = {
  label: string;
  value: string;
  delta?: string;
  tone: "cyan" | "green" | "amber" | "red";
};

export type CameraHealth = {
  id: string;
  name: string;
  zone: string;
  status: CameraStatus;
  fps: number;
  heartbeatSecondsAgo: number;
  accuracy: number;
};

export type MonitoringAlert = {
  id: string;
  title: string;
  operatorName?: string;
  severity: Severity;
  status: AlertStatus;
  createdAt: string;
  cameraName?: string;
  message: string;
};

export type ViolationSummary = {
  type: string;
  count: number;
  severity: Severity;
};

export type DepartmentOccupancy = {
  department: string;
  activeOperators: number;
  compliance: number;
};

export type DailyTrendPoint = {
  label: string;
  events: number;
  violations: number;
};
