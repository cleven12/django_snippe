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
}

export interface StoredPayout {
  reference: string;
  status: "pending" | "completed" | "failed" | "reversed";
  amount: { value: number; currency: string };
  fees: { value: number; currency: string };
  total: { value: number; currency: string };
  channel: { type: "mobile" | "bank"; provider: string };
  recipient: {
    name: string;
    phone?: string;
    bank?: string;
    account?: string;
  };
  narration?: string;
  webhook_url?: string;
  metadata: Record<string, unknown>;
  created_at: string;
  completed_at?: string;
  failure_reason?: string;
}

export interface StoredSession {
  reference: string;
  amount: number | null;
  currency: string;
  allow_custom_amount: boolean;
  allowed_methods: string[];
  status: "active" | "completed" | "expired" | "cancelled";
  checkout_url: string;
  redirect_url?: string;
  webhook_url?: string;
  customer?: Record<string, unknown>;
  metadata: Record<string, unknown>;
  expires_at: string;
  created_at: string;
  completed_at?: string;
}

export function detectMobileProvider(phone: string): string {
  const digits = phone.replace(/\D/g, "");
  const local = digits.startsWith("255") ? "0" + digits.slice(3) : digits;
  if (local.startsWith("074") || local.startsWith("075") || local.startsWith("076")) {
    return "M-PESA";
  }
  if (local.startsWith("078") || local.startsWith("068") || local.startsWith("069")) {
    return "AIRTEL-MONEY";
  }
  if (local.startsWith("071") || local.startsWith("065") || local.startsWith("067")) {
    return "MIXX-BY-YAS";
  }
  if (local.startsWith("062") || local.startsWith("061")) {
    return "HALOPESA";
