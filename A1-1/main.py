# -*- coding: utf-8 -*-
"""나만의 프롬프트 관리 (Prompt Manager)"""

import json
import os

CATEGORIES = ["텍스트 생성", "이미지 생성", "영상 생성", "페르소나", "자동화", "기타"]
DATA_FILE = "prompts.json"

prompts = [
    {"title": "블로그 글 작성 도우미", "content": "당신은 10년 경력의 전문 블로거입니다.\n주어진 주제에 대해 SEO에 최적화된 블로그 글을 작성해주세요.\n서론, 본론, 결론 구조를 갖추고,\n독자의 관심을 끄는 제목을 3개 제안해주세요.", "category": "텍스트 생성", "favorite": True, "views": 0},
    {"title": "제품 썸네일 생성", "content": "다음 제품의 매력적인 썸네일 이미지를 생성해주세요.\n밝은 조명, 깔끔한 배경, 제품이 중앙에 배치된 구도.\n고해상도, 상업 사진 스타일로 표현해주세요.", "category": "이미지 생성", "favorite": False, "views": 0},
    {"title": "제품 홍보 숏폼 영상", "content": "다음 제품을 소개하는 30초 숏폼 영상 구성안을 작성해주세요.\n첫 3초 안에 시선을 끄는 훅을 넣고, 제품의 핵심 장점 3개를 보여주세요.\n장면별 화면 구성과 자막을 제안하고, 마지막에는 명확한 CTA를 포함해주세요.", "category": "영상 생성", "favorite": False, "views": 0},
    {"title": "IT 컨설턴트 페르소나", "content": "당신은 15년 경력의 IT 전략 컨설턴트입니다.\n기업의 디지털 전환에 대해 실용적이고 근거 있는 조언을 제공합니다.\n전문 용어는 쉽게 풀어 설명하고, 항상 실행 가능한 다음 단계를 제안합니다.", "category": "페르소나", "favorite": False, "views": 0},
    {"title": "뉴스 요약 프롬프트", "content": "다음 뉴스 기사를 3문장으로 요약해주세요.\n핵심 사실 위주로 정리하고, 마지막에 한 줄 시사점을 추가해주세요.", "category": "자동화", "favorite": False, "views": 0},
    {"title": "아이디어 브레인스토밍", "content": "다음 주제에 대해 실현 가능한 아이디어를 10개 제안해주세요.\n각 아이디어마다 한 줄 설명을 붙이고, 장점과 주의할 점을 간단히 정리해주세요.", "category": "기타", "favorite": False, "views": 0},
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
        "1. 프롬프트 추가", "2. 프롬프트 목록", "3. 카테고리별 조회",
        "4. 프롬프트 검색", "5. 프롬프트 상세 보기", "6. 즐겨찾기 관리",
        "7. 즐겨찾기 목록", "-- 보너스 --", "8. 프롬프트 수정",
        "9. 프롬프트 삭제", "10. 인기 프롬프트(조회수 Top)",
        "11. JSON으로 저장", "12. JSON에서 불러오기",
        "13. 카테고리별 Markdown 내보내기", "0. 종료",
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
        return CATEGORIES[num - 1] if 1 <= num <= len(CATEGORIES) else "기타"
    return choice or "기타"


def get_index(message):
    choice = input(message).strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(prompts):
        print("⚠️ 잘못된 번호입니다.")
        return None
    return int(choice) - 1


def add_prompt():
    prompts.append({"title": input_nonempty("제목: "), "content": input_nonempty("내용: "), "category": select_category(), "favorite": False, "views": 0})
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
    found = [p for p in prompts if p["category"] == category]
    print(f"\n[{category}] 카테고리 프롬프트:")
    if not found:
        print("해당 카테고리에 프롬프트가 없습니다.")
        return
    for i, prompt in enumerate(found, 1):
        print(f"{i}. {prompt['title']}{star(prompt['favorite'])}")


def search_prompt():
    keyword = input("검색어: ").strip().lower()
    results = [p for p in prompts if keyword in p["title"].lower() or keyword in p["content"].lower()] if keyword else []
    if not results:
        print("검색 결과가 없습니다.")
        return
    for i, prompt in enumerate(results, 1):
        print_prompt_line(i, prompt)


def show_detail():
    idx = get_index("번호 입력: ")
    if idx is None:
        return
    prompt = prompts[idx]
    prompt["views"] += 1
    print(f"\n제목: {prompt['title']}\n카테고리: {prompt['category']}\n즐겨찾기: {'⭐' if prompt['favorite'] else '없음'}\n조회수: {prompt['views']}\n내용:\n{prompt['content']}")


def toggle_favorite():
    idx = get_index("프롬프트 번호 입력: ")
    if idx is None:
        return
    prompts[idx]["favorite"] = not prompts[idx]["favorite"]
    print("✅ 즐겨찾기 상태를 변경했습니다.")


def show_favorites():
    favorites = [p for p in prompts if p["favorite"]]
    if not favorites:
        print("즐겨찾기된 프롬프트가 없습니다.")
        return
    for i, prompt in enumerate(favorites, 1):
        print_prompt_line(i, prompt)


def edit_prompt():
    idx = get_index("수정할 번호 입력: ")
    if idx is None:
        return
    prompt = prompts[idx]
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
    idx = get_index("삭제할 번호 입력: ")
    if idx is not None and input(f"'{prompts[idx]['title']}'을(를) 삭제할까요? (y/N): ").strip().lower() == "y":
        removed = prompts.pop(idx)
        print(f"🗑️ '{removed['title']}' 프롬프트를 삭제했습니다.")


def show_top_viewed():
    for i, prompt in enumerate(sorted(prompts, key=lambda p: p["views"], reverse=True)[:5], 1):
        print(f"{i}. [{prompt['category']}] {prompt['title']} (조회수 {prompt['views']}){star(prompt['favorite'])}")


def save_to_json():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
        print(f"✅ '{DATA_FILE}' 파일로 {len(prompts)}개를 저장했습니다.")
    except OSError as e:
        print(f"⚠️ 저장 오류: {e}")


def load_from_json():
    if not os.path.exists(DATA_FILE):
        print(f"⚠️ '{DATA_FILE}' 파일이 없습니다.")
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        prompts.clear()
        for item in loaded:
            item.setdefault("views", 0)
            item.setdefault("favorite", False)
            prompts.append(item)
        print(f"✅ '{DATA_FILE}'에서 {len(prompts)}개를 불러왔습니다.")
    except (OSError, json.JSONDecodeError) as e:
        print(f"⚠️ 불러오기 오류: {e}")


def export_markdown():
    lines = ["# 나만의 프롬프트 모음\n"]
    for category in CATEGORIES:
        items = [p for p in prompts if p["category"] == category]
        if items:
            lines.append(f"\n## {category}\n")
            for p in items:
                lines.append(f"### {p['title']}{star(p['favorite'])}\n")
                lines.append(f"```\n{p['content']}\n```\n")
    try:
        with open("prompts_export.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print("✅ 'prompts_export.md' 파일로 내보냈습니다.")
    except OSError as e:
        print(f"⚠️ 내보내기 오류: {e}")


def main():
    actions = {
        "1": add_prompt, "2": show_list, "3": show_by_category, "4": search_prompt,
        "5": show_detail, "6": toggle_favorite, "7": show_favorites, "8": edit_prompt,
        "9": delete_prompt, "10": show_top_viewed, "11": save_to_json,
        "12": load_from_json, "13": export_markdown,
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
