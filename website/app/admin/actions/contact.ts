"use server";

import { db } from "@/lib/db";
import { contactOptions, serviceOptions } from "@/lib/schema";
import { eq } from "drizzle-orm";
import { revalidatePath } from "next/cache";

export async function upsertContactOption(_prev: unknown, formData: FormData) {
  const id = formData.get("id") as string;
  const icon = formData.get("icon") as string;
  const title = formData.get("title") as string;
  const description = formData.get("description") as string;
  const href = formData.get("href") as string;
  const sortOrder = parseInt(formData.get("sortOrder") as string) || 0;

  if (id) {
    await db.update(contactOptions).set({ icon, title, description, href, sortOrder }).where(eq(contactOptions.id, parseInt(id)));
  } else {
    await db.insert(contactOptions).values({ icon, title, description, href, sortOrder });
  }
  revalidatePath("/", "layout");
  return "Contact option saved.";
}

export async function deleteContactOption(id: number) {
  await db.delete(contactOptions).where(eq(contactOptions.id, id));
  revalidatePath("/", "layout");
}

export async function upsertServiceOption(_prev: unknown, formData: FormData) {
  const id = formData.get("id") as string;
  const name = formData.get("name") as string;
  const sortOrder = parseInt(formData.get("sortOrder") as string) || 0;

  if (id) {
    await db.update(serviceOptions).set({ name, sortOrder }).where(eq(serviceOptions.id, parseInt(id)));
  } else {
    await db.insert(serviceOptions).values({ name, sortOrder });
  }
  revalidatePath("/", "layout");
  return "Service option saved.";
}

export async function deleteServiceOption(id: number) {
  await db.delete(serviceOptions).where(eq(serviceOptions.id, id));
  revalidatePath("/", "layout");
}
