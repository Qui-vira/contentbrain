"use server";

import { db } from "@/lib/db";
import { services } from "@/lib/schema";
import { eq } from "drizzle-orm";
import { revalidatePath } from "next/cache";

export async function upsertService(_prev: unknown, formData: FormData) {
  const id = formData.get("id") as string;
  const category = formData.get("category") as string;
  const title = formData.get("title") as string;
  const description = formData.get("description") as string;
  const price = (formData.get("price") as string) || null;
  const priceDetail = (formData.get("priceDetail") as string) || null;
  const icon = (formData.get("icon") as string) || null;
  const ctaText = (formData.get("ctaText") as string) || null;
  const ctaHref = (formData.get("ctaHref") as string) || null;
  const sortOrder = parseInt(formData.get("sortOrder") as string) || 0;

  if (id) {
    await db.update(services).set({ category, title, description, price, priceDetail, icon, ctaText, ctaHref, sortOrder }).where(eq(services.id, parseInt(id)));
  } else {
    await db.insert(services).values({ category, title, description, price, priceDetail, icon, ctaText, ctaHref, sortOrder });
  }
  revalidatePath("/", "layout");
  return "Service saved.";
}

export async function deleteService(id: number) {
  await db.delete(services).where(eq(services.id, id));
  revalidatePath("/", "layout");
}
