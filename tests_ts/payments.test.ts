import { afterAll, beforeAll, beforeEach, describe, expect, test } from "bun:test";
import { SnippeMockServer } from "./mock_server";

describe("Snippe 2026-01-25 Payments API Contract", () => {
  const mock = new SnippeMockServer();
  let baseUrl = "";
  const headers = {
    Authorization: "Bearer snp_live_test_key_2026",
    "Content-Type": "application/json",
  };

  beforeAll(() => {
    baseUrl = mock.start();
  });

  afterAll(() => {
    mock.stop();
  });

  beforeEach(() => {
    mock.reset();
  });

  test("POST /v1/payments creates a mobile money payment (USSD push)", async () => {
    const res = await mock.fetch(`${baseUrl}/v1/payments`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        payment_type: "mobile",
        details: { amount: 5000, currency: "TZS" },
        phone_number: "0712345678",
        customer: { firstname: "John", lastname: "Doe", email: "john@example.com" },
        webhook_url: "https://example.com/payments/webhook/",
        metadata: { order_id: "ORD-101" },
      }),
    });
    expect(res.status).toBe(201);
    const json = await res.json();
    expect(json.status).toBe("success");
    expect(json.data.reference).toStartWith("pay_");
    expect(json.data.status).toBe("pending");
    expect(json.data.amount).toBe(5000);
    expect(json.data.currency).toBe("TZS");
    expect(json.data.payment_type).toBe("mobile");
    expect(json.data.push_count).toBe(1);
  });

  test("POST /v1/payments enforces minimum 500 TZS requirement", async () => {
    const res = await mock.fetch(`${baseUrl}/v1/payments`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        payment_type: "mobile",
        details: { amount: 400, currency: "TZS" },
        phone_number: "0712345678",
        customer: { firstname: "John", lastname: "Doe" },
      }),
    });
    expect(res.status).toBe(400);
    const json = await res.json();
    expect(json.status).toBe("error");
    expect(json.code).toBe(400);
    expect(json.error_code).toBe("validation_error");
  });

  test("POST /v1/payments creates a card payment and returns hosted payment_url", async () => {
    const res = await mock.fetch(`${baseUrl}/v1/payments`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        payment_type: "card",
        details: {
          amount: 25000,
          currency: "TZS",
          redirect_url: "https://example.com/success",
          cancel_url: "https://example.com/cancel",
        },
        phone_number: "0712345678",
        customer: { firstname: "Amina", lastname: "Yusuf" },
      }),
    });
    expect(res.status).toBe(201);
    const json = await res.json();
    expect(json.data.payment_type).toBe("card");
    expect(json.data.payment_url).toContain("https://checkout.snippe.sh/pay/");
  });

  test("POST /v1/payments creates a dynamic QR payment and returns QR data + token", async () => {
    const res = await mock.fetch(`${baseUrl}/v1/payments`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        payment_type: "dynamic-qr",
        details: { amount: 12000, currency: "TZS" },
        phone_number: "0712345678",
        customer: { firstname: "Baraka", lastname: "Mushi" },
      }),
    });
    expect(res.status).toBe(201);
    const json = await res.json();
    expect(json.data.payment_type).toBe("dynamic-qr");
    expect(json.data.payment_qr_code).toBeDefined();
    expect(json.data.payment_token).toStartWith("tok_");
  });

  test("POST /v1/payments/{reference}/push triggers manual USSD push on pending payment", async () => {
    const createRes = await mock.fetch(`${baseUrl}/v1/payments`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        payment_type: "mobile",
        details: { amount: 5000, currency: "TZS" },
        phone_number: "0712345678",
        customer: { firstname: "John", lastname: "Doe" },
