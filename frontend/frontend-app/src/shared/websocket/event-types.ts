import type { RecognitionEvent } from "../types/domain";

export type RealtimeEvent =
  | {
      type: "recognition.event";
      payload: RecognitionEvent;
    }
  | {
      type: "recognition.batch";
      payload: RecognitionEvent[];
    }
  | {
      type: "heartbeat";
      payload?: {
        serverTime?: string;
      };
    };

export type RealtimeTopic = "recognition" | "alerts" | "camera-health";

export function parseRealtimeMessage(raw: string): RealtimeEvent | null {
  try {
    const payload = JSON.parse(raw) as unknown;

    if (isEnvelope(payload)) {
      return payload;
    }

    if (Array.isArray(payload)) {
      return { type: "recognition.batch", payload: payload.filter(isRecognitionEvent) };
    }

    if (isRecognitionEvent(payload)) {
      return { type: "recognition.event", payload };
    }

    return null;
  } catch {
    return null;
  }
}

function isEnvelope(value: unknown): value is RealtimeEvent {
  if (!value || typeof value !== "object" || !("type" in value)) return false;
  const event = value as { type?: string; payload?: unknown };

  if (event.type === "heartbeat") return true;
  if (event.type === "recognition.event") return isRecognitionEvent(event.payload);
  if (event.type === "recognition.batch") return Array.isArray(event.payload);
  return false;
}

function isRecognitionEvent(value: unknown): value is RecognitionEvent {
  if (!value || typeof value !== "object") return false;
  const event = value as Partial<RecognitionEvent>;
  return Boolean(event.id && event.operatorName && event.cameraName && event.timestamp);
}
