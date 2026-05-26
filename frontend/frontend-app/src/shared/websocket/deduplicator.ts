export class EventDeduplicator {
  private ids: string[] = [];
  private seen = new Set<string>();

  constructor(private readonly maxSize = 1_000) {}

  accept(id: string) {
    if (this.seen.has(id)) return false;

    this.seen.add(id);
    this.ids.push(id);

    while (this.ids.length > this.maxSize) {
      const oldest = this.ids.shift();
      if (oldest) this.seen.delete(oldest);
    }

    return true;
  }
}
