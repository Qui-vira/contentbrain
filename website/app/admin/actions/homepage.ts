"use server";

import { db } from "@/lib/db";
import { stats, testimonials } from "@/lib/schema";
import { eq } from "drizzle-orm";
import { revalidatePath } from "next/cache";

export async function upsertStat(_prev: unknown, formData: FormData) {
  const id = formData.get("id") as string;
  const page = formData.get("page") as string;
  const label = formData.get("label") as string;
  const value = parseInt(formData.get("value") as string) || 0;
  const suffix = (formData.get("suffix") as string) || "";
  const sortOrder = parseInt(formData.get("sortOrder") as string) || 0;

  if (id) {
    await db.update(stats).set({ page, label, value, suffix, sortOrder }).where(eq(stats.id, parseInt(id)));
  } else {
    await db.insert(stats).values({ page, label, value, suffix, sortOrder });
  }
  revalidatePath("/", "layout");
  return "Stat saved.";
}

export async function deleteStat(id: number) {
  await db.delete(stats).where(eq(stats.id, id));
  revalidatePath("/", "layout");
}

export async function upsertTestimonial(_prev: unknown, formData: FormData) {
  const id = formData.get("id") as string;
  const page = formData.get("page") as string;
  const quote = formData.get("quote") as string;
  const attribution = formData.get("attribution") as string;
  const sortOrder = parseInt(formData.get("sortOrder") as string) || 0;

  // Collect images
  const imageUrls: string[] = [];
  for (let i = 0; i < 5; i++) {
    const url = (formData.get(`image_${i}`) as string)?.trim();
    if (url) imageUrls.push(url);
  }

  const rating = parseInt(formData.get("rating") as string) || 5;
  const avatar = (formData.get("avatar") as string)?.trim() || null;
  const category = (formData.get("category") as string)?.trim() || "general";

  const data = {
    page,
    quote,
    attribution,
    image: imageUrls[0] || null,
    images: imageUrls.length > 0 ? JSON.stringify(imageUrls) : null,
    rating,
    avatar,
    category,
    sortOrder,
  };

  if (id) {
    await db.update(testimonials).set(data).where(eq(testimonials.id, parseInt(id)));
  } else {
    await db.insert(testimonials).values(data);
  }
  revalidatePath("/", "layout");
  return "Testimonial saved.";
}

export async function deleteTestimonial(id: number) {
  await db.delete(testimonials).where(eq(testimonials.id, id));
  revalidatePath("/", "layout");
}
