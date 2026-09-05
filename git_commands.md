# Git 실습 명령어 순서 (커밋 10개+ · 브랜치 병합 · 8개 명령어 포함)

> 아래 순서를 그대로 따라 하면 과제 요건(커밋 10개 이상, 브랜치 생성·병합,
> `init/add/commit/push/pull/checkout/clone/merge` 각 1회 이상)을 모두 충족합니다.
> `<사용자명>`, 저장소 이름 등은 본인 값으로 바꿔주세요.

---

## 0. 사전 설정 (최초 1회)
```bash
git --version
git config --global user.name  "본인이름"
git config --global user.email "본인이메일@example.com"
git config --global init.defaultBranch main
```

## 1. 저장소 초기화 + 첫 커밋 (init, add, commit)
```bash
mkdir prompt-manager && cd prompt-manager
git init

# README.md, .gitignore 파일을 폴더에 넣은 뒤
git add README.md .gitignore
git commit -m "docs: 프로젝트 초기화 및 README 작성"   # [커밋 1]
```

## 2. 원격 연결 + 첫 푸시 (push)
```bash
# GitHub에서 prompt-manager 저장소를 먼저 생성한 뒤
git remote add origin https://github.com/<사용자명>/prompt-manager.git
git branch -M main
git push -u origin main
```

## 3. 기능 단위 커밋 (기본 구조)
```bash
# main.py에 기본 데이터(딕셔너리 3개+)만 먼저 작성
git add main.py
git commit -m "feat: 기본 프롬프트 데이터 및 카테고리 정의"   # [커밋 2]

# show_menu() + main 루프 작성
git add main.py
git commit -m "feat: 메뉴 출력 및 메인 루프 구현"             # [커밋 3]

# add_prompt() 작성
git add main.py
git commit -m "feat: 프롬프트 추가 기능 구현"                 # [커밋 4]
```

## 4. 브랜치 생성 → 작업 → 병합 (checkout, merge)
```bash
# 프롬프트 목록 기능을 별도 브랜치에서 작업
git checkout -b feature/list

# show_list() 작성 후
git add main.py
git commit -m "feat: 프롬프트 목록 출력 기능 구현"           # [커밋 5]

# main 브랜치로 돌아와 병합
git checkout main
git merge feature/list
git branch -d feature/list      # 병합된 브랜치 정리(선택)
```

## 5. 나머지 기능 커밋
```bash
git add main.py && git commit -m "feat: 카테고리별 조회 기능 구현"   # [커밋 6]
git add main.py && git commit -m "feat: 프롬프트 검색 기능 구현"     # [커밋 7]
git add main.py && git commit -m "feat: 프롬프트 상세 보기 기능 구현" # [커밋 8]
git add main.py && git commit -m "feat: 즐겨찾기 추가/해제 기능 구현" # [커밋 9]
git add main.py && git commit -m "feat: 즐겨찾기 목록 기능 구현"     # [커밋 10]
git add README.md && git commit -m "docs: 실행 방법 및 기능 목록 보완" # [커밋 11]

# --- 보너스 기능 (선택) ---
git add main.py && git commit -m "feat: 프롬프트 수정/삭제(CRUD) 기능 추가"       # [커밋 12]
git add main.py && git commit -m "feat: 조회수 기록 및 Top 정렬 기능 추가"        # [커밋 13]
git add main.py && git commit -m "feat: JSON 저장/불러오기 및 Markdown 내보내기 추가" # [커밋 14]
```

## 6. 원격 반영 (push)
```bash
git push
```

## 7. pull 사용 기록 만들기 (pull)
```bash
# GitHub 웹에서 README를 살짝 수정/커밋한 뒤 로컬로 가져오기
git pull
```

## 8. clone 실습 (clone) — 확인 후 삭제 가능
```bash
cd ..
git clone https://github.com/octocat/Hello-World.git
cd Hello-World
git log --oneline        # 폴더 구조와 로그 확인
cd ..
rm -rf Hello-World       # 확인 후 삭제 (Windows: rmdir /s Hello-World)
```

---

## ✅ 제출용 확인 명령어
```bash
git log --oneline --graph --all      # 커밋/브랜치 그래프 스크린샷
git log --oneline | wc -l            # 커밋 개수 확인 (10개 이상)
```

## 사용한 Git 명령어 체크리스트
- [x] init   — 1단계
- [x] add    — 1,3,5단계 등
- [x] commit — 커밋 1~11
- [x] push   — 2,6단계
- [x] pull   — 7단계
- [x] checkout — 4단계 (브랜치 생성/이동)
- [x] merge  — 4단계 (feature/list 병합)
- [x] clone  — 8단계
