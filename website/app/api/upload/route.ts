import { NextRequest, NextResponse } from "next/server";
import { jwtVerify } from "jose";

const ALLOWED_TYPES = ["image/", "video/"];
const MAX_SIZE = 10 * 1024 * 1024; // 10MB

export async function POST(request: NextRequest) {
  // Auth check - only admin can upload
  const token = request.cookies.get("admin_session")?.value;
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
  try {
    const secret = new TextEncoder().encode(process.env.ADMIN_SESSION_SECRET!);
    await jwtVerify(token, secret);
  } catch {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const formData = await request.formData();
  const file = formData.get("file") as File | null;

  if (!file) {
    return NextResponse.json({ error: "No file provided" }, { status: 400 });
  }

  if (file.size > MAX_SIZE) {
    return NextResponse.json({ error: "File too large. Max 10MB." }, { status: 400 });
  }

  const isAllowed = ALLOWED_TYPES.some((t) => file.type.startsWith(t));
  if (!isAllowed) {
    return NextResponse.json({ error: "Only images and videos allowed" }, { status: 400 });
  }

  // Try Vercel Blob first, fallback to base64 data URL
  try {
    const { put } = await import("@vercel/blob");
    const blob = await put(file.name, file, { access: "public" });
    return NextResponse.json({ url: blob.url });
  } catch {
    // Fallback: convert to base64 data URL
    const bytes = await file.arrayBuffer();
    const base64 = Buffer.from(bytes).toString("base64");
    const dataUrl = `data:${file.type};base64,${base64}`;
    return NextResponse.json({ url: dataUrl });
  }
}
