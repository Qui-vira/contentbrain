"use server";

import { db } from "@/lib/db";
import { adminUsers } from "@/lib/schema";
import { eq } from "drizzle-orm";
import { compare } from "bcryptjs";
import { createSession, destroySession } from "@/lib/auth";
import { redirect } from "next/navigation";

export async function login(
  _prevState: string | null,
  formData: FormData
): Promise<string | null> {
  const username = formData.get("username") as string;
  const password = formData.get("password") as string;

  if (!username || !password) {
    return "Username and password are required.";
  }

  const [user] = await db
    .select()
    .from(adminUsers)
    .where(eq(adminUsers.username, username))
    .limit(1);

  if (!user) {
    return "Invalid credentials.";
  }

  const valid = await compare(password, user.passwordHash);
  if (!valid) {
    return "Invalid credentials.";
  }

  await createSession(user.id);
  redirect("/admin");
}

export async function logout() {
  await destroySession();
  redirect("/admin/login");
}
