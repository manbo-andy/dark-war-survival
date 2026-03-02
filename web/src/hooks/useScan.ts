import { useMutation, useQueryClient } from "@tanstack/react-query";
import { scanScreenshot } from "@/src/lib/api";

export function useScanMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, playerId }: { file: File; playerId?: string }) =>
      scanScreenshot(file, playerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["power"] });
      queryClient.invalidateQueries({ queryKey: ["players"] });
    },
  });
}
