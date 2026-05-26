import { apiRequest } from "../../../shared/api/httpClient";
import { stableEventId } from "../../../shared/lib/ids";
import type { Direction, RecognitionEvent } from "../../../shared/types/domain";

type AttendanceApiRow = {
  id?: number | string;
  employee_id?: string;
  operator_id?: string | number;
  employee_name?: string;
  operator_name?: string;
  event_type?: string;
  camera_name?: string;
  created_at?: string;
  event_time?: string;
  confidence_score?: number;
  snapshot_path?: string;
  zone?: string;
  department?: string;
};

function normalizeDirection(value?: string): Direction {
  if (value === "IN" || value === "OUT") return value;
  return "UNKNOWN";
}

function normalizeAttendanceRow(row: AttendanceApiRow, index: number): RecognitionEvent {
  const timestamp = row.event_time ?? row.created_at ?? new Date().toISOString();
  const operatorName = row.operator_name ?? row.employee_name ?? "Unknown operator";
  const cameraName = row.camera_name ?? "Unassigned camera";

  return {
    id:
      row.id?.toString() ??
      stableEventId([operatorName, row.event_type, cameraName, timestamp, index]),
    operatorId: String(row.operator_id ?? row.employee_id ?? operatorName),
    operatorName,
    cameraName,
    zone: row.zone ?? inferZone(cameraName),
    department: row.department ?? inferDepartment(cameraName),
    timestamp,
    direction: normalizeDirection(row.event_type),
    confidence: row.confidence_score ?? 0.92,
    snapshotUrl: row.snapshot_path
  };
}

function inferZone(cameraName: string) {
  const upper = cameraName.toUpperCase();
  if (upper.includes("ENTRY")) return "Factory Entry";
  if (upper.includes("EXIT")) return "Factory Exit";
  if (upper.includes("DORM")) return "Dormitory";
  return "Production Floor";
}

function inferDepartment(cameraName: string) {
  const upper = cameraName.toUpperCase();
  if (upper.includes("PACK")) return "Packaging";
  if (upper.includes("QC")) return "Quality";
  if (upper.includes("ASSEMBLY")) return "Assembly";
  return "General";
}

export async function getRecognitionEvents() {
  const rows = await apiRequest<AttendanceApiRow[]>("/attendance");
  return rows.map(normalizeAttendanceRow);
}
