/**
 * One-time migration: set ctaHref = null for all services that currently
 * link to calendly, so they open the payment modal instead.
 *
 * Run: npx tsx scripts/fix-service-cta-hrefs.ts
 */
import { createClient } from "@libsql/client";
import { drizzle } from "drizzle-orm/libsql";
import { sql, isNotNull } from "drizzle-orm";
import * as schema from "../lib/schema";

async function main() {
  const url = process.env.TURSO_DATABASE_URL;
  if (!url) throw new Error("TURSO_DATABASE_URL not set");

  const client = createClient({ url, authToken: process.env.TURSO_AUTH_TOKEN });
  const db = drizzle(client, { schema });

  // Show current state
  const all = await db.select().from(schema.services);
  console.log("Current services:");
  all.forEach((s) => console.log(`  [${s.id}] ${s.title} | price: ${s.price} | ctaHref: ${s.ctaHref}`));

  // Set ctaHref = null for any service whose ctaHref contains "calendly"
  await db
    .update(schema.services)
    .set({ ctaHref: null })
    .where(sql`${schema.services.ctaHref} LIKE '%calendly%'`);

  console.log("\nDone — set ctaHref = null for all calendly-linked services");

  const updated = await db.select().from(schema.services);
  console.log("\nAfter update:");
  updated.forEach((s) => console.log(`  [${s.id}] ${s.title} | price: ${s.price} | ctaHref: ${s.ctaHref}`));

  process.exit(0);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
