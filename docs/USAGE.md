# Usage Guide (Snippe API 2026-01-25)

Complete integration reference for `django-snippe` aligned with the official [Snippe API `2026-01-25` documentation](https://docs.snippe.sh/docs/2026-01-25).

## Architecture Overview

```text
Customer / Merchant App
   |
   v
PaymentHelper / PayoutHelper / SessionHelper  -->  Snippe API (https://api.snippe.sh)
   |                                                      |
   +-- SnippePayment / SnippePayout / SnippeSession       |
                                                          v
                                            Webhook (POST /payments/webhook/)
                                                          |
                                                          v
                                            HMAC-SHA256 Verification + Idempotency
                                                          |
                                                          v
                                            Update ORM Model + Dispatch Django Signal
```

## Django Settings Reference

| Setting | Required | Default | Description |
|---|---|---|---|
| `SNIPPE_API_KEY` | Yes | - | Your Snippe API key (`Bearer snp_...`) |
| `SNIPPE_WEBHOOK_SECRET` | Recommended | `None` | Webhook signing key used to verify `X-Webhook-Signature` |
| `SNIPPE_API_VERSION` | No | `"2026-01-25"` | Target Snippe API schema version |
| `SNIPPE_BASE_URL` | No | `"https://api.snippe.sh/api/v1"` | Override API base URL for local testing or staging |
| `SNIPPE_TIMEOUT` | No | `30.0` | HTTP request timeout in seconds |
| `SNIPPE_DEFAULT_CURRENCY` | No | `"TZS"` | Default transaction currency (`TZS`, `KES`, `UGX`) |
| `SNIPPE_MIN_PAYMENT_AMOUNT` | No | `500` | Minimum collection amount (500 TZS per 2026-01-25 spec) |
| `SNIPPE_MIN_PAYOUT_AMOUNT` | No | `5000` | Minimum disbursement amount (5,000 TZS per 2026-01-25 spec) |
| `SNIPPE_WEBHOOK_TOLERANCE` | No | `300` | Maximum allowed webhook timestamp age in seconds |
