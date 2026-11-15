import { afterAll, beforeAll, beforeEach, describe, expect, test } from "bun:test";
import { SnippeMockServer } from "./mock_server";

describe("Snippe 2026-01-25 Payment Sessions (Hosted Checkout) API Contract", () => {
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

  test("POST /api/v1/sessions creates a fixed-amount hosted checkout session", async () => {
    const res = await mock.fetch(`${baseUrl}/api/v1/sessions`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        amount: 25000,
        currency: "TZS",
        allowed_methods: ["mobile_money", "card"],
        customer: {
          first_name: "Jane",
          last_name: "Doe",
          email: "jane@example.com",
          phone: "+255781000000",
        },
        redirect_url: "https://example.com/thank-you",
        webhook_url: "https://example.com/payments/webhook/",
      }),
    });
    expect(res.status).toBe(201);
