import { useQuery } from "@tanstack/react-query";
import { getPlayers, getPlayer } from "@/src/lib/api";

export function usePlayers() {
  return useQuery({
    queryKey: ["players"],
    queryFn: getPlayers,
  });
}

export function usePlayer(id: string | null) {
  return useQuery({
    queryKey: ["players", id],
    queryFn: () => getPlayer(id!),
    enabled: !!id,
  });
}
