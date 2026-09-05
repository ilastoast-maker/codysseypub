# Git 실습 명령어 순서

> 대상 저장소: `https://github.com/ilastoast-maker/codysseypub.git`  
> 작업 브랜치: `09a1`  
> 과제 파일 위치: `A1-1/`

## 0. 사전 설정
```bash
git --version
git config --global user.name "본인이름"
git config --global user.email "본인이메일@example.com"
```

## 1. 저장소 받기 + 작업 위치 이동
```bash
git clone -b 09a1 https://github.com/ilastoast-maker/codysseypub.git
cd codysseypub/A1-1
```

> `A1-1`은 `codysseypub` 저장소 내부 폴더이므로 이 폴더 안에서 다시 `git init`을 실행하지 않습니다.

## 2. 원격 저장소와 브랜치 확인
```bash
git remote -v
git branch --show-current
```

정상이라면 `origin`은 다음 저장소를 가리키고 현재 브랜치는 `09a1`입니다.

```text
https://github.com/ilastoast-maker/codysseypub.git
09a1
```

## 3. 변경 사항 확인 및 커밋
```bash
git status
git add A1-1/main.py A1-1/README.md A1-1/prompts.json A1-1/prompts_export.md A1-1/git_commands.md
```

> 위 명령은 저장소 루트(`codysseypub`)에서 실행하는 경우입니다. 이미 `A1-1` 폴더 안이라면 `git add main.py README.md prompts.json prompts_export.md git_commands.md`처럼 입력합니다.

```bash
git commit -m "feat: A1-1 프롬프트 관리 프로그램 완성"
```

## 4. 기능 브랜치 실습 예시
```bash
git checkout -b feature/list
# 기능 수정 후
git add main.py
git commit -m "feat: 프롬프트 목록 출력 기능 구현"
git checkout 09a1
git merge feature/list
git branch -d feature/list
```

## 5. 원격 반영
```bash
git push origin 09a1
```

## 6. 원격 변경 사항 가져오기
```bash
git pull origin 09a1
```

## 7. clone 명령 사용 기록이 필요한 경우
```bash
cd ..
git clone -b 09a1 https://github.com/ilastoast-maker/codysseypub.git codysseypub-clone-test
cd codysseypub-clone-test/A1-1
python main.py
```

확인 후 테스트 폴더는 삭제할 수 있습니다.

## 제출용 확인 명령어
```bash
git status
git branch --show-current
git log --oneline --graph --all
git remote -v
```
