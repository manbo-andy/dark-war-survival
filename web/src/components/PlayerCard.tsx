import { Link } from "react-router-dom";
import { type Player, formatPower } from "@/src/lib/api";

interface Props {
  player: Player;
  latestPower?: number;
}

export default function PlayerCard({ player, latestPower }: Props) {
  return (
    <Link to={`/players?id=${player.id}`}>
      <div className="rounded-lg border border-border bg-card p-4 hover:bg-card/80 transition-colors cursor-pointer">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold text-foreground">{player.name}</h3>
          {player.is_enemy && (
            <span className="text-xs bg-destructive/20 text-destructive px-2 py-0.5 rounded">
              적
            </span>
          )}
        </div>
        <div className="text-sm text-muted-foreground space-y-1">
          <div>연맹: {player.alliance || "-"}</div>
          <div>서버: {player.server}</div>
          {player.tags.length > 0 && (
            <div className="flex gap-1 mt-2">
              {player.tags.map((tag) => (
                <span
                  key={tag}
                  className="text-xs bg-primary/20 text-primary px-2 py-0.5 rounded"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
          {latestPower !== undefined && latestPower > 0 && (
            <div className="mt-2 text-primary font-mono">
              {formatPower(latestPower)}
            </div>
          )}
        </div>
      </div>
    </Link>
  );
}
