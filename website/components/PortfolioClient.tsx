"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";
import { SectionWrapper } from "@/components/SectionWrapper";
import { GlassCard3D } from "@/components/GlassCard3D";
import { CTABanner } from "@/components/CTABanner";
import { TextReveal } from "@/components/TextReveal";
import { StaggerGrid } from "@/components/StaggerGrid";
import { CountUp } from "@/components/CountUp";
import { TestimonialCard } from "@/components/TestimonialCard";
import { AutoCarousel } from "@/components/AutoCarousel";
import { Marquee } from "@/components/Marquee";

interface CaseStudy {
  title: string;
  stats: string[];
  allImages: string[];
  allVideos: string[];
}

interface Testimonial {
  quote: string;
  attribution: string;
  allImages: string[];
  rating: number;
  avatar: string | null;
  category: string;
}

interface PortfolioStat {
  label: string;
  value: number;
  suffix: string | null;
}

interface ClientLogo {
  name: string;
  image: string;
}

interface PortfolioClientProps {
  caseStudies: CaseStudy[];
  testimonials: Testimonial[];
  portfolioStats: PortfolioStat[];
  clientLogos: ClientLogo[];
  cta: { headline: string; subtext: string; buttonText: string; buttonHref: string } | null;
}

const CATEGORY_LABELS: Record<string, string> = {
  all: "All",
  general: "General",
  trading: "Trading Signals",
  content: "Content Strategy",
  consulting: "Consulting",
};

