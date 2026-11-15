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

