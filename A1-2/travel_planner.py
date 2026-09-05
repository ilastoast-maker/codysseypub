"""Travel Planner CLI: Gemini 추천 + Kakao 장소 검색 + Markdown 리포트."""

import argparse
import json
import os
from datetime import datetime

from dotenv import load_dotenv

import llm_client
import place_client
import report as report_mod

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
API_ENV_FILE = os.path.join(BASE_DIR, "API.env")
FALLBACK_ENV_FILE = os.path.join(BASE_DIR, ".env")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="국내 여행 추천 프로그램 (LLM + 지도 API)")
    parser.add_argument("--date", required=True, help="여행 날짜 (형식: YYYY-MM-DD)")
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="같은 날짜의 캐시가 있어도 API를 다시 호출한다",
    )
    return parser.parse_args()


def validate_date(date_str: str) -> str:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        print('날짜 형식 오류. 사용법: --date "YYYY-MM-DD"')
        raise SystemExit(1)


def load_env() -> None:
    """API.env를 최우선으로 로드하고 없으면 .env를 사용한다."""
    if os.path.exists(API_ENV_FILE):
        load_dotenv(API_ENV_FILE, override=True)
    elif os.path.exists(FALLBACK_ENV_FILE):
        load_dotenv(FALLBACK_ENV_FILE, override=True)


def require_keys(*keys: str) -> None:
    missing = [key for key in keys if not os.getenv(key)]
    if not missing:
        return
    print(f"[오류] API 키 미설정: {', '.join(missing)}")
    print("프로젝트 폴더의 API.env에 필요한 키를 입력하세요.")
    raise SystemExit(1)


def raw_json_path(date: str) -> str:
    return os.path.join(RESULTS_DIR, f"{date}_raw.json")


def report_path(date: str) -> str:
    return os.path.join(RESULTS_DIR, f"{date}_travel_plan.md")


def save_raw(date: str, rec: dict, restaurants_by_city: dict, errors: list) -> str:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = raw_json_path(date)
    data = {
        "date": date,
        "recommendation": rec,
        "restaurants_by_city": restaurants_by_city,
        "errors": errors,
    }
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    return path


def load_cache(date: str):
    """정상 캐시만 반환한다. 손상 캐시는 경고 후 무시한다."""
    path = raw_json_path(date)
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
        rec = data["recommendation"]
        restaurants = data.get("restaurants_by_city", {})
        errors = data.get("errors", [])
        if not isinstance(rec, dict) or not isinstance(restaurants, dict) or not isinstance(errors, list):
            raise ValueError("캐시 스키마 오류")
        if not isinstance(rec.get("recommended_cities"), list):
            raise ValueError("recommended_cities 누락")
        return rec, restaurants, errors
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[캐시 경고] {path} 읽기 실패 → 새로 생성합니다. ({exc})")
        return None


def main() -> None:
    args = parse_args()
    date = validate_date(args.date)
    load_env()

    cache = None if args.no_cache else load_cache(date)
    if cache:
        rec, restaurants_by_city, errors = cache
        print(f"[캐시] {raw_json_path(date)} 사용 → 외부 API 호출 건너뜀")
        markdown = report_mod.build_report(
            date,
            rec,
            restaurants_by_city,
            errors,
            use_llm=False,
        )
        md_path = report_mod.save_report(date, markdown, RESULTS_DIR)
        print(f"완료! {md_path} 를 확인하세요.")
        return

    require_keys("GEMINI_API_KEY", "KAKAO_REST_API_KEY")
    errors: list = []

    print("[1/3] 1차 추천 생성 중(LLM)...")
    try:
        rec = llm_client.get_recommendation(date, errors)
    except Exception as exc:
        print(f"  - 오류: 1차 추천 생성 실패 → 종료 ({exc})")
        raise SystemExit(1)

    cities = rec["recommended_cities"]
    print(f"  - recommended_cities: {cities}")

    print("[2/3] 맛집 검색 중(지도/장소 API)...")
    restaurants_by_city = {}
    for city in cities:
        found = place_client.search_restaurants(city, errors, size=5)
        restaurants_by_city[city] = found
        if found:
            print(f"  - {city}: 맛집 {len(found)}곳 검색 완료")
        else:
            print(f"  - {city}: 맛집 0건 → '데이터 없음' 처리하고 계속 진행")

    save_raw(date, rec, restaurants_by_city, errors)

    print("[3/3] 최종 리포트 생성 중(LLM)...")
    markdown = report_mod.build_report(date, rec, restaurants_by_city, errors, use_llm=True)
    md_path = report_mod.save_report(date, markdown, RESULTS_DIR)
    save_raw(date, rec, restaurants_by_city, errors)
    print("  - 리포트 생성 완료")
    print(f"\n완료! {md_path} 를 확인하세요.")


if __name__ == "__main__":
    main()
