import { useQuery } from "@tanstack/react-query";
import { getEvents } from "@/src/lib/api";

export default function EventsPage() {
  const { data: events = [], isLoading } = useQuery({
    queryKey: ["events"],
    queryFn: getEvents,
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">이벤트</h1>
      <p className="text-muted-foreground text-sm">
        이벤트 관리 기능은 Phase 5에서 구현 예정입니다.
      </p>

      {isLoading ? (
        <div className="text-muted-foreground">로딩중...</div>
      ) : events.length === 0 ? (
        <div className="rounded-lg border border-border bg-card p-8 text-center text-muted-foreground">
          등록된 이벤트가 없습니다.
        </div>
      ) : (
        <div className="space-y-2">
          {events.map((event, i) => (
            <div
              key={i}
              className="rounded-lg border border-border bg-card p-4"
            >
              {JSON.stringify(event)}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
