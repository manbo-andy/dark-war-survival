import { useState } from "react";
import { toast } from "sonner";
import { generateReport } from "@/src/lib/api";

export default function ReportsPage() {
  const [generating, setGenerating] = useState(false);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const res = await generateReport();
      toast.success(res.message || "리포트가 생성되었습니다.");
    } catch {
      toast.error("리포트 생성에 실패했습니다.");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">리포트</h1>
      <p className="text-muted-foreground text-sm">
        일일 리포트를 생성하여 docs/reports/ 폴더에 저장합니다 (Obsidian 호환).
      </p>

      <button
        onClick={handleGenerate}
        disabled={generating}
        className="bg-primary hover:bg-primary/90 disabled:opacity-50 text-primary-foreground px-6 py-2 rounded-lg transition-colors"
      >
        {generating ? "생성 중..." : "리포트 생성"}
      </button>
    </div>
  );
}
