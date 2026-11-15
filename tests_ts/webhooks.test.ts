import { describe, expect, test } from "bun:test";
import {
  buildWebhookPayload2026,
  signWebhookPayload,
  verifyWebhookSignature,
} from "./mock_server";

describe("Snippe 2026-01-25 Webhooks & HMAC-SHA256 Signature Verification", () => {
  const secret = "whsec_snippe_2026_secret_key";

  test("2026-01-25 webhook payload wraps amount as { value, currency } object", () => {
    const payload = buildWebhookPayload2026({
      event: "payment.completed",
      reference: "pay_2026_abc",
      status: "completed",
      amount: 50000,
      currency: "TZS",
    });
