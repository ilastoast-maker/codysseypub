# -*- coding: utf-8 -*-
"""나만의 프롬프트 관리 (Prompt Manager).

Python 기본 문법을 중심으로 프롬프트 추가/조회/검색/즐겨찾기/수정/삭제와
JSON 저장·불러오기, 조회수 정렬, Markdown 내보내기를 제공한다.
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "prompts.json")
EXPORT_FILE = os.path.join(BASE_DIR, "prompts_export.md")

CATEGORIES = ["텍스트 생성", "이미지 생성", "영상 생성", "페르소나", "자동화", "기타"]

prompts = [
    {
        "title": "블로그 글 작성 도우미",
        "content": (
            "당신은 10년 경력의 전문 블로거입니다.\n"
            "주어진 주제에 대해 SEO에 최적화된 블로그 글을 작성해주세요.\n"
            "서론, 본론, 결론 구조를 갖추고,\n"
            "독자의 관심을 끄는 제목을 3개 제안해주세요."
        ),
        "category": "텍스트 생성",
        "favorite": True,
        "views": 0,
    },
    {
        "title": "제품 썸네일 생성",
        "content": (
            "다음 제품의 매력적인 썸네일 이미지를 생성해주세요.\n"
            "밝은 조명, 깔끔한 배경, 제품이 중앙에 배치된 구도.\n"
            "고해상도, 상업 사진 스타일로 표현해주세요."
        ),
        "category": "이미지 생성",
        "favorite": False,
        "views": 0,
    },
    {
        "title": "제품 홍보 숏폼 영상",
        "content": (
            "다음 제품을 소개하는 30초 숏폼 영상 구성안을 작성해주세요.\n"
            "첫 3초 안에 시선을 끄는 훅을 넣고, 제품의 핵심 장점 3개를 보여주세요.\n"
            "장면별 화면 구성과 자막을 제안하고, 마지막에는 명확한 CTA를 포함해주세요."
        ),
        "category": "영상 생성",
        "favorite": False,
        "views": 0,
    },
    {
        "title": "IT 컨설턴트 페르소나",
        "content": (
            "당신은 15년 경력의 IT 전략 컨설턴트입니다.\n"
            "기업의 디지털 전환에 대해 실용적이고 근거 있는 조언을 제공합니다.\n"
            "전문 용어는 쉽게 풀어 설명하고, 항상 실행 가능한 다음 단계를 제안합니다."
        ),
        "category": "페르소나",
        "favorite": False,
        "views": 0,
    },
    {
        "title": "뉴스 요약 프롬프트",
        "content": (
            "다음 뉴스 기사를 3문장으로 요약해주세요.\n"
            "핵심 사실 위주로 정리하고, 마지막에 한 줄 시사점을 추가해주세요."
        ),
        "category": "자동화",
        "favorite": False,
        "views": 0,
    },
    {
        "title": "아이디어 브레인스토밍",
        "content": (
            "다음 주제에 대해 실현 가능한 아이디어를 10개 제안해주세요.\n"
            "각 아이디어마다 한 줄 설명을 붙이고, 장점과 주의할 점을 간단히 정리해주세요."
        ),
        "category": "기타",
        "favorite": False,
        "views": 0,
    },
]


def star(favorite):
    return " ⭐" if favorite else ""


def print_prompt_line(index, prompt):
    print(f"{index}. [{prompt['category']}] {prompt['title']}{star(prompt['favorite'])}")


def print_category_menu():
    for i, category in enumerate(CATEGORIES, 1):
        print(f"{i}) {category}")


def show_menu():
    print("\n=== 나만의 프롬프트 관리 ===")
    for line in [
        "1. 프롬프트 추가",
        "2. 프롬프트 목록",
        "3. 카테고리별 조회",
        "4. 프롬프트 검색",
        "5. 프롬프트 상세 보기",
        "6. 즐겨찾기 관리",
        "7. 즐겨찾기 목록",
        "-- 보너스 --",
        "8. 프롬프트 수정",
        "9. 프롬프트 삭제",
        "10. 인기 프롬프트(조회수 Top)",
        "11. JSON으로 저장",
        "12. JSON에서 불러오기",
        "13. 카테고리별 Markdown 내보내기",
        "0. 종료",
    ]:
        print(line)


def input_nonempty(message):
    while True:
        value = input(message).strip()
        if value:
            return value
        print("⚠️ 값을 입력해주세요.")


def select_category():
    print("\n카테고리 선택:")
    print_category_menu()
    choice = input("선택(번호 또는 직접 입력): ").strip()
    if choice.isdigit():
        num = int(choice)
        if 1 <= num <= len(CATEGORIES):
            return CATEGORIES[num - 1]
        print("⚠️ 잘못된 번호입니다. '기타'로 저장합니다.")
        return "기타"
    return choice or "기타"


def get_index(message):
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return None
    choice = input(message).strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(prompts):
        print("⚠️ 잘못된 번호입니다.")
        return None
    return int(choice) - 1


def show_indexed_subset(predicate, empty_message):
    """필터 결과에서도 전체 prompts의 원래 번호를 유지해 출력한다."""
    count = 0
    for i, prompt in enumerate(prompts, 1):
        if predicate(prompt):
            print_prompt_line(i, prompt)
            count += 1
    if count == 0:
        print(empty_message)
    return count


def add_prompt():
    print("\n=== 프롬프트 추가 ===")
    title = input_nonempty("제목: ")
    content = input_nonempty("내용: ")
    category = select_category()
    prompts.append(
        {
            "title": title,
            "content": content,
            "category": category,
            "favorite": False,
            "views": 0,
        }
    )
    print("✅ 프롬프트가 추가되었습니다!")


def show_list():
    print("\n=== 프롬프트 목록 ===")
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return
    for i, prompt in enumerate(prompts, 1):
        print_prompt_line(i, prompt)
    print(f"\n총 {len(prompts)}개의 프롬프트")


def show_by_category():
    print("\n=== 카테고리별 조회 ===")
    print_category_menu()
    choice = input("선택: ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(CATEGORIES):
        print("⚠️ 잘못된 번호입니다.")
        return
    category = CATEGORIES[int(choice) - 1]
    print(f"\n[{category}] 카테고리 프롬프트:")
    count = show_indexed_subset(
        lambda p: p["category"] == category,
        "해당 카테고리에 프롬프트가 없습니다.",
    )
    if count:
        print(f"\n총 {count}개의 프롬프트")


def search_prompt():
    print("\n=== 프롬프트 검색 ===")
    keyword = input("검색어: ").strip()
    if not keyword:
        print("⚠️ 검색어를 입력해주세요.")
        return
    lowered = keyword.lower()
    print("\n검색 결과:")
    count = show_indexed_subset(
        lambda p: lowered in p["title"].lower() or lowered in p["content"].lower(),
        "검색 결과가 없습니다.",
    )
    if count:
        print(f"\n{count}개의 프롬프트를 찾았습니다.")


def show_detail():
    print("\n=== 프롬프트 상세 보기 ===")
    show_list()
    if not prompts:
        return
    idx = get_index("번호 입력: ")
    if idx is None:
        return
    prompt = prompts[idx]
    prompt["views"] += 1
    line = "─" * 28
    print("\n" + line)
    print(f"제목: {prompt['title']}")
    print(f"카테고리: {prompt['category']}")
    print(f"즐겨찾기: {'⭐' if prompt['favorite'] else '없음'}")
    print(f"조회수: {prompt['views']}")
    print(line)
    print("내용:")
    print(prompt["content"])
    print(line)


def toggle_favorite():
    print("\n=== 즐겨찾기 관리 ===")
    show_list()
    if not prompts:
        return
    idx = get_index("즐겨찾기를 변경할 프롬프트 번호 입력: ")
    if idx is None:
        return
    prompt = prompts[idx]
    prompt["favorite"] = not prompt["favorite"]
    if prompt["favorite"]:
        print(f"✅ '{prompt['title']}'을(를) 즐겨찾기에 추가했습니다.")
    else:
        print(f"✅ '{prompt['title']}'을(를) 즐겨찾기에서 해제했습니다.")


def show_favorites():
    print("\n=== 즐겨찾기 목록 ===")
    count = show_indexed_subset(
        lambda p: p["favorite"],
        "즐겨찾기된 프롬프트가 없습니다.",
    )
    if count:
        print(f"\n총 {count}개의 즐겨찾기")


def edit_prompt():
    print("\n=== 프롬프트 수정 ===")
    show_list()
    if not prompts:
        return
    idx = get_index("수정할 번호 입력: ")
    if idx is None:
        return
    prompt = prompts[idx]
    print("(엔터만 누르면 기존 값을 유지합니다)")
    title = input(f"제목 [{prompt['title']}]: ").strip()
    content = input("내용(유지하려면 엔터): ").strip()
    if title:
        prompt["title"] = title
    if content:
        prompt["content"] = content
    if input("카테고리를 변경하시겠습니까? (y/N): ").strip().lower() == "y":
        prompt["category"] = select_category()
    print("✅ 프롬프트가 수정되었습니다!")


def delete_prompt():
    print("\n=== 프롬프트 삭제 ===")
    show_list()
    if not prompts:
        return
    idx = get_index("삭제할 번호 입력: ")
    if idx is None:
        return
    confirm = input(f"'{prompts[idx]['title']}'을(를) 삭제할까요? (y/N): ").strip().lower()
    if confirm == "y":
        removed = prompts.pop(idx)
        print(f"🗑️ '{removed['title']}' 프롬프트를 삭제했습니다.")
    else:
        print("삭제를 취소했습니다.")


def show_top_viewed():
    print("\n=== 인기 프롬프트 (조회수 Top) ===")
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return
    indexed = list(enumerate(prompts, 1))
    ranked = sorted(indexed, key=lambda item: item[1]["views"], reverse=True)[:5]
    for rank, (original_index, prompt) in enumerate(ranked, 1):
        print(
            f"{rank}위 (원본 {original_index}번) [{prompt['category']}] "
            f"{prompt['title']} (조회수 {prompt['views']}){star(prompt['favorite'])}"
        )


def _normalize_loaded_prompt(item):
    """JSON 항목을 검증하고 누락된 선택 필드를 기본값으로 보정한다."""
    if not isinstance(item, dict):
        raise ValueError("프롬프트 항목은 객체(dict)여야 합니다.")
    if not isinstance(item.get("title"), str) or not item["title"].strip():
        raise ValueError("title이 비어 있거나 문자열이 아닙니다.")
    if not isinstance(item.get("content"), str) or not item["content"].strip():
        raise ValueError("content가 비어 있거나 문자열이 아닙니다.")
    if not isinstance(item.get("category"), str) or not item["category"].strip():
        raise ValueError("category가 비어 있거나 문자열이 아닙니다.")

    normalized = dict(item)
    normalized["favorite"] = bool(item.get("favorite", False))
    views = item.get("views", 0)
    normalized["views"] = views if isinstance(views, int) and views >= 0 else 0
    return normalized


def save_to_json():
    print("\n=== JSON으로 저장 ===")
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
        print(f"✅ '{os.path.basename(DATA_FILE)}' 파일로 {len(prompts)}개를 저장했습니다.")
    except OSError as e:
        print(f"⚠️ 저장 오류: {e}")


def load_from_json():
    print("\n=== JSON에서 불러오기 ===")
    if not os.path.exists(DATA_FILE):
        print(f"⚠️ '{os.path.basename(DATA_FILE)}' 파일이 없습니다.")
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        if not isinstance(loaded, list):
            raise ValueError("최상위 JSON 구조는 배열(list)이어야 합니다.")
        normalized = [_normalize_loaded_prompt(item) for item in loaded]
    except (OSError, json.JSONDecodeError, ValueError) as e:
        print(f"⚠️ 불러오기 오류: {e}")
        return

    prompts.clear()
    prompts.extend(normalized)
    print(f"✅ '{os.path.basename(DATA_FILE)}'에서 {len(prompts)}개를 불러왔습니다.")


def export_markdown():
    print("\n=== 카테고리별 Markdown 내보내기 ===")
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return

    categories = list(CATEGORIES)
    for prompt in prompts:
        if prompt["category"] not in categories:
            categories.append(prompt["category"])

    lines = ["# 나만의 프롬프트 모음\n"]
    for category in categories:
        items = [p for p in prompts if p["category"] == category]
        if not items:
            continue
        lines.append(f"\n## {category}\n")
        for prompt in items:
            lines.append(f"### {prompt['title']}{star(prompt['favorite'])}\n")
            lines.append(f"```\n{prompt['content']}\n```\n")

    try:
        with open(EXPORT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"✅ '{os.path.basename(EXPORT_FILE)}' 파일로 내보냈습니다.")
    except OSError as e:
        print(f"⚠️ 내보내기 오류: {e}")


def main():
    actions = {
        "1": add_prompt,
        "2": show_list,
        "3": show_by_category,
        "4": search_prompt,
        "5": show_detail,
        "6": toggle_favorite,
        "7": show_favorites,
        "8": edit_prompt,
        "9": delete_prompt,
        "10": show_top_viewed,
        "11": save_to_json,
        "12": load_from_json,
        "13": export_markdown,
    }
    while True:
        show_menu()
        choice = input("선택: ").strip()
        if choice == "0":
            print("\n프로그램을 종료합니다. 안녕히 가세요! 👋")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("⚠️ 잘못된 번호입니다. 다시 선택해주세요.")


if __name__ == "__main__":
    main()
