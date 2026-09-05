# -*- coding: utf-8 -*-
"""
나만의 프롬프트 관리 (Prompt Manager)
- 필수 기능: Python 기본 문법(리스트, 딕셔너리, 조건문, 반복문, 함수)만 사용
- 보너스 기능: JSON 저장/불러오기, Markdown 내보내기, 수정/삭제(CRUD),
              조회수 기록, 조회수 Top 정렬
  (JSON/Markdown은 Python 표준 라이브러리 json만 사용 — 외부 라이브러리 없음)
"""

import json
import os

# =========================================================
# 전역 데이터
# =========================================================

# 미리 정의된 카테고리 목록
CATEGORIES = ["텍스트 생성", "이미지 생성", "영상 생성", "페르소나", "자동화", "기타"]

DATA_FILE = "prompts.json"   # 보너스1: 영속화 파일

# 이전 미션에서 작성한 기본 프롬프트 (3개 이상)
# views(조회수)는 보너스2 기능용 필드
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
]


# =========================================================
# 출력 보조 함수
# =========================================================

def star(favorite):
    """즐겨찾기 여부를 별표 문자열로 반환"""
    return " ⭐" if favorite else ""


def print_prompt_line(index, prompt):
    """목록용 한 줄 출력"""
    print(f"{index}. [{prompt['category']}] {prompt['title']}{star(prompt['favorite'])}")


def print_category_menu():
    """카테고리 선택 메뉴 출력"""
    for i, category in enumerate(CATEGORIES, start=1):
        print(f"{i}) {category}")


# =========================================================
# 메뉴
# =========================================================

def show_menu():
    print("\n=== 나만의 프롬프트 관리 ===")
    print("1. 프롬프트 추가")
    print("2. 프롬프트 목록")
    print("3. 카테고리별 조회")
    print("4. 프롬프트 검색")
    print("5. 프롬프트 상세 보기")
    print("6. 즐겨찾기 관리")
    print("7. 즐겨찾기 목록")
    print("-- 보너스 --")
    print("8. 프롬프트 수정")
    print("9. 프롬프트 삭제")
    print("10. 인기 프롬프트(조회수 Top)")
    print("11. JSON으로 저장")
    print("12. JSON에서 불러오기")
    print("13. 카테고리별 Markdown 내보내기")
    print("0. 종료")


# =========================================================
# 입력 보조 함수
# =========================================================

def input_nonempty(message):
    """빈 값이면 다시 입력받는다"""
    while True:
        value = input(message).strip()
        if value:
            return value
        print("⚠️  값을 입력해주세요.")


def select_category():
    """카테고리를 목록에서 선택하거나 직접 입력"""
    print("\n카테고리 선택:")
    print_category_menu()
    choice = input("선택(번호 또는 직접 입력): ").strip()

    if choice.isdigit():
        num = int(choice)
        if 1 <= num <= len(CATEGORIES):
            return CATEGORIES[num - 1]
        print("⚠️  잘못된 번호입니다. '기타'로 저장합니다.")
        return "기타"

    if choice:
        return choice
    return "기타"


def get_index_from_input(message):
    """1-based 번호를 입력받아 유효하면 0-based 인덱스 반환, 아니면 None"""
    choice = input(message).strip()
    if not choice.isdigit():
        print("⚠️  숫자를 입력해주세요.")
        return None
    num = int(choice)
    if not (1 <= num <= len(prompts)):
        print("⚠️  잘못된 번호입니다.")
        return None
    return num - 1


# =========================================================
# 1. 프롬프트 추가
# =========================================================

def add_prompt():
    print("\n=== 프롬프트 추가 ===")
    title = input_nonempty("제목: ")
    content = input_nonempty("내용: ")
    category = select_category()

    prompts.append({
        "title": title,
        "content": content,
        "category": category,
        "favorite": False,
        "views": 0,
    })
    print("\n✅ 프롬프트가 추가되었습니다!")


# =========================================================
# 2. 프롬프트 목록
# =========================================================

def show_list():
    print("\n=== 프롬프트 목록 ===")
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return
    for i, prompt in enumerate(prompts, start=1):
        print_prompt_line(i, prompt)
    print(f"\n총 {len(prompts)}개의 프롬프트")


