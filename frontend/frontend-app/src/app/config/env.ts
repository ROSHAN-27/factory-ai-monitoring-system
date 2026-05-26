const rawApiUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const rawWsUrl = import.meta.env.VITE_WS_URL ?? rawApiUrl.replace(/^http/, "ws") + "/ws/events";

export const env = {
  apiBaseUrl: rawApiUrl.replace(/\/$/, ""),
  wsUrl: rawWsUrl,
  realtimeEnabled: import.meta.env.VITE_REALTIME_ENABLED !== "false",
  pollingIntervalMs: Number(import.meta.env.VITE_POLLING_INTERVAL_MS ?? 10_000),
  maxLiveEvents: Number(import.meta.env.VITE_MAX_LIVE_EVENTS ?? 250),
  websocketBatchMs: Number(import.meta.env.VITE_WS_BATCH_MS ?? 500),
  websocketHeartbeatMs: Number(import.meta.env.VITE_WS_HEARTBEAT_MS ?? 15_000)
} as const;
