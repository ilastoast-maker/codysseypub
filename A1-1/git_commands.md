# A1-1 Git 확인 명령어

저장소: `ilastoast-maker/codysseypub`  
브랜치: `09a1`  
폴더: `A1-1`

## 저장소 받기

```bash
git clone -b 09a1 https://github.com/ilastoast-maker/codysseypub.git
cd codysseypub/A1-1
```

## 브랜치 확인

```bash
git branch --show-current
# 09a1
```

## 의미 있는 커밋 개수 확인

```bash
git log --oneline --graph
git rev-list --count HEAD
```

A1-1에 영향을 준 커밋만 확인:

```bash
git log --oneline -- A1-1
```

## 실행 및 테스트

```bash
python main.py
python -m py_compile main.py tests/test_main.py
python -m unittest discover -s tests -v
```

## 수정 후 일반적인 반영 순서

```bash
git checkout 09a1
git pull origin 09a1
git status
git add A1-1/main.py
git commit -m "fix: 프롬프트 선택 번호와 즐겨찾기 관리 수정"
git push origin 09a1
```

기능별 변경은 가능한 한 하나의 목적을 가진 커밋으로 나눕니다. 예:

```text
fix: 프롬프트 선택 번호와 즐겨찾기 관리 수정
test: 프롬프트 관리 전체 기능 회귀 테스트 추가
docs: README 실행 방법과 테스트 절차 보완
test: 전체 기능 검증 결과 문서화
docs: Git 커밋 확인 절차 보완
```
