import { createClient } from "@supabase/supabase-js";

let _client: ReturnType<typeof createClient> | null = null;

/**
 * Supabase client for the hustlers-krib-bot project (outreach drafts, KOL leads, Altara leads).
 * Separate from the main getSupabase() which connects to content-engine (drone signups, CMS).
 */
export function getOutreachSupabase() {
  if (!_client) {
    const url = process.env.OUTREACH_SUPABASE_URL;
    const key = process.env.OUTREACH_SUPABASE_ANON_KEY;
    if (!url || !key) {
      throw new Error(
        "OUTREACH_SUPABASE_URL and OUTREACH_SUPABASE_ANON_KEY must be set"
      );
    }
    _client = createClient(url, key);
  }
  return _client;
}
