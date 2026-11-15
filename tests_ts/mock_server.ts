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
      const paymentType = String(parsedBody.payment_type ?? "mobile") as StoredPayment["payment_type"];
      const phone = String(parsedBody.phone_number ?? "");

      if (!Number.isInteger(amount) || amount < 500) {
        return this.errorJson(400, "validation_error", "Minimum payment amount is 500 TZS");
      }
      if (!["TZS", "KES", "UGX"].includes(currency)) {
        return this.errorJson(400, "validation_error", `Unsupported currency: ${currency}`);
      }
      if (!["mobile", "card", "dynamic-qr"].includes(paymentType)) {
        return this.errorJson(400, "validation_error", `Unsupported payment_type: ${paymentType}`);
      }
      if (paymentType === "mobile" && !phone) {
        return this.errorJson(400, "validation_error", "phone_number is required for mobile payments");
      }

      const reference = `pay_${crypto.randomUUID().slice(0, 12)}`;
      const now = new Date();
      const expires = new Date(now.getTime() + 4 * 60 * 60 * 1000);
      const fee = Math.round(amount * 0.01);

      const record: StoredPayment = {
        reference,
        status: "pending",
        amount,
        currency: currency as StoredPayment["currency"],
        payment_type: paymentType,
        phone_number: phone,
        customer: parsedBody.customer ?? {},
        payment_url:
          paymentType === "card" ? `https://checkout.snippe.sh/pay/${reference}` : undefined,
        payment_qr_code:
          paymentType === "dynamic-qr" ? `iVBORw0KGgoAAAANSUhEUgAAAAUA_${reference}` : undefined,
        payment_token: paymentType === "dynamic-qr" ? `tok_${reference}` : undefined,
        webhook_url: parsedBody.webhook_url,
        callback_url: details.callback_url,
        redirect_url: details.redirect_url,
        cancel_url: details.cancel_url,
        metadata: parsedBody.metadata ?? {},
        fee_amount: fee,
        net_amount: amount - fee,
        psp_reference: `psp_${reference}`,
        push_count: paymentType === "mobile" ? 1 : 0,
        expires_at: expires.toISOString(),
        created_at: now.toISOString(),
      };
      this.payments.set(reference, record);
      return saveIdempotent(201, { status: "success", data: record });
    }

    // 2. GET /payments/balance
    if (req.method === "GET" && normalizedPath === "/payments/balance") {
      const scopeErr = this.checkScope(apiKey, "collection:read");
      if (scopeErr) return scopeErr;

      return Response.json({
        status: "success",
        data: {
          available_balance: this.availableBalance,
          balance: this.totalBalance,
          currency: "TZS",
        },
      });
    }

    // 3. GET /payments/search
    if (req.method === "GET" && normalizedPath === "/payments/search") {
      const scopeErr = this.checkScope(apiKey, "collection:read");
      if (scopeErr) return scopeErr;

      const q = (url.searchParams.get("q") ?? "").toLowerCase();
      const limit = Math.min(100, Number(url.searchParams.get("limit") ?? 20));
      const offset = Number(url.searchParams.get("offset") ?? 0);

      const matched = Array.from(this.payments.values()).filter(
        (p) =>
          p.reference.toLowerCase().includes(q) ||
          p.phone_number.toLowerCase().includes(q) ||
          JSON.stringify(p.customer).toLowerCase().includes(q)
      );

      return Response.json({
        status: "success",
        data: {
          payments: matched.slice(offset, offset + limit),
          total: matched.length,
          limit,
          offset,
        },
      });
    }

    // 4. GET /payments
    if (req.method === "GET" && normalizedPath === "/payments") {
      const scopeErr = this.checkScope(apiKey, "collection:read");
      if (scopeErr) return scopeErr;

      const limit = Math.min(100, Number(url.searchParams.get("limit") ?? 20));
      const offset = Number(url.searchParams.get("offset") ?? 0);
      const all = Array.from(this.payments.values());

      return Response.json({
        status: "success",
        data: {
          payments: all.slice(offset, offset + limit),
          limit,
          offset,
        },
      });
    }

    // 5. POST /payments/:reference/push
    const pushMatch = normalizedPath.match(/^\/payments\/([^/]+)\/push$/);
    if (req.method === "POST" && pushMatch) {
      const scopeErr = this.checkScope(apiKey, "collection:create");
      if (scopeErr) return scopeErr;

      const reference = pushMatch[1];
      const payment = this.payments.get(reference);
      if (!payment) {
        return this.errorJson(404, "not_found", `Payment ${reference} not found`);
      }
      if (payment.status !== "pending") {
        return this.errorJson(409, "conflict", `Cannot trigger push for ${payment.status} payment`);
      }
      payment.push_count += 1;
      if (parsedBody.phone_number) {
        payment.phone_number = String(parsedBody.phone_number);
      }
      return Response.json({
        status: "success",
        data: {
          reference: payment.reference,
          status: "pushed",
          push_count: payment.push_count,
          phone_number: payment.phone_number,
        },
      });
    }

    // 6. GET /payments/:reference
    const getPayMatch = normalizedPath.match(/^\/payments\/([^/]+)$/);
    if (req.method === "GET" && getPayMatch) {
      const scopeErr = this.checkScope(apiKey, "collection:read");
      if (scopeErr) return scopeErr;

      const reference = getPayMatch[1];
      const payment = this.payments.get(reference);
      if (!payment) {
        return this.errorJson(404, "not_found", `Payment ${reference} not found`);
      }
      return Response.json({ status: "success", data: payment });
    }

    // 7. POST /payouts/send
    if (req.method === "POST" && normalizedPath === "/payouts/send") {
      const scopeErr = this.checkScope(apiKey, "disbursement:create");
      if (scopeErr) return scopeErr;

      const amount = Number(parsedBody.amount ?? 0);
      const channel = String(parsedBody.channel ?? "mobile") as "mobile" | "bank";
      const recipientName = String(parsedBody.recipient_name ?? "").trim();

      if (!Number.isInteger(amount) || amount < 5000) {
        return this.errorJson(400, "validation_error", "Minimum payout amount is 5000 TZS");
      }
      if (recipientName.length < 2) {
        return this.errorJson(400, "validation_error", "recipient_name is required");
      }
      if (!["mobile", "bank"].includes(channel)) {
        return this.errorJson(400, "validation_error", `Unsupported payout channel: ${channel}`);
      }

      const feeValue = channel === "bank" ? 1500 : 500;
      const totalValue = amount + feeValue;
      if (totalValue > this.availableBalance) {
        return this.errorJson(400, "insufficient_balance", "Insufficient balance for payout + fee");
      }

      this.availableBalance -= totalValue;
      const reference = `po_${crypto.randomUUID().slice(0, 12)}`;
      const provider =
        channel === "mobile"
          ? detectMobileProvider(String(parsedBody.recipient_phone ?? ""))
          : String(parsedBody.recipient_bank ?? "CRDB");

      const payout: StoredPayout = {
        reference,
        status: "pending",
        amount: { value: amount, currency: "TZS" },
        fees: { value: feeValue, currency: "TZS" },
        total: { value: totalValue, currency: "TZS" },
        channel: { type: channel, provider },
        recipient: {
          name: recipientName,
          phone: parsedBody.recipient_phone,
          bank: parsedBody.recipient_bank,
          account: parsedBody.recipient_account,
        },
        narration: parsedBody.narration,
        webhook_url: parsedBody.webhook_url,
        metadata: parsedBody.metadata ?? {},
        created_at: new Date().toISOString(),
      };
      this.payouts.set(reference, payout);
      return saveIdempotent(201, { status: "success", data: payout });
    }

    // 8. GET /payouts/fee
    if (req.method === "GET" && normalizedPath === "/payouts/fee") {
      const scopeErr = this.checkScope(apiKey, "disbursement:read");
      if (scopeErr) return scopeErr;

      const amount = Number(url.searchParams.get("amount") ?? 5000);
      const feeAmount = 500;
      return Response.json({
        status: "success",
        data: {
          amount,
          fee_amount: feeAmount,
          total_amount: amount + feeAmount,
          currency: "TZS",
        },
      });
    }

    // 9. GET /payouts
    if (req.method === "GET" && normalizedPath === "/payouts") {
      const scopeErr = this.checkScope(apiKey, "disbursement:read");
      if (scopeErr) return scopeErr;

      const limit = Math.min(100, Number(url.searchParams.get("limit") ?? 20));
      const offset = Number(url.searchParams.get("offset") ?? 0);
      const items = Array.from(this.payouts.values());

      return Response.json({
        status: "success",
        data: {
          items: items.slice(offset, offset + limit),
          total: items.length,
          limit,
          offset,
        },
      });
    }

    // 10. GET /payouts/:reference
    const getPayoutMatch = normalizedPath.match(/^\/payouts\/([^/]+)$/);
    if (req.method === "GET" && getPayoutMatch) {
      const scopeErr = this.checkScope(apiKey, "disbursement:read");
      if (scopeErr) return scopeErr;

      const reference = getPayoutMatch[1];
      const payout = this.payouts.get(reference);
      if (!payout) {
        return this.errorJson(404, "not_found", `Payout ${reference} not found`);
      }
      return Response.json({ status: "success", data: payout });
    }

    // 11. POST /sessions
    if (req.method === "POST" && normalizedPath === "/sessions") {
      const scopeErr = this.checkScope(apiKey, "collection:create");
      if (scopeErr) return scopeErr;

      const allowCustom = Boolean(parsedBody.allow_custom_amount ?? false);
      const amount = parsedBody.amount !== undefined ? Number(parsedBody.amount) : null;
      if (!allowCustom && (amount === null || !Number.isInteger(amount) || amount < 500)) {
        return this.errorJson(
          400,
          "validation_error",
          "Session amount must be at least 500 TZS when allow_custom_amount is false"
        );
      }

      const reference = `ses_${crypto.randomUUID().slice(0, 12)}`;
      const now = new Date();
      const expires = new Date(now.getTime() + 60 * 60 * 1000);
      const session: StoredSession = {
        reference,
        amount,
        currency: String(parsedBody.currency ?? "TZS"),
        allow_custom_amount: allowCustom,
        allowed_methods: Array.isArray(parsedBody.allowed_methods)
          ? parsedBody.allowed_methods
          : ["mobile_money"],
        status: "active",
        checkout_url: `https://checkout.snippe.sh/s/${reference}`,
        redirect_url: parsedBody.redirect_url,
        webhook_url: parsedBody.webhook_url,
        customer: parsedBody.customer,
        metadata: parsedBody.metadata ?? {},
        expires_at: expires.toISOString(),
        created_at: now.toISOString(),
      };
      this.sessions.set(reference, session);
      return saveIdempotent(201, { status: "success", data: session });
    }

    // 12. GET /sessions
    if (req.method === "GET" && normalizedPath === "/sessions") {
      const scopeErr = this.checkScope(apiKey, "collection:read");
      if (scopeErr) return scopeErr;

      const limit = Math.min(100, Number(url.searchParams.get("limit") ?? 20));
      const offset = Number(url.searchParams.get("offset") ?? 0);
      const all = Array.from(this.sessions.values());

      return Response.json({
        status: "success",
        data: {
          sessions: all.slice(offset, offset + limit),
          total: all.length,
          limit,
          offset,
        },
      });
    }

    // 13. POST /sessions/:reference/cancel
    const cancelSessionMatch = normalizedPath.match(/^\/sessions\/([^/]+)\/cancel$/);
    if (req.method === "POST" && cancelSessionMatch) {
      const scopeErr = this.checkScope(apiKey, "collection:create");
      if (scopeErr) return scopeErr;

      const reference = cancelSessionMatch[1];
      const session = this.sessions.get(reference);
      if (!session) {
        return this.errorJson(404, "not_found", `Session ${reference} not found`);
      }
      session.status = "cancelled";
      return Response.json({ status: "success", data: session });
    }

    // 14. GET /sessions/:reference
    const getSessionMatch = normalizedPath.match(/^\/sessions\/([^/]+)$/);
    if (req.method === "GET" && getSessionMatch) {
      const scopeErr = this.checkScope(apiKey, "collection:read");
      if (scopeErr) return scopeErr;

      const reference = getSessionMatch[1];
      const session = this.sessions.get(reference);
      if (!session) {
        return this.errorJson(404, "not_found", `Session ${reference} not found`);
      }
      return Response.json({ status: "success", data: session });
    }

    return this.errorJson(404, "not_found", `Endpoint ${req.method} ${url.pathname} not found`);
  }
}
