"use client";

import { useState } from "react";
import { SectionWrapper } from "@/components/SectionWrapper";
import { GlassCard3D } from "@/components/GlassCard3D";
import { MagneticButton } from "@/components/MagneticButton";
import { TextReveal } from "@/components/TextReveal";
import { StaggerGrid } from "@/components/StaggerGrid";
import { motion } from "framer-motion";
import { getIcon } from "@/lib/icons";

interface ContactOption {
  icon: string;
  title: string;
  description: string;
  href: string;
}

interface ContactClientProps {
  contactOptions: ContactOption[];
  socialLinks: { name: string; href: string }[];
  serviceOptions: string[];
  formsubmitEmail: string;
}

function AnimatedInput({
  type = "text",
  id,
  name,
  required,
  placeholder,
  as,
  rows,
  children,
}: {
  type?: string;
  id: string;
  name: string;
  required?: boolean;
  placeholder?: string;
  as?: "textarea" | "select";
  rows?: number;
  children?: React.ReactNode;
}) {
  const baseClass =
    "w-full rounded-lg border bg-bg-tertiary px-4 py-3 text-text-primary placeholder:text-text-muted focus:outline-none transition-colors";

  if (as === "textarea") {
    return (
      <motion.textarea
        id={id}
        name={name}
        rows={rows}
        required={required}
        placeholder={placeholder}
        className={`${baseClass} resize-none`}
        initial={{ borderColor: "var(--color-border)" }}
        whileFocus={{ borderColor: "var(--color-accent)" }}
        transition={{ duration: 0.2 }}
      />
    );
  }

  if (as === "select") {
    return (
      <motion.select
        id={id}
        name={name}
        required={required}
        className={baseClass}
        initial={{ borderColor: "var(--color-border)" }}
        whileFocus={{ borderColor: "var(--color-accent)" }}
        transition={{ duration: 0.2 }}
      >
        {children}
      </motion.select>
    );
  }

  return (
    <motion.input
      type={type}
      id={id}
      name={name}
      required={required}
      placeholder={placeholder}
      className={baseClass}
      initial={{ borderColor: "var(--color-border)" }}
      whileFocus={{ borderColor: "var(--color-accent)" }}
      transition={{ duration: 0.2 }}
    />
  );
}

export function ContactClient({ contactOptions, socialLinks, serviceOptions, formsubmitEmail }: ContactClientProps) {
  const [submitted, setSubmitted] = useState(false);

  return (
    <main className="min-h-screen bg-bg-primary">
      {/* Hero */}
      <SectionWrapper className="pt-32 pb-16 md:pt-40">
        <div className="mx-auto max-w-[1200px] px-6 text-center">
          <TextReveal as="h1" mode="words" className="text-4xl font-bold tracking-tight text-text-primary md:text-6xl md:leading-tight">
            Let&apos;s build something.
          </TextReveal>
          <p className="mx-auto mt-4 max-w-xl text-lg text-text-secondary">
            Whether you need signals, strategy, or a full system, the first step is a conversation.
          </p>
        </div>
      </SectionWrapper>

      {/* Contact Options */}
      <SectionWrapper className="py-16 md:py-24">
        <div className="mx-auto max-w-[1200px] px-6">
          <StaggerGrid direction="up" className="grid grid-cols-1 gap-6 md:grid-cols-3">
            {contactOptions.map((opt) => {
              const Icon = getIcon(opt.icon);
              return (
                <a key={opt.title} href={opt.href} target="_blank" rel="noopener noreferrer">
                  <GlassCard3D className="text-center">
                    <Icon className="mx-auto h-8 w-8 text-accent" />
                    <h3 className="mt-4 text-xl font-bold text-text-primary">{opt.title}</h3>
                    <p className="mt-2 text-text-secondary whitespace-pre-line">{opt.description}</p>
                  </GlassCard3D>
                </a>
              );
            })}
          </StaggerGrid>
        </div>
      </SectionWrapper>

      {/* Social Links */}
      <SectionWrapper className="py-8">
        <div className="mx-auto max-w-[1200px] px-6">
          <div className="flex flex-wrap items-center justify-center gap-6">
            {socialLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-medium text-text-secondary transition-colors hover:text-accent"
              >
                {link.name}
              </a>
            ))}
          </div>
        </div>
      </SectionWrapper>

      {/* Contact Form */}
      <SectionWrapper className="py-16 md:py-24">
        <div className="mx-auto max-w-xl px-6">
          <TextReveal as="h2" mode="words" className="mb-8 text-center text-3xl font-bold tracking-tight text-text-primary md:text-4xl">
            Send a Message
          </TextReveal>

          {submitted ? (
            <div className="rounded-xl border border-accent/30 bg-bg-secondary p-8 text-center">
              <p className="text-lg font-semibold text-text-primary">Message sent.</p>
              <p className="mt-2 text-text-secondary">I&apos;ll get back to you within 24 hours.</p>
            </div>
          ) : (
            <form
              action={`https://formsubmit.co/${formsubmitEmail}`}
              method="POST"
              onSubmit={() => setSubmitted(true)}
              className="space-y-5"
            >
              <input type="hidden" name="_subject" value="New inquiry from bigquivdigitals.com" />
              <input type="hidden" name="_captcha" value="false" />
              <input type="hidden" name="_next" value="https://bigquivdigitals.com/contact" />

              <div>
                <label htmlFor="name" className="mb-2 block text-sm font-medium text-text-secondary">Name</label>
                <AnimatedInput type="text" id="name" name="name" required placeholder="Your name" />
              </div>

              <div>
                <label htmlFor="email" className="mb-2 block text-sm font-medium text-text-secondary">Email</label>
                <AnimatedInput type="email" id="email" name="email" required placeholder="you@example.com" />
              </div>

              <div>
                <label htmlFor="service" className="mb-2 block text-sm font-medium text-text-secondary">Service</label>
                <AnimatedInput as="select" id="service" name="service" required>
                  <option value="" disabled>Select a service</option>
                  {serviceOptions.map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </AnimatedInput>
              </div>

              <div>
                <label htmlFor="message" className="mb-2 block text-sm font-medium text-text-secondary">Message</label>
                <AnimatedInput as="textarea" id="message" name="message" rows={5} required placeholder="Tell me about your project or what you need help with..." />
              </div>

              <MagneticButton className="w-full justify-center" showArrow={false}>
                Send Message
              </MagneticButton>
            </form>
          )}
        </div>
      </SectionWrapper>
    </main>
  );
}
