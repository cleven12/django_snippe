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
