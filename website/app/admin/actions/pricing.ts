"use server";

import { db } from "@/lib/db";
import { pricingTiers, pricingFeatures, faqItems, personalServices } from "@/lib/schema";
import { eq } from "drizzle-orm";
import { revalidatePath } from "next/cache";

export async function upsertPricingTier(_prev: unknown, formData: FormData) {
  const id = formData.get("id") as string;
  const product = formData.get("product") as string;
  const productTitle = formData.get("productTitle") as string;
  const productSubtitle = formData.get("productSubtitle") as string;
  const tierKey = formData.get("tierKey") as string;
  const tierLabel = formData.get("tierLabel") as string;
  const tierPrice = formData.get("tierPrice") as string;
  const sortOrder = parseInt(formData.get("sortOrder") as string) || 0;

  if (id) {
    await db.update(pricingTiers).set({ product, productTitle, productSubtitle, tierKey, tierLabel, tierPrice, sortOrder }).where(eq(pricingTiers.id, parseInt(id)));
  } else {
    await db.insert(pricingTiers).values({ product, productTitle, productSubtitle, tierKey, tierLabel, tierPrice, sortOrder });
  }
  revalidatePath("/", "layout");
  return "Pricing tier saved.";
}

export async function deletePricingTier(id: number) {
  await db.delete(pricingTiers).where(eq(pricingTiers.id, id));
  revalidatePath("/", "layout");
}

export async function upsertPricingFeature(_prev: unknown, formData: FormData) {
  const id = formData.get("id") as string;
  const product = formData.get("product") as string;
  const featureName = formData.get("featureName") as string;
  const starter = formData.get("starter") as string;
  const pro = formData.get("pro") as string;
  const premium = formData.get("premium") as string;
  const sortOrder = parseInt(formData.get("sortOrder") as string) || 0;

  if (id) {
    await db.update(pricingFeatures).set({ product, featureName, starter, pro, premium, sortOrder }).where(eq(pricingFeatures.id, parseInt(id)));
  } else {
    await db.insert(pricingFeatures).values({ product, featureName, starter, pro, premium, sortOrder });
  }
  revalidatePath("/", "layout");
  return "Feature saved.";
}

export async function deletePricingFeature(id: number) {
  await db.delete(pricingFeatures).where(eq(pricingFeatures.id, id));
  revalidatePath("/", "layout");
}

export async function upsertFaqItem(_prev: unknown, formData: FormData) {
  const id = formData.get("id") as string;
  const question = formData.get("question") as string;
  const answer = formData.get("answer") as string;
  const sortOrder = parseInt(formData.get("sortOrder") as string) || 0;

  if (id) {
    await db.update(faqItems).set({ question, answer, sortOrder }).where(eq(faqItems.id, parseInt(id)));
  } else {
    await db.insert(faqItems).values({ question, answer, sortOrder });
  }
  revalidatePath("/", "layout");
  return "FAQ item saved.";
}

export async function deleteFaqItem(id: number) {
  await db.delete(faqItems).where(eq(faqItems.id, id));
  revalidatePath("/", "layout");
}

export async function upsertPersonalService(_prev: unknown, formData: FormData) {
  const id = formData.get("id") as string;
  const name = formData.get("name") as string;
  const price = formData.get("price") as string;
  const detail = formData.get("detail") as string;
  const ctaText = (formData.get("ctaText") as string) || null;
  const ctaHref = (formData.get("ctaHref") as string) || null;
  const sortOrder = parseInt(formData.get("sortOrder") as string) || 0;

  if (id) {
    await db.update(personalServices).set({ name, price, detail, ctaText, ctaHref, sortOrder }).where(eq(personalServices.id, parseInt(id)));
  } else {
    await db.insert(personalServices).values({ name, price, detail, ctaText, ctaHref, sortOrder });
  }
  revalidatePath("/", "layout");
  return "Personal service saved.";
}

export async function deletePersonalService(id: number) {
  await db.delete(personalServices).where(eq(personalServices.id, id));
  revalidatePath("/", "layout");
}
