import { afterAll, beforeAll, beforeEach, describe, expect, test } from "bun:test";
import { SnippeMockServer, detectMobileProvider } from "./mock_server";

describe("Snippe 2026-01-25 Payouts (Disbursements) API Contract", () => {
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

  test("Mobile money provider auto-detection covers M-Pesa, Airtel Money, Mixx by Yas, HaloPesa", () => {
    expect(detectMobileProvider("255754123456")).toBe("M-PESA");
    expect(detectMobileProvider("0784123456")).toBe("AIRTEL-MONEY");
    expect(detectMobileProvider("0713123456")).toBe("MIXX-BY-YAS");
    expect(detectMobileProvider("0622123456")).toBe("HALOPESA");
  });

  test("POST /v1/payouts/send creates a mobile payout and deducts balance + fee immediately", async () => {
    const initialBalance = mock.availableBalance;
    const res = await mock.fetch(`${baseUrl}/v1/payouts/send`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        amount: 50000,
        channel: "mobile",
        recipient_phone: "255781000000",
        recipient_name: "Jane Doe",
        narration: "Salary payment January 2026",
        metadata: { employee_id: "EMP-001" },
      }),
    });
    expect(res.status).toBe(201);
    const json = await res.json();
    expect(json.data.reference).toStartWith("po_");
    expect(json.data.amount).toEqual({ value: 50000, currency: "TZS" });
    expect(json.data.fees).toEqual({ value: 500, currency: "TZS" });
    expect(json.data.total).toEqual({ value: 50500, currency: "TZS" });
    expect(json.data.channel).toEqual({ type: "mobile", provider: "AIRTEL-MONEY" });
    expect(mock.availableBalance).toBe(initialBalance - 50500);
  });

  test("POST /v1/payouts/send enforces minimum 5,000 TZS requirement", async () => {
    const res = await mock.fetch(`${baseUrl}/v1/payouts/send`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        amount: 2000,
        channel: "mobile",
        recipient_phone: "255781000000",
        recipient_name: "Jane Doe",
      }),
    });
    expect(res.status).toBe(400);
    const json = await res.json();
    expect(json.error_code).toBe("validation_error");
  });

  test("POST /v1/payouts/send creates a bank transfer payout", async () => {
    const res = await mock.fetch(`${baseUrl}/v1/payouts/send`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        amount: 100000,
        channel: "bank",
        recipient_bank: "CRDB",
        recipient_account: "0150000000000",
        recipient_name: "Vendor Ltd",
        narration: "Invoice settlement",
      }),
    });
    expect(res.status).toBe(201);
    const json = await res.json();
    expect(json.data.channel).toEqual({ type: "bank", provider: "CRDB" });
    expect(json.data.recipient.bank).toBe("CRDB");
    expect(json.data.recipient.account).toBe("0150000000000");
  });

  test("GET /v1/payouts/fee, /v1/payouts, and /v1/payouts/{reference}", async () => {
    const feeRes = await mock.fetch(`${baseUrl}/v1/payouts/fee?amount=20000`, { headers });
    expect(feeRes.status).toBe(200);
    const feeJson = await feeRes.json();
    expect(feeJson.data.total_amount).toBe(20500);

    const createRes = await mock.fetch(`${baseUrl}/v1/payouts/send`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        amount: 10000,
        channel: "mobile",
