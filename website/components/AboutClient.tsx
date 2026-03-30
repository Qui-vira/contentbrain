"use client";

import { motion } from "framer-motion";
import { SectionWrapper } from "@/components/SectionWrapper";
import { GlassCard3D } from "@/components/GlassCard3D";
import { TextReveal } from "@/components/TextReveal";
import Image from "next/image";
import { StaggerGrid } from "@/components/StaggerGrid";
import { Marquee } from "@/components/Marquee";
import { AutoCarousel } from "@/components/AutoCarousel";
import { getIcon } from "@/lib/icons";

interface Value {
  icon: string;
  title: string;
  description: string;
}

interface EcosystemItem {
  name: string;
  role: string;
  description: string;
}

interface Milestone {
  year: string;
  title: string;
  text: string;
  allImages: string[];
  imageLayout: "carousel" | "grid";
}

interface AboutClientProps {
  content: Record<string, string>;
  values: Value[];
  ecosystem: EcosystemItem[];
  marqueeItems: string[];
  milestones: Milestone[];
}

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] as const } },
};

/* ─── Image Grid ─── */
function ImageGrid({ images, alt }: { images: string[]; alt: string }) {
  if (images.length === 1) {
    return (
      <div className="group relative overflow-hidden rounded-2xl border border-border">
        <Image src={images[0]} alt={alt} width={600} height={400} className="h-auto w-full transition-transform duration-700 group-hover:scale-105" />
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-2">
      {images.map((img, idx) => (
        <div key={idx} className={`group relative overflow-hidden rounded-xl border border-border ${images.length === 3 && idx === 2 ? "col-span-2" : ""}`}>
          <Image src={img} alt={`${alt} ${idx + 1}`} width={300} height={200} className="h-auto w-full transition-transform duration-700 group-hover:scale-105" />
        </div>
      ))}
    </div>
  );
}

export function AboutClient({ content, values, ecosystem, marqueeItems, milestones }: AboutClientProps) {
  return (
    <main className="min-h-screen bg-bg-primary">

      {/* ═══════════════════════════════════════════
          HERO
      ═══════════════════════════════════════════ */}
      <section className="relative overflow-hidden pt-32 pb-20 md:pt-44 md:pb-28">
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
          <div className="h-[600px] w-[600px] rounded-full bg-accent/5 blur-[120px]" />
        </div>

        <div className="relative mx-auto max-w-[1000px] px-6 text-center">
          {/* Profile image */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="mx-auto mb-10 w-full max-w-[480px]"
          >
            <div className="relative overflow-hidden rounded-2xl border border-border">
              <Image
                src={content.hero_image || "/quivira-hero.webp"}
                alt="Big Quiv"
                width={1376}
                height={768}
                className="h-auto w-full"
                priority
              />
            </div>
          </motion.div>

          <TextReveal as="h1" mode="words" className="text-3xl font-bold tracking-tight text-text-primary sm:text-4xl md:text-5xl md:leading-tight">
            {content.hero_title || "The person behind the brand."}
          </TextReveal>
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-text-secondary whitespace-pre-line"
          >
            {content.hero_subtitle || ""}
          </motion.p>
        </div>
      </section>

      {/* ═══════════════════════════════════════════
          WHAT I DO
      ═══════════════════════════════════════════ */}
      {content.what_i_do && (
        <SectionWrapper className="py-20 md:py-28">
          <div className="mx-auto max-w-[900px] px-6">
            <div className="mb-4 text-xs font-semibold uppercase tracking-[0.2em] text-accent">
              What I Do
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-text-primary md:text-3xl">
              {content.what_i_do}
            </h2>

            {content.services_list && (
              <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2">
                {content.services_list.split("\n").filter(Boolean).map((s, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -12 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.06, duration: 0.4 }}
                    className="flex items-center gap-4 rounded-xl border border-border bg-bg-secondary/40 px-5 py-4"
                  >
                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent/10 text-xs font-bold text-accent">
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <span className="text-sm font-medium text-text-primary">{s}</span>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </SectionWrapper>
      )}


      {/* ═══════════════════════════════════════════
          GROWTH TIMELINE (milestone cards with images)
      ═══════════════════════════════════════════ */}
      {milestones.length > 0 && (
        <SectionWrapper className="py-20 md:py-28">
          <div className="mx-auto max-w-[1000px] px-6">
            <div className="mb-4 text-center text-xs font-semibold uppercase tracking-[0.2em] text-accent">
              The Journey
            </div>
            <TextReveal as="h2" mode="words" className="mb-16 text-center text-3xl font-bold tracking-tight text-text-primary md:text-4xl">
              Growth Timeline
            </TextReveal>

            <div className="space-y-20 md:space-y-28">
              {milestones.map((m, i) => {
                const imageOnLeft = i % 2 === 0;
                const hasImages = m.allImages.length > 0;

                return (
                  <motion.div
                    key={i}
                    variants={fadeUp}
                    initial="hidden"
                    whileInView="show"
                    viewport={{ once: true, margin: "-10%" }}
                    className={`flex flex-col gap-8 md:flex-row md:items-center md:gap-14 ${!imageOnLeft ? "md:flex-row-reverse" : ""}`}
                  >
                    {/* Image side */}
                    {hasImages ? (
                      <div className="w-full shrink-0 md:w-[45%]">
                        {m.imageLayout === "grid" ? (
                          <ImageGrid images={m.allImages} alt={m.title} />
                        ) : (
                          <AutoCarousel images={m.allImages} alt={m.title} interval={4000} />
                        )}
                      </div>
                    ) : (
                      <div className="hidden w-full shrink-0 md:block md:w-[45%]">
                        <div className="flex aspect-[3/2] items-center justify-center rounded-2xl border border-border/50 bg-bg-secondary/30">
                          <span className="text-6xl font-black text-border">{m.year}</span>
                        </div>
                      </div>
                    )}

                    {/* Text side */}
                    <div className="flex-1">
                      <span className="inline-block rounded-full bg-accent/10 px-4 py-1.5 text-xs font-bold tracking-wide text-accent">
                        {m.year}
                      </span>
                      <h3 className="mt-4 text-2xl font-bold text-text-primary md:text-3xl">
                        {m.title}
                      </h3>
                      {/* Render text with line breaks preserved */}
                      <div className="mt-4 space-y-3">
                        {m.text.split("\n").map((paragraph, pi) => {
                          const trimmed = paragraph.trim();
                          if (!trimmed) return null;
                          return (
                            <p key={pi} className="text-[17px] leading-[1.85] text-text-secondary">
                              {trimmed}
                            </p>
                          );
                        })}
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </SectionWrapper>
      )}

      {/* ═══════════════════════════════════════════
          THE MISSION
      ═══════════════════════════════════════════ */}
      <SectionWrapper className="py-20 md:py-28">
        <div className="mx-auto max-w-[800px] px-6 text-center">
          <div className="mb-4 text-xs font-semibold uppercase tracking-[0.2em] text-accent">
            {content.mission_title || "The Mission"}
          </div>
          <TextReveal as="h2" mode="words" className="text-2xl font-bold leading-snug tracking-tight text-text-primary md:text-4xl md:leading-snug">
            {content.mission || ""}
          </TextReveal>
          <motion.div
            initial={{ scaleX: 0 }}
            whileInView={{ scaleX: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.5, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="mx-auto mt-8 h-[2px] w-24 origin-left bg-accent"
          />
        </div>
      </SectionWrapper>

      {/* ═══════════════════════════════════════════
          WHY PEOPLE TRUST ME / VALUES
      ═══════════════════════════════════════════ */}
      <SectionWrapper className="py-20 md:py-28">
        <div className="mx-auto max-w-[1000px] px-6">
          <div className="text-center">
            <div className="mb-4 text-xs font-semibold uppercase tracking-[0.2em] text-accent">
              Why People Trust Me
            </div>
            <TextReveal as="h2" mode="words" className="text-3xl font-bold tracking-tight text-text-primary md:text-4xl">
              What Quivira Stands For
            </TextReveal>
          </div>

          <StaggerGrid direction="up" className="mt-14 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {values.map((v) => {
              const Icon = getIcon(v.icon);
              return (
                <GlassCard3D key={v.title}>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent/10">
                    <Icon className="h-6 w-6 text-accent" />
                  </div>
                  <h3 className="mt-5 text-lg font-bold text-text-primary">{v.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-text-secondary whitespace-pre-line">{v.description}</p>
                </GlassCard3D>
              );
            })}
          </StaggerGrid>
        </div>
      </SectionWrapper>

      {/* ═══════════════════════════════════════════
          MARQUEE
      ═══════════════════════════════════════════ */}
      <Marquee
        items={marqueeItems}
        className="py-8 text-lg font-bold tracking-widest text-text-secondary/50"
      />

      {/* ═══════════════════════════════════════════
          ECOSYSTEM
      ═══════════════════════════════════════════ */}
      <SectionWrapper className="py-20 md:py-28">
        <div className="mx-auto max-w-[1000px] px-6">
          <div className="text-center">
            <div className="mb-4 text-xs font-semibold uppercase tracking-[0.2em] text-accent">
              The Brands
            </div>
            <TextReveal as="h2" mode="words" className="text-3xl font-bold tracking-tight text-text-primary md:text-4xl">
              The Ecosystem
            </TextReveal>
          </div>

          <StaggerGrid direction="scale" className="mt-14 grid grid-cols-2 gap-5 md:grid-cols-4">
            {ecosystem.map((e) => (
              <GlassCard3D key={e.name}>
                <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-accent">{e.role}</div>
                <h3 className="mt-3 text-lg font-bold text-text-primary">{e.name}</h3>
                <p className="mt-2 text-sm text-text-secondary leading-relaxed whitespace-pre-line">{e.description}</p>
              </GlassCard3D>
            ))}
          </StaggerGrid>
        </div>
      </SectionWrapper>
    </main>
  );
}
