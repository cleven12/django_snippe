# Usage Guide (Snippe API 2026-01-25)

Complete integration reference for `django-snippe` aligned with the official [Snippe API `2026-01-25` documentation](https://docs.snippe.sh/docs/2026-01-25).

## Architecture Overview

```text
Customer / Merchant App
   |
   v
PaymentHelper / PayoutHelper / SessionHelper  -->  Snippe API (https://api.snippe.sh)
   |                                                      |
