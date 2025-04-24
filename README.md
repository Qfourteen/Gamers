# Gamers
목차
1. [기여](#기여)
2. [시작하기(백엔드)](#시작하기백엔드)
3. [시작하기(프론트엔드)](#시작하기프론트엔드)
4. [참고문헌](#참고문헌)

## 기여

아래 3가지만 필수적으로 지켜주시면 됩니다.
1. commit은 무조건 [`.gitmessage`](.gitmessage)를 이용해주세요.
commit을 하기 전 **.gitmessage** 파일에 메시지를 적어주세요(기존 메시지는 지우고).
```shell
git commit -F .gitmessage
```

2. (백엔드 개발에서) 외부 데이터베이스 주소같이 github에 올라가면 안 좋은 결과가 생길 데이터들이 있으면,
코드에 데이터를 직접 넣지 말고 **env.py에** 다 몰아 넣어주세요. env.py는 `src/backend` 디렉터리 아래에 생성합니다.
```python
# src/backend/env.py
DATABASE_URL = "..."
DATABASE_PASSWORD = "..."
```

3. 분산 주도 개발하기:
기능은 완성되기 전까지 가능하면 `main` 브렌치에서 commit을 넣지 말아주세요.
해당 기능을 위한 브렌치를 만들어서 그 브렌치에서 작업해주세요.
그리고 기능이 완성되면 pull request를 요청하여 병합하면 됩니다.
정리하자면 아래 workflow를 따르면 됩니다.
   1. [`https://github.com/Qfourteen/Gamers`](https://github.com/Qfourteen/Gamers)를 본인 컴퓨터에 clone합니다.
   2. 브렌치를 만듭니다.
   3. 그 브렌티로 이동합니다.
   4. 이제 여기서 개발하면 됩니다.
   5. 자세한 내용은 [`기여_상세.md`](docs/how_to/기여_상세.md)

---

아래 내용도 지켜주시면 좋아요.

4. 문서 쓸 때는 맞춤법 지키기

5. commit 한 번에 몰아서 하지 말고, 작업의 최소 단위가 완료될 때마다 commit 하기.

## 시작하기(백엔드)

1. **파이썬이 설치되어 있는지 확인합니다.**
터미널에 아래 명령을 입력해봅니다.
```shell
python3 --version
```
이 명령이 실패한다면,
```shell
python --version
```
도 시도해보세요. 앞으로 파이썬 명령은 둘 중 성공하는 것을 사용하면 됩니다.
(이하 `python`을 기준으로 설명)

2. **파이썬 패키지 가상환경을 생성합니다.**
패키지 가상환경은 이 프로젝트를 전역(全域) 파이썬 환경과 분리해줍니다.
```shell
python -m venv venv
```

이후 아래 명령을 입력하면 현재 터미널이 파이썬 가상환경으로 변합니다.
```shell
source venv/bin/activate
```
이 명령이 실패한다면,
```shell
source venv/Scripts/activate
```
도 시도해보세요.
이후 터미널에 변화가 생겼다면 성공입니다.

3. **가상환경 내에서 패키지를 설치합니다.**
```shell
pip install -r requirements.txt
```

4. **프론트엔드를 빌드합니다.**
[아래에 있는 과정을 따라해주세요.](#시작하기프론트엔드)
프론트엔드 빌드는 필수가 아니지만, 홈 화면을 비롯해서 사용이 불가능한 URL이 생길 수 있습니다.

5. **이제 준비가 끝났습니다!**
코드를 실행해보고 싶으면 src/backend 아래에 있는 `run.py`를 실행하면 됩니다.

그 이후 과정
* 브라우저에서 `localhost:8000`로 접속합니다.
* `localhost:8000/docs`나 `localhost:8000/redoc`으로 접근하여 웹에서 코드 문서를 볼 수 있습니다.


## 시작하기(프론트엔드)

> 일러두기: 현재 프로젝트 구조는 프론트엔드가 백엔드에 종속되는 구조입니다.
> 백엔드 구현 없이 프론트엔드만 사용해서 개발하려면 별도의 환경이 필요합니다.

1. node.js가 설치되어 있는지 확인합니다.
터미널에 아래 명령을 입력해봅니다.
```shell
node -v
npm -v
```

2. 라이브러리를 설치합니다.
```shell
npm install
```

3. 정적 파일을 빌드합니다. 이 결과물은 `src/backend/static`에 있습니다.
```shell
cd src/frontend && vite build
```


## 참고문헌

### 데이터 구조
데이터를 안정적으로 저장하고 처리하기 위해서는 데이터베이스가 필요합니다.
데이터베이스는 데이터가 어떤 식으로 저장될지, 어떤 타입으로 저장될지 미리 정해야 합니다.
[자세한 내용을 확인해보세요.](./docs/데이터구조/README.md)

### Pygame

#### 예제 기반 튜토리얼

1. [창 열기](docs/how_to/pygame/open_window.md)
2. [키보드 입력 감지](docs/how_to/pygame/keypress.md)
3. [마우스 클릭 감지](docs/how_to/pygame/mouse_click.md)
4. [화면 조정](docs/how_to/pygame/set_display.md)
5. [충돌 감지](docs/how_to/pygame/colliderect.md)
6. [음악 설정](docs/how_to/pygame/music.md)