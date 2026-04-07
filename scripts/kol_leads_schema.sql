-- =============================================================
-- KOL & Consulting Lead Pipeline — Supabase Schema
-- Run this in Supabase SQL Editor before deploying.
-- =============================================================

-- 1. KOL LEADS (unified for all lead types)
CREATE TABLE IF NOT EXISTS kol_leads (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    lead_type TEXT NOT NULL CHECK (lead_type IN (
        'new_exchange', 'new_token', 'defi_protocol',
        'funded_project', 'ai_consulting', 'competitor_deal',
        'leadgen_service_client'
    )),
    project_name TEXT NOT NULL DEFAULT '',
    token_symbol TEXT DEFAULT '',
    website TEXT DEFAULT '',
    twitter_handle TEXT DEFAULT '',
    email TEXT DEFAULT '',
    contact_name TEXT DEFAULT '',
    category TEXT DEFAULT '',
    description TEXT DEFAULT '',

    -- Scoring
    score FLOAT DEFAULT 0,
    priority TEXT DEFAULT 'normal'
        CHECK (priority IN ('low', 'normal', 'high', 'urgent')),

    -- Funding data (funded_project type)
    funding_amount FLOAT DEFAULT 0,
    funding_round TEXT DEFAULT '',
    investors TEXT DEFAULT '',

    -- Exchange data (new_exchange type)
    trust_score FLOAT DEFAULT 0,
    volume_24h FLOAT DEFAULT 0,
    year_established INTEGER DEFAULT 0,

    -- Protocol data (defi_protocol / new_token type)
    tvl FLOAT DEFAULT 0,
    chain TEXT DEFAULT '',

    -- Competitor deal data
    competitor_handle TEXT DEFAULT '',
    deal_type TEXT DEFAULT '',
    detected_post_url TEXT DEFAULT '',

    -- Lifecycle
    lifecycle_stage TEXT DEFAULT 'subscriber'
        CHECK (lifecycle_stage IN ('subscriber', 'mql', 'sql', 'opportunity', 'customer')),
    outreach_status TEXT DEFAULT 'not_contacted'
        CHECK (outreach_status IN ('not_contacted', 'draft_ready', 'sent', 'replied', 'meeting_booked', 'closed', 'rejected')),
    source TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Dedup constraint: one record per project per lead type
    UNIQUE (project_name, lead_type)
);

CREATE INDEX IF NOT EXISTS idx_kol_leads_type ON kol_leads(lead_type);
CREATE INDEX IF NOT EXISTS idx_kol_leads_score ON kol_leads(score DESC);
CREATE INDEX IF NOT EXISTS idx_kol_leads_outreach ON kol_leads(outreach_status);
CREATE INDEX IF NOT EXISTS idx_kol_leads_priority ON kol_leads(priority);
CREATE INDEX IF NOT EXISTS idx_kol_leads_stage ON kol_leads(lifecycle_stage);
CREATE INDEX IF NOT EXISTS idx_kol_leads_project ON kol_leads(project_name, lead_type);

