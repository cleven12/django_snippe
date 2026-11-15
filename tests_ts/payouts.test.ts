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
