import { useQuery } from "@tanstack/react-query";
import { env } from "../../../app/config/env";
import { getRecognitionEvents } from "../../live-monitoring/api/attendanceApi";

export const dashboardQueryKeys = {
  events: ["dashboard", "events"] as const
};

export function useRecognitionEventsQuery() {
  return useQuery({
    queryKey: dashboardQueryKeys.events,
    queryFn: getRecognitionEvents,
    refetchInterval: env.pollingIntervalMs
  });
}
