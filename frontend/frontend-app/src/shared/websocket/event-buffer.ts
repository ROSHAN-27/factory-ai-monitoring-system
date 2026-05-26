export class EventBuffer<T> {
  private buffer: T[] = [];
  private timer: number | null = null;

  constructor(
    private readonly flushMs: number,
    private readonly onFlush: (items: T[]) => void
  ) {}

  push(items: T[]) {
    this.buffer.push(...items);
    this.scheduleFlush();
  }

  flush() {
    if (this.timer) {
      window.clearTimeout(this.timer);
      this.timer = null;
    }

    if (this.buffer.length === 0) return;
    const items = this.buffer;
    this.buffer = [];
    this.onFlush(items);
  }

  clear() {
    if (this.timer) window.clearTimeout(this.timer);
    this.timer = null;
    this.buffer = [];
  }

  private scheduleFlush() {
    if (this.timer) return;
    this.timer = window.setTimeout(() => this.flush(), this.flushMs);
  }
}
