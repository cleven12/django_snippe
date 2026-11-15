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
  }
  return "MOBILE-MONEY";
}

export function signWebhookPayload(
  rawBody: string,
  timestamp: string,
  signingKey: string
): string {
  const hasher = new Bun.CryptoHasher("sha256", signingKey);
  hasher.update(`${timestamp}.${rawBody}`);
  return hasher.digest("hex");
}

export function verifyWebhookSignature(
  rawBody: string,
  signature: string,
  timestamp: string,
  signingKey: string,
  toleranceSeconds = 300
): boolean {
  if (!signature || !timestamp) return false;
  const ts = Number(timestamp);
  if (!Number.isFinite(ts)) return false;
  const nowSec = Math.floor(Date.now() / 1000);
  if (Math.abs(nowSec - ts) > toleranceSeconds) return false;
  const cleanSig = signature.startsWith("sha256=") ? signature.slice(7) : signature;
  const expected = signWebhookPayload(rawBody, timestamp, signingKey);
  return cleanSig === expected;
}

export function buildWebhookPayload2026(params: {
  id?: string;
  event: string;
  reference: string;
  status: string;
  amount: number;
  currency?: string;
  payment_channel?: string;
  payment_fee?: number;
  customer?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  failure_reason?: string;
  timestamp?: number;
}) {
  const ts = params.timestamp ?? Math.floor(Date.now() / 1000);
  const nowIso = new Date(ts * 1000).toISOString();
  return {
    id: params.id ?? `evt_${crypto.randomUUID().slice(0, 12)}`,
    api_version: "2026-01-25",
    event: params.event,
    reference: params.reference,
    status: params.status,
    amount: {
      value: params.amount,
      currency: params.currency ?? "TZS",
    },
    payment_channel: params.payment_channel ?? "M-PESA",
    payment_fee: params.payment_fee ?? Math.round(params.amount * 0.01),
    customer: params.customer ?? { firstname: "John", lastname: "Doe" },
    metadata: params.metadata ?? {},
    completed_at: params.status === "completed" ? nowIso : null,
    created_at: nowIso,
    timestamp: ts,
    failure_reason: params.failure_reason ?? null,
    data: {
      reference: params.reference,
      status: params.status,
      amount: {
        value: params.amount,
        currency: params.currency ?? "TZS",
      },
      payment_channel: params.payment_channel ?? "M-PESA",
      payment_fee: params.payment_fee ?? Math.round(params.amount * 0.01),
      completed_at: params.status === "completed" ? nowIso : null,
      failure_reason: params.failure_reason ?? null,
    },
  };
}

export class SnippeMockServer {
  public server: ReturnType<typeof Bun.serve> | null = null;
  public payments = new Map<string, StoredPayment>();
  public payouts = new Map<string, StoredPayout>();
  public sessions = new Map<string, StoredSession>();
  public idempotencyStore = new Map<string, { bodyHash: string; status: number; response: unknown }>();
  public keyScopes = new Map<string, Set<ApiScope>>();
  public availableBalance = 10_000_000;
  public totalBalance = 10_500_000;
  public forceRateLimit = false;

  public start(port = 0): string {
    try {
      this.server = Bun.serve({
        port,
        fetch: (req) => this.handleRequest(req),
      });
      return `http://127.0.0.1:${this.server.port}`;
    } catch {
      return "http://snippe.local";
    }
  }

  public async fetch(input: string | URL | Request, init?: RequestInit): Promise<Response> {
    const req = input instanceof Request ? input : new Request(String(input), init);
    return this.handleRequest(req);
  }

  public stop(): void {
    if (this.server) {
      this.server.stop(true);
      this.server = null;
    }
  }

  public reset(): void {
    this.payments.clear();
    this.payouts.clear();
    this.sessions.clear();
    this.idempotencyStore.clear();
    this.keyScopes.clear();
    this.availableBalance = 10_000_000;
    this.totalBalance = 10_500_000;
    this.forceRateLimit = false;
  }

  private errorJson(code: number, error_code: string, message: string): Response {
    return Response.json(
      {
        status: "error",
        code,
        error_code,
        message,
      },
      { status: code }
    );
  }

  private checkScope(apiKey: string, requiredScope: ApiScope): Response | null {
    const configured = this.keyScopes.get(apiKey);
    if (configured && !configured.has(requiredScope)) {
      return this.errorJson(
        403,
        "forbidden_scope",
        `API key lacks required scope: ${requiredScope}`
      );
    }
    return null;
  }

  private async handleRequest(req: Request): Promise<Response> {
    if (this.forceRateLimit) {
      return this.errorJson(429, "rate_limit_exceeded", "Too many requests, please retry later");
    }

    const auth = req.headers.get("Authorization") ?? "";
    if (!auth.startsWith("Bearer snp_") || auth.length <= "Bearer snp_".length) {
      return this.errorJson(401, "unauthorized", "Missing or invalid Authorization Bearer token");
    }
    const apiKey = auth.slice("Bearer ".length).trim();

    const url = new URL(req.url);
    const normalizedPath = url.pathname
      .replace(/^\/api\/v1/, "")
      .replace(/^\/v1/, "")
      .replace(/\/+$/, "") || "/";

    const idempKey = req.headers.get("Idempotency-Key");
    let rawBody = "";
    let parsedBody: Record<string, any> = {};

    if (req.method === "POST") {
      rawBody = await req.text();
      if (rawBody.trim().length > 0) {
        try {
          parsedBody = JSON.parse(rawBody);
        } catch {
          return this.errorJson(400, "validation_error", "Malformed JSON request body");
        }
      }

      if (idempKey !== null) {
        if (idempKey.trim().length === 0 || idempKey.length > 30) {
          return this.errorJson(
            400,
            "validation_error",
            "Idempotency-Key must be between 1 and 30 characters"
          );
        }
        const existing = this.idempotencyStore.get(`${req.method}:${normalizedPath}:${idempKey}`);
        if (existing) {
          if (existing.bodyHash !== rawBody) {
            return this.errorJson(
              422,
              "idempotency_key_mismatch",
              "Idempotency-Key was already used with different request parameters"
            );
          }
          return Response.json(existing.response, { status: existing.status });
        }
      }
    }

    const saveIdempotent = (status: number, bodyObj: unknown): Response => {
      if (idempKey) {
        this.idempotencyStore.set(`${req.method}:${normalizedPath}:${idempKey}`, {
          bodyHash: rawBody,
          status,
          response: bodyObj,
        });
      }
      return Response.json(bodyObj, { status });
    };

    // 1. POST /payments
    if (req.method === "POST" && normalizedPath === "/payments") {
      const scopeErr = this.checkScope(apiKey, "collection:create");
      if (scopeErr) return scopeErr;

      const details = parsedBody.details ?? parsedBody;
      const amount = Number(details.amount ?? parsedBody.amount ?? 0);
      const currency = String(details.currency ?? parsedBody.currency ?? "TZS");
