import { NextRequest, NextResponse } from "next/server";

// POST — create a new BNB chain payment address
export async function POST(req: NextRequest) {
  try {
    const { serviceName, amount } = await req.json();

    const apiKey = process.env.BLOCKRADAR_API_KEY;
    const walletId = process.env.BLOCKRADAR_WALLET_ID;

    if (!apiKey || !walletId) {
      return NextResponse.json(
        { error: "Crypto payments not yet configured. Contact @Quivira_Ophir on Telegram." },
        { status: 503 }
      );
    }

    const label = `QV-${String(serviceName).replace(/\s+/g, "-").toLowerCase().slice(0, 40)}-${Date.now()}`;

    const res = await fetch(`https://api.blockradar.co/v1/wallets/${walletId}/addresses`, {
      method: "POST",
      headers: {
        "x-api-key": apiKey,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ network: "bnb-smart-chain", label }),
    });

    const data = await res.json();

    if (!res.ok) {
      return NextResponse.json(
        { error: data.message || "Failed to create payment address" },
        { status: res.status }
      );
    }

    const address = data.data?.address || data.address;
    const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=${encodeURIComponent(address)}&bgcolor=ffffff&color=000000`;

    return NextResponse.json({
      address,
      qrCodeUrl,
      network: "BNB Chain",
      tokens: ["USDC", "BUSD"],
    });
  } catch {
    return NextResponse.json({ error: "Failed to create payment address" }, { status: 500 });
  }
}

// GET — poll address for confirmed transactions
export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const address = searchParams.get("address");
  const check = searchParams.get("check");

  if (!address || !check) {
    return NextResponse.json({ confirmed: false });
  }

  const apiKey = process.env.BLOCKRADAR_API_KEY;
  if (!apiKey) {
    return NextResponse.json({ confirmed: false });
  }

  try {
    const res = await fetch(
      `https://api.blockradar.co/v1/addresses/${encodeURIComponent(address)}/transactions`,
      { headers: { "x-api-key": apiKey } }
    );

    if (!res.ok) return NextResponse.json({ confirmed: false });

    const data = await res.json();
    const transactions: Record<string, unknown>[] = data.data || data.transactions || [];

    const confirmed = transactions.some(
      (tx) => tx.status === "confirmed" || tx.status === "success"
    );

    return NextResponse.json({ confirmed });
  } catch {
    return NextResponse.json({ confirmed: false });
  }
}