# =========================================================
# 3. 카테고리별 조회
# =========================================================

def show_by_category():
    print("\n=== 카테고리별 조회 ===")
    print_category_menu()
    choice = input("선택: ").strip()

    if not choice.isdigit() or not (1 <= int(choice) <= len(CATEGORIES)):
        print("⚠️  잘못된 번호입니다.")
        return

    category = CATEGORIES[int(choice) - 1]
    filtered = [p for p in prompts if p["category"] == category]

    print(f"\n[{category}] 카테고리 프롬프트:")
    if not filtered:
        print("해당 카테고리에 프롬프트가 없습니다.")
        return
    for i, prompt in enumerate(filtered, start=1):
        print(f"{i}. {prompt['title']}{star(prompt['favorite'])}")
    print(f"\n총 {len(filtered)}개의 프롬프트")


# =========================================================
# 4. 프롬프트 검색
# =========================================================

def search_prompt():
    print("\n=== 프롬프트 검색 ===")
    keyword = input("검색어: ").strip()
    if not keyword:
        print("⚠️  검색어를 입력해주세요.")
        return

    results = [
        p for p in prompts
        if keyword.lower() in p["title"].lower()
        or keyword.lower() in p["content"].lower()
    ]

    print("\n검색 결과:")
    if not results:
        print("검색 결과가 없습니다.")
        return
    for i, prompt in enumerate(results, start=1):
        print_prompt_line(i, prompt)
    print(f"\n{len(results)}개의 프롬프트를 찾았습니다.")


# =========================================================
# 5. 프롬프트 상세 보기 (보너스2: 조회수 기록)
# =========================================================

def show_detail():
    print("\n=== 프롬프트 상세 보기 ===")
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return
    idx = get_index_from_input("번호 입력: ")
    if idx is None:
        return

    prompt = prompts[idx]
    prompt["views"] += 1   # 보너스2: 조회수 증가

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


# =========================================================
# 6. 즐겨찾기 관리
# =========================================================

def toggle_favorite():
    print("\n=== 즐겨찾기 관리 ===")
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return
    idx = get_index_from_input("프롬프트 번호 입력: ")
    if idx is None:
        return

    prompt = prompts[idx]
    prompt["favorite"] = not prompt["favorite"]
    if prompt["favorite"]:
        print(f"'{prompt['title']}' 프롬프트를 즐겨찾기에 추가했습니다!")
    else:
        print(f"'{prompt['title']}' 프롬프트를 즐겨찾기에서 해제했습니다!")


# =========================================================
# 7. 즐겨찾기 목록
# =========================================================

def show_favorites():
    print("\n=== 즐겨찾기 목록 ===")
    favorites = [p for p in prompts if p["favorite"]]
    if not favorites:
        print("즐겨찾기된 프롬프트가 없습니다.")
        return
    for i, prompt in enumerate(favorites, start=1):
        print_prompt_line(i, prompt)
    print(f"\n총 {len(favorites)}개의 즐겨찾기")


# =========================================================
# 8. 프롬프트 수정 (보너스2: Update)
# =========================================================

def edit_prompt():
    print("\n=== 프롬프트 수정 ===")
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return
    idx = get_index_from_input("수정할 번호 입력: ")
    if idx is None:
        return

    prompt = prompts[idx]
    print("(엔터만 누르면 기존 값을 유지합니다)")

    new_title = input(f"제목 [{prompt['title']}]: ").strip()
    if new_title:
        prompt["title"] = new_title

    new_content = input("내용(수정하려면 입력, 유지하려면 엔터): ").strip()
    if new_content:
        prompt["content"] = new_content

    change = input("카테고리를 변경하시겠습니까? (y/N): ").strip().lower()
    if change == "y":
        prompt["category"] = select_category()

    print("\n✅ 프롬프트가 수정되었습니다!")


# =========================================================
# 9. 프롬프트 삭제 (보너스2: Delete)
# =========================================================

def delete_prompt():
    print("\n=== 프롬프트 삭제 ===")
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return
    idx = get_index_from_input("삭제할 번호 입력: ")
    if idx is None:
        return

    confirm = input(f"'{prompts[idx]['title']}'을(를) 삭제할까요? (y/N): ").strip().lower()
    if confirm == "y":
        removed = prompts.pop(idx)
        print(f"\n🗑️  '{removed['title']}' 프롬프트를 삭제했습니다.")
    else:
        print("삭제를 취소했습니다.")


