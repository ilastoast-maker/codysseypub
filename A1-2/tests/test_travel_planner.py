import argparse
import copy
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import errors as E
import llm_client
import place_client
import report
import travel_planner


class TravelPlannerTests(unittest.TestCase):
    def setUp(self):
        self.env_backup = {k: os.environ.get(k) for k in ("GEMINI_API_KEY", "KAKAO_REST_API_KEY")}

    def tearDown(self):
        for key, value in self.env_backup.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_01_validate_date(self):
        self.assertEqual(travel_planner.validate_date("2026-09-20"), "2026-09-20")
        with self.assertRaises(SystemExit):
            travel_planner.validate_date("2026-02-30")

    def test_02_api_env_has_priority(self):
        with tempfile.TemporaryDirectory() as tmp:
            api_env = os.path.join(tmp, "API.env")
            fallback = os.path.join(tmp, ".env")
            with open(api_env, "w", encoding="utf-8") as f:
                f.write("GEMINI_API_KEY=file-gemini\nKAKAO_REST_API_KEY=file-kakao\n")
            with open(fallback, "w", encoding="utf-8") as f:
                f.write("GEMINI_API_KEY=fallback\nKAKAO_REST_API_KEY=fallback\n")
            os.environ["GEMINI_API_KEY"] = "shell-gemini"
            os.environ["KAKAO_REST_API_KEY"] = "shell-kakao"
            with patch.object(travel_planner, "API_ENV_FILE", api_env), patch.object(travel_planner, "FALLBACK_ENV_FILE", fallback):
                travel_planner.load_env()
            self.assertEqual(os.getenv("GEMINI_API_KEY"), "file-gemini")
            self.assertEqual(os.getenv("KAKAO_REST_API_KEY"), "file-kakao")

    def test_03_require_keys(self):
        os.environ.pop("GEMINI_API_KEY", None)
        with self.assertRaises(SystemExit):
            travel_planner.require_keys("GEMINI_API_KEY")
        os.environ["GEMINI_API_KEY"] = "x"
        travel_planner.require_keys("GEMINI_API_KEY")

    def test_04_save_and_load_cache(self):
        rec = {"recommended_cities": ["제주"], "weather": "맑음", "events": [], "reason": "좋음"}
        rests = {"제주": []}
        with tempfile.TemporaryDirectory() as tmp, patch.object(travel_planner, "RESULTS_DIR", tmp):
            travel_planner.save_raw("2026-09-20", rec, rests, [])
            loaded = travel_planner.load_cache("2026-09-20")
            self.assertEqual(loaded, (rec, rests, []))

    def test_05_corrupt_cache_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(travel_planner, "RESULTS_DIR", tmp):
            path = travel_planner.raw_json_path("2026-09-20")
            with open(path, "w", encoding="utf-8") as f:
                f.write("{broken")
            self.assertIsNone(travel_planner.load_cache("2026-09-20"))

    def test_06_llm_json_mode_only_for_recommendation(self):
        os.environ["GEMINI_API_KEY"] = "dummy"
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"candidates": [{"content": {"parts": [{"text": "{}"}]}}]}
        with patch("llm_client.requests.post", return_value=response) as post:
            llm_client._call_llm("x", json_mode=True)
            payload = post.call_args.kwargs["json"]
            self.assertEqual(payload["generationConfig"]["responseMimeType"], "application/json")
        with patch("llm_client.requests.post", return_value=response) as post:
            llm_client._call_llm("x", json_mode=False)
            payload = post.call_args.kwargs["json"]
            self.assertNotIn("generationConfig", payload)

    def test_07_normalize_single_city_and_deduplicate(self):
        obj = llm_client._normalize({"recommended_city": " 제주 "})
        self.assertEqual(obj["recommended_cities"], ["제주"])
        obj2 = llm_client._normalize({"recommended_cities": ["제주", " 제주 ", "", 123]})
        self.assertEqual(obj2["recommended_cities"], ["제주"])

    def test_08_schema_validation(self):
        valid = {"recommended_cities": ["제주"], "weather": "맑음", "events": ["축제"], "reason": "좋음"}
        self.assertTrue(llm_client._has_required_keys(valid))
        invalid = copy.deepcopy(valid)
        invalid["events"] = "축제"
        self.assertFalse(llm_client._has_required_keys(invalid))

    def test_09_recommendation_retries_once(self):
        errors = []
        good = json.dumps({"recommended_cities": ["제주", "강릉"], "weather": "맑음", "events": [], "reason": "좋음"}, ensure_ascii=False)
        with patch("llm_client._call_llm", side_effect=["not-json", good]) as call:
            rec = llm_client.get_recommendation("2026-09-20", errors)
        self.assertEqual(call.call_count, 2)
        self.assertEqual(rec["recommended_cities"], ["제주", "강릉"])
        self.assertEqual(errors[0]["type"], E.LLM_PARSE_ERROR)

    def test_10_place_missing_key(self):
        os.environ.pop("KAKAO_REST_API_KEY", None)
        errors = []
        self.assertEqual(place_client.search_restaurants("제주", errors), [])
        self.assertEqual(errors[0]["type"], E.AUTH_ERROR)

    def test_11_place_403_preserves_kakao_detail(self):
        os.environ["KAKAO_REST_API_KEY"] = "dummy"
        resp = Mock(status_code=403)
        resp.json.return_value = {"code": -3, "msg": "API not enabled"}
        errors = []
        with patch("place_client.requests.get", return_value=resp):
            result = place_client.search_restaurants("제주", errors)
        self.assertEqual(result, [])
        self.assertIn("code=-3", errors[0]["message"])
        self.assertIn("API not enabled", errors[0]["message"])

    def test_12_place_invalid_size(self):
        os.environ["KAKAO_REST_API_KEY"] = "dummy"
        errors = []
        self.assertEqual(place_client.search_restaurants("제주", errors, size=16), [])
        self.assertEqual(errors[0]["type"], E.REQUEST_ERROR)

    def test_13_place_success_mapping(self):
        os.environ["KAKAO_REST_API_KEY"] = "dummy"
        resp = Mock(status_code=200)
        resp.json.return_value = {"documents": [{"place_name": "식당", "road_address_name": "주소", "category_name": "음식점", "place_url": "https://x", "x": "127.1", "y": "37.5"}]}
        errors = []
        with patch("place_client.requests.get", return_value=resp):
            result = place_client.search_restaurants("서울", errors)
        self.assertEqual(result[0]["name"], "식당")
        self.assertEqual(result[0]["x"], 127.1)
        self.assertEqual(errors, [])

    def test_14_place_bad_json_is_recorded(self):
        os.environ["KAKAO_REST_API_KEY"] = "dummy"
        resp = Mock(status_code=200)
        resp.json.side_effect = ValueError("bad json")
        errors = []
        with patch("place_client.requests.get", return_value=resp):
            self.assertEqual(place_client.search_restaurants("서울", errors), [])
        self.assertEqual(errors[0]["type"], E.RESPONSE_ERROR)

    def test_15_report_fallback_on_llm_error(self):
        rec = {"recommended_cities": ["제주"], "weather": "맑음", "events": [], "reason": "좋음"}
        errors = []
        with patch("report.llm_client.generate_report_body", side_effect=RuntimeError("down")):
            markdown = report.build_report("2026-09-20", rec, {"제주": []}, errors)
        self.assertIn("# 2026-09-20", markdown)
        self.assertEqual(errors[0]["type"], E.LLM_REPORT_ERROR)

    def test_16_cached_report_never_calls_llm(self):
        rec = {"recommended_cities": ["제주"], "weather": "맑음", "events": [], "reason": "좋음"}
        errors = []
        with patch("report.llm_client.generate_report_body") as mocked:
            markdown = report.build_report("2026-09-20", rec, {"제주": []}, errors, use_llm=False)
        mocked.assert_not_called()
        self.assertIn("데이터 없음", markdown)

    def test_17_main_cache_hit_skips_all_external_clients(self):
        rec = {"recommended_cities": ["제주"], "weather": "맑음", "events": [], "reason": "좋음"}
        cache = (rec, {"제주": []}, [])
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(travel_planner, "RESULTS_DIR", tmp), \
             patch.object(travel_planner, "parse_args", return_value=argparse.Namespace(date="2026-09-20", no_cache=False)), \
             patch.object(travel_planner, "load_env"), \
             patch.object(travel_planner, "load_cache", return_value=cache), \
             patch.object(travel_planner, "require_keys") as require, \
             patch.object(travel_planner.llm_client, "get_recommendation") as recommend, \
             patch.object(travel_planner.place_client, "search_restaurants") as places:
            travel_planner.main()
        require.assert_not_called()
        recommend.assert_not_called()
        places.assert_not_called()

    def test_18_main_no_cache_runs_pipeline(self):
        rec = {"recommended_cities": ["제주", "강릉"], "weather": "맑음", "events": [], "reason": "좋음"}
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(travel_planner, "RESULTS_DIR", tmp), \
             patch.object(travel_planner, "parse_args", return_value=argparse.Namespace(date="2026-09-20", no_cache=True)), \
             patch.object(travel_planner, "load_env"), \
             patch.object(travel_planner, "require_keys"), \
             patch.object(travel_planner.llm_client, "get_recommendation", return_value=rec), \
             patch.object(travel_planner.place_client, "search_restaurants", return_value=[] ) as places, \
             patch.object(travel_planner.report_mod, "build_report", return_value="# report"):
            travel_planner.main()
            self.assertTrue(os.path.exists(os.path.join(tmp, "2026-09-20_raw.json")))
            self.assertTrue(os.path.exists(os.path.join(tmp, "2026-09-20_travel_plan.md")))
        self.assertEqual(places.call_count, 2)


if __name__ == "__main__":
    unittest.main()
