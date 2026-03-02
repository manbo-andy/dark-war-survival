import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { usePowerHistory } from "@/src/hooks/usePower";
import { formatPower } from "@/src/lib/api";

interface Props {
  playerId: string;
}

export default function PowerTrendChart({ playerId }: Props) {
  const { data: history = [], isLoading } = usePowerHistory(playerId);

  if (isLoading) return <div className="text-muted-foreground">로딩중...</div>;
  if (!history.length)
    return <div className="text-muted-foreground">전투력 이력이 없습니다.</div>;

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={history}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" fontSize={12} />
          <YAxis
            stroke="hsl(var(--muted-foreground))"
            fontSize={12}
            tickFormatter={(v) => formatPower(v)}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
              color: "hsl(var(--foreground))",
            }}
            formatter={(value: number) => [formatPower(value), ""]}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="total_power"
            name="총전투력"
            stroke="hsl(var(--chart-green))"
            strokeWidth={2}
            dot={{ r: 4 }}
          />
          <Line
            type="monotone"
            dataKey="building_power"
            name="건물"
            stroke="hsl(var(--chart-red))"
            strokeWidth={1}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="tech_power"
            name="기술"
            stroke="hsl(var(--chart-blue))"
            strokeWidth={1}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="troop_power"
            name="병력"
            stroke="hsl(var(--chart-yellow))"
            strokeWidth={1}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
