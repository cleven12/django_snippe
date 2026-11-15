import { describe, expect, test } from "bun:test";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import {
  SnippeMockServer,
  buildWebhookPayload2026,
  signWebhookPayload,
} from "./mock_server";

describe("Django <-> Bun Mock Snippe 2026-01-25 End-to-End Integration Bridge", () => {
  test("Django PaymentHelper, PayoutHelper, SessionHelper, and SnippeWebhookView work end-to-end with Snippe 2026-01-25 contract", async () => {
    const mock = new SnippeMockServer();
    const baseUrl = "https://api.snippe.sh/api/v1";
    const headers = {
      Authorization: "Bearer snp_live_bridge_key",
      "Content-Type": "application/json",
    };

    // 1. Generate contract-verified responses from Bun SnippeMockServer
    const payResp = await (
      await mock.fetch(`${baseUrl}/payments`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          payment_type: "mobile",
          details: { amount: 7500, currency: "TZS" },
          phone_number: "0754123456",
          customer: { firstname: "John", lastname: "Sarwi" },
        }),
      })
    ).json();

    const pushResp = await (
      await mock.fetch(`${baseUrl}/payments/${payResp.data.reference}/push`, {
        method: "POST",
        headers,
        body: JSON.stringify({ phone_number: "255754123456" }),
      })
    ).json();

    const payoutResp = await (
      await mock.fetch(`${baseUrl}/payouts/send`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          amount: 10000,
          channel: "mobile",
          recipient_name: "Cleven Godson",
          recipient_phone: "255784111222",
        }),
      })
    ).json();

    const sessionResp = await (
      await mock.fetch(`${baseUrl}/sessions`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          amount: 15000,
          currency: "TZS",
          allowed_methods: ["mobile_money", "card"],
        }),
      })
    ).json();

    const webhookSecret = "whsec_bridge_2026_secret";
    const ts = String(Math.floor(Date.now() / 1000));
    const sampleWebhook = buildWebhookPayload2026({
      id: "evt_bridge_001",
      event: "payment.completed",
      reference: payResp.data.reference,
      status: "completed",
      amount: 7500,
      currency: "TZS",
      payment_channel: "M-PESA",
      payment_fee: 75,
      timestamp: Number(ts),
    });
    const rawWebhookBody = JSON.stringify(sampleWebhook);
    const webhookSig = signWebhookPayload(rawWebhookBody, ts, webhookSecret);

    const repoRoot = resolve(import.meta.dir, "..");
    const venvPython = resolve(repoRoot, ".venv/bin/python");
    const pythonBin = existsSync(venvPython) ? venvPython : "python3";

    const pyScript = `
import json, os, httpx, django
from django.conf import settings
from django.core.management import call_command
from django.test import Client

os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"
django.setup()
call_command("migrate", verbosity=0)

settings.SNIPPE_API_KEY = "snp_live_bridge_key"
settings.SNIPPE_WEBHOOK_SECRET = "${webhookSecret}"

import django_snippe.conf as snippe_conf
from snippe import Snippe

responses_map = {
    ("POST", "/api/v1/payments"): json.loads(${JSON.stringify(JSON.stringify(payResp))}),
    ("POST", "/api/v1/payments/${payResp.data.reference}/push"): json.loads(${JSON.stringify(JSON.stringify(pushResp))}),
    ("POST", "/api/v1/payouts/send"): json.loads(${JSON.stringify(JSON.stringify(payoutResp))}),
    ("POST", "/api/v1/sessions"): json.loads(${JSON.stringify(JSON.stringify(sessionResp))}),
}

def handler(request: httpx.Request) -> httpx.Response:
    key = (request.method, request.url.path)
    body = responses_map.get(key, {"status": "success", "data": {}})
    return httpx.Response(200, json=body)

orig_get_client = snippe_conf.get_client
def patched_get_client():
    c = Snippe(api_key="snp_live_bridge_key")
    c._client = httpx.Client(base_url="https://api.snippe.sh/api/v1", transport=httpx.MockTransport(handler))
    return c

import django_snippe.helpers as helpers_mod
import django_snippe.services as services_mod
helpers_mod.get_client = patched_get_client
services_mod.get_client = patched_get_client

from django_snippe.helpers import PaymentHelper, PayoutHelper, SessionHelper
from django_snippe.models import SnippePayment, SnippePayout, SnippeSession, SnippeWebhookEvent

payment = PaymentHelper.create_mobile_payment(
    amount=7500,
    currency="TZS",
    phone_number="0754123456",
    customer_firstname="John",
    customer_lastname="Sarwi",
    idempotency_key="bridge-pay-1",
)
assert payment.reference == "${payResp.data.reference}"
assert payment.status == "pending"

push_res = PaymentHelper.trigger_push(payment.reference, phone_number="255754123456")
assert push_res["status"] == "pushed"

payout = PayoutHelper.create_mobile_payout(
    amount=10000,
    currency="TZS",
    recipient_name="Cleven Godson",
    recipient_phone="255784111222",
    narration="Bonus payout",
    idempotency_key="bridge-po-1",
)
assert payout.reference == "${payoutResp.data.reference}"

session = SessionHelper.create_checkout_session(
    amount=15000,
    currency="TZS",
    allowed_methods=["mobile_money", "card"],
)
assert session.reference == "${sessionResp.data.reference}"
assert session.status == "active"

raw_body = ${JSON.stringify(rawWebhookBody)}
c = Client()
resp = c.post(
    "/payments/webhook/",
    data=raw_body,
    content_type="application/json",
    HTTP_X_WEBHOOK_SIGNATURE="${webhookSig}",
    HTTP_X_WEBHOOK_TIMESTAMP="${ts}",
)
assert resp.status_code == 200, f"Webhook failed: {resp.content}"
payment.refresh_from_db()
assert payment.status == "completed"
assert payment.fee_amount == 75
assert payment.payment_channel == "M-PESA"
assert SnippeWebhookEvent.objects.filter(reference=payment.reference, processed=True).exists()
print("BRIDGE_OK")
`;

    const proc = Bun.spawn([pythonBin, "-c", pyScript], {
      cwd: repoRoot,
      stdout: "pipe",
      stderr: "pipe",
    });
    const stdout = await new Response(proc.stdout).text();
    const stderr = await new Response(proc.stderr).text();
    const exitCode = await proc.exited;

    if (exitCode !== 0) {
      throw new Error(`Django bridge failed: ${stderr}`);
    }
    expect(exitCode).toBe(0);
    expect(stdout).toContain("BRIDGE_OK");
  });
});
