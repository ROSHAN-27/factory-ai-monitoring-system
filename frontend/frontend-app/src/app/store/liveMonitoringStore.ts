import { create } from "zustand";
import { env } from "../config/env";
import type { MonitoringAlert, RecognitionEvent } from "../../shared/types/domain";

export type ConnectionState = "connecting" | "connected" | "disconnected" | "polling";

type LiveMonitoringState = {
  connectionState: ConnectionState;
  events: RecognitionEvent[];
  alerts: MonitoringAlert[];
  seenEventIds: string[];
  setConnectionState: (state: ConnectionState) => void;
  ingestEvents: (events: RecognitionEvent[], source?: "api" | "ws") => void;
  acknowledgeAlert: (alertId: string) => void;
};

function eventToAlert(event: RecognitionEvent): MonitoringAlert | null {
  if (!event.violationType && event.confidence >= 0.72) {
    return null;
  }

  return {
    id: `alert:${event.id}`,
    title: event.violationType ?? "Low recognition confidence",
    operatorName: event.operatorName,
    severity: event.confidence < 0.65 ? "high" : "medium",
    status: "open",
    createdAt: event.timestamp,
    cameraName: event.cameraName,
    message: `${event.operatorName} requires review at ${event.zone}.`
  };
}

export const useLiveMonitoringStore = create<LiveMonitoringState>((set, get) => ({
  connectionState: "connecting",
  events: [],
  alerts: [],
  seenEventIds: [],
  setConnectionState: (connectionState) => set({ connectionState }),
  ingestEvents: (incomingEvents) => {
    const { seenEventIds, events, alerts } = get();
    const seen = new Set(seenEventIds);
    const accepted: RecognitionEvent[] = [];
    const nextAlerts = [...alerts];

    for (const event of incomingEvents) {
      if (seen.has(event.id)) continue;
      seen.add(event.id);
      accepted.push(event);

      const alert = eventToAlert(event);
      if (alert && !nextAlerts.some((item) => item.id === alert.id)) {
        nextAlerts.unshift(alert);
      }
    }

    if (accepted.length === 0) return;

    const nextEvents = [...accepted, ...events]
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, env.maxLiveEvents);

    set({
      seenEventIds: Array.from(seen).slice(-env.maxLiveEvents * 3),
      events: nextEvents,
      alerts: nextAlerts.slice(0, 100)
    });
  },
  acknowledgeAlert: (alertId) =>
    set((state) => ({
      alerts: state.alerts.map((alert) =>
        alert.id === alertId ? { ...alert, status: "acknowledged" } : alert
      )
    }))
}));
