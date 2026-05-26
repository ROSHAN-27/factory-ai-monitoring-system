export function ErrorState({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-signal-red/25 bg-signal-red/10 px-4 py-3 text-sm text-red-100">
      {message}
    </div>
  );
}
