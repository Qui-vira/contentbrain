import { NextRequest, NextResponse } from "next/server";
import { getSupabase } from "@/lib/supabase";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    const required = ["full_name", "email", "phone", "city", "state", "drone_model", "experience_years", "availability"];
    for (const field of required) {
      if (!body[field]) {
        return NextResponse.json({ error: `${field} is required` }, { status: 400 });
      }
    }

    const supabase = getSupabase();
    const row = {
      full_name: body.full_name,
      email: body.email,
      phone: body.phone,
      instagram_handle: body.instagram_handle || null,
      city: body.city,
      state: body.state,
      drone_model: body.drone_model,
      has_license: body.has_license || false,
      license_type: body.license_type || null,
      experience_years: parseInt(body.experience_years),
      portfolio_url: body.portfolio_url || null,
      services_offered: body.services_offered || [],
      availability: body.availability,
      rate_per_hour: body.rate_per_hour || null,
      additional_notes: body.additional_notes || null,
    };

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const { error } = await (supabase.from("drone_pilot_signups") as any).insert(row);

    if (error) {
      console.error("Supabase insert error:", error);
      return NextResponse.json({ error: "Failed to submit signup" }, { status: 500 });
    }

    return NextResponse.json({ success: true });
  } catch (err) {
    console.error("Drone signup error:", err);
    return NextResponse.json({ error: "Server error" }, { status: 500 });
  }
}
