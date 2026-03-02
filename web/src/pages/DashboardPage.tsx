import { usePlayers } from "@/src/hooks/usePlayers";
import { usePowerRanking } from "@/src/hooks/usePower";
import { formatPower } from "@/src/lib/api";
import PowerRankingTable from "@/src/components/PowerRankingTable";

export default function DashboardPage() {
  const { data: players = [] } = usePlayers();
  const { data: topRanking = [] } = usePowerRanking(1);

  const topPower = topRanking[0] ?? null;
  const allianceCount = new Set(
    players.filter((p) => !p.is_enemy).map((p) => p.alliance),
  ).size;

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">대시보드</h1>

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="rounded-lg border border-border bg-card p-4">
          <div className="text-sm text-muted-foreground">등록 플레이어</div>
          <div className="text-2xl font-bold mt-1">{players.length}</div>
        </div>
        <div className="rounded-lg border border-border bg-card p-4">
          <div className="text-sm text-muted-foreground">최고 전투력</div>
          <div className="text-2xl font-bold text-primary mt-1">
            {topPower ? formatPower(topPower.total_power) : "-"}
          </div>
          {topPower && (
            <div className="text-xs text-muted-foreground mt-1">
              {topPower.player_id}
            </div>
          )}
        </div>
        <div className="rounded-lg border border-border bg-card p-4">
          <div className="text-sm text-muted-foreground">아군 연맹</div>
          <div className="text-2xl font-bold mt-1">{allianceCount || "-"}</div>
        </div>
      </div>

      {/* Power ranking */}
      <div className="rounded-lg border border-border bg-card p-6">
        <h2 className="text-lg font-semibold mb-4">전투력 랭킹</h2>
        <PowerRankingTable />
      </div>
    </div>
  );
}
