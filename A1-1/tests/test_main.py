import copy
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import main


class PromptManagerTests(unittest.TestCase):
    def setUp(self):
        self.original_prompts = copy.deepcopy(main.prompts)
        self.original_data_file = main.DATA_FILE
        self.original_export_file = main.EXPORT_FILE

    def tearDown(self):
        main.prompts[:] = copy.deepcopy(self.original_prompts)
        main.DATA_FILE = self.original_data_file
        main.EXPORT_FILE = self.original_export_file

    def capture(self, func, inputs=None):
        output = io.StringIO()
        values = inputs or []
        with patch("builtins.input", side_effect=values), redirect_stdout(output):
            func()
        return output.getvalue()

    def test_01_add_prompt(self):
        before = len(main.prompts)
        out = self.capture(main.add_prompt, ["새 프롬프트", "새 내용", "1"])
        self.assertEqual(len(main.prompts), before + 1)
        self.assertEqual(main.prompts[-1]["category"], "텍스트 생성")
        self.assertIn("추가되었습니다", out)

    def test_02_show_list(self):
        out = self.capture(main.show_list)
        self.assertIn("총 6개의 프롬프트", out)
        self.assertIn("1. [텍스트 생성]", out)
        self.assertIn("6. [기타]", out)

    def test_03_category_keeps_original_number(self):
        out = self.capture(main.show_by_category, ["4"])
        self.assertIn("4. [페르소나] IT 컨설턴트 페르소나", out)
        self.assertNotIn("1. [페르소나]", out)

    def test_04_search_keeps_original_number(self):
        out = self.capture(main.search_prompt, ["뉴스"])
        self.assertIn("5. [자동화] 뉴스 요약 프롬프트", out)

    def test_05_empty_search_is_rejected(self):
        out = self.capture(main.search_prompt, [""])
        self.assertIn("검색어를 입력해주세요", out)

    def test_06_detail_increments_views(self):
        self.assertEqual(main.prompts[2]["views"], 0)
        out = self.capture(main.show_detail, ["3"])
        self.assertEqual(main.prompts[2]["views"], 1)
        self.assertIn("조회수: 1", out)

    def test_07_toggle_favorite_targets_original_number(self):
        self.assertFalse(main.prompts[4]["favorite"])
        out = self.capture(main.toggle_favorite, ["5"])
        self.assertTrue(main.prompts[4]["favorite"])
        self.assertFalse(main.prompts[1]["favorite"])
        self.assertIn("뉴스 요약 프롬프트", out)

    def test_08_favorite_list_keeps_original_numbers(self):
        main.prompts[4]["favorite"] = True
        out = self.capture(main.show_favorites)
        self.assertIn("1. [텍스트 생성] 블로그 글 작성 도우미", out)
        self.assertIn("5. [자동화] 뉴스 요약 프롬프트", out)
        self.assertNotIn("2. [자동화] 뉴스 요약 프롬프트", out)

    def test_09_edit_prompt(self):
        out = self.capture(main.edit_prompt, ["2", "수정된 제목", "수정된 내용", "n"])
        self.assertEqual(main.prompts[1]["title"], "수정된 제목")
        self.assertEqual(main.prompts[1]["content"], "수정된 내용")
        self.assertIn("수정되었습니다", out)

    def test_10_delete_prompt_cancel_and_confirm(self):
        before = len(main.prompts)
        out_cancel = self.capture(main.delete_prompt, ["2", "n"])
        self.assertEqual(len(main.prompts), before)
        self.assertIn("취소", out_cancel)
        out_delete = self.capture(main.delete_prompt, ["2", "y"])
        self.assertEqual(len(main.prompts), before - 1)
        self.assertIn("삭제했습니다", out_delete)

    def test_11_top_viewed(self):
        main.prompts[4]["views"] = 9
        main.prompts[1]["views"] = 3
        out = self.capture(main.show_top_viewed)
        self.assertIn("1위 (원본 5번)", out)
        self.assertIn("조회수 9", out)

    def test_12_save_and_load_json(self):
        with tempfile.TemporaryDirectory() as tempdir:
            main.DATA_FILE = os.path.join(tempdir, "prompts.json")
            self.capture(main.save_to_json)
            main.prompts.clear()
            self.capture(main.load_from_json)
            self.assertEqual(len(main.prompts), 6)
            self.assertEqual(main.prompts[0]["title"], "블로그 글 작성 도우미")

    def test_13_invalid_json_does_not_destroy_current_data(self):
        with tempfile.TemporaryDirectory() as tempdir:
            main.DATA_FILE = os.path.join(tempdir, "prompts.json")
            with open(main.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({"not": "a list"}, f)
            before = copy.deepcopy(main.prompts)
            out = self.capture(main.load_from_json)
            self.assertEqual(main.prompts, before)
            self.assertIn("불러오기 오류", out)

    def test_14_export_markdown_includes_custom_category(self):
        main.prompts.append(
            {
                "title": "사용자 정의",
                "content": "사용자 정의 내용",
                "category": "연구",
                "favorite": False,
                "views": 0,
            }
        )
        with tempfile.TemporaryDirectory() as tempdir:
            main.EXPORT_FILE = os.path.join(tempdir, "prompts_export.md")
            self.capture(main.export_markdown)
            with open(main.EXPORT_FILE, encoding="utf-8") as f:
                exported = f.read()
            self.assertIn("## 연구", exported)
            self.assertIn("### 사용자 정의", exported)

    def test_15_main_dispatch_and_exit(self):
        out = self.capture(main.main, ["2", "0"])
        self.assertIn("프롬프트 목록", out)
        self.assertIn("프로그램을 종료합니다", out)


if __name__ == "__main__":
    unittest.main()
