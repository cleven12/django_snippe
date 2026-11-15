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

    expect(payload.api_version).toBe("2026-01-25");
    expect(payload.amount).toEqual({ value: 50000, currency: "TZS" });
    expect(payload.data.amount).toEqual({ value: 50000, currency: "TZS" });
    expect(payload.data.reference).toBe("pay_2026_abc");
  });

  test("HMAC-SHA256 X-Webhook-Signature validates authentic payload and rejects tampered body", () => {
    const ts = String(Math.floor(Date.now() / 1000));
    const payload = buildWebhookPayload2026({
      event: "payment.completed",
      reference: "pay_sig_1",
      status: "completed",
      amount: 15000,
      timestamp: Number(ts),
    });
    const rawBody = JSON.stringify(payload);
    const sig = signWebhookPayload(rawBody, ts, secret);
