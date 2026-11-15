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
