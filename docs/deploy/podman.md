# Podman (rootless) 배포 가이드

이 문서는 rootless Podman 환경에서 Gamers 서비스를 컨테이너로 빌드/실행하는 방법과
비밀 값을 안전하게 주입하는 실무 패턴을 설명합니다.

## 1) 이미지 빌드

프로젝트 루트에서 다음 명령으로 이미지를 빌드합니다.

```bash
podman build -t gamers:latest -f Containerfile .
```

- 멀티 스테이지 빌드로 프론트엔드를 먼저 빌드한 뒤, Python 런타임 이미지에 결과물만 복사합니다.
- 기본 포트는 `8000`입니다.

## 2) 구성 값과 비밀 값 주입

애플리케이션은 `src/backend/env.py`에서 다음 키를 환경변수 또는 파일로 읽습니다.

- `MONGODB_URL` 또는 `MONGODB_URL_FILE`
- `SECRET_KEY` 또는 `SECRET_KEY_FILE`
- `SECURE_COOKIE` 또는 `SECURE_COOKIE_FILE` (true/false)

우선순위는 `*_FILE` > 환경변수입니다. 파일 방식은 Podman/Docker의 secret/mount 패턴과 잘 맞습니다.

### 2-1) Podman secret 사용 (권장)

`SECRET_KEY` 같은 비밀은 이미지에 포함하지 말고, Podman secret으로 주입하세요.

```bash
# 비밀 생성 (한 번만)
echo -n "<프로덕션_랜덤_시크릿>" | podman secret create gamers_secret_key -

# 실행 시 시크릿 마운트 + 경로를 *_FILE 로 알려주기
podman run -d \
  --name gamers \
  -p 8000:8000 \
  --secret gamers_secret_key,type=mount \
  -e SECRET_KEY_FILE=/run/secrets/gamers_secret_key \
  -e MONGODB_URL="mongodb://<호스트IP>:27017" \
  -e SECURE_COOKIE=true \
  gamers:latest
```

- `--secret ... type=mount`는 시크릿을 컨테이너 내부 `/run/secrets/<name>` 파일로 마운트합니다.
- `SECRET_KEY_FILE` 환경변수로 해당 파일 경로를 알리면, 앱이 자동으로 파일 내용을 읽습니다.

### 2-2) .env 파일 사용 (간단)

프로덕션에서 비추천이지만, 개발/테스트 용도로는 `.env` 파일을 사용할 수 있습니다.

`.env.example` 형식:

```
MONGODB_URL=mongodb://localhost:27017
SECURE_COOKIE=false
# SECRET_KEY=개발용_값(프로덕션에서 사용 금지)
```

실행:

```bash
podman run -d \
  --name gamers \
  --env-file .env \
  -p 8000:8000 \
  gamers:latest
```

## 3) MongoDB 연결 주의사항

- 컨테이너 내부에서 외부 MongoDB(호스트 또는 다른 컨테이너)로 접속합니다.
- 호스트 DB에 붙는 경우 Linux에서 `host.containers.internal`이 동작하지 않을 수 있습니다. 이때는 호스트 IP를 직접 넣으세요.
- 동일 Podman 네트워크의 다른 컨테이너에 붙을 경우, `--network <net>` + 서비스명 또는 컨테이너 이름으로 접속하세요.

예:

```bash
# 동일 네트워크 구성
podman network create gamers-net
podman run -d --name mongodb --network gamers-net -e MONGO_INITDB_ROOT_USERNAME=... -e MONGO_INITDB_ROOT_PASSWORD=... docker.io/library/mongo:7

# 앱 실행 (같은 네트워크)
podman run -d --name gamers --network gamers-net \
  -e MONGODB_URL="mongodb://mongodb:27017" \
  --secret gamers_secret_key,type=mount \
  -e SECRET_KEY_FILE=/run/secrets/gamers_secret_key \
  -p 8000:8000 gamers:latest
```

## 4) 루트리스 실행 팁

- 이미지는 비루트 사용자(`app`)로 실행되며, 포트는 8000(1024 이상)이라 추가 권한이 필요 없습니다.
- 로그는 표준출력으로 나옵니다. `podman logs -f gamers`로 확인하세요.
- 업데이트 시에는 `podman pull`이 아닌, 로컬 빌드(`podman build`) 후 `podman rm -f gamers && podman run ...`로 재실행하세요.

## 5) 헬스 체크

이미지에 간단한 TCP 헬스체크가 포함되어 있습니다. 컨테이너 오케스트레이션(예: systemd quadlet, play kube)에서 참조할 수 있습니다.

---

추가 자동화(quadlet, podman-compose 등)가 필요하면 알려주세요. 해당 방식에 맞춘 파일을 생성해 드릴 수 있습니다.

