# Marketing Skills Merge Log

**Date:** 2026-03-25
**Source:** /tmp/marketingskills/skills/ (33 skills)
**Target:** skills/marketing-external/
**Performed by:** Claude Code

---

## Merge Summary

| Metric | Count |
|--------|-------|
| Total external skills evaluated | 33 |
| Skills added | 26 |
| Skills skipped (overlap) | 7 |
| Existing ContentBrain files modified | 0 |

---

## Skipped Skills (7) - Direct Overlap with Existing ContentBrain Skills

| External Skill | Overlapping ContentBrain Skill(s) | Reason |
|---------------|----------------------------------|--------|
| content-strategy | content-strategist | Same core function: content planning, topic selection, editorial calendar |
| social-content | ghostwriter, content-strategist | Writes social posts (LinkedIn, Twitter, IG, TikTok); scheduling/calendar overlap |
| copywriting | ghostwriter, funnel-builder | Marketing copy, captions, sales copy, landing page copy |
| email-sequence | funnel-builder | Email sequences, drip campaigns, lead magnets |
| lead-magnets | funnel-builder | Lead magnet creation and planning |
| churn-prevention | community-manager | Churn prevention sequences |
| sales-enablement | sales-closer | Objection handling, pitch templates, DM scripts |

---

## Added Skills (26)

### With Partial Overlap (5)
| External Skill | Partial Overlap With | Why Added |
|---------------|---------------------|-----------|
| copy-editing | ghostwriter | Ghostwriter writes new copy; no dedicated editing/polishing skill exists |
| competitor-alternatives | scrape-instagram | Scraping exists but no comparison/alternative page creation |
| marketing-psychology | content-strategist | No dedicated psychology reference; strategy overlap is minor |
| launch-strategy | content-strategist, funnel-builder | No dedicated launch planning workflow |
| pricing-strategy | funnel-builder | No dedicated pricing analysis; funnel-builder has only pricing context |

### No Overlap (21)
ab-test-setup, ad-creative, ai-seo, analytics-tracking, cold-email, form-cro, free-tool-strategy, marketing-ideas, onboarding-cro, page-cro, paid-ads, paywall-upgrade-cro, popup-cro, product-marketing-context, programmatic-seo, referral-program, revops, schema-markup, seo-audit, signup-flow-cro, site-architecture

---

## Phase 2: Wiring & Tools Import (2026-03-25)

### Slash Commands Wired
All 26 added skills were registered as slash commands in `.claude/commands/`:

| Command | Status |
|---------|--------|
| `/ab-test-setup` | WIRED |
| `/ad-creative` | WIRED |
| `/ai-seo` | WIRED |
| `/analytics-tracking` | WIRED |
| `/cold-email` | WIRED |
| `/competitor-alternatives` | WIRED |
| `/copy-editing` | WIRED |
| `/form-cro` | WIRED |
| `/free-tool-strategy` | WIRED |
| `/launch-strategy` | WIRED |
| `/marketing-ideas` | WIRED |
| `/marketing-psychology` | WIRED |
| `/onboarding-cro` | WIRED |
| `/page-cro` | WIRED |
| `/paid-ads` | WIRED |
| `/paywall-upgrade-cro` | WIRED |
| `/popup-cro` | WIRED |
| `/pricing-strategy` | WIRED |
| `/product-marketing-context` | WIRED |
| `/programmatic-seo` | WIRED |
| `/referral-program` | WIRED |
| `/revops` | WIRED |
| `/schema-markup` | WIRED |
| `/seo-audit` | WIRED |
| `/signup-flow-cro` | WIRED |
| `/site-architecture` | WIRED |

### Tools Imported
The full `tools/` directory from the external repo was imported to `skills/marketing-external/tools/`:
- **REGISTRY.md** — tool index and descriptions
- **clis/** — 64 CLI wrapper scripts (.js) for marketing platforms (GA4, Ahrefs, Semrush, Meta Ads, Google Ads, Mailchimp, HubSpot, Klaviyo, etc.)
- **composio/** — Composio marketing tool integrations
- **integrations/** — 70+ integration guides (.md) for marketing platforms

### Total Command Count
- Before merge: 27 commands
- After merge: 53 commands (+26 new)
- No existing commands were modified

---

## What Was NOT Touched
- No existing ContentBrain command files were modified
- No files in 09-Skills/ were changed
- No configuration files were altered
- New command files only ADD to .claude/commands/ — no overwrites

---

## Directory Structure Created
```
skills/
  marketing-external/
    INDEX.md
    tools/
      REGISTRY.md
      clis/          (64 CLI scripts)
      composio/      (Composio integrations)
      integrations/  (70+ platform guides)
    ab-test-setup/
    ad-creative/
    ai-seo/
    analytics-tracking/
    cold-email/
    competitor-alternatives/
    copy-editing/
    form-cro/
    free-tool-strategy/
    launch-strategy/
    marketing-ideas/
    marketing-psychology/
    onboarding-cro/
    page-cro/
    paid-ads/
    paywall-upgrade-cro/
    popup-cro/
    pricing-strategy/
    product-marketing-context/
    programmatic-seo/
    referral-program/
    revops/
    schema-markup/
    seo-audit/
    signup-flow-cro/
    site-architecture/
```
