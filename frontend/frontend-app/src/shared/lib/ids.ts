export function stableEventId(parts: Array<string | number | undefined | null>) {
  return parts
    .map((part) => String(part ?? "na").trim().toLowerCase().replace(/\s+/g, "-"))
    .join(":");
}
