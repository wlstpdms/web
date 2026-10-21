# DOJI 의류 상품 결제 API

DOJI는 말랑 학습 앱과 별도 화면으로 제공됩니다. 말랑은 `http://localhost:5173/`, DOJI 마켓은 `http://127.0.0.1:8000/posts`에서 엽니다. Vite 멀티 페이지 빌드에서 DOJI 전용 `doji.html`을 만들고 FastAPI가 `/posts` 경로에 이 파일을 제공합니다.

## 흐름

1. 로그인한 구매자가 `POST /api/payments/clothing/orders`에 `board_idx`를 보냅니다.
2. 서버가 게시글 내용에서 `판매가: 45,000원` 형식의 판매가를 읽고 주문을 저장합니다. 요청의 금액은 받지 않습니다.
3. 브라우저 PortOne V2 SDK가 Toss Payments(신모듈) 카드 결제를 요청합니다.
4. 결제 결과의 `paymentId`를 `POST /api/payments/clothing/verify`로 보내면 서버가 PortOne 결제 단건 조회 API에서 실제 상태, 금액, 통화, 상점 ID를 확인한 뒤 `paid`로 기록합니다.

## 설정

- PortOne 콘솔의 결제 연동 채널에서 PG `토스페이먼츠(신모듈)`을 선택해 채널을 설정합니다.
- 프로젝트 루트 `.env`의 `PORTONE_STORE_ID`, `PORTONE_CHANNEL_KEY`에 상점 ID와 채널 키를 저장합니다.
- 같은 `.env`의 `PORTONE_API_SECRET`에는 PG 자체 시크릿이 아니라 PortOne V2 API Secret을 저장합니다. 이 값은 서버 전용이며 프런트엔드 환경변수로 복사하지 않습니다.
- 결제 API는 DOJI와 같은 `http://127.0.0.1:8000/api`에서 호출합니다.

## 계약

### `POST /api/payments/clothing/orders`

요청: `{ "board_idx": 1 }`

응답: `{ "payment_id": "cloth-…", "order_name": "상품명", "amount": 45000, "currency": "KRW", "store_id": "…", "channel_key": "…" }`

인증 필요. 미등록 상품은 `404`, 판매가 누락·범위 오류는 `422`, 이미 결제된 상품은 `409`, PortOne 공개 설정 누락은 `503`입니다.

### `POST /api/payments/clothing/verify`

요청: `{ "payment_id": "cloth-…" }`

응답: `{ "status": "paid", "payment_id": "cloth-…" }`

인증 필요. 주문 소유자만 확인할 수 있습니다. PortOne API 확인 실패는 `502`, 주문과 결제 정보가 맞지 않으면 `409`입니다.
