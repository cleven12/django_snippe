import { afterAll, beforeAll, beforeEach, describe, expect, test } from "bun:test";
import { SnippeMockServer } from "./mock_server";

describe("Snippe 2026-01-25 Payments API Contract", () => {
  const mock = new SnippeMockServer();
  let baseUrl = "";
