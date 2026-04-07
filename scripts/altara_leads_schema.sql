-- =============================================================
-- Altara Aerial Lead Pipeline — Supabase Schema
-- Run this in Supabase SQL Editor before deploying.
-- =============================================================

-- 1. PILOT PROSPECTS (supply side — drone pilots for recruitment)
CREATE TABLE IF NOT EXISTS altara_pilot_prospects (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    full_name TEXT DEFAULT '',
    bio TEXT DEFAULT '',
    followers INTEGER DEFAULT 0,
    city TEXT DEFAULT '',
    profile_url TEXT DEFAULT '',
    external_url TEXT DEFAULT '',
    is_verified BOOLEAN DEFAULT FALSE,
    score FLOAT DEFAULT 0,
    source TEXT DEFAULT '',
    outreach_status TEXT DEFAULT 'not_contacted'
        CHECK (outreach_status IN ('not_contacted', 'draft_ready', 'sent', 'replied', 'onboarded', 'rejected')),
    notes TEXT DEFAULT '',
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pilots_score ON altara_pilot_prospects(score DESC);
CREATE INDEX IF NOT EXISTS idx_pilots_city ON altara_pilot_prospects(city);
CREATE INDEX IF NOT EXISTS idx_pilots_outreach ON altara_pilot_prospects(outreach_status);

-- 2. CLIENT LEADS (demand side — businesses needing drone services)
CREATE TABLE IF NOT EXISTS altara_client_leads (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    lead_type TEXT NOT NULL CHECK (lead_type IN ('real_estate', 'construction', 'wedding')),
    name TEXT DEFAULT '',
    company TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    email TEXT DEFAULT '',
    website TEXT DEFAULT '',
    address TEXT DEFAULT '',
    city TEXT DEFAULT '',
    listing_url TEXT DEFAULT '',
    instagram TEXT DEFAULT '',
    followers INTEGER DEFAULT 0,
    score FLOAT DEFAULT 0,
    lifecycle_stage TEXT DEFAULT 'subscriber'
        CHECK (lifecycle_stage IN ('subscriber', 'mql', 'sql', 'opportunity', 'customer')),
    outreach_status TEXT DEFAULT 'not_contacted'
        CHECK (outreach_status IN ('not_contacted', 'draft_ready', 'sent', 'replied', 'meeting_booked', 'closed', 'rejected')),
    source TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clients_type ON altara_client_leads(lead_type);
CREATE INDEX IF NOT EXISTS idx_clients_stage ON altara_client_leads(lifecycle_stage);
CREATE INDEX IF NOT EXISTS idx_clients_city ON altara_client_leads(city);
CREATE INDEX IF NOT EXISTS idx_clients_score ON altara_client_leads(score DESC);
CREATE INDEX IF NOT EXISTS idx_clients_outreach ON altara_client_leads(outreach_status);
CREATE INDEX IF NOT EXISTS idx_clients_phone_type ON altara_client_leads(phone, lead_type);

-- 3. OUTREACH DRAFTS (email/DM drafts for review and sending)
CREATE TABLE IF NOT EXISTS altara_outreach_drafts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    lead_id UUID,
    lead_type TEXT DEFAULT '',
    lead_name TEXT DEFAULT '',
    lead_city TEXT DEFAULT '',
    lead_contact TEXT DEFAULT '',
    channel TEXT DEFAULT 'email' CHECK (channel IN ('email', 'dm', 'whatsapp', 'linkedin')),
    subject TEXT DEFAULT '',
    body TEXT DEFAULT '',
    status TEXT DEFAULT 'pending'
        CHECK (status IN ('pending', 'approved', 'sent', 'manual_required', 'rejected')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,
    notes TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_drafts_status ON altara_outreach_drafts(status);
CREATE INDEX IF NOT EXISTS idx_drafts_lead_type ON altara_outreach_drafts(lead_type);
CREATE INDEX IF NOT EXISTS idx_drafts_created ON altara_outreach_drafts(created_at DESC);

-- =============================================================
-- ROW LEVEL SECURITY
-- =============================================================

ALTER TABLE altara_pilot_prospects ENABLE ROW LEVEL SECURITY;
ALTER TABLE altara_client_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE altara_outreach_drafts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "anon_full_pilots" ON altara_pilot_prospects FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "anon_full_clients" ON altara_client_leads FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "anon_full_drafts" ON altara_outreach_drafts FOR ALL USING (true) WITH CHECK (true);

-- =============================================================
-- AUTO-UPDATE TRIGGERS
-- =============================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS pilots_updated_at ON altara_pilot_prospects;
CREATE TRIGGER pilots_updated_at
    BEFORE UPDATE ON altara_pilot_prospects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

DROP TRIGGER IF EXISTS clients_updated_at ON altara_client_leads;
CREATE TRIGGER clients_updated_at
    BEFORE UPDATE ON altara_client_leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =============================================================
-- DASHBOARD VIEW: Altara Lead Pipeline
-- =============================================================

CREATE OR REPLACE VIEW altara_lead_pipeline AS

-- Client leads summary
SELECT
    'clients' AS segment,
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
    ROUND(
        CASE WHEN COUNT(*) FILTER (WHERE outreach_status = 'sent') > 0
        THEN COUNT(*) FILTER (WHERE outreach_status IN ('replied', 'meeting_booked', 'closed'))::numeric
             / COUNT(*) FILTER (WHERE outreach_status = 'sent')::numeric * 100
        ELSE 0 END, 1
    ) AS response_rate_pct,
    COUNT(*) FILTER (WHERE scraped_at >= NOW() - INTERVAL '7 days') AS new_this_week,
    AVG(score)::numeric(4,1) AS avg_score
FROM altara_client_leads
GROUP BY lead_type

UNION ALL

-- Pilot prospects summary
SELECT
    'pilots' AS segment,
    'drone_pilot' AS lead_type,
    COUNT(*) AS total_leads,
    COUNT(*) FILTER (WHERE outreach_status = 'not_contacted') AS pending,
    COUNT(*) FILTER (WHERE outreach_status = 'draft_ready') AS drafted,
    COUNT(*) FILTER (WHERE outreach_status = 'sent') AS sent,
    COUNT(*) FILTER (WHERE outreach_status = 'replied') AS responded,
    0 AS meetings,
    COUNT(*) FILTER (WHERE outreach_status = 'onboarded') AS closed,
    0 AS subscribers,
    0 AS mqls,
    0 AS sqls,
    0 AS opportunities,
    0 AS customers,
    ROUND(
        CASE WHEN COUNT(*) FILTER (WHERE outreach_status = 'sent') > 0
        THEN COUNT(*) FILTER (WHERE outreach_status IN ('replied', 'onboarded'))::numeric
             / COUNT(*) FILTER (WHERE outreach_status = 'sent')::numeric * 100
        ELSE 0 END, 1
    ) AS response_rate_pct,
    COUNT(*) FILTER (WHERE scraped_at >= NOW() - INTERVAL '7 days') AS new_this_week,
    AVG(score)::numeric(4,1) AS avg_score
FROM altara_pilot_prospects;

-- =============================================================
-- OUTREACH DRAFTS SUMMARY VIEW
-- =============================================================

CREATE OR REPLACE VIEW altara_outreach_summary AS
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
FROM altara_outreach_drafts
GROUP BY lead_type;
