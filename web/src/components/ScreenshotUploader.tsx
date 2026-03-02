import { useState, useCallback, useRef } from "react";
import { Upload } from "lucide-react";
import { toast } from "sonner";
import { scanScreenshot, type ScanResult, formatPower } from "@/src/lib/api";
import { useQueryClient } from "@tanstack/react-query";

export default function ScreenshotUploader() {
  const [results, setResults] = useState<ScanResult[]>([]);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const handleFiles = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    setUploading(true);
    const newResults: ScanResult[] = [];

    for (const file of Array.from(files)) {
      try {
        const result = await scanScreenshot(file);
        newResults.push(result);
        if (result.saved) {
          toast.success(`${result.filename} 저장 완료`);
        } else {
          toast.warning(`${result.filename}: ${result.status}`);
        }
      } catch (e) {
        const errorResult: ScanResult = {
          status: "error",
          saved: false,
          filename: file.name,
          error: e instanceof Error ? e.message : "업로드 실패",
        };
        newResults.push(errorResult);
        toast.error(`${file.name} 업로드 실패`);
      }
    }

    setResults((prev) => [...newResults, ...prev]);
    setUploading(false);
    queryClient.invalidateQueries({ queryKey: ["power"] });
    queryClient.invalidateQueries({ queryKey: ["players"] });
  }, [queryClient]);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      handleFiles(e.dataTransfer.files);
    },
    [handleFiles],
  );

  return (
    <div className="space-y-4">
      {/* Drag & drop area */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors ${
          dragOver
            ? "border-primary bg-primary/10"
            : "border-border hover:border-primary/50"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          multiple
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        <Upload className="h-10 w-10 mx-auto mb-4 text-muted-foreground" />
        <p className="text-muted-foreground">
          {uploading
            ? "처리 중..."
            : "스크린샷을 드래그하거나 클릭하여 업로드"}
        </p>
        <p className="text-xs text-muted-foreground/60 mt-2">
          JPG, PNG 지원 / 여러 파일 동시 업로드 가능
        </p>
      </div>

      {/* Results list */}
      {results.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-muted-foreground">
            처리 결과
          </h3>
          {results.map((r, i) => (
            <div
              key={i}
              className={`p-3 rounded-lg text-sm ${
                r.saved
                  ? "bg-primary/10 border border-primary/30"
                  : "bg-destructive/10 border border-destructive/30"
              }`}
            >
              <div className="flex justify-between">
                <span className="font-medium">{r.filename}</span>
                <span>{r.saved ? "저장 완료" : "실패"}</span>
              </div>
              {r.reading && (
                <div className="text-muted-foreground mt-1">
                  {r.player_name_ocr} - {formatPower(r.reading.total_power)}
                </div>
              )}
              {r.error && (
                <div className="text-destructive mt-1">{r.error}</div>
              )}
              {r.warnings?.map((w, j) => (
                <div key={j} className="text-yellow-400 mt-1 text-xs">
                  {w}
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
