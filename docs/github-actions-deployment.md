# GitHub Actions SSH 자동 배포

`main`에 PR을 머지하면 변경 경로에 따라 배포합니다. `main` 직접 push에도 실행되므로 PR을 통해서만 배포하려면 GitHub에서 main 브랜치 보호 규칙으로 직접 push를 제한하세요.

- `app/**`, `requirements.txt` 변경: `.github/workflows/deploy-backend.yml`
- `frontend/**` 변경: `.github/workflows/deploy-frontend.yml`
- 각 서비스의 Dockerfile, 워크플로 변경도 해당 배포를 실행합니다. 공통 배포 스크립트 변경 시 두 배포 모두 실행합니다.
- GitHub Actions의 **Run workflow → main**으로 각각 수동 배포할 수 있습니다. 다른 브랜치에서는 배포하지 않습니다.

GitHub이 인식하는 폴더는 **`.github/workflows/`**입니다. 배포 워크플로 두 개와 실행 확인용 `test.yml`을 이 폴더에 모았습니다. `github/workflows/`처럼 앞에 점이 없는 경로는 실행 대상이 아닙니다. 파일 확장자는 `.yml` 또는 `.yaml`이어야 하며 `.yml.py`는 사용할 수 없습니다.

## 1. GitHub Secrets

저장소 **Settings → Secrets and variables → Actions → Secrets → New repository secret**에서 등록하세요. 비밀번호를 yml에 직접 입력하지 마세요.

| Secret 이름 | 값 |
| --- | --- |
| `BACKEND_SSH_HOST` | `222.112.208.68` |
| `BACKEND_SSH_PORT` | `9009` |
| `BACKEND_SSH_USERNAME` | 백엔드 서버 SSH 계정 |
| `BACKEND_SSH_PASSWORD` | 해당 계정 SSH 비밀번호 |
| `FRONTEND_SSH_HOST` | `222.112.208.68` |
| `FRONTEND_SSH_PORT` | `9109` |
| `FRONTEND_SSH_USERNAME` | 프론트엔드 서버 SSH 계정 |
| `FRONTEND_SSH_PASSWORD` | 해당 계정 SSH 비밀번호 |
| `BACKEND_SSH_FINGERPRINT` | 선택: 백엔드 SSH 호스트 키의 SHA256 지문 |
| `FRONTEND_SSH_FINGERPRINT` | 선택: 프론트엔드 SSH 호스트 키의 SHA256 지문 |

위 표는 **9009와 9109가 SSH 접속 포트**라는 해석입니다. 예를 들어 `ssh -p 9009 계정@222.112.208.68`로 접속되는 구성이어야 합니다. 두 포트가 NAT로 서로 다른 내부 서버를 가리킬 수도 있으므로 실제 연결 대상을 확인하세요.

**9009와 9109가 브라우저 접속용 서비스 포트인 경우**, SSH_PORT Secrets에는 실제 SSH 포트(보통 `22`)를 입력하고 다음 Variables를 `9009`, `9109`로 설정하세요. SSH 리스너와 웹 서버가 같은 서버의 동일 포트를 사용할 수는 없습니다.

## 2. GitHub Variables

같은 화면의 **Variables → New repository variable**에서 필요할 때 등록하세요.

| Variable 이름 | 기본값 | 설명 |
| --- | --- | --- |
| `BACKEND_HTTP_PORT` | `8000` | 서버가 외부에 제공하는 백엔드 HTTP 포트 |
| `FRONTEND_HTTP_PORT` | `80` | Nginx가 제공하는 프론트엔드 HTTP 포트 |
| `BACKEND_UPSTREAM` | `127.0.0.1:8000` | 프론트엔드 서버에서 접근할 백엔드 HTTP 주소, 프로토콜 없이 `호스트:포트` |

기본 구성은 두 배포 대상이 **같은 Linux 호스트**라는 전제입니다. 서로 다른 내부 서버라면 `BACKEND_UPSTREAM`을 백엔드 내부 IP와 서비스 포트로 바꾸세요. `BACKEND_HTTP_PORT`를 변경한 경우 `BACKEND_UPSTREAM`의 포트도 맞춰야 합니다. 이 주소에는 SSH 포트를 입력하지 않습니다.

## 3. 서버 최초 준비

서버는 **Linux x86_64 + Docker Engine** 환경을 기준으로 합니다. 두 SSH 접속 대상이 다른 서버라면 각각 준비하세요.

1. Docker Engine, Bash, curl, tar를 설치하고 Docker 서비스를 활성화합니다.
2. 배포 SSH 계정이 비밀번호 인증으로 접속할 수 있고 `docker info`를 sudo 없이 실행할 수 있도록 설정합니다. Docker 그룹 권한을 변경했다면 재로그인합니다.
3. 방화벽/NAT에서 GitHub Actions가 SSH 포트에 접근할 수 있도록 설정합니다. 브라우저 접속용 HTTP 포트도 별도로 열어야 합니다.
4. 프론트엔드 서비스 포트(기본 80)를 다른 Nginx/Apache 등이 사용 중이면 포트를 조정합니다.
5. 백엔드 서버에서 다음 디렉터리를 만들고 배포 계정에 소유권을 부여합니다. 아래 `DEPLOY_USER`는 실제 계정으로 바꾸세요.

