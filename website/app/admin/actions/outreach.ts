"use server";

import { revalidatePath } from "next/cache";

const SUPABASE_URL = process.env.OUTREACH_SUPABASE_URL || "";
const SUPABASE_KEY = process.env.OUTREACH_SUPABASE_ANON_KEY || "";

const TABLES: Record<string, string> = {
  altara: "altara_outreach_drafts",
  kol: "kol_outreach_drafts",
};

function headers() {
  return {
    apikey: SUPABASE_KEY,
    Authorization: `Bearer ${SUPABASE_KEY}`,
    "Content-Type": "application/json",
    Prefer: "return=minimal",
  };
}

export async function approveDraft(pipeline: string, draftId: string) {
  const table = TABLES[pipeline];
  if (!table) return "Invalid pipeline";

  const res = await fetch(
    `${SUPABASE_URL}/rest/v1/${table}?id=eq.${draftId}`,
    {
      method: "PATCH",
      headers: headers(),
      body: JSON.stringify({
        status: "approved",
        approved_at: new Date().toISOString(),
      }),
    }
  );

  revalidatePath("/admin/outreach");
  return res.ok ? "Approved" : `Error: ${res.status}`;
}

export async function rejectDraft(pipeline: string, draftId: string) {
  const table = TABLES[pipeline];
  if (!table) return "Invalid pipeline";

  const res = await fetch(
    `${SUPABASE_URL}/rest/v1/${table}?id=eq.${draftId}`,
    {
      method: "PATCH",
      headers: headers(),
      body: JSON.stringify({ status: "rejected" }),
    }
  );

  revalidatePath("/admin/outreach");
  return res.ok ? "Rejected" : `Error: ${res.status}`;
}

export async function approveAll(pipeline: string) {
  const table = TABLES[pipeline];
  if (!table) return "Invalid pipeline";

  const res = await fetch(
    `${SUPABASE_URL}/rest/v1/${table}?status=eq.pending`,
    {
      method: "PATCH",
      headers: headers(),
      body: JSON.stringify({
        status: "approved",
        approved_at: new Date().toISOString(),
      }),
    }
  );

  revalidatePath("/admin/outreach");
  return res.ok ? "All approved" : `Error: ${res.status}`;
}