# =========================================================
# 10. 인기 프롬프트 (보너스2: 조회수 Top 정렬)
# =========================================================

def show_top_viewed():
    print("\n=== 인기 프롬프트 (조회수 Top) ===")
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return
    ranked = sorted(prompts, key=lambda p: p["views"], reverse=True)
    top = ranked[:5]   # 상위 5개
    for i, prompt in enumerate(top, start=1):
        print(f"{i}. [{prompt['category']}] {prompt['title']} "
              f"(조회수 {prompt['views']}){star(prompt['favorite'])}")


# =========================================================
# 11. JSON 저장 (보너스1: 영속화 - 저장)
# =========================================================

def save_to_json():
    print("\n=== JSON으로 저장 ===")
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
        print(f"✅ '{DATA_FILE}' 파일로 {len(prompts)}개를 저장했습니다.")
    except OSError as e:
        print(f"⚠️  저장 중 오류가 발생했습니다: {e}")


# =========================================================
# 12. JSON 불러오기 (보너스1: 영속화 - 불러오기)
# =========================================================

def load_from_json():
    print("\n=== JSON에서 불러오기 ===")
    if not os.path.exists(DATA_FILE):
        print(f"⚠️  '{DATA_FILE}' 파일이 없습니다. 먼저 저장해주세요.")
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        # 이전 데이터를 대체 (원본 리스트를 유지하며 내용 교체)
        prompts.clear()
        for item in loaded:
            item.setdefault("views", 0)       # 구버전 데이터 호환
            item.setdefault("favorite", False)
            prompts.append(item)
        print(f"✅ '{DATA_FILE}'에서 {len(prompts)}개를 불러왔습니다.")
    except (OSError, json.JSONDecodeError) as e:
        print(f"⚠️  불러오는 중 오류가 발생했습니다: {e}")


# =========================================================
# 13. 카테고리별 Markdown 내보내기 (보너스1)
# =========================================================

def export_markdown():
    print("\n=== 카테고리별 Markdown 내보내기 ===")
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return

    filename = "prompts_export.md"
    lines = ["# 나만의 프롬프트 모음\n"]

    for category in CATEGORIES:
        items = [p for p in prompts if p["category"] == category]
        if not items:
            continue
        lines.append(f"\n## {category}\n")
        for p in items:
            fav = " ⭐" if p["favorite"] else ""
            lines.append(f"### {p['title']}{fav}\n")
            lines.append(f"```\n{p['content']}\n```\n")

    # 미리 정의되지 않은(직접 입력) 카테고리 처리
    others = [p for p in prompts if p["category"] not in CATEGORIES]
    if others:
        lines.append("\n## 기타(사용자 지정)\n")
        for p in others:
            fav = " ⭐" if p["favorite"] else ""
            lines.append(f"### {p['title']} ({p['category']}){fav}\n")
            lines.append(f"```\n{p['content']}\n```\n")

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"✅ '{filename}' 파일로 내보냈습니다.")
    except OSError as e:
        print(f"⚠️  내보내는 중 오류가 발생했습니다: {e}")


# =========================================================
# 메인 루프
# =========================================================

def main():
    while True:
        show_menu()
        choice = input("선택: ").strip()

        if choice == "1":
            add_prompt()
        elif choice == "2":
            show_list()
        elif choice == "3":
            show_by_category()
        elif choice == "4":
            search_prompt()
        elif choice == "5":
            show_detail()
        elif choice == "6":
            toggle_favorite()
        elif choice == "7":
            show_favorites()
        elif choice == "8":
            edit_prompt()
        elif choice == "9":
            delete_prompt()
        elif choice == "10":
            show_top_viewed()
        elif choice == "11":
            save_to_json()
        elif choice == "12":
            load_from_json()
        elif choice == "13":
            export_markdown()
        elif choice == "0":
            print("\n프로그램을 종료합니다. 안녕히 가세요! 👋")
            break
        else:
            print("⚠️  잘못된 번호입니다. 다시 선택해주세요.")


if __name__ == "__main__":
    main()
