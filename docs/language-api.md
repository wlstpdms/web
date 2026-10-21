# Language learning API

Endpoints are available under `/api` and without `/api` for deployments whose proxy strips that prefix. Requests and responses use UTF-8 JSON. Account-specific data uses the existing `EN_AT` login cookie. The dashboard, catalog, and plan catalog are readable while logged out; mutations require login. Premium lesson details require an active trial or premium entitlement and otherwise return 403 with `{"detail":{"code":"premium_required","message":"Premium plan required"}}`.

## Dashboard

`GET /api/learning/dashboard`

```json
{
  "user": {"display_name": "민지", "level": "beginner"},
  "progress": {"streak_days": 2, "xp": 40, "weekly": [{"day": "2026-10-20", "xp": 20}]},
  "next_lesson": {"id": 1, "title": "카페에서 주문하기", "subtitle": "travel", "duration_minutes": 5, "xp_reward": 20},
  "groups": [{"id": 1, "name": "점심 영어", "members": 3, "activity": "함께 영어를 공부해요"}],
  "credits": {"available": 1, "daily_limit": 3},
  "subscription": {"plan": "free", "trial_days_left": 0}
}
```

Logged-out values are initialized (`display_name` is `학습자`; counts are zero; `weekly` and `groups` are empty). `weekly` contains a seven-day sequence with ISO date strings and XP totals.

## Lessons

`GET /api/learning/lessons` returns `{ "items": [LessonSummary] }`. The first read seeds three sample Korean-first lessons. Summary shape:

```json
{"id":1,"title":"카페에서 주문하기","level":"beginner","category":"travel","duration_minutes":5,"premium":false,"progress":null}
```

`GET /api/learning/lessons/{id}` returns the summary fields plus `steps`, an array of `{ "id", "kind", "prompt_ko", "answer_en", "explanation_ko", "order" }`.

`POST /api/learning/lessons/{id}/complete` takes no body. It marks every lesson step complete and awards 20 XP once per lesson:

```json
{"xp_earned":20,"streak_days":1,"credits":0}
```

Repeat completion returns `xp_earned: 0`. The progress API `PUT /api/language/lessons/{id}/progress` accepts `{"completed_steps":1,"total_steps":2}` and responds with `lesson_id`, the saved counts, `status` (`in_progress` or `completed`), and `xp_awarded`.

## Study groups

`GET /api/study-groups` returns `{ "items": [Group] }`; logged-out visitors get an empty list. `POST /api/study-groups` requires login and accepts `{"name":"점심 영어"}` (optional `description`, up to 500 characters). It returns HTTP 201 and `{ "id", "name", "description", "join_code", "member_count", "created_at" }`. The creator is the first member. `POST /api/language/groups/join` accepts `{"join_code":"..."}` to join.

## Plan, trial, and PortOne checkout

`GET /api/billing/plans` returns `{ "items": [...], "checkout_mode":"portone_v2" }`. Plan entries contain `id`, `name`, `price` (KRW), `currency`, `interval`, `description`, `badge`, `saving`, and `features`. The catalog includes free access, Plus monthly (9,900 KRW), Plus quarterly (26,900 KRW), and Plus yearly (79,000 KRW).

`POST /api/billing/checkout` requires login and accepts `{"plan_id":"premium_monthly"}` (or quarterly/yearly). The server creates a pending order and returns `payment_id`, `order_name`, server-selected `amount`, `currency`, `store_id`, and `channel_key` for the PortOne Browser SDK. The client must not activate an entitlement from the checkout response.

`POST /api/billing/verify` requires login and accepts `{"payment_id":"..."}`. The server fetches the payment from PortOne V2 and checks paid status, payment ID, currency, Store ID, and the amount against its saved order before activating the selected plan. Verification is idempotent for an already-paid order. PortOne Store ID, Toss Payments channel key, and PortOne V2 API secret must be configured server-side; absent configuration returns 503. The legacy demo endpoint `/api/language/checkout` is disabled and returns 410.

`POST /api/language/trial` starts a one-time seven-day trial. `GET /api/language/entitlement` returns the same entitlement object. Checkout changes only local demo state; no payment provider, charge, or external service is used.

## Rewarded-ad demo

`POST /api/rewards/ad-credit` requires login and simulates a completed rewarded ad. It does not contact an ad network:

```json
{"credits":1,"available":1,"mode":"demo"}
```

`available` is the user's resulting ad credit balance.
