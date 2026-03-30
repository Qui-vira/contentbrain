"use server";

import { db } from "@/lib/db";
import { settings, socialLinks } from "@/lib/schema";
import { eq } from "drizzle-orm";
import { revalidatePath } from "next/cache";

export async function updateSetting(key: string, value: string) {
  await db
    .insert(settings)
    .values({ key, value })
    .onConflictDoUpdate({ target: settings.key, set: { value } });
  revalidatePath("/", "layout");
}

export async function updateSettings(_prev: unknown, formData: FormData) {
  const entries = Array.from(formData.entries());
  for (const [key, value] of entries) {
    if (key.startsWith("setting_")) {
      await updateSetting(key.replace("setting_", ""), value as string);
    }
  }
  revalidatePath("/", "layout");
  return "Settings saved.";
}

export async function upsertSocialLink(_prev: unknown, formData: FormData) {
  const id = formData.get("id") as string;
  const name = formData.get("name") as string;
  const href = formData.get("href") as string;
  const sortOrder = parseInt(formData.get("sortOrder") as string) || 0;

  if (id) {
    await db.update(socialLinks).set({ name, href, sortOrder }).where(eq(socialLinks.id, parseInt(id)));
  } else {
    await db.insert(socialLinks).values({ name, href, sortOrder });
  }
  revalidatePath("/", "layout");
  return "Social link saved.";
}

export async function deleteSocialLink(id: number) {
  await db.delete(socialLinks).where(eq(socialLinks.id, id));
  revalidatePath("/", "layout");
}
