"use server";

import { db } from "@/lib/db";
import { aboutValues, aboutEcosystem, aboutContent } from "@/lib/schema";
import { eq } from "drizzle-orm";
import { revalidatePath } from "next/cache";

export async function upsertAboutValue(_prev: unknown, formData: FormData) {
  const id = formData.get("id") as string;
  const icon = formData.get("icon") as string;
  const title = formData.get("title") as string;
  const description = formData.get("description") as string;
  const sortOrder = parseInt(formData.get("sortOrder") as string) || 0;

  if (id) {
    await db.update(aboutValues).set({ icon, title, description, sortOrder }).where(eq(aboutValues.id, parseInt(id)));
  } else {
    await db.insert(aboutValues).values({ icon, title, description, sortOrder });
  }
  revalidatePath("/", "layout");
  return "Value saved.";
}

export async function deleteAboutValue(id: number) {
  await db.delete(aboutValues).where(eq(aboutValues.id, id));
  revalidatePath("/", "layout");
}

export async function upsertEcosystem(_prev: unknown, formData: FormData) {
  const id = formData.get("id") as string;
  const name = formData.get("name") as string;
  const role = formData.get("role") as string;
  const description = formData.get("description") as string;
  const sortOrder = parseInt(formData.get("sortOrder") as string) || 0;

  if (id) {
    await db.update(aboutEcosystem).set({ name, role, description, sortOrder }).where(eq(aboutEcosystem.id, parseInt(id)));
  } else {
    await db.insert(aboutEcosystem).values({ name, role, description, sortOrder });
  }
  revalidatePath("/", "layout");
  return "Ecosystem item saved.";
}

export async function deleteEcosystem(id: number) {
  await db.delete(aboutEcosystem).where(eq(aboutEcosystem.id, id));
  revalidatePath("/", "layout");
}

export async function updateAboutContent(_prev: unknown, formData: FormData) {
  const entries = Array.from(formData.entries());
  for (const [key, value] of entries) {
    if (key.startsWith("content_")) {
      const contentKey = key.replace("content_", "");
      await db
        .insert(aboutContent)
        .values({ key: contentKey, value: value as string })
        .onConflictDoUpdate({ target: aboutContent.key, set: { value: value as string } });
    }
  }
  revalidatePath("/", "layout");
  return "Content saved.";
}
