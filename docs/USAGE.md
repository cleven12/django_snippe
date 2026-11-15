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
