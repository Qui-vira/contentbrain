import { NextRequest, NextResponse } from "next/server";
import { createHmac } from "crypto";

export async function POST(req: NextRequest) {
  try {
    const body = await req.text();
    const signature = req.headers.get("x-blockradar-signature") || "";
    const webhookSecret = process.env.BLOCKRADAR_WEBHOOK_SECRET;

    // Verify HMAC signature if secret is configured
    if (webhookSecret) {
      const expected = createHmac("sha256", webhookSecret).update(body).digest("hex");
      if (signature !== expected) {
        return NextResponse.json({ error: "Invalid signature" }, { status: 401 });
      }
    }

    const event = JSON.parse(body) as Record<string, unknown>;
    const eventType = (event.event || event.type) as string;

    if (eventType === "transaction.confirmed" || eventType === "deposit.confirmed") {
      const txData = (event.data || {}) as Record<string, unknown>;
      console.log("[Blockradar] Payment confirmed:", {
        address: txData.address,
        amount: txData.amount,
        token: txData.token,
        txHash: txData.hash,
        timestamp: new Date().toISOString(),
      });
      // TODO: trigger email notification and unlock customer access
    }

    return NextResponse.json({ received: true });
  } catch {
    return NextResponse.json({ error: "Webhook processing failed" }, { status: 500 });
  }
}
