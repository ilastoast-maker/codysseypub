# 국내 여행 추천 프로그램 (Travel Planner CLI)

Google Gemini와 Kakao Local API를 조합해 여행 날짜에 맞는 국내 여행지를 추천하고, 추천 지역별 맛집을 검색한 뒤 Markdown 여행 리포트를 생성하는 Python CLI 프로젝트입니다.

> 저장소: `ilastoast-maker/codysseypub`  
> 브랜치: `09a2`  
> 과제 폴더: `A1-2`

## 주요 기능

- `--date YYYY-MM-DD` 형식의 여행 날짜 입력 및 검증
- Gemini를 이용한 국내 여행 도시 2~3곳 추천
- `recommended_cities` 복수 지역 구조 지원
- Kakao Local API를 이용한 도시별 맛집 검색
- `restaurants_by_city` 구조로 도시별 결과 저장
- Gemini 기반 Markdown 리포트 생성
- Gemini 리포트 실패 시 로컬 폴백 리포트 생성
- 날짜별 raw JSON 캐시 저장/재사용
- 정상 캐시 사용 시 외부 API 호출 없이 결과 재생성
- Kakao 401/403/429/기타 HTTP 오류 및 응답 상세 기록
- Gemini 추천 JSON 파싱 실패 시 1회 재시도

## 프로젝트 구조

```text
A1-2/
├── travel_planner.py
├── llm_client.py
├── place_client.py
├── report.py
├── errors.py
├── requirements.txt
├── .gitignore
├── README.md
├── TEST_REPORT.md
├── git_commands.md
└── tests/
    └── test_travel_planner.py
```

실행 결과인 `results/`, 실제 API 키 파일인 `API.env`와 `.env`는 Git에서 제외합니다. `API.env`는 사용자가 로컬에서 직접 생성합니다.

## 설치

```bash
git clone -b 09a2 https://github.com/ilastoast-maker/codysseypub.git
cd codysseypub/A1-2
python -m venv venv
```

macOS/Linux:

```bash
source venv/bin/activate
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

의존성 설치:

```bash
pip install -r requirements.txt
```

## API 키 설정

프로젝트 폴더(`A1-2`)에 `API.env` 파일을 직접 생성한 뒤 실제 키를 입력합니다.

macOS/Linux 예시:

```bash
touch API.env
```

Windows PowerShell 예시:

```powershell
New-Item API.env -ItemType File
```

생성한 `API.env`에 실제 키를 입력합니다.

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
KAKAO_REST_API_KEY=YOUR_KAKAO_REST_API_KEY
```

프로그램은 `travel_planner.py`가 있는 폴더의 `API.env`를 가장 먼저 읽고, 없으면 `.env`, 그 다음 기존 셸 환경변수를 사용합니다. 실제 키 파일은 절대 GitHub에 커밋하지 않습니다.

## 실행

```bash
python travel_planner.py --date "2026-09-20"
```

캐시를 무시하고 API를 새로 호출하려면:

```bash
python travel_planner.py --date "2026-09-20" --no-cache
```

도움말:

```bash
python travel_planner.py --help
```

## 실행 흐름

```text
날짜 입력
  ↓
날짜 형식 검증 + API.env 로드
  ↓
캐시 확인
  ├─ 캐시 있음 → 외부 API 호출 없이 로컬 Markdown 리포트 재생성
  └─ 캐시 없음
       ↓
    API 키 확인
       ↓
    Gemini 여행지 추천(JSON)
       ↓
    recommended_cities 순회
       ↓
    Kakao 맛집 검색
       ↓
    raw JSON 저장
       ↓
    Gemini Markdown 리포트 생성
       └─ 실패 시 로컬 폴백
       ↓
    Markdown + raw JSON 저장
```

## 데이터 구조

Gemini 추천 결과:

```json
{
  "recommended_cities": ["제주", "강릉"],
  "weather": "날씨 요약",
  "events": ["행사/축제 후보"],
  "reason": "추천 이유"
}
```

단일 `recommended_city`가 반환돼도 내부에서 `recommended_cities` 배열로 보정합니다.

지역별 맛집 결과:

```json
{
  "restaurants_by_city": {
    "제주": [
      {
        "name": "식당명",
        "address": "주소",
        "category": "음식점 카테고리",
        "url": "장소 URL",
        "x": 126.0,
        "y": 33.0
      }
    ],
    "강릉": []
  }
}
```

