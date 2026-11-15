import { describe, expect, test } from "bun:test";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import {
  SnippeMockServer,
  buildWebhookPayload2026,
  signWebhookPayload,
} from "./mock_server";

describe("Django <-> Bun Mock Snippe 2026-01-25 End-to-End Integration Bridge", () => {
  test("Django PaymentHelper, PayoutHelper, SessionHelper, and SnippeWebhookView work end-to-end with Snippe 2026-01-25 contract", async () => {
    const mock = new SnippeMockServer();
    const baseUrl = "https://api.snippe.sh/api/v1";
    const headers = {
      Authorization: "Bearer snp_live_bridge_key",
      "Content-Type": "application/json",
    };

    // 1. Generate contract-verified responses from Bun SnippeMockServer
    const payResp = await (
      await mock.fetch(`${baseUrl}/payments`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          payment_type: "mobile",
          details: { amount: 7500, currency: "TZS" },
          phone_number: "0754123456",
          customer: { firstname: "John", lastname: "Sarwi" },
        }),
      })
    ).json();

    const pushResp = await (
      await mock.fetch(`${baseUrl}/payments/${payResp.data.reference}/push`, {
        method: "POST",
        headers,
        body: JSON.stringify({ phone_number: "255754123456" }),
      })
    ).json();

    const payoutResp = await (
      await mock.fetch(`${baseUrl}/payouts/send`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          amount: 10000,
          channel: "mobile",
          recipient_name: "Cleven Godson",
          recipient_phone: "255784111222",
        }),
      })
    ).json();

    const sessionResp = await (
