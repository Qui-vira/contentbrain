import { getOutreachSupabase } from "@/lib/supabase-outreach";
import OutreachDashboard from "./client";

type Draft = {
  id: string;
  lead_type: string;
  lead_name: string;
  lead_contact: string;
  channel: string;
  subject: string;
  body: string;
  status: string;
  created_at: string;
  approved_at: string | null;
  sent_at: string | null;
};

type Stats = {
  pending: number;
  approved: number;
  sent: number;
  rejected: number;
  total: number;
};

function countStats(drafts: Draft[]): Stats {
  return {
    pending: drafts.filter((d) => d.status === "pending").length,
    approved: drafts.filter((d) => d.status === "approved").length,
    sent: drafts.filter((d) => d.status === "sent").length,
    rejected: drafts.filter((d) => d.status === "rejected").length,
    total: drafts.length,
  };
}

export default async function OutreachPage() {
  const supabase = getOutreachSupabase();

  const { data: altaraDrafts } = await supabase
    .from("altara_outreach_drafts")
    .select("*")
    .order("created_at", { ascending: false })
    .limit(100);

  const { data: kolDrafts } = await supabase
    .from("kol_outreach_drafts")
    .select("*")
    .order("created_at", { ascending: false })
    .limit(100);

  const altara = (altaraDrafts || []) as Draft[];
  const kol = (kolDrafts || []) as Draft[];

  const altaraStats = countStats(altara);
  const kolStats = countStats(kol);

  const combinedStats = {
    pending: altaraStats.pending + kolStats.pending,
    approved: altaraStats.approved + kolStats.approved,
    sent: altaraStats.sent + kolStats.sent,
    rejected: altaraStats.rejected + kolStats.rejected,
    total: altaraStats.total + kolStats.total,
  };

  return (
    <OutreachDashboard
      altaraDrafts={altara}
      kolDrafts={kol}
      combinedStats={combinedStats}
      altaraStats={altaraStats}
      kolStats={kolStats}
    />
  );
}
