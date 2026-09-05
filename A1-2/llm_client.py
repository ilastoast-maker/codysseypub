"""Gemini API 호출, 추천 JSON 파싱, 최종 Markdown 리포트 생성."""

import json
import os
import re

import requests

import errors as E

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)
REQUIRED_KEYS = ["recommended_cities", "weather", "events", "reason"]


def _call_llm(prompt: str, *, json_mode: bool = False) -> str:
    """Gemini를 호출하고 첫 번째 텍스트 응답을 반환한다.

    추천 단계만 JSON 모드를 사용하고, Markdown 리포트 단계는 일반 텍스트 모드를 사용한다.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY 미설정")

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    if json_mode:
        payload["generationConfig"] = {"responseMimeType": "application/json"}

    resp = requests.post(
        GEMINI_URL,
        headers={"Content-Type": "application/json"},
        params={"key": api_key},
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    try:
        parts = data["candidates"][0]["content"]["parts"]
        text = "".join(part.get("text", "") for part in parts).strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("Gemini 응답에서 텍스트를 찾을 수 없음") from exc

    if not text:
        raise RuntimeError("Gemini가 빈 응답을 반환함")
    return text


def _extract_json(text: str) -> dict:
    """텍스트에서 JSON 객체를 추출한다."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("JSON 블록을 찾을 수 없음")
    obj = json.loads(text[start:end + 1])
    if not isinstance(obj, dict):
        raise ValueError("JSON 최상위 값이 객체가 아님")
    return obj


def _normalize(obj: dict) -> dict:
    """단일 도시 응답을 복수 도시 배열로 보정하고 도시명을 정리한다."""
    obj = dict(obj)
    if "recommended_cities" not in obj and "recommended_city" in obj:
        obj["recommended_cities"] = [obj["recommended_city"]]

    cities = obj.get("recommended_cities")
    if isinstance(cities, list):
        cleaned = []
        for city in cities:
            if isinstance(city, str):
                city = city.strip()
                if city and city not in cleaned:
                    cleaned.append(city)
        obj["recommended_cities"] = cleaned
    return obj


def _has_required_keys(obj: dict) -> bool:
    if not all(k in obj for k in REQUIRED_KEYS):
        return False
    cities = obj.get("recommended_cities")
    return (
        isinstance(cities, list)
        and len(cities) >= 1
        and all(isinstance(city, str) and city.strip() for city in cities)
        and isinstance(obj.get("weather"), str)
        and isinstance(obj.get("events"), list)
        and all(isinstance(event, str) for event in obj["events"])
        and isinstance(obj.get("reason"), str)
    )


def _prompt_recommendation(date: str) -> str:
    return f"""당신은 국내 여행 추천 전문가입니다.
여행 날짜: {date}
이 시기에 여행하기 좋은 국내 도시 2~3곳을 추천하고 아래 JSON만 출력하세요.

{{
  "recommended_cities": ["제주", "강릉"],
  "weather": "해당 시기 전반적 날씨 요약",
  "events": ["행사/축제 후보"],
  "reason": "추천 근거 2~4문장"
}}"""


def _prompt_recommendation_retry(date: str) -> str:
    return f"""여행 날짜 {date}에 대해 아래 4개 키만 가진 JSON 객체 하나만 출력하세요.
키: recommended_cities(array of string, 2~3개), weather(string), events(array of string), reason(string)
다른 텍스트와 코드펜스는 출력하지 마세요."""


def get_recommendation(date: str, errors: list) -> dict:
    """추천 JSON을 생성한다. 파싱/스키마 실패 시 1회 재시도한다."""
    try:
        raw = _call_llm(_prompt_recommendation(date), json_mode=True)
        obj = _normalize(_extract_json(raw))
        if _has_required_keys(obj):
            return obj
        raise ValueError("필수 키 또는 값 형식 오류")
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        E.add_error(errors, "llm_recommend", E.LLM_PARSE_ERROR, f"1차 파싱 실패: {exc}")

    raw = _call_llm(_prompt_recommendation_retry(date), json_mode=True)
    obj = _normalize(_extract_json(raw))
    if not _has_required_keys(obj):
        raise RuntimeError("LLM 1차 추천 JSON 파싱 재시도 실패")
    return obj


def _prompt_report(date: str, recommendation: dict, restaurants_by_city: dict) -> str:
    return f"""아래 데이터를 바탕으로 한국어 여행 리포트를 Markdown으로 작성하세요.
반드시 다음 섹션을 포함하세요: 추천 지역, 추천 이유, 날씨 요약, 행사/축제, 맛집 추천, 1일 일정 제안.
맛집은 지역별로 정리하고 검색 결과가 0건이면 '데이터 없음 (장소 검색 결과 0건)'으로 표기하세요.

날짜: {date}
추천 JSON:
{json.dumps(recommendation, ensure_ascii=False, indent=2)}

지역별 맛집:
{json.dumps(restaurants_by_city, ensure_ascii=False, indent=2)}
"""


def generate_report_body(date: str, recommendation: dict, restaurants_by_city: dict) -> str:
    """Gemini의 일반 텍스트 모드로 Markdown 본문을 생성한다."""
    return _call_llm(
        _prompt_report(date, recommendation, restaurants_by_city),
        json_mode=False,
    )