raw JSON:

```json
{
  "date": "2026-09-20",
  "recommendation": {
    "recommended_cities": ["제주", "강릉"],
    "weather": "...",
    "events": [],
    "reason": "..."
  },
  "restaurants_by_city": {
    "제주": [],
    "강릉": []
  },
  "errors": []
}
```

## 외부 API 처리

### Gemini

추천 단계에서는 JSON 응답이 필요하므로 `responseMimeType: application/json`을 사용합니다. 최종 리포트는 Markdown 일반 텍스트가 필요하므로 JSON 모드를 사용하지 않습니다.

추천 JSON에 필요한 필드:

- `recommended_cities`: 문자열 배열
- `weather`: 문자열
- `events`: 문자열 배열
- `reason`: 문자열

파싱/스키마 검증에 실패하면 한 번 더 요청합니다.

### Kakao Local

요청 헤더:

```text
Authorization: KakaoAK {KAKAO_REST_API_KEY}
```

키워드 검색의 `size`는 코드에서 1~15 범위로 검증합니다.

오류 처리:

- 401/403 → `AUTH_ERROR`
- 429 → `QUOTA_ERROR`
- 기타 HTTP 오류 → `HTTP_ERROR`
- 네트워크 오류 → `NETWORK_ERROR`
- JSON 파싱 실패 → `RESPONSE_ERROR`
- 검색 결과 0건 → `EMPTY_RESULT`

특히 403에서는 단순히 `HTTP 403`만 기록하지 않고 Kakao가 반환하는 `code`와 `msg`를 함께 남깁니다. 예:

```text
HTTP 403 / code=-3 / msg=...
```

따라서 카카오맵 API 활성화/권한 문제를 구분하기 쉬워집니다.

## 캐시

`results/{date}_raw.json`이 정상적으로 존재하면 해당 데이터를 사용합니다. 캐시를 사용할 때는 Gemini/Kakao API 키가 없어도 되고 외부 API도 호출하지 않습니다.

손상된 JSON이나 필요한 스키마가 없는 캐시는 프로그램을 종료시키지 않고 경고를 출력한 뒤 새 데이터 생성을 시도합니다.

## 결과 파일

```text
results/
├── 2026-09-20_raw.json
└── 2026-09-20_travel_plan.md
```

Markdown 리포트에는 다음 항목이 포함됩니다.

- 추천 지역
- 추천 이유
- 날씨 요약
- 행사/축제
- 맛집 추천
- 1일 일정 제안
- 오류 요약(errors)

## 테스트

문법 검사:

```bash
python -m py_compile travel_planner.py llm_client.py place_client.py report.py errors.py tests/test_travel_planner.py
```

자동 테스트:

```bash
python -m unittest discover -s tests -v
```

현재 검증 결과는 `TEST_REPORT.md`에 기록되어 있습니다.

자동 테스트는 실제 API 키를 저장소에 넣지 않기 위해 HTTP 호출을 mock으로 검증합니다. 실제 API 호출 시에는 본인의 `API.env`가 필요합니다.

## 수정 과정에서 확인한 주요 문제

- Gemini 최종 Markdown 리포트 요청에도 JSON 응답 모드를 사용하던 문제 수정
- Kakao 403 응답의 실제 `code`/`msg`가 사라지던 문제 수정
- 손상된 캐시가 프로그램을 종료시키던 문제 수정
- 캐시 사용 시에도 외부 API 키와 Gemini 호출이 필요하던 문제 수정
- `results/` 경로가 실행한 현재 디렉터리에 따라 달라지던 문제 수정
- `API.env` 우선순위가 기존 셸 환경변수 때문에 실제로 적용되지 않을 수 있던 문제 수정
- README가 존재하지 않는 `API.env.example`을 안내하던 문제 수정 → 로컬 `API.env` 직접 생성 방식으로 정정
- 추천 JSON의 필수 값 타입 검증 강화

## 보안

- 실제 `API.env` 또는 `.env`를 저장소에 올리지 않습니다.
- 키를 소스 코드에 하드코딩하지 않습니다.
- 키가 외부에 노출되면 해당 서비스에서 즉시 폐기 후 재발급합니다.