export function PortfolioClient({ caseStudies, testimonials, portfolioStats, clientLogos, cta }: PortfolioClientProps) {
  const [activeCategory, setActiveCategory] = useState("all");

  // Determine which category tabs to show based on actual testimonial data
  const availableCategories = ["all", ...Array.from(new Set(testimonials.map((t) => t.category)))];
  const showFilters = availableCategories.length > 2; // Only show if there are 2+ actual categories

  const filteredTestimonials = activeCategory === "all"
    ? testimonials
    : testimonials.filter((t) => t.category === activeCategory);

  // Compute aggregate rating
  const avgRating = testimonials.length > 0
    ? (testimonials.reduce((sum, t) => sum + (t.rating || 5), 0) / testimonials.length).toFixed(1)
    : "5.0";

  return (
    <main className="min-h-screen bg-bg-primary">
      {/* ───────── HERO ───────── */}
      <SectionWrapper className="pt-32 pb-16 md:pt-40">
        <div className="mx-auto max-w-[1200px] px-6 text-center">
          <TextReveal as="h1" mode="words" className="text-4xl font-bold tracking-tight text-text-primary md:text-6xl md:leading-tight">
            Results speak.
          </TextReveal>
          <p className="mx-auto mt-4 max-w-xl text-lg text-text-secondary">
            Data, not claims. Here&apos;s what the systems produce.
          </p>
        </div>
      </SectionWrapper>

      {/* ───────── STATS BAR ───────── */}
      {portfolioStats.length > 0 && (
        <SectionWrapper className="pb-16">
          <div className="mx-auto grid max-w-[1200px] grid-cols-2 gap-6 px-6 md:grid-cols-4">
            {portfolioStats.map((stat) => (
              <div key={stat.label} className="rounded-xl bg-bg-secondary p-6 text-center">
                <div className="text-4xl font-extrabold text-text-primary md:text-[56px] md:leading-none" style={{ textShadow: "0 0 20px rgba(230, 57, 70, 0.2)" }}>
                  <CountUp target={stat.value} suffix={stat.suffix || ""} />
                </div>
                <div className="mt-2 text-sm font-medium tracking-widest text-text-secondary uppercase">{stat.label}</div>
              </div>
            ))}
          </div>
        </SectionWrapper>
      )}

      {/* ───────── CLIENT LOGO BAR ───────── */}
      {clientLogos.length > 0 && (
        <div className="pb-12">
          <p className="mb-6 text-center text-xs font-semibold uppercase tracking-[0.2em] text-text-secondary/60">
            Trusted by
          </p>
          <Marquee
            items={clientLogos.map((l) => l.name)}
            speed={35}
            className="py-4"
            renderItem={(_, i) => {
              const logo = clientLogos[i % clientLogos.length];
              return (
                <div className="mx-8 flex h-10 w-24 items-center justify-center grayscale opacity-50 transition-all hover:grayscale-0 hover:opacity-100">
                  <Image src={logo.image} alt={logo.name} width={96} height={40} className="h-auto max-h-10 w-auto object-contain" />
                </div>
              );
            }}
          />
        </div>
      )}

      {/* ───────── CASE STUDIES ───────── */}
      <SectionWrapper className="py-16 md:py-24">
        <div className="mx-auto max-w-[1200px] px-6">
          <StaggerGrid direction="left" className="grid grid-cols-1 gap-6 md:grid-cols-2">
            {caseStudies.map((cs) => (
              <GlassCard3D key={cs.title}>
                {(cs.allImages.length > 0 || cs.allVideos.length > 0) && (
                  <div className="mb-5">
                    <AutoCarousel images={cs.allImages} videos={cs.allVideos} alt={cs.title} interval={5000} />
                  </div>
                )}
                <h3 className="text-xl font-bold text-text-primary">{cs.title}</h3>
                <ul className="mt-4 space-y-3">
                  {cs.stats.map((stat) => (
                    <li key={stat} className="flex items-start gap-3 text-text-secondary">
                      <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-accent" />
                      {stat}
                    </li>
                  ))}
                </ul>
              </GlassCard3D>
            ))}
          </StaggerGrid>
        </div>
      </SectionWrapper>

      {/* ───────── MID-PAGE CTA (Sandwich Pattern) ───────── */}
      {cta && (
        <CTABanner
          headline="See results like these?"
          subtext="Let&apos;s build your system."
          buttonText={cta.buttonText}
          buttonHref={cta.buttonHref}
        />
      )}

      {/* ───────── TESTIMONIALS ───────── */}
      <SectionWrapper className="py-16 md:py-24">
        <div className="mx-auto max-w-[1200px] px-6">
          {/* Header with aggregate stats */}
          <div className="mb-4 text-center">
            <TextReveal as="h2" mode="words" className="text-3xl font-bold tracking-tight text-text-primary md:text-4xl">
              What People Say
            </TextReveal>
            {testimonials.length > 0 && (
              <p className="mt-3 text-sm text-text-secondary">
                <span className="font-bold text-accent">{avgRating}/5</span> average rating from{" "}
                <span className="font-bold text-text-primary">{testimonials.length}</span> reviews
              </p>
            )}
          </div>

          {/* Category filter tabs */}
          {showFilters && (
            <div className="mb-10 flex flex-wrap justify-center gap-2">
              {availableCategories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={`rounded-full px-5 py-2 text-xs font-semibold tracking-wide transition-all ${
                    activeCategory === cat
                      ? "bg-accent text-white"
                      : "bg-bg-secondary text-text-secondary hover:text-text-primary"
                  }`}
                >
                  {CATEGORY_LABELS[cat] || cat}
                </button>
              ))}
            </div>
          )}

          {/* Testimonial grid */}
          <AnimatePresence mode="wait">
            <motion.div
              key={activeCategory}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.3 }}
              className="grid gap-8 md:grid-cols-2 lg:grid-cols-3"
            >
              {filteredTestimonials.map((t) => (
                <TestimonialCard
                  key={t.attribution}
                  quote={t.quote}
                  attribution={t.attribution}
                  images={t.allImages}
                  rating={t.rating}
                  avatar={t.avatar}
                />
              ))}
            </motion.div>
          </AnimatePresence>
        </div>
      </SectionWrapper>

      {/* ───────── FINAL CTA ───────── */}
      {cta && (
        <CTABanner
          headline={cta.headline}
          subtext={cta.subtext}
          buttonText={cta.buttonText}
          buttonHref={cta.buttonHref}
        />
      )}
    </main>
  );
}
