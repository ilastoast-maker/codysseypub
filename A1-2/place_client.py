"""Kakao Local 장소 검색 클라이언트."""

import os

import requests

import errors as E

KAKAO_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"


def _map_item(doc: dict) -> dict:
    def to_float(value):
        try:
            return float(value) if value not in (None, "") else None
        except (TypeError, ValueError):
            return None

    return {
        "name": doc.get("place_name", ""),
        "address": doc.get("road_address_name") or doc.get("address_name", ""),
        "category": doc.get("category_name", ""),
        "url": doc.get("place_url", ""),
        "x": to_float(doc.get("x")),
        "y": to_float(doc.get("y")),
    }


def _error_detail(resp) -> str:
    """Kakao 오류 응답의 code/msg를 가능한 범위에서 보존한다."""
    try:
        body = resp.json()
    except (ValueError, requests.RequestException):
        text = (getattr(resp, "text", "") or "").strip()
        return text[:300] if text else "응답 본문 없음"

    if isinstance(body, dict):
        code = body.get("code")
        msg = body.get("msg") or body.get("message")
        parts = []
        if code is not None:
            parts.append(f"code={code}")
        if msg:
            parts.append(f"msg={msg}")
        if parts:
            return " / ".join(parts)
    return str(body)[:300]


def search_restaurants(city: str, errors: list, size: int = 5) -> list:
    """도시명으로 맛집을 검색한다. 오류는 기록하고 빈 리스트를 반환한다."""
    api_key = os.getenv("KAKAO_REST_API_KEY")
    if not api_key:
        E.add_error(errors, "place_search", E.AUTH_ERROR, "KAKAO_REST_API_KEY 미설정")
        return []

    if not isinstance(size, int) or not 1 <= size <= 15:
        E.add_error(errors, "place_search", E.REQUEST_ERROR, "size는 1~15 정수여야 함")
        return []

    city = str(city).strip()
    if not city:
        E.add_error(errors, "place_search", E.REQUEST_ERROR, "검색 도시명이 비어 있음")
        return []

    query = f"{city} 맛집"
    try:
        resp = requests.get(
            KAKAO_URL,
            headers={"Authorization": f"KakaoAK {api_key}"},
            params={"query": query, "size": size},
            timeout=15,
        )
    except requests.RequestException as exc:
        E.add_error(errors, "place_search", E.NETWORK_ERROR, str(exc))
        return []

    detail = _error_detail(resp) if resp.status_code != 200 else ""
    if resp.status_code in (401, 403):
        E.add_error(errors, "place_search", E.AUTH_ERROR, f"HTTP {resp.status_code} / {detail}")
        return []
    if resp.status_code == 429:
        E.add_error(errors, "place_search", E.QUOTA_ERROR, f"HTTP 429 / {detail}")
        return []
    if resp.status_code != 200:
        E.add_error(errors, "place_search", E.HTTP_ERROR, f"HTTP {resp.status_code} / {detail}")
        return []

    try:
        body = resp.json()
    except ValueError as exc:
        E.add_error(errors, "place_search", E.RESPONSE_ERROR, f"JSON 응답 파싱 실패: {exc}")
        return []

    docs = body.get("documents", []) if isinstance(body, dict) else []
    if not docs:
        E.add_error(errors, "place_search", E.EMPTY_RESULT, f"0 results for query={query}")
        return []

    return [_map_item(doc) for doc in docs if isinstance(doc, dict)]
