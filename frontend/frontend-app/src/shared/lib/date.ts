export function formatTime(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Invalid time";
  }

  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  }).format(date);
}

export function minutesAgo(value: string) {
  const date = new Date(value);
  const diff = Date.now() - date.getTime();

  if (Number.isNaN(diff) || diff < 0) {
    return "just now";
  }

  const minutes = Math.floor(diff / 60_000);
  if (minutes < 1) return "just now";
  if (minutes === 1) return "1 min ago";
  return `${minutes} mins ago`;
}
