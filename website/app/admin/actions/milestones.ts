"use server";

import { db } from "@/lib/db";
import { milestones } from "@/lib/schema";
import { eq } from "drizzle-orm";
import { revalidatePath } from "next/cache";

export async function upsertMilestone(_prev: unknown, formData: FormData) {
  const id = formData.get("id") as string;
  const year = formData.get("year") as string;
  const title = formData.get("title") as string;
  const text = formData.get("text") as string;
  const imageLayout = (formData.get("imageLayout") as string) || "carousel";
  const sortOrder = parseInt(formData.get("sortOrder") as string) || 0;

  // Collect all image URLs from form (image_0, image_1, ... image_4)
  const imageUrls: string[] = [];
  for (let i = 0; i < 5; i++) {
    const url = (formData.get(`image_${i}`) as string)?.trim();
    if (url) imageUrls.push(url);
  }

  const data = {
    year,
    title,
    text,
    image: imageUrls[0] || null,
    images: imageUrls.length > 0 ? JSON.stringify(imageUrls) : null,
    imageLayout,
    sortOrder,
  };

  if (id) {
    await db.update(milestones).set(data).where(eq(milestones.id, parseInt(id)));
  } else {
    await db.insert(milestones).values(data);
  }
  revalidatePath("/", "layout");
  return "Milestone saved.";
}

export async function deleteMilestone(id: number) {
  await db.delete(milestones).where(eq(milestones.id, id));
  revalidatePath("/", "layout");
}
