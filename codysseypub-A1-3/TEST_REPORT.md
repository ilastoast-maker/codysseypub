# A1-3 테스트 결과

검증 대상: `09a3/codysseypub-A1-3`

## 자동 테스트

```text
Backend pytest: 21 / 21 PASS
Frontend Node simulation: 5 / 5 PASS
Python syntax check: PASS
JavaScript syntax check: PASS
```

## 주요 검증 항목

- 빈/누락/과도하게 긴 작품명 입력 검증
- 작품 제목 공백 정규화
- Google Search grounding 출처 추출 및 중복 제거
- 비정상 URL 제거
- grounding 실패 시 강제 재검색 및 422 처리
- 독자 리뷰/커뮤니티/번역 평가가 조사 프롬프트에 포함되는지 확인
- 조사 리뷰 메모가 2차 태그 생성 단계까지 전달되는지 확인
- `genre_tags`, `atmosphere_tags`, `translation_tags` 정규화
- 리뷰 기반 태그와 grounding 출처의 최종 API 응답 결합
- API 키 누락 500, upstream 장애 502 처리
- 프론트 정상 태그/출처 렌더링
- 잘못된 JSON 및 잘못된 응답 스키마 차단
- 55초 타임아웃 및 로딩 상태 복구

## 라이브 API 관련

자동 테스트는 실제 Gemini 과금을 발생시키지 않는 mock 기반 검증입니다. 실제 배포 후에는 Vercel 환경변수에 `GEMINI_API_KEY`를 설정하고 `/api/health` 및 `/api/analyze`를 호출해 Google Search grounding 결과의 `sources`가 1개 이상인지 확인해야 합니다.
