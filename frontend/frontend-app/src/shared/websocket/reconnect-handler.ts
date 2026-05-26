export class ReconnectHandler {
  private attempts = 0;
  private timer: number | null = null;

  constructor(
    private readonly reconnect: () => void,
    private readonly maxDelayMs = 30_000
  ) {}

  reset() {
    this.attempts = 0;
    if (this.timer) window.clearTimeout(this.timer);
    this.timer = null;
  }

  schedule() {
    const delay = Math.min(this.maxDelayMs, 1_000 * 2 ** this.attempts);
    this.attempts += 1;
    this.timer = window.setTimeout(this.reconnect, delay);
  }
}
