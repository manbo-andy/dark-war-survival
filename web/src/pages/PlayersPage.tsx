import { useSearchParams, Link } from "react-router-dom";
import { usePlayers, usePlayer } from "@/src/hooks/usePlayers";
import { usePowerRanking } from "@/src/hooks/usePower";
import PlayerCard from "@/src/components/PlayerCard";
import PowerTrendChart from "@/src/components/PowerTrendChart";
import { formatPower } from "@/src/lib/api";

export default function PlayersPage() {
  const [searchParams] = useSearchParams();
  const selectedId = searchParams.get("id");

  const { data: players = [], isLoading } = usePlayers();
  const { data: selectedPlayer } = usePlayer(selectedId);
  const { data: rankings = [] } = usePowerRanking(100);

  const latestPowers: Record<string, number> = {};
  for (const reading of rankings) {
    latestPowers[reading.player_id] = reading.total_power;
  }

  if (isLoading) return <div className="text-muted-foreground">로딩중...</div>;

  if (selectedPlayer) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Link to="/players" className="text-muted-foreground hover:text-foreground">
            &larr; 목록
          </Link>
          <h1 className="text-2xl font-bold">{selectedPlayer.name}</h1>
          {selectedPlayer.is_enemy && (
            <span className="text-xs bg-destructive/20 text-destructive px-2 py-1 rounded">
              적
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="rounded-lg border border-border bg-card p-4">
            <h3 className="text-sm text-muted-foreground mb-3">플레이어 정보</h3>
            <div className="space-y-2 text-sm">
              <div>ID: {selectedPlayer.id}</div>
              <div>연맹: {selectedPlayer.alliance || "-"}</div>
              <div>서버: {selectedPlayer.server}</div>
              <div>
                태그:{" "}
                {selectedPlayer.tags.length > 0
                  ? selectedPlayer.tags.join(", ")
                  : "-"}
              </div>
              <div>메모: {selectedPlayer.notes || "-"}</div>
            </div>
          </div>
          <div className="rounded-lg border border-border bg-card p-4">
            <h3 className="text-sm text-muted-foreground mb-3">전투력</h3>
            <div className="text-3xl font-bold text-primary">
              {latestPowers[selectedPlayer.id]
                ? formatPower(latestPowers[selectedPlayer.id])
                : "-"}
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-card p-6">
          <h3 className="text-sm text-muted-foreground mb-4">전투력 추이</h3>
          <PowerTrendChart playerId={selectedPlayer.id} />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">플레이어</h1>
      {players.length === 0 ? (
        <div className="text-muted-foreground">등록된 플레이어가 없습니다.</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {players.map((p) => (
            <PlayerCard
              key={p.id}
              player={p}
              latestPower={latestPowers[p.id]}
            />
          ))}
        </div>
      )}
    </div>
  );
}
