import { NextRequest, NextResponse } from "next/server";

const BOT_TOKEN = process.env.OUTREACH_BOT_TOKEN || "";
const WEBHOOK_SECRET = process.env.TELEGRAM_WEBHOOK_SECRET || "";
const SUPABASE_URL = process.env.OUTREACH_SUPABASE_URL || "";
const SUPABASE_KEY = process.env.OUTREACH_SUPABASE_ANON_KEY || "";

const TABLES: Record<string, string> = {
  al: "altara_outreach_drafts",
  kl: "kol_outreach_drafts",
};

const PIPELINE_LABELS: Record<string, string> = {
  al: "Altara",
  kl: "KOL",
};

function sbHeaders() {
  return {
    apikey: SUPABASE_KEY,
    Authorization: `Bearer ${SUPABASE_KEY}`,
    "Content-Type": "application/json",
    Prefer: "return=representation",
  };
}

async function answerCallback(callbackId: string, text: string) {
  try {
    await fetch(
      `https://api.telegram.org/bot${BOT_TOKEN}/answerCallbackQuery`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ callback_query_id: callbackId, text }),
      }
    );
  } catch {
    // Silently ignore — callback may have expired
  }
}

async function editMessage(chatId: number, messageId: number, text: string) {
  try {
    await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/editMessageText`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        message_id: messageId,
        text,
        parse_mode: "HTML",
      }),
    });
  } catch {
    // Silently ignore
  }
}

export async function POST(req: NextRequest) {
  const secret = req.headers.get("x-telegram-bot-api-secret-token");
  if (WEBHOOK_SECRET && secret !== WEBHOOK_SECRET) {
    return NextResponse.json({ ok: false }, { status: 403 });
  }

  let body;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ ok: true });
  }

  const callback = body.callback_query;
  if (!callback) {
    return NextResponse.json({ ok: true });
  }

  const data = (callback.data || "") as string;
  const parts = data.split(":");
  if (parts.length !== 3) {
    await answerCallback(callback.id, "Invalid action");
    return NextResponse.json({ ok: true });
  }

  const [action, pipeline, draftId] = parts;
  const table = TABLES[pipeline];
  if (!table) {
    await answerCallback(callback.id, "Unknown pipeline");
    return NextResponse.json({ ok: true });
  }

  if (!SUPABASE_URL || !SUPABASE_KEY) {
    await answerCallback(callback.id, "Supabase not configured");
    return NextResponse.json({ ok: true });
  }

  // Fetch current draft
  let existing: { status: string; lead_name: string; subject: string } | null =
    null;
  try {
    const checkRes = await fetch(
      `${SUPABASE_URL}/rest/v1/${table}?id=eq.${draftId}&select=status,lead_name,subject`,
      { headers: sbHeaders() }
    );
    const rows = await checkRes.json();
    if (Array.isArray(rows) && rows.length > 0) {
      existing = rows[0];
    }
  } catch {
    await answerCallback(callback.id, "Supabase error");
    return NextResponse.json({ ok: true });
  }

  if (!existing) {
    await answerCallback(callback.id, "Draft not found");
    return NextResponse.json({ ok: true });
  }

  if (existing.status !== "pending") {
    await answerCallback(callback.id, `Already ${existing.status}`);
    return NextResponse.json({ ok: true });
  }

  const pipelineLabel = PIPELINE_LABELS[pipeline];
  const leadName = existing.lead_name || "Unknown";
  const subject = existing.subject || "";
  const chatId = callback.message?.chat?.id;
  const msgId = callback.message?.message_id;

  if (action === "a") {
    // Approve
    await fetch(`${SUPABASE_URL}/rest/v1/${table}?id=eq.${draftId}`, {
      method: "PATCH",
      headers: sbHeaders(),
      body: JSON.stringify({
        status: "approved",
        approved_at: new Date().toISOString(),
      }),
    });

    await answerCallback(callback.id, `Approved: ${leadName}`);
    if (chatId && msgId) {
      await editMessage(
        chatId,
        msgId,
        `\u2705 <b>APPROVED</b> [${pipelineLabel}] ${leadName}\n<i>${subject}</i>`
      );
    }
  } else if (action === "r") {
    // Reject
    await fetch(`${SUPABASE_URL}/rest/v1/${table}?id=eq.${draftId}`, {
      method: "PATCH",
      headers: sbHeaders(),
      body: JSON.stringify({ status: "rejected" }),
    });

    await answerCallback(callback.id, `Rejected: ${leadName}`);
    if (chatId && msgId) {
      await editMessage(
        chatId,
        msgId,
        `\u274c <b>REJECTED</b> [${pipelineLabel}] ${leadName}\n<s>${subject}</s>`
      );
    }
  } else {
    await answerCallback(callback.id, "Unknown action");
  }

  return NextResponse.json({ ok: true });
}

export async function GET() {
  return NextResponse.json({ status: "Outreach review webhook active" });
}
