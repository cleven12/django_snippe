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
    const json = await res.json();
    expect(json.data.reference).toStartWith("ses_");
    expect(json.data.status).toBe("active");
    expect(json.data.amount).toBe(25000);
    expect(json.data.checkout_url).toContain("https://checkout.snippe.sh/s/");
  });

  test("POST /api/v1/sessions supports allow_custom_amount without fixed amount", async () => {
    const res = await mock.fetch(`${baseUrl}/api/v1/sessions`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        allow_custom_amount: true,
        currency: "TZS",
        allowed_methods: ["mobile_money"],
      }),
    });
    expect(res.status).toBe(201);
    const json = await res.json();
    expect(json.data.allow_custom_amount).toBe(true);
    expect(json.data.amount).toBeNull();
  });

  test("GET /api/v1/sessions, GET /api/v1/sessions/:reference, and POST /api/v1/sessions/:reference/cancel", async () => {
    const createRes = await mock.fetch(`${baseUrl}/api/v1/sessions`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        amount: 10000,
        currency: "TZS",
      }),
    });
    const session = (await createRes.json()).data;

    const getRes = await mock.fetch(`${baseUrl}/api/v1/sessions/${session.reference}`, { headers });
    expect(getRes.status).toBe(200);
    expect((await getRes.json()).data.status).toBe("active");

    const listRes = await mock.fetch(`${baseUrl}/api/v1/sessions`, { headers });
    expect(listRes.status).toBe(200);
    expect((await listRes.json()).data.sessions.length).toBe(1);

