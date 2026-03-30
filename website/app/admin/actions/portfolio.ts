"use server";

import { db } from "@/lib/db";
import { caseStudies, caseStudyStats } from "@/lib/schema";
import { eq } from "drizzle-orm";
import { revalidatePath } from "next/cache";

export async function upsertCaseStudy(_prev: unknown, formData: FormData) {
  const id = formData.get("id") as string;
  const title = formData.get("title") as string;
  const sortOrder = parseInt(formData.get("sortOrder") as string) || 0;
  const statsText = formData.get("stats") as string;

  // Collect images
  const imageUrls: string[] = [];
  for (let i = 0; i < 5; i++) {
    const url = (formData.get(`image_${i}`) as string)?.trim();
    if (url) imageUrls.push(url);
  }

  // Collect videos
  const videoUrls: string[] = [];
  for (let i = 0; i < 5; i++) {
    const url = (formData.get(`video_${i}`) as string)?.trim();
    if (url) videoUrls.push(url);
  }

  let caseStudyId: number;

  const data = {
    title,
    image: imageUrls[0] || null,
    images: imageUrls.length > 0 ? JSON.stringify(imageUrls) : null,
    videos: videoUrls.length > 0 ? JSON.stringify(videoUrls) : null,
    sortOrder,
  };

  if (id) {
    await db.update(caseStudies).set(data).where(eq(caseStudies.id, parseInt(id)));
    caseStudyId = parseInt(id);
    // Delete old stats and re-insert
    await db.delete(caseStudyStats).where(eq(caseStudyStats.caseStudyId, caseStudyId));
  } else {
    const [inserted] = await db.insert(caseStudies).values(data).returning();
    caseStudyId = inserted.id;
  }

  // Insert stats
  const lines = statsText.split("\n").map((l) => l.trim()).filter(Boolean);
  for (let i = 0; i < lines.length; i++) {
    await db.insert(caseStudyStats).values({ caseStudyId, stat: lines[i], sortOrder: i });
  }

  revalidatePath("/", "layout");
  return "Case study saved.";
}

export async function deleteCaseStudy(id: number) {
  await db.delete(caseStudyStats).where(eq(caseStudyStats.caseStudyId, id));
  await db.delete(caseStudies).where(eq(caseStudies.id, id));
  revalidatePath("/", "layout");
}
