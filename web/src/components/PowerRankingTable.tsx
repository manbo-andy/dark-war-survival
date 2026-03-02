import { Link } from "react-router-dom";
import { usePowerRanking } from "@/src/hooks/usePower";
import { formatPower } from "@/src/lib/api";

export default function PowerRankingTable() {
  const { data: rankings = [], isLoading } = usePowerRanking(20);

  if (isLoading) return <div className="text-muted-foreground">로딩중...</div>;
  if (!rankings.length)
    return <div className="text-muted-foreground">데이터가 없습니다.</div>;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-muted-foreground">
            <th className="py-3 px-2 text-left w-12">#</th>
            <th className="py-3 px-2 text-left">플레이어</th>
            <th className="py-3 px-2 text-right">전투력</th>
            <th className="py-3 px-2 text-right hidden sm:table-cell">건물</th>
            <th className="py-3 px-2 text-right hidden sm:table-cell">기술</th>
            <th className="py-3 px-2 text-right hidden md:table-cell">병력</th>
            <th className="py-3 px-2 text-right hidden md:table-cell">영웅</th>
            <th className="py-3 px-2 text-right hidden lg:table-cell">차량</th>
            <th className="py-3 px-2 text-right">적처치</th>
            <th className="py-3 px-2 text-right hidden sm:table-cell">날짜</th>
          </tr>
        </thead>
        <tbody>
          {rankings.map((r, i) => (
            <tr
              key={`${r.player_id}-${r.date}`}
              className="border-b border-border/50 hover:bg-card transition-colors"
            >
              <td className="py-2 px-2 text-muted-foreground">{i + 1}</td>
              <td className="py-2 px-2">
                <Link
                  to={`/players?id=${r.player_id}`}
                  className="text-primary hover:underline"
                >
                  {r.player_id}
                </Link>
              </td>
              <td className="py-2 px-2 text-right font-mono">
                {formatPower(r.total_power)}
              </td>
              <td className="py-2 px-2 text-right font-mono hidden sm:table-cell">
                {formatPower(r.building_power)}
              </td>
              <td className="py-2 px-2 text-right font-mono hidden sm:table-cell">
                {formatPower(r.tech_power)}
              </td>
              <td className="py-2 px-2 text-right font-mono hidden md:table-cell">
                {formatPower(r.troop_power)}
              </td>
              <td className="py-2 px-2 text-right font-mono hidden md:table-cell">
                {formatPower(r.hero_power)}
              </td>
              <td className="py-2 px-2 text-right font-mono hidden lg:table-cell">
                {formatPower(r.vehicle_power)}
              </td>
              <td className="py-2 px-2 text-right font-mono">
                {r.kill_count.toLocaleString()}
              </td>
              <td className="py-2 px-2 text-right text-muted-foreground hidden sm:table-cell">
                {r.date}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
