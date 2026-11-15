import { afterAll, beforeAll, beforeEach, describe, expect, test } from "bun:test";
import { SnippeMockServer } from "./mock_server";

describe("Snippe 2026-01-25 Error Envelopes, Scopes, Idempotency & Rate Limits", () => {
  const mock = new SnippeMockServer();
  let baseUrl = "";

  beforeAll(() => {
    baseUrl = mock.start();
  });

  afterAll(() => {
    mock.stop();
  });

  beforeEach(() => {
    mock.reset();
  });

  test("Returns 401 Unauthorized when Authorization Bearer header is missing or invalid", async () => {
    const res = await mock.fetch(`${baseUrl}/v1/payments/balance`);
    expect(res.status).toBe(401);
    const json = await res.json();
    expect(json).toEqual({
      status: "error",
      code: 401,
      error_code: "unauthorized",
      message: "Missing or invalid Authorization Bearer token",
    });
  });

  test("Returns 403 Forbidden when API key lacks required scope (e.g. disbursement:create)", async () => {
    const readOnlyKey = "snp_scoped_readonly";
    mock.keyScopes.set(readOnlyKey, new Set(["collection:read"]));

    const res = await mock.fetch(`${baseUrl}/v1/payouts/send`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${readOnlyKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        amount: 5000,
        channel: "mobile",
        recipient_name: "John Doe",
        recipient_phone: "255712345678",
      }),
    });
    expect(res.status).toBe(403);
    const json = await res.json();
    expect(json.error_code).toBe("forbidden_scope");
  });

  test("Supports Idempotency-Key deduplication and returns 422 on payload mismatch", async () => {
    const headers = {
      Authorization: "Bearer snp_live_key",
      "Content-Type": "application/json",
      "Idempotency-Key": "idem-order-2026-01",
    };
    const body1 = JSON.stringify({
      payment_type: "mobile",
      details: { amount: 5000, currency: "TZS" },
      phone_number: "0712345678",
      customer: { firstname: "John", lastname: "Doe" },
    });

