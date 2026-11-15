/**
 * Mock Snippe API Server (Version 2026-01-25) implemented in Bun + TypeScript.
 * Enforces official Snippe 2026-01-25 schemas, scopes, minimum amounts,
 * idempotency keys, and HMAC-SHA256 webhook signatures for fast local testing.
 */

export type ApiScope =
  | "collection:read"
  | "collection:create"
  | "disbursement:read"
  | "disbursement:create";

export interface StoredPayment {
  reference: string;
  status: "pending" | "completed" | "failed" | "expired" | "voided";
  amount: number;
  currency: "TZS" | "KES" | "UGX";
  payment_type: "mobile" | "card" | "dynamic-qr";
