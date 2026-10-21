# 카카오 로그인 설정

## 카카오 디벨로퍼스

1. 앱에서 카카오 로그인을 활성화합니다.
2. 플랫폼 키에서 REST API 키와 Client Secret을 확인합니다.
3. REST API 키에 Redirect URI `http://localhost:5173/login/kakao/callback`을 등록합니다.
4. 카카오 로그인 사용 설정을 켭니다.
5. 동의 항목에서 프로필 닉네임을 설정합니다. 이 구현은 이메일 동의를 요청하지 않습니다.

## 로컬 실행

- Kakao Developers에서 REST API 키와 Client Secret을 준비합니다. Client Secret은 현재 기본 활성화 상태이므로 실제 값을 입력해야 합니다.
- 루트 `.env`에 아래 값을 설정합니다. 이미 `.env` 파일이 있으면 덮어쓰지 말고 해당 항목만 추가하거나 수정합니다.

  ```dotenv
  KAKAO_REST_API_KEY=카카오_REST_API_키
  KAKAO_REDIRECT_URI=http://localhost:5173/login/kakao/callback
  KAKAO_CLIENT_SECRET=발급받은_Client_Secret
  ```

- 프론트엔드 키 파일은 필요하지 않습니다. 프론트는 백엔드에서 발급한 OAuth 인증 주소로 이동합니다.
- Kakao Developers에 등록한 Redirect URI는 루트 `.env`의 `KAKAO_REDIRECT_URI`와 완전히 같아야 합니다.
- 동의 항목에서 프로필 닉네임을 사용할 수 있게 설정합니다.
- 백엔드와 프런트엔드를 다시 시작합니다.

프런트에서 카카오 로그인을 누르면 백엔드가 OAuth `state`와 REST API 키를 사용해 인증 주소를 만들고, 브라우저가 그 주소로 이동합니다. 카카오 인증 후 콜백 화면에서 백엔드 로그인 API로 인가 코드를 전달합니다. 설정 키가 누락된 경우 화면에 필요한 환경 변수 위치가 표시됩니다.

백엔드는 인가 코드를 토큰으로 교환한 뒤 카카오 사용자 ID와 닉네임만 사용합니다. 사용자의 서비스 계정은 카카오 사용자 ID에 연결하고, 닉네임을 서비스 프로필 이름으로 저장합니다. 현재 로컬 사용자 테이블의 이메일 필수 제약 때문에 카카오 계정에는 `.invalid` 도메인의 내부용 식별자를 저장하며, 이 주소를 로그인 이메일로 사용하지 않습니다.

이메일을 받지 않는 설정에서는 카카오 이메일과 기존 로컬 이메일의 충돌을 비교할 수 없습니다. 실제 이메일 충돌 검사를 추가하려면 카카오 이메일 동의를 받아야 합니다.

운영 환경에서는 실제 도메인과 등록된 콜백 URL을 사용합니다. Redirect URI는 Kakao Developers에 등록한 값과 `KAKAO_REDIRECT_URI`가 정확히 같아야 합니다.
