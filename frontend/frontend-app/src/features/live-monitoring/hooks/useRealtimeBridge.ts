import { useEffect } from "react";
import { env } from "../../../app/config/env";
import { useLiveMonitoringStore } from "../../../app/store/liveMonitoringStore";
import { WebSocketManager } from "../../../shared/websocket/websocket-manager";

export function useRealtimeBridge() {
  const ingestEvents = useLiveMonitoringStore((state) => state.ingestEvents);
  const setConnectionState = useLiveMonitoringStore((state) => state.setConnectionState);

  useEffect(() => {
    if (!env.realtimeEnabled) {
      setConnectionState("polling");
      return;
    }

    setConnectionState("connecting");

    const client = new WebSocketManager({
      onOpen: () => setConnectionState("connected"),
      onClose: () => setConnectionState("polling"),
      onEvents: (events) => ingestEvents(events, "ws")
    });

    client.connect();
    client.subscribe("recognition");
    return () => client.disconnect();
  }, [ingestEvents, setConnectionState]);
}
