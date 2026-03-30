import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    // Flutterwave verifies webhooks via a secret hash header, not HMAC
    const signature = req.headers.get("verif-hash");
    const secretHash = process.env.FLW_SECRET_HASH;

    if (secretHash && signature !== secretHash) {
      return NextResponse.json({ error: "Invalid signature" }, { status: 401 });
    }

    const event = await req.json() as Record<string, unknown>;
    const eventType = event.event as string;
    const data = (event.data || {}) as Record<string, unknown>;

    if (eventType === "charge.completed" && data.status === "successful") {
      console.log("[Flutterwave] Payment confirmed:", {
        txRef: data.tx_ref,
        txId: data.id,
        amount: data.amount,
        currency: data.currency,
        email: (data.customer as Record<string, unknown>)?.email,
        timestamp: new Date().toISOString(),
      });
      // TODO: unlock access, trigger email, update DB
    }

    return NextResponse.json({ received: true });
  } catch {
    return NextResponse.json({ error: "Webhook processing failed" }, { status: 500 });
  }
}
