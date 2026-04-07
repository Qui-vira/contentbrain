"use client";

import { useState, useTransition } from "react";
import { approveDraft, rejectDraft, approveAll } from "@/app/admin/actions/outreach";

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

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-yellow-500/20 text-yellow-400",
  approved: "bg-green-500/20 text-green-400",
  sent: "bg-blue-500/20 text-blue-400",
  rejected: "bg-red-500/20 text-red-400",
  manual_required: "bg-orange-500/20 text-orange-400",
};

const LEAD_TYPE_LABELS: Record<string, string> = {
  real_estate: "Real Estate",
  construction: "Construction",
  wedding: "Wedding",
  new_exchange: "Exchange",
  defi_protocol: "DeFi Protocol",
  funded_project: "Funded Project",
  ai_consulting: "AI Consulting",
  competitor_deal: "Competitor Deal",
  new_token: "New Token",
};

function StatBadge({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex flex-col items-center rounded-lg border border-[#222] bg-[#111] px-4 py-3">
      <span className={`text-2xl font-bold ${color}`}>{value}</span>
      <span className="text-xs text-[#666]">{label}</span>
    </div>
  );
}

function DraftCard({
  draft,
  pipeline,
}: {
  draft: Draft;
  pipeline: "altara" | "kol";
}) {
  const [expanded, setExpanded] = useState(false);
  const [isPending, startTransition] = useTransition();
  const [localStatus, setLocalStatus] = useState(draft.status);

  function handleApprove() {
    startTransition(async () => {
      await approveDraft(pipeline, draft.id);
      setLocalStatus("approved");
    });
  }

  function handleReject() {
    startTransition(async () => {
      await rejectDraft(pipeline, draft.id);
      setLocalStatus("rejected");
    });
  }

  const statusColor = STATUS_COLORS[localStatus] || "bg-[#333] text-[#888]";
  const typeLabel = LEAD_TYPE_LABELS[draft.lead_type] || draft.lead_type;
  const createdDate = new Date(draft.created_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="rounded-xl border border-[#222] bg-[#111] p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${statusColor}`}>
              {localStatus}
            </span>
            <span className="rounded-full bg-[#1a1a1a] px-2 py-0.5 text-[10px] text-[#888]">
              {typeLabel}
            </span>
            <span className="text-[10px] text-[#555]">{createdDate}</span>
          </div>
          <h4 className="text-sm font-medium text-white truncate">{draft.lead_name || "Unknown"}</h4>
          <p className="text-xs text-[#888] truncate">{draft.subject}</p>
        </div>

        {localStatus === "pending" && (
          <div className="flex gap-1.5 shrink-0">
            <button
              onClick={handleApprove}
              disabled={isPending}
              className="rounded-lg bg-green-600/20 px-3 py-1.5 text-xs font-medium text-green-400 hover:bg-green-600/30 transition-colors disabled:opacity-50 cursor-pointer"
            >
              Approve
            </button>
            <button
              onClick={handleReject}
              disabled={isPending}
              className="rounded-lg bg-red-600/20 px-3 py-1.5 text-xs font-medium text-red-400 hover:bg-red-600/30 transition-colors disabled:opacity-50 cursor-pointer"
            >
              Reject
            </button>
          </div>
        )}
      </div>

      <button
        onClick={() => setExpanded(!expanded)}
        className="mt-2 text-[10px] text-[#555] hover:text-[#888] transition-colors cursor-pointer"
      >
        {expanded ? "Hide body" : "Show body"}
      </button>

      {expanded && (
        <div className="mt-2 rounded-lg bg-[#0d0d0d] p-3 text-xs text-[#aaa] whitespace-pre-wrap max-h-60 overflow-y-auto">
          {draft.body}
        </div>
      )}
    </div>
  );
}

export default function OutreachDashboard({
  altaraDrafts,
  kolDrafts,
  combinedStats,
  altaraStats,
  kolStats,
}: {
  altaraDrafts: Draft[];
  kolDrafts: Draft[];
  combinedStats: Stats;
  altaraStats: Stats;
  kolStats: Stats;
}) {
  const [tab, setTab] = useState<"altara" | "kol">("altara");
  const [filter, setFilter] = useState<string>("all");
  const [isPending, startTransition] = useTransition();

  const drafts = tab === "altara" ? altaraDrafts : kolDrafts;
  const stats = tab === "altara" ? altaraStats : kolStats;
  const filtered = filter === "all" ? drafts : drafts.filter((d) => d.status === filter);

  function handleApproveAll() {
    if (!confirm(`Approve all ${stats.pending} pending ${tab} drafts?`)) return;
    startTransition(async () => {
      await approveAll(tab);
    });
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-white">Outreach Review</h1>

      {/* Combined stats bar */}
      <div className="mb-6 grid grid-cols-5 gap-3">
        <StatBadge label="Total" value={combinedStats.total} color="text-white" />
        <StatBadge label="Pending" value={combinedStats.pending} color="text-yellow-400" />
        <StatBadge label="Approved" value={combinedStats.approved} color="text-green-400" />
        <StatBadge label="Sent" value={combinedStats.sent} color="text-blue-400" />
        <StatBadge label="Rejected" value={combinedStats.rejected} color="text-red-400" />
      </div>

      {/* Tab bar */}
      <div className="mb-4 flex items-center justify-between">
        <div className="flex gap-1 rounded-lg bg-[#111] p-1 border border-[#222]">
          <button
            onClick={() => setTab("altara")}
            className={`rounded-md px-4 py-2 text-sm font-medium transition-colors cursor-pointer ${
              tab === "altara" ? "bg-[#E63946] text-white" : "text-[#888] hover:text-white"
            }`}
          >
            Altara Aerial ({altaraStats.total})
          </button>
          <button
            onClick={() => setTab("kol")}
            className={`rounded-md px-4 py-2 text-sm font-medium transition-colors cursor-pointer ${
              tab === "kol" ? "bg-[#E63946] text-white" : "text-[#888] hover:text-white"
            }`}
          >
            KOL Business ({kolStats.total})
          </button>
        </div>

        <div className="flex items-center gap-3">
          {/* Filter */}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="rounded-lg border border-[#333] bg-[#1a1a1a] px-3 py-1.5 text-xs text-white focus:border-[#E63946] focus:outline-none"
          >
            <option value="all">All ({stats.total})</option>
            <option value="pending">Pending ({stats.pending})</option>
            <option value="approved">Approved ({stats.approved})</option>
            <option value="sent">Sent ({stats.sent})</option>
            <option value="rejected">Rejected ({stats.rejected})</option>
          </select>

          {/* Bulk approve */}
          {stats.pending > 0 && (
            <button
              onClick={handleApproveAll}
              disabled={isPending}
              className="rounded-lg bg-green-600/20 px-4 py-1.5 text-xs font-medium text-green-400 hover:bg-green-600/30 transition-colors disabled:opacity-50 cursor-pointer"
            >
              {isPending ? "Approving..." : `Approve All (${stats.pending})`}
            </button>
          )}
        </div>
      </div>

      {/* Draft cards */}
      <div className="space-y-3">
        {filtered.length === 0 && (
          <div className="rounded-xl border border-[#222] bg-[#111] p-8 text-center text-sm text-[#555]">
            No {filter === "all" ? "" : filter} drafts in {tab === "altara" ? "Altara Aerial" : "KOL Business"}
          </div>
        )}
        {filtered.map((draft) => (
          <DraftCard key={draft.id} draft={draft} pipeline={tab} />
        ))}
      </div>
    </div>
  );
}
