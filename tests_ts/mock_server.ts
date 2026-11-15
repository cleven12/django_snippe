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
  phone_number: string;
  customer: Record<string, unknown>;
  payment_url?: string;
  payment_qr_code?: string;
  payment_token?: string;
  webhook_url?: string;
  callback_url?: string;
  redirect_url?: string;
  cancel_url?: string;
  metadata: Record<string, unknown>;
  fee_amount: number;
  net_amount: number;
  psp_reference: string;
  push_count: number;
  expires_at: string;
  created_at: string;
  completed_at?: string;
  failure_reason?: string;
