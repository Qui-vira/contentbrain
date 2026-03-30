import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const { transaction_id } = await req.json();

    if (!transaction_id) {
      return NextResponse.json({ success: false, error: "Missing transaction_id" }, { status: 400 });
    }

    const secretKey = process.env.FLW_SECRET_KEY;
    if (!secretKey) {
      return NextResponse.json({ success: false, error: "Payment not configured" }, { status: 503 });
    }

    const res = await fetch(`https://api.flutterwave.com/v3/transactions/${transaction_id}/verify`, {
      headers: {
        Authorization: `Bearer ${secretKey}`,
        "Content-Type": "application/json",
      },
    });

    if (!res.ok) {
      return NextResponse.json({ success: false, error: "Flutterwave API error" }, { status: 502 });
    }

    const data = await res.json();

    if (data.status === "success" && data.data?.status === "successful") {
      return NextResponse.json({
        success: true,
        email: data.data.customer?.email,
        amount: data.data.amount,
        currency: data.data.currency,
      });
    }

    return NextResponse.json({ success: false, error: "Payment not verified" }, { status: 400 });
  } catch {
    return NextResponse.json({ success: false, error: "Verification failed" }, { status: 500 });
  }
}
