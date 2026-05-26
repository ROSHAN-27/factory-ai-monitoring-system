import type { RealtimeTopic } from "./event-types";

export class SubscriptionRegistry {
  private topics = new Set<RealtimeTopic>();

  subscribe(topic: RealtimeTopic) {
    this.topics.add(topic);
  }

  unsubscribe(topic: RealtimeTopic) {
    this.topics.delete(topic);
  }

  payload() {
    return {
      type: "subscribe",
      topics: Array.from(this.topics)
    };
  }
}