```bash
sudo mkdir -p /opt/ai02/data /opt/ai02/uploads
sudo chown -R DEPLOY_USER:DEPLOY_USER /opt/ai02
install -m 600 /dev/null /opt/ai02/backend.env
```

`/opt/ai02/backend.env`에 운영 환경 값을 작성하세요. Docker `--env-file` 형식이므로 값에 셸용 따옴표를 붙이지 않습니다.

```dotenv
SECRET_KEY=충분히_긴_임의의_운영용_비밀값
DATABASE_URL=sqlite:////data/db.sqlite
KAKAO_REST_API_KEY=
KAKAO_CLIENT_SECRET=
KAKAO_REDIRECT_URI=http://서비스주소/login/kakao/callback
PORTONE_STORE_ID=
PORTONE_CHANNEL_KEY=
PORTONE_API_SECRET=
```

Kakao/PortOne 값은 사용 시 실제 운영값을 입력하고 서비스 제공자에 등록된 주소도 맞추세요. 기존 SQLite 데이터가 필요하면 최초 배포 전에 실제 사용 중인 DB를 `/opt/ai02/data/db.sqlite`로 복사하세요. 기존 상품 사진도 `/opt/ai02/uploads/products/`로 복사하세요. 복사 전에 기존 서비스를 중지하여 일관된 DB 백업을 확보하세요.

선택적 SSH 지문은 접속 대상 서버에서 다음 명령으로 확인할 수 있습니다.

```bash
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256
```

출력 중 `SHA256:...` 값을 해당 FINGERPRINT Secret에 저장합니다.

## 4. 배포 동작과 확인

GitHub 러너에서 머지된 커밋의 Docker 이미지를 빌드하고, 이미지와 배포 스크립트를 SCP로 전송한 다음 SSH로 실행합니다. 서버에 GitHub 저장소 접근 토큰이나 Node.js/Python을 별도로 설치할 필요는 없습니다. 프론트엔드 빌드는 Node.js **22.23.3**과 `npm ci`를 사용합니다.

- 백엔드: `ai02-backend` 컨테이너, Uvicorn 내부 포트 8000, 외부 포트는 `BACKEND_HTTP_PORT`.
- 프론트엔드: `ai02-frontend` 컨테이너, Linux 호스트 네트워크를 사용하는 Nginx, 서비스 포트는 `FRONTEND_HTTP_PORT`.
- Nginx가 `/api/`를 백엔드로 프록시하므로 프론트엔드는 기본 상대 주소 `/api`를 사용합니다. 개발용 Vite 프록시는 `http://127.0.0.1:8000`을 유지합니다.
- 새 백엔드는 `/openapi.json`, 프론트엔드는 `/`의 HTTP 성공 응답을 확인합니다. 시작 확인 실패 시 새 컨테이너를 제거하고 이전 컨테이너를 복구합니다. 프론트엔드 확인은 백엔드 API 연결 성공까지 보장하지 않습니다.
- 교체 중 잠깐의 중단이 발생할 수 있습니다. SQLite DB와 업로드는 컨테이너 외부에 보존하며 DB 스키마 변경은 컨테이너 복구로 되돌리지 않습니다.
- `--restart unless-stopped`로 서버 재부팅 후에도 다시 실행합니다. 같은 서비스의 배포는 동시 실행하지 않습니다.
- 이전 이미지 태그는 수동 복구용으로 보존하므로 서버 디스크 사용량을 확인하고 오래된 미사용 이미지를 정리하세요. 전송된 이미지 tar 파일은 성공 시 제거됩니다.

배포 후 서버에서 확인:

```bash
docker ps --filter name=ai02
docker logs --tail 100 ai02-backend
docker logs --tail 100 ai02-frontend
curl -f http://127.0.0.1:8000/openapi.json
curl -f http://127.0.0.1/
curl -f http://127.0.0.1/api/learning/lessons
```

실제 API 경로는 로그인 등 해당 API의 요구 조건을 맞춰 확인하세요. 포트를 변경했다면 확인 명령에도 변경 포트를 사용하세요. 첫 배포는 백엔드, 프론트엔드 순으로 수동 실행하는 편이 확인하기 쉽습니다.

배포 도중 강제 취소 등으로 `ai02-서비스-previous` 컨테이너가 남으면 다음 배포는 중단됩니다. `docker ps -a`와 로그로 현재/이전 컨테이너 상태를 확인한 뒤 복구 또는 불필요한 이전 컨테이너 제거를 수행하세요.

설정 근거: [GitHub 워크플로 경로와 트리거](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [SCP 비밀번호 인증](https://github.com/appleboy/scp-action), [SSH 액션 설정](https://github.com/appleboy/ssh-action).
