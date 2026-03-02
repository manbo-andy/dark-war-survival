import { useQuery } from "@tanstack/react-query";
import { getPowerRanking, getPowerHistory } from "@/src/lib/api";

export function usePowerRanking(top = 20) {
  return useQuery({
    queryKey: ["power", "ranking", top],
    queryFn: () => getPowerRanking(top),
  });
}

export function usePowerHistory(playerId: string) {
  return useQuery({
    queryKey: ["power", "history", playerId],
    queryFn: () => getPowerHistory(playerId),
    enabled: !!playerId,
  });
}
