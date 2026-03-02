# Dark War Survival - 전략 관리 도구 (DWS)

다크워 서바이벌 게임의 연맹 운영/전략 정보를 체계적으로 관리하기 위한 도구.
Python 백엔드(OCR, 데이터 분석, API) + Next.js 웹 대시보드(시각화, UI) 구조.

---

## 목차

- [프로젝트 구조](#프로젝트-구조)
- [설치](#설치)
- [CLI 사용법](#cli-사용법-dws)
- [웹 대시보드](#웹-대시보드)
- [REST API](#rest-api)
- [OCR 스크린샷 스캔](#ocr-스크린샷-스캔)
- [리포트 생성](#리포트-생성)
- [데이터 스키마](#데이터-스키마)
- [크로스 플랫폼](#크로스-플랫폼)

---

## 프로젝트 구조

```
dark-war-survival/
├── docs/                   # Obsidian 호환 마크다운 문서
│   ├── event/              # 이벤트 가이드
│   ├── info/               # 연맹/서버 정보, 스크린샷
│   └── reports/            # 자동 생성 리포트
├── data/                   # 구조화된 데이터 (JSON/CSV)
│   ├── players.json        # 플레이어 등록정보
│   ├── power_history.csv   # 전투력 시계열 데이터
│   └── ocr_log.json        # OCR 처리 로그
├── screenshots/            # 스크린샷 처리
│   ├── inbox/              # 처리 대기
│   └── processed/          # 처리 완료
├── server/                 # Python 백엔드
│   ├── pyproject.toml
│   └── src/
│       ├── api.py          # FastAPI REST API
│       ├── cli.py          # Click CLI
│       ├── ocr/            # EasyOCR 파이프라인
│       ├── models/         # 데이터 모델
│       ├── storage/        # JSON/CSV 스토리지
│       ├── reports/        # 차트 + 마크다운 리포트
│       └── utils/          # 유틸리티 (한국어 포맷 등)
└── web/                    # Next.js 웹 대시보드
    ├── package.json
    └── src/
        ├── app/            # 페이지 (대시보드, 플레이어, 스캔, 리포트, 이벤트)
        ├── components/     # UI 컴포넌트
        └── lib/            # API 클라이언트
```

---

## 설치

### 요구사항

- Python 3.10+
- Node.js 18+

### Python 백엔드

```bash
cd server
pip install -e .
```

설치가 완료되면 `dws` 명령어를 사용할 수 있습니다.

### 웹 대시보드

```bash
cd web
npm install
```

---

## CLI 사용법 (`dws`)

### 플레이어 관리

```bash
# 플레이어 등록
dws player add momonabi --alliance GaNG --tag R5 --notes "연맹장"
dws player add DarkKnight --alliance GaNG --tag R4
dws player add EnemyOne --alliance XYZ --server 510 --enemy

# 이름을 ID와 다르게 지정
dws player add user123 --name "표시이름" --alliance GaNG

# 플레이어 목록
dws player list                     # 전체 목록
dws player list --alliance GaNG     # 연맹별 필터
dws player list --enemy             # 적군만 표시

# 플레이어 상세 정보 (전투력 포함)
dws player info momonabi
```

**`dws player add` 옵션:**

| 옵션 | 단축 | 설명 | 기본값 |
|------|------|------|--------|
| `--name` | | 표시 이름 | ID와 동일 |
| `--alliance` | `-a` | 연맹 태그 | (없음) |
| `--server` | `-s` | 서버 번호 | 510 |
| `--enemy` | | 적군으로 등록 | false |
| `--tag` | `-t` | 태그 (여러 번 사용 가능) | (없음) |
| `--notes` | | 메모 | (없음) |

### 전투력 관리

```bash
# 전투력 기록 (총전투력 필수, 세부 항목은 선택)
dws power add momonabi 206589465

# 세부 항목 포함하여 기록
dws power add momonabi 206589465 \
    --building 45000000 \
    --tech 38000000 \
    --troop 65000000 \
    --hero 35000000 \
    --vehicle 23000000 \
    --kills 1250000

# 특정 날짜로 기록
dws power add momonabi 200000000 --date 2026-02-28

# 전투력 랭킹 (각 플레이어별 최신 기록 기준)
dws power rank              # 상위 20명
dws power rank --top 10     # 상위 10명

# 특정 플레이어의 전투력 이력
dws power history momonabi
```

**`dws power add` 옵션:**

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--building` | 건물 전투력 | 0 |
| `--tech` | 기술 전투력 | 0 |
| `--troop` | 병력 전투력 | 0 |
| `--hero` | 영웅 전투력 | 0 |
| `--vehicle` | 차량 전투력 | 0 |
| `--kills` | 적 처치 수 | 0 |
| `--date` | 기록 날짜 (YYYY-MM-DD) | 오늘 |

### 스크린샷 OCR

```bash
# 단일 스크린샷 스캔 (결과만 출력, 저장하지 않음)
dws scan screenshot.jpg

# 플레이어 ID 지정하여 스캔
dws scan screenshot.jpg --player momonabi

# screenshots/inbox/ 폴더의 모든 스크린샷 일괄 처리
# 처리 완료된 파일은 screenshots/processed/로 이동
dws scan --all
```

### 리포트 생성

```bash
# 오늘 날짜 리포트 생성 (docs/reports/에 저장)
dws report generate

# 특정 날짜 리포트
dws report generate --date 2026-03-01
```

생성된 리포트는 `docs/reports/daily_YYYY-MM-DD.md` 형식으로 저장되며, Obsidian에서 바로 열 수 있습니다.

### API 서버 실행

```bash
# 기본 (0.0.0.0:8000)
dws serve

# 포트 변경
dws serve --port 9000

# 특정 호스트
dws serve --host 127.0.0.1 --port 8080
```

---

## 웹 대시보드

### 실행

두 터미널이 필요합니다:

```bash
# 터미널 1: Python API 서버
cd server
dws serve

# 터미널 2: Next.js 개발 서버
cd web
npm run dev
```

브라우저에서 `http://localhost:3000` 에 접속합니다.

### 페이지 구성

| 페이지 | 경로 | 기능 |
|--------|------|------|
| 대시보드 | `/` | 요약 카드 + 전투력 랭킹 테이블 |
| 플레이어 | `/players` | 플레이어 카드 목록, 상세 정보 + 전투력 추이 차트 |
| 스캔 | `/scan` | 스크린샷 드래그&드롭 업로드 → OCR 처리 |
| 리포트 | `/reports` | 리포트 생성 버튼 |
| 이벤트 | `/events` | 이벤트 관리 (추후 구현) |

### 아키텍처

```
브라우저 (:3000)  ──API 프록시──▶  Python FastAPI (:8000)
  Next.js                            │
  Recharts (차트)                     ├── data/ (JSON/CSV)
  Tailwind CSS                        ├── screenshots/
                                      └── docs/reports/
```

웹 대시보드는 Next.js의 `rewrites` 설정으로 `/api/*` 요청을 Python 서버(`localhost:8000`)로 프록시합니다.

---

## REST API

Python API 서버가 실행 중일 때 (`dws serve`) 사용 가능합니다.
API 문서는 `http://localhost:8000/docs` (Swagger UI)에서도 확인할 수 있습니다.

### 플레이어

```bash
# 플레이어 목록
curl http://localhost:8000/api/players

# 연맹별 필터
curl "http://localhost:8000/api/players?alliance=GaNG"

# 적군만
curl "http://localhost:8000/api/players?enemy=true"

# 플레이어 등록
curl -X POST http://localhost:8000/api/players \
  -H "Content-Type: application/json" \
  -d '{"id": "momonabi", "name": "momonabi", "alliance": "GaNG", "tags": ["R5"]}'

# 플레이어 상세
curl http://localhost:8000/api/players/momonabi
```

### 전투력

```bash
# 전투력 랭킹
curl "http://localhost:8000/api/power/rank?top=10"

# 전투력 이력
curl http://localhost:8000/api/power/history/momonabi

# 전투력 입력
curl -X POST http://localhost:8000/api/power \
  -H "Content-Type: application/json" \
  -d '{
    "player_id": "momonabi",
    "total_power": 206589465,
    "building_power": 45000000,
    "tech_power": 38000000,
    "troop_power": 65000000,
    "hero_power": 35000000,
    "vehicle_power": 23000000,
    "kill_count": 1250000
  }'
```

### 스크린샷 OCR

```bash
# 스크린샷 업로드
curl -X POST http://localhost:8000/api/scan \
  -F "file=@screenshot.jpg"

# 플레이어 ID 지정
curl -X POST "http://localhost:8000/api/scan?player_id=momonabi" \
  -F "file=@screenshot.jpg"
```

### API 전체 목록

| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/players` | 플레이어 목록 (`?alliance=`, `?enemy=true`) |
| POST | `/api/players` | 플레이어 등록 |
| GET | `/api/players/{id}` | 플레이어 상세 |
| GET | `/api/power/rank` | 전투력 랭킹 (`?top=20`) |
| GET | `/api/power/history/{id}` | 전투력 이력 |
| POST | `/api/power` | 전투력 수동 입력 |
| POST | `/api/scan` | 스크린샷 OCR (multipart) |
| GET | `/api/events` | 이벤트 목록 |
| POST | `/api/reports/generate` | 리포트 생성 |

---

## OCR 스크린샷 스캔

### 지원하는 스크린샷

게임 내 **'상세' 다이얼로그** 화면의 스크린샷을 처리합니다.
추출 항목: 플레이어 이름, 총전투력, 건물/기술/병력/영웅/차량 전투력, 적처치 수

### 처리 흐름

```
1. 스크린샷 → screenshots/inbox/ 에 배치 (또는 웹에서 업로드)
2. dws scan --all 실행 (또는 웹 대시보드에서 업로드)
3. EasyOCR로 텍스트 추출
4. 전투력 데이터 파싱 + 검증 (세부합계 ≈ 총전투력)
5. data/power_history.csv에 저장
6. 스크린샷을 screenshots/processed/로 이동
7. 처리 로그를 data/ocr_log.json에 기록
```

### OCR 엔진

- **EasyOCR** (한국어 + 영어)
- 전처리: 그레이스케일 → 대비 강화 → 샤프닝
- 숫자 추출 시 `allowlist='0123456789,.'` 사용
- 신뢰도 0.3 미만인 결과는 저장하지 않음

### 해상도 지원

| 해상도 | 비율 | 예시 기기 |
|--------|------|-----------|
| 1080x2340 | 19.5:9 | 일반 FHD+ 스마트폰 |
| 1080x1920 | 16:9 | PC 에뮬레이터 |

새 해상도를 추가하려면 `server/src/ocr/regions.py`의 `LAYOUTS` 딕셔너리에 영역 좌표를 정의합니다.

---

## 리포트 생성

### 일일 리포트

`dws report generate` 또는 웹 대시보드에서 생성합니다.

생성 파일:
- `docs/reports/daily_YYYY-MM-DD.md` - 마크다운 리포트
- `docs/reports/assets/ranking_YYYY-MM-DD.png` - 랭킹 바 차트

리포트에 포함되는 내용:
- 등록 플레이어 수, 전투력 기록 수, 최고 전투력
- 전투력 랭킹 테이블 (순위, 이름, 연맹, 전투력, 적처치)
- 랭킹 차트 이미지

### Obsidian 연동

`docs/` 폴더를 Obsidian vault로 열면 리포트, 이벤트 가이드, 연맹 정보를 한곳에서 관리할 수 있습니다. 리포트 내 차트 이미지는 `![[assets/ranking_YYYY-MM-DD.png]]` 형태로 임베드됩니다.

---

## 데이터 스키마

### players.json

```json
{
  "id": "momonabi",
  "name": "momonabi",
  "alliance": "GaNG",
  "server": 510,
  "is_enemy": false,
  "tags": ["R5"],
  "notes": "연맹장",
  "active": true
}
```

### power_history.csv

```csv
date,player_id,total_power,building_power,tech_power,troop_power,hero_power,vehicle_power,kill_count,source
2026-03-02,momonabi,206589465,45000000,38000000,65000000,35000000,23000000,1250000,manual
```

| 컬럼 | 설명 |
|------|------|
| `date` | 기록 날짜 (YYYY-MM-DD) |
| `player_id` | 플레이어 ID |
| `total_power` | 총전투력 |
| `building_power` | 건물 전투력 |
| `tech_power` | 기술 전투력 |
| `troop_power` | 병력 전투력 |
| `hero_power` | 영웅 전투력 |
| `vehicle_power` | 차량 전투력 |
| `kill_count` | 적 처치 수 |
| `source` | 입력 소스 (`manual` 또는 `ocr`) |

---

## 크로스 플랫폼

Windows와 Linux 모두 지원합니다.

| 항목 | Windows | Linux |
|------|---------|-------|
| 경로 처리 | `pathlib.Path` 자동 처리 | `pathlib.Path` 자동 처리 |
| 한국어 폰트 (차트) | Malgun Gothic | NanumGothic |
| Python | 3.10+ | 3.10+ |
| Node.js | 18+ | 18+ |

### Windows 참고사항

터미널에서 한국어가 깨지는 경우 환경변수를 설정하세요:

```bash
set PYTHONIOENCODING=utf-8
```

또는 PowerShell:

```powershell
$env:PYTHONIOENCODING="utf-8"
```

---

## 기술 스택

### Python 백엔드

| 패키지 | 용도 |
|--------|------|
| FastAPI + Uvicorn | REST API 서버 |
| Click | CLI 프레임워크 |
| EasyOCR | OCR 엔진 (한국어+영어) |
| pandas | 데이터 분석, CSV 처리 |
| matplotlib | 차트 생성 |
| Pillow | 이미지 전처리 |

### 웹 대시보드

| 패키지 | 용도 |
|--------|------|
| Next.js 15 | React 프레임워크 |
| Recharts | 인터랙티브 차트 |
| Tailwind CSS 4 | 스타일링 |
| Axios | API 클라이언트 |
