"use client";

import { useState } from "react";

const SERVICES = [
  "Real Estate Photography",
  "Event Coverage",
  "Wedding Photography",
  "Construction/Survey",
  "Agriculture/Mapping",
  "Music Videos",
  "Commercial Ads",
  "Documentary/Film",
  "Social Media Content",
  "Inspection Services",
];

const CITIES = [
  "Lagos",
  "Abuja",
  "Port Harcourt",
  "Ibadan",
  "Enugu",
  "Calabar",
  "Owerri",
  "Benin City",
  "Kano",
  "Other",
];

const STATES = [
  "Lagos",
  "FCT (Abuja)",
  "Rivers",
  "Oyo",
  "Enugu",
  "Cross River",
  "Imo",
  "Edo",
  "Kano",
  "Delta",
  "Ogun",
  "Kaduna",
  "Anambra",
  "Other",
];

export default function DroneSignupPage() {
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    phone: "",
    instagram_handle: "",
    city: "",
    state: "",
    drone_model: "",
    has_license: false,
    license_type: "",
    experience_years: "",
    portfolio_url: "",
    services_offered: [] as string[],
    availability: "",
    rate_per_hour: "",
    additional_notes: "",
  });

  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");

  function update(field: string, value: string | boolean | string[]) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function toggleService(service: string) {
    setForm((prev) => ({
      ...prev,
      services_offered: prev.services_offered.includes(service)
        ? prev.services_offered.filter((s) => s !== service)
        : [...prev.services_offered, service],
    }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("submitting");
    setErrorMsg("");

    try {
      const res = await fetch("/api/drone-signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Submission failed");
      }

      setStatus("success");
    } catch (err: unknown) {
      setStatus("error");
      setErrorMsg(err instanceof Error ? err.message : "Something went wrong. Try again.");
    }
  }

  if (status === "success") {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center space-y-6">
          <div className="w-20 h-20 mx-auto rounded-full bg-accent/20 flex items-center justify-center">
            <svg className="w-10 h-10 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-text-primary">You're In!</h1>
          <p className="text-text-secondary text-lg">
            Your application has been submitted. We'll review your profile and reach out within 48 hours.
          </p>
          <p className="text-text-muted text-sm">
            Founding pilots get priority bookings and featured profiles at launch.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-16 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12 space-y-4">
          <div className="inline-block px-4 py-1.5 rounded-full bg-accent/10 text-accent text-sm font-medium mb-2">
            Founding Pilot Program
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-text-primary">
            Join Nigeria's First Drone Marketplace
          </h1>
          <p className="text-text-secondary text-lg max-w-lg mx-auto">
            We're recruiting 20 skilled drone camera pilots in Lagos, Abuja, and Port Harcourt.
            Early pilots get featured profiles and first access to paid gigs.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Personal Info */}
          <section className="space-y-4">
            <h2 className="text-lg font-semibold text-text-primary border-b border-border pb-2">
              Personal Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input label="Full Name *" value={form.full_name} onChange={(v) => update("full_name", v)} required />
              <Input label="Email *" type="email" value={form.email} onChange={(v) => update("email", v)} required />
              <Input label="Phone (WhatsApp) *" type="tel" value={form.phone} onChange={(v) => update("phone", v)} placeholder="+234..." required />
              <Input label="Instagram Handle" value={form.instagram_handle} onChange={(v) => update("instagram_handle", v)} placeholder="@username" />
            </div>
          </section>

          {/* Location */}
          <section className="space-y-4">
            <h2 className="text-lg font-semibold text-text-primary border-b border-border pb-2">
              Location
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Select label="City *" value={form.city} onChange={(v) => update("city", v)} options={CITIES} required />
              <Select label="State *" value={form.state} onChange={(v) => update("state", v)} options={STATES} required />
            </div>
          </section>

          {/* Drone Info */}
          <section className="space-y-4">
            <h2 className="text-lg font-semibold text-text-primary border-b border-border pb-2">
              Drone Equipment & Experience
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input label="Drone Model(s) *" value={form.drone_model} onChange={(v) => update("drone_model", v)} placeholder="e.g. DJI Mavic 3, Mini 4 Pro" required />
              <Input label="Years of Experience *" type="number" value={form.experience_years} onChange={(v) => update("experience_years", v)} placeholder="e.g. 2" required />
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => update("has_license", !form.has_license)}
                className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                  form.has_license ? "bg-accent border-accent" : "border-border-hover"
                }`}
              >
                {form.has_license && (
                  <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </button>
              <span className="text-text-secondary text-sm">I have a drone pilot license / NCAA certification</span>
            </div>

            {form.has_license && (
              <Input label="License Type" value={form.license_type} onChange={(v) => update("license_type", v)} placeholder="e.g. NCAA ROC, Part 107" />
            )}

            <Input label="Portfolio URL" value={form.portfolio_url} onChange={(v) => update("portfolio_url", v)} placeholder="Website, YouTube, or Google Drive link" />
          </section>

          {/* Services */}
          <section className="space-y-4">
            <h2 className="text-lg font-semibold text-text-primary border-b border-border pb-2">
              Services You Offer
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {SERVICES.map((service) => (
                <button
                  key={service}
                  type="button"
                  onClick={() => toggleService(service)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors border ${
                    form.services_offered.includes(service)
                      ? "bg-accent/20 border-accent text-accent"
                      : "border-border bg-bg-secondary text-text-secondary hover:border-border-hover"
                  }`}
                >
                  {service}
                </button>
              ))}
            </div>
          </section>

          {/* Availability & Rate */}
          <section className="space-y-4">
            <h2 className="text-lg font-semibold text-text-primary border-b border-border pb-2">
              Availability & Pricing
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Select
                label="Availability *"
                value={form.availability}
                onChange={(v) => update("availability", v)}
                options={["Full-time", "Part-time (weekdays)", "Weekends only", "On-call / Flexible"]}
                required
              />
              <Input label="Rate per Hour (NGN)" value={form.rate_per_hour} onChange={(v) => update("rate_per_hour", v)} placeholder="e.g. 25000" />
            </div>
          </section>

          {/* Notes */}
          <section className="space-y-4">
            <h2 className="text-lg font-semibold text-text-primary border-b border-border pb-2">
              Anything Else?
            </h2>
            <textarea
              value={form.additional_notes}
              onChange={(e) => update("additional_notes", e.target.value)}
              className="w-full px-4 py-3 rounded-lg bg-bg-secondary border border-border text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent transition-colors resize-none"
              rows={3}
              placeholder="Tell us about your experience, notable projects, or anything we should know..."
            />
          </section>

          {/* Error */}
          {status === "error" && (
            <div className="px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
              {errorMsg}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={status === "submitting"}
            className="w-full py-4 rounded-lg bg-accent hover:bg-accent-hover text-white font-semibold text-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {status === "submitting" ? "Submitting..." : "Apply as Founding Pilot"}
          </button>

          <p className="text-center text-text-muted text-xs">
            By submitting, you agree to be contacted about drone pilot opportunities.
          </p>
        </form>
      </div>
    </div>
  );
}

/* --- Reusable form components --- */

function Input({
  label,
  type = "text",
  value,
  onChange,
  placeholder,
  required,
}: {
  label: string;
  type?: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  required?: boolean;
}) {
  return (
    <label className="block space-y-1.5">
      <span className="text-text-secondary text-sm">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        className="w-full px-4 py-3 rounded-lg bg-bg-secondary border border-border text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent transition-colors"
      />
    </label>
  );
}

function Select({
  label,
  value,
  onChange,
  options,
  required,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: string[];
  required?: boolean;
}) {
  return (
    <label className="block space-y-1.5">
      <span className="text-text-secondary text-sm">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        className="w-full px-4 py-3 rounded-lg bg-bg-secondary border border-border text-text-primary focus:outline-none focus:border-accent transition-colors appearance-none"
      >
        <option value="">Select...</option>
        {options.map((opt) => (
          <option key={opt} value={opt}>{opt}</option>
        ))}
      </select>
    </label>
  );
}
