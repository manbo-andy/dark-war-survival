import ScreenshotUploader from "@/src/components/ScreenshotUploader";

export default function ScanPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">스크린샷 스캔</h1>
      <p className="text-muted-foreground text-sm">
        게임 '상세' 화면 스크린샷을 업로드하면 OCR로 전투력 데이터를 자동
        추출합니다.
      </p>
      <ScreenshotUploader />
    </div>
  );
}
