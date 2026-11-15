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
