"""최종 Markdown 여행 리포트 생성/저장."""

import os

import errors as E
import llm_client


def _restaurants_md(restaurants: list) -> str:
    if not restaurants:
        return "- 데이터 없음 (장소 검색 결과 0건)"
    lines = []
    for restaurant in restaurants:
        name = restaurant.get("name", "이름 없음")
        category = restaurant.get("category", "")
        address = restaurant.get("address", "")
        line = f"- **{name}** ({category})\n  - 주소: {address}"
        if restaurant.get("url"):
            line += f"\n  - 링크: {restaurant['url']}"
        lines.append(line)
    return "\n".join(lines)


def _errors_md(errors: list) -> str:
    if not errors:
        return "- 없음"
    return "\n".join(
        f"- [{e.get('step', '?')}] {e.get('type', '?')}: {e.get('message', '')}"
        for e in errors
    )


def fallback_body(date: str, rec: dict, restaurants_by_city: dict) -> str:
    """외부 API 없이 생성할 수 있는 결정적 Markdown 폴백 본문."""
    events = "\n".join(f"- {event}" for event in rec.get("events", [])) or "- 정보 없음"
    cities = rec.get("recommended_cities", [])
    rest_sections = [
        f"### {city}\n{_restaurants_md(restaurants_by_city.get(city, []))}"
        for city in cities
    ]
    rest_md = "\n\n".join(rest_sections) or "- 데이터 없음"

    return f"""# {date} 국내 여행 추천 리포트

## 추천 지역
{', '.join(cities) if cities else '정보 없음'}

## 추천 이유
{rec.get('reason', '')}

## 날씨 요약
{rec.get('weather', '')}

## 행사/축제
{events}

## 맛집 추천
{rest_md}

## 1일 일정 제안
- 오전: 추천 지역 대표 명소 방문
- 오후: 인근 관광 + 맛집 점심
- 저녁: 지역 야경/휴식
"""


def build_report(
    date: str,
    rec: dict,
    restaurants_by_city: dict,
    errors: list,
    *,
    use_llm: bool = True,
) -> str:
    """리포트를 생성한다. use_llm=False이면 외부 API 없이 폴백만 사용한다."""
    if use_llm:
        try:
            body = llm_client.generate_report_body(date, rec, restaurants_by_city)
        except Exception as exc:
            E.add_error(
                errors,
                "llm_report",
                E.LLM_REPORT_ERROR,
                f"리포트 생성 실패, 폴백 사용: {exc}",
            )
            body = fallback_body(date, rec, restaurants_by_city)
    else:
        body = fallback_body(date, rec, restaurants_by_city)

    return f"{body.rstrip()}\n\n## 오류 요약(errors)\n{_errors_md(errors)}\n"


def save_report(date: str, markdown: str, results_dir: str = "results") -> str:
    os.makedirs(results_dir, exist_ok=True)
    path = os.path.join(results_dir, f"{date}_travel_plan.md")
    with open(path, "w", encoding="utf-8") as file:
        file.write(markdown)
    return path