-- 2. KOL OUTREACH DRAFTS
CREATE TABLE IF NOT EXISTS kol_outreach_drafts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    lead_id UUID REFERENCES kol_leads(id),
    lead_type TEXT DEFAULT '',
    lead_name TEXT DEFAULT '',
    lead_contact TEXT DEFAULT '',
    channel TEXT DEFAULT 'email' CHECK (channel IN ('email', 'dm', 'telegram', 'linkedin')),
    subject TEXT DEFAULT '',
    body TEXT DEFAULT '',
    status TEXT DEFAULT 'pending'
        CHECK (status IN ('pending', 'approved', 'sent', 'manual_required', 'rejected')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,
    notes TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_kol_drafts_status ON kol_outreach_drafts(status);
CREATE INDEX IF NOT EXISTS idx_kol_drafts_lead_type ON kol_outreach_drafts(lead_type);
CREATE INDEX IF NOT EXISTS idx_kol_drafts_created ON kol_outreach_drafts(created_at DESC);

-- =============================================================
-- ROW LEVEL SECURITY
-- =============================================================

ALTER TABLE kol_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE kol_outreach_drafts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "anon_full_kol_leads" ON kol_leads FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "anon_full_kol_drafts" ON kol_outreach_drafts FOR ALL USING (true) WITH CHECK (true);

-- =============================================================
-- AUTO-UPDATE TRIGGERS (reuse existing function if available)
-- =============================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS kol_leads_updated_at ON kol_leads;
CREATE TRIGGER kol_leads_updated_at
    BEFORE UPDATE ON kol_leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =============================================================
-- DASHBOARD VIEW: KOL Lead Pipeline
-- =============================================================

CREATE OR REPLACE VIEW kol_lead_pipeline AS
SELECT
    lead_type,
    COUNT(*) AS total_leads,
    COUNT(*) FILTER (WHERE outreach_status = 'not_contacted') AS pending,
    COUNT(*) FILTER (WHERE outreach_status = 'draft_ready') AS drafted,
    COUNT(*) FILTER (WHERE outreach_status = 'sent') AS sent,
    COUNT(*) FILTER (WHERE outreach_status = 'replied') AS responded,
    COUNT(*) FILTER (WHERE outreach_status = 'meeting_booked') AS meetings,
    COUNT(*) FILTER (WHERE outreach_status = 'closed') AS closed,
    COUNT(*) FILTER (WHERE lifecycle_stage = 'subscriber') AS subscribers,
    COUNT(*) FILTER (WHERE lifecycle_stage = 'mql') AS mqls,
    COUNT(*) FILTER (WHERE lifecycle_stage = 'sql') AS sqls,
    COUNT(*) FILTER (WHERE lifecycle_stage = 'opportunity') AS opportunities,
    COUNT(*) FILTER (WHERE lifecycle_stage = 'customer') AS customers,
    COUNT(*) FILTER (WHERE priority = 'high' OR priority = 'urgent') AS hot_leads,
    ROUND(
        CASE WHEN COUNT(*) FILTER (WHERE outreach_status = 'sent') > 0
        THEN COUNT(*) FILTER (WHERE outreach_status IN ('replied', 'meeting_booked', 'closed'))::numeric
             / COUNT(*) FILTER (WHERE outreach_status = 'sent')::numeric * 100
        ELSE 0 END, 1
    ) AS response_rate_pct,
    COUNT(*) FILTER (WHERE scraped_at >= NOW() - INTERVAL '7 days') AS new_this_week,
    AVG(score)::numeric(4,1) AS avg_score
FROM kol_leads
GROUP BY lead_type;

-- =============================================================
-- UNIFIED VIEW: All Business Pipelines
-- =============================================================

CREATE OR REPLACE VIEW all_business_pipelines AS

-- Altara client leads
SELECT
    'altara' AS business,
    lead_type,
    COUNT(*) AS total_leads,
    COUNT(*) FILTER (WHERE outreach_status = 'not_contacted') AS pending,
    COUNT(*) FILTER (WHERE outreach_status = 'sent') AS sent,
    COUNT(*) FILTER (WHERE outreach_status IN ('replied', 'meeting_booked')) AS engaged,
    COUNT(*) FILTER (WHERE outreach_status = 'closed') AS closed,
    AVG(score)::numeric(4,1) AS avg_score
FROM altara_client_leads
GROUP BY lead_type

UNION ALL

-- KOL leads
SELECT
    'kol' AS business,
    lead_type,
    COUNT(*) AS total_leads,
    COUNT(*) FILTER (WHERE outreach_status = 'not_contacted') AS pending,
    COUNT(*) FILTER (WHERE outreach_status = 'sent') AS sent,
    COUNT(*) FILTER (WHERE outreach_status IN ('replied', 'meeting_booked')) AS engaged,
    COUNT(*) FILTER (WHERE outreach_status = 'closed') AS closed,
    AVG(score)::numeric(4,1) AS avg_score
FROM kol_leads
GROUP BY lead_type;

-- =============================================================
-- KOL OUTREACH SUMMARY VIEW
-- =============================================================

CREATE OR REPLACE VIEW kol_outreach_summary AS
SELECT
    lead_type,
    COUNT(*) AS total_drafts,
    COUNT(*) FILTER (WHERE status = 'pending') AS pending_review,
    COUNT(*) FILTER (WHERE status = 'approved') AS approved,
    COUNT(*) FILTER (WHERE status = 'sent') AS sent,
    COUNT(*) FILTER (WHERE status = 'manual_required') AS manual_needed,
    COUNT(*) FILTER (WHERE status = 'rejected') AS rejected,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '24 hours') AS created_today,
    COUNT(*) FILTER (WHERE sent_at >= NOW() - INTERVAL '7 days') AS sent_this_week
FROM kol_outreach_drafts
GROUP BY lead_type;
