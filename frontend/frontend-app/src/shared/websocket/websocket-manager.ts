import { env } from "../../app/config/env";
import type { RecognitionEvent } from "../types/domain";
import { EventBuffer } from "./event-buffer";
import { EventDeduplicator } from "./deduplicator";
import { HeartbeatMonitor } from "./heartbeat";
import { ReconnectHandler } from "./reconnect-handler";
import { parseRealtimeMessage, type RealtimeTopic } from "./event-types";
import { SubscriptionRegistry } from "./subscriptions";

type WebSocketManagerOptions = {
  onOpen: () => void;
  onClose: () => void;
  onEvents: (events: RecognitionEvent[]) => void;
  onInvalidMessage?: (raw: string) => void;
};

export class WebSocketManager {
  private socket: WebSocket | null = null;
  private closedByConsumer = false;
  private readonly subscriptions = new SubscriptionRegistry();
  private readonly deduplicator = new EventDeduplicator();
  private readonly buffer = new EventBuffer<RecognitionEvent>(env.websocketBatchMs, (events) =>
    this.options.onEvents(events)
  );
  private readonly heartbeat = new HeartbeatMonitor(env.websocketHeartbeatMs, () => this.restart());
  private readonly reconnect = new ReconnectHandler(() => this.connect());

  constructor(private readonly options: WebSocketManagerOptions) {}

  connect() {
    if (!env.realtimeEnabled || this.socket) return;

    this.closedByConsumer = false;
    this.socket = new WebSocket(env.wsUrl);

    this.socket.onopen = () => {
      this.reconnect.reset();
      this.options.onOpen();
      this.send(this.subscriptions.payload());
      this.heartbeat.start(() => this.send({ type: "ping" }));
    };

    this.socket.onmessage = (message) => this.handleMessage(String(message.data));
    this.socket.onerror = () => this.restart();
    this.socket.onclose = () => {
      this.socket = null;
      this.heartbeat.stop();
      this.options.onClose();

      if (!this.closedByConsumer) {
        this.reconnect.schedule();
      }
    };
  }

  disconnect() {
    this.closedByConsumer = true;
    this.buffer.flush();
    this.heartbeat.stop();
    this.reconnect.reset();
    this.socket?.close();
    this.socket = null;
  }

  subscribe(topic: RealtimeTopic) {
    this.subscriptions.subscribe(topic);
    this.send(this.subscriptions.payload());
  }

  private restart() {
    if (!this.socket) return;
    this.socket.close();
  }

  private handleMessage(raw: string) {
    const event = parseRealtimeMessage(raw);

    if (!event) {
      this.options.onInvalidMessage?.(raw);
      return;
    }

    if (event.type === "heartbeat") {
      this.heartbeat.beat();
      return;
    }

    const events = event.type === "recognition.event" ? [event.payload] : event.payload;
    this.buffer.push(events.filter((item) => this.deduplicator.accept(item.id)));
  }

  private send(payload: unknown) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(payload));
    }
  }
}
