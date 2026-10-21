# Windows 프론트엔드 빌드와 백엔드 연결

## 백엔드 주소를 바꾸는 곳

`frontend/.env.production`의 `BACKEND_ORIGIN` 한 줄에서 운영 백엔드를 설정합니다.

```dotenv
BACKEND_ORIGIN=http://100.100.100.20:8000
VITE_API_BASE_URL=${BACKEND_ORIGIN}/api
```

다른 서버로 옮기면 첫 줄만 바꿉니다. 예: `http://100.100.100.127:8000`.
모든 JSON API, 회원가입, 로그인, 카카오 인증 이동, 이미지 업로드와 업로드 이미지 표시가
`frontend/src/api/config.js`의 공통 설정을 사용합니다. 개별 JS 파일에 IP를 적지 않습니다.

Node.js 22.23.3에서 프론트엔드를 빌드합니다.

```powershell
cd frontend
nvm use 22.23.3
npm run build
```

이 설정에서는 로그인 요청 주소가 `http://100.100.100.20:8000/api/user/login`이 됩니다.
Vite는 빌드 때 값을 번들에 넣으므로 주소를 바꾼 뒤에는 다시 빌드하고 배포해야 합니다.
기존 `VITE_API_BASE_URL` 셸 환경변수나 `.env.production.local`이 있으면 해당 값이 우선하므로
원치 않는 덮어쓰기가 없는지 확인합니다. VITE_ 변수에는 시크릿을 넣지 않습니다.

## HTTP에서 로그인 쿠키를 사용하는 운영 설정

`http://www.my-do.kro.kr`에서 백엔드 IP를 직접 호출하는 방식은 현재 쿠키 로그인에 적합하지 않습니다.
백엔드 IP 응답은 `Domain=my-do.kro.kr` 쿠키를 발급할 수 없으며, `SameSite=Lax` 쿠키는
이런 cross-site fetch에 전송되지 않습니다. `SameSite=None`에는 HTTPS의 Secure 쿠키가 필요합니다.
`credentials: include`와 CORS 허용만으로 해결되지 않습니다.

현재 HTTP 구성에서 쿠키 로그인을 사용하려면 같은 설정 파일의 두 번째 줄을 바꿉니다.

```dotenv
BACKEND_ORIGIN=http://100.100.100.20:8000
VITE_API_BASE_URL=/api
```

이후 `npm run build`를 실행하면 다음 두 결과가 생성됩니다.

- `frontend/dist/`: 정적 프론트엔드 파일
- `frontend/nginx.conf`: `/api`를 위 BACKEND_ORIGIN으로 전달하는 nginx 설정

nginx 설정은 빌드 시 자동 생성하므로 서버 주소를 다시 적을 필요가 없습니다.
`frontend/nginx.conf.template`은 생성용 템플릿이며 서버에 직접 적용하지 않습니다.

프론트엔드 서버에는 `dist`와 생성된 `nginx.conf`를 같은 폴더 아래에 복사합니다.
`dist`의 내용을 nginx의 `html`로, `nginx.conf`를 `conf/nginx.conf`로 반영합니다.
nginx `root html`은 실제 nginx 실행 prefix를 기준으로 하므로 경로 철자와 무관하게 사용할 수 있습니다.
실제 확인된 nginx 설치 폴더는 `C:\Users\test\Downloads\nginx-1.30.5`입니다.

선택적으로 백업 및 설정 검사를 포함한 적용 스크립트를 사용할 수 있습니다.

```powershell
powershell -NoProfile -File .\deploy\apply-windows-frontend.ps1 `
  -NginxRoot C:\Users\test\Downloads\nginx-1.30.5 `
  -DistPath .\frontend\dist
```

스크립트는 기존 설정과 html을 백업하고 `nginx -t` 검사 후 실행 중인 마스터에 reload 신호를 보냅니다.
서버를 새로 시작하지 않습니다. 고아 작업 프로세스가 있으면 경고를 확인하고 별도로 점검합니다.

## 백엔드와 연결 확인

사용자가 백엔드 배포 폴더에서 uvicorn을 `0.0.0.0:8000`으로 실행하고,
Windows 방화벽에서 프론트엔드 서버의 8000 포트 접근을 허용해야 합니다.
직접 API 호출을 선택하면 사용자 브라우저에서도 해당 IP와 포트에 접근할 수 있어야 합니다.

```powershell
Test-NetConnection 100.100.100.20 -Port 8000
```

프록시 방식에서 운영 백엔드 `.env`는 다음을 사용합니다.

```dotenv
COOKIE_DOMAIN=my-do.kro.kr
COOKIE_SECURE=false
KAKAO_REDIRECT_URI=http://www.my-do.kro.kr/login/kakao/callback
```

기존 DB 연결 및 시크릿은 유지합니다. 카카오 개발자 콘솔에도 같은 Redirect URI를 등록합니다.
코드나 `.env`를 변경하면 사용자가 백엔드를 재시작해야 합니다.
HTTPS 프론트엔드로 전환하면 COOKIE_SECURE와 카카오 Redirect URI를 함께 변경합니다.
로컬 개발에서는 COOKIE_DOMAIN을 비워 두며, Vite `/api` 프록시는 `127.0.0.1:8000`을 사용합니다.

브라우저에서 확인할 항목:

1. 회원가입 요청의 URL이 선택한 방식과 일치하고 응답이 200인지 확인합니다.
2. 로그인 응답이 200이고 EN_AT 쿠키가 저장되는지 확인합니다.
3. `/api/learning/dashboard` 요청에 쿠키가 포함되어 인증되는지 확인합니다.

연결 거부는 서버 실행/포트/방화벽 문제, nginx HTML 404는 프록시 설정 문제,
JSON 401은 계정/비밀번호 또는 쿠키 문제입니다.
상대경로 `sqlite:///db.sqlite`는 uvicorn을 실행한 폴더에 따라 다른 DB를 사용하므로,
기존 회원 데이터가 있는지와 실제 DB 경로도 확인합니다.
