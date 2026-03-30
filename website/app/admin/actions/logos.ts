"use server";

import { db } from "@/lib/db";
import { clientLogos } from "@/lib/schema";
import { eq } from "drizzle-orm";
import { revalidatePath } from "next/cache";

export async function upsertClientLogo(_prev: unknown, formData: FormData) {
  const id = formData.get("id") as string;
  const name = formData.get("name") as string;
  const image = (formData.get("image") as string)?.trim() || "";
  const sortOrder = parseInt(formData.get("sortOrder") as string) || 0;

  if (id) {
    await db.update(clientLogos).set({ name, image, sortOrder }).where(eq(clientLogos.id, parseInt(id)));
  } else {
    await db.insert(clientLogos).values({ name, image, sortOrder });
  }
  revalidatePath("/", "layout");
  return "Logo saved.";
}

export async function deleteClientLogo(id: number) {
  await db.delete(clientLogos).where(eq(clientLogos.id, id));
  revalidatePath("/", "layout");
}
