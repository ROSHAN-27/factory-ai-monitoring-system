export class HeartbeatMonitor {
  private timer: number | null = null;
  private lastBeat = Date.now();

  constructor(
    private readonly intervalMs: number,
    private readonly onTimeout: () => void
  ) {}

  start(sendPing: () => void) {
    this.stop();
    this.lastBeat = Date.now();
    this.timer = window.setInterval(() => {
      sendPing();
      if (Date.now() - this.lastBeat > this.intervalMs * 2.5) {
        this.onTimeout();
      }
    }, this.intervalMs);
  }

  beat() {
    this.lastBeat = Date.now();
  }

  stop() {
    if (this.timer) window.clearInterval(this.timer);
    this.timer = null;
  }
}
