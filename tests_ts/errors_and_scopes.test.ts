import { afterAll, beforeAll, beforeEach, describe, expect, test } from "bun:test";
import { SnippeMockServer } from "./mock_server";

describe("Snippe 2026-01-25 Error Envelopes, Scopes, Idempotency & Rate Limits", () => {
  const mock = new SnippeMockServer();
  let baseUrl = "";

  beforeAll(() => {
    baseUrl = mock.start();
  });

  afterAll(() => {
