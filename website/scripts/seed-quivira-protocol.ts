/**
 * One-time migration: seeds Quivira Protocol tiers + features into an existing database.
 * Run: npx tsx scripts/seed-quivira-protocol.ts
 *
 * Safe to run multiple times — checks for existing data first.
 */

import { createClient } from "@libsql/client";
import { drizzle } from "drizzle-orm/libsql";
import { eq } from "drizzle-orm";
import * as schema from "../lib/schema";

async function run() {
  const url = process.env.TURSO_DATABASE_URL;
  if (!url) throw new Error("TURSO_DATABASE_URL not set");

  const client = createClient({ url, authToken: process.env.TURSO_AUTH_TOKEN });
  const db = drizzle(client, { schema });

  // Check if already seeded
  const existing = await db
    .select()
    .from(schema.pricingTiers)
    .where(eq(schema.pricingTiers.product, "quivira_protocol"));

  if (existing.length > 0) {
    console.log("✓ Quivira Protocol already seeded — skipping.");
    process.exit(0);
  }

  // ─── Tiers ───
  await db.insert(schema.pricingTiers).values([
    {
      product: "quivira_protocol",
      productTitle: "Quivira Protocol",
      productSubtitle: "High-Ticket Mentorship",
      tierKey: "starter",
      tierLabel: "Standard",
      tierPrice: "$3,000",
      sortOrder: 0,
    },
    {
      product: "quivira_protocol",
      productTitle: "Quivira Protocol",
      productSubtitle: "High-Ticket Mentorship",
      tierKey: "pro",
      tierLabel: "Pro",
      tierPrice: "$5,000",
      sortOrder: 1,
    },
    {
      product: "quivira_protocol",
      productTitle: "Quivira Protocol",
      productSubtitle: "High-Ticket Mentorship",
      tierKey: "premium",
      tierLabel: "Inner Circle",
      tierPrice: "$10,000",
      sortOrder: 2,
    },
  ]);
  console.log("✓ Quivira Protocol tiers seeded");

  // ─── Features ───
  await db.insert(schema.pricingFeatures).values([
    { product: "quivira_protocol", featureName: "Weekly strategy calls", starter: "1/week", pro: "2/week", premium: "Daily access", sortOrder: 0 },
    { product: "quivira_protocol", featureName: "Web3 portfolio buildout", starter: "true", pro: "true", premium: "true", sortOrder: 1 },
    { product: "quivira_protocol", featureName: "SignalOS setup", starter: "true", pro: "true", premium: "true", sortOrder: 2 },
    { product: "quivira_protocol", featureName: "ContentBrain system", starter: "true", pro: "true", premium: "true", sortOrder: 3 },
    { product: "quivira_protocol", featureName: "Quivira OS access", starter: "true", pro: "true", premium: "true", sortOrder: 4 },
    { product: "quivira_protocol", featureName: "Milestone guarantee", starter: "true", pro: "true", premium: "true", sortOrder: 5 },
    { product: "quivira_protocol", featureName: "Community + pipeline", starter: "true", pro: "true", premium: "true", sortOrder: 6 },
    { product: "quivira_protocol", featureName: "1:1 Slack/Telegram access", starter: "false", pro: "true", premium: "true", sortOrder: 7 },
    { product: "quivira_protocol", featureName: "Guest speaker network", starter: "false", pro: "false", premium: "true", sortOrder: 8 },
    { product: "quivira_protocol", featureName: "Cohort size", starter: "20 seats", pro: "10 seats", premium: "5 seats", sortOrder: 9 },
  ]);
  console.log("✓ Quivira Protocol features seeded");

  // ─── Add cal_paid_url setting (if not set) ───
  await db
    .insert(schema.settings)
    .values({ key: "cal_paid_url", value: "" })
    .onConflictDoNothing();
  console.log("✓ cal_paid_url setting added (set your Cal.com URL in admin → Settings)");

  console.log("\n✅ Quivira Protocol seeded successfully!");
  process.exit(0);
}

run().catch((err) => {
  console.error("Migration failed:", err);
  process.exit(1);
});
