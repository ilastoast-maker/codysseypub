# A1-2 전체 기능 검증 보고서

검증 대상: `09a2 / A1-2`

## 결과 요약

- Python 문법 검사: PASS
- unittest 자동 회귀 테스트: **18 / 18 PASS**
- CLI `--help`: PASS (exit 0)
- 잘못된 날짜: PASS (exit 1)
- 정상 캐시 실행: PASS (exit 0)
- 캐시 실행 시 외부 API 미호출: PASS
- 캐시 없이 API 키 누락: PASS (명확한 오류 + exit 1)
- 생성 Markdown 필수 섹션 7개: PASS

## 자동 테스트 항목

1. 정상/비정상 날짜 검증
2. `API.env` 우선 로딩
3. 필요한 API 키 검증
4. raw JSON 저장/캐시 불러오기
5. 손상 캐시 무시
6. Gemini 추천 단계만 JSON 모드 사용
7. 단일 도시 응답의 배열 승격 및 중복 정리
8. 추천 JSON 값 타입 검증
9. Gemini 추천 파싱 실패 시 1회 재시도
10. Kakao 키 누락 처리
11. Kakao 403 `code/msg` 상세 보존
12. Kakao `size` 범위 검증
13. Kakao 정상 응답 필드 매핑
14. Kakao 비정상 JSON 응답 처리
15. Gemini 리포트 실패 시 폴백 처리
16. 캐시 리포트에서 Gemini 호출 없음
17. 메인 캐시 적중 시 외부 클라이언트 미호출
18. `--no-cache` 메인 파이프라인의 복수 도시 순회/파일 저장

## CLI 스모크 테스트

```text
python travel_planner.py --help
→ exit 0

python travel_planner.py --date 2026-02-30
→ 날짜 형식 오류, exit 1

python travel_planner.py --date 2026-09-20
→ 준비한 정상 raw 캐시 사용
→ 외부 API 호출 건너뜀
→ Markdown 생성, exit 0

python travel_planner.py --date 2026-09-21 --no-cache
(API 키가 없는 테스트 환경)
→ 필요한 키 두 개를 표시하고 exit 1
```

생성 Markdown에서 확인한 섹션:

- 추천 지역
- 추천 이유
- 날씨 요약
- 행사/축제
- 맛집 추천
- 1일 일정 제안
- 오류 요약(errors)

## 외부 API 검토 범위

실제 비밀키를 테스트 코드나 저장소에 넣지 않기 위해 자동 테스트에서는 HTTP 호출을 mock 처리했습니다. 대신 요청 URL, 헤더, 파라미터, HTTP 상태별 처리와 응답 데이터 매핑을 검증했습니다.

확인한 사항:

- Gemini 추천 요청은 JSON 응답 모드 사용
- Gemini 최종 리포트는 일반 텍스트/Markdown 모드 사용
- Kakao 장소 검색은 `Authorization: KakaoAK {REST_API_KEY}` 방식
- Kakao 장소 검색 `size`는 1~15 범위
- Kakao 403은 응답의 `code`/`msg`를 보존하도록 구현
