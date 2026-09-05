# A1-2 Git 확인 명령어

저장소: `ilastoast-maker/codysseypub`  
브랜치: `09a2`  
폴더: `A1-2`

## clone 및 이동

```bash
git clone -b 09a2 https://github.com/ilastoast-maker/codysseypub.git
cd codysseypub/A1-2
```

## 브랜치 확인

```bash
git branch --show-current
# 09a2
```

## A1-2 관련 커밋 확인

저장소 루트에서:

```bash
git log --oneline -- A1-2
```

전체 브랜치 커밋:

```bash
git log --oneline --graph
```

## 실행/테스트

```bash
pip install -r requirements.txt
python travel_planner.py --help
python -m py_compile travel_planner.py llm_client.py place_client.py report.py errors.py tests/test_travel_planner.py
python -m unittest discover -s tests -v
```

## 일반적인 수정 반영 순서

```bash
git checkout 09a2
git pull origin 09a2
git status
git add A1-2/<수정파일>
git commit -m "fix: 변경 목적"
git push origin 09a2
```

기능, 버그 수정, 테스트, 문서처럼 서로 다른 목적은 가능한 한 별도 커밋으로 나눕니다.
