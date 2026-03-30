"use client";

import { motion } from "framer-motion";
import { Handshake, GraduationCap, Cpu, ArrowRight } from "lucide-react";
import { KeywordRotator } from "@/components/KeywordRotator";
import { TextReveal } from "@/components/TextReveal";
import { CountUp } from "@/components/CountUp";
import { MagneticButton } from "@/components/MagneticButton";
import { Marquee } from "@/components/Marquee";
import { StaggerGrid } from "@/components/StaggerGrid";
import { GlassCard3D } from "@/components/GlassCard3D";
import { TestimonialCard } from "@/components/TestimonialCard";
import { CTABanner } from "@/components/CTABanner";
import { SectionWrapper } from "@/components/SectionWrapper";
import { GlobeHero } from "@/components/GlobeHero";

interface Stat {
  label: string;
  value: number;
  suffix: string | null;
}

interface Testimonial {
  quote: string;
  attribution: string;
  allImages: string[];
  rating: number;
  avatar: string | null;
}

interface HomeClientProps {
  calendlyUrl: string;
  heroTagline: string;
  heroSubtitle: string;
  trustStats: Stat[];
  resultStats: Stat[];
  testimonials: Testimonial[];
  marqueeItems: string[];
  cta: { headline: string; subtext: string; buttonText: string; buttonHref: string } | null;
}

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.15 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 24, filter: "blur(4px)" },
  show: { opacity: 1, y: 0, filter: "blur(0px)", transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] as const } },
};

export function HomeClient({
  calendlyUrl,
  heroTagline,
  heroSubtitle,
  trustStats,
  resultStats,
  testimonials,
  marqueeItems,
  cta,
}: HomeClientProps) {
  return (
    <main>
      {/* ───────── HERO ───────── */}
      <GlobeHero>
        <div className="mx-auto max-w-[1200px] px-6 text-center pt-16">
          <motion.div variants={stagger} initial="hidden" animate="show" className="flex flex-col items-center gap-6">
            <motion.div variants={fadeUp} className="text-lg font-medium tracking-wide text-accent md:text-xl">
              <TextReveal as="p" mode="words">
                {heroTagline}
              </TextReveal>
            </motion.div>

            <motion.div variants={fadeUp}>
              <h1 className="text-5xl font-extrabold leading-[1.08] tracking-tight text-text-primary md:text-7xl">
                Build. <KeywordRotator />. Dominate.
              </h1>
            </motion.div>

            <motion.div variants={fadeUp} className="max-w-xl text-lg leading-relaxed text-text-secondary whitespace-pre-line">
              {heroSubtitle}
            </motion.div>

            <motion.div variants={fadeUp} className="flex flex-wrap gap-4">
              <MagneticButton href="/services">Explore Services</MagneticButton>
              <MagneticButton href={calendlyUrl} variant="secondary">
                Book a Call
              </MagneticButton>
            </motion.div>
          </motion.div>
        </div>
      </GlobeHero>

      {/* ───────── TRUST BAR ───────── */}
      <SectionWrapper className="py-16 md:py-24">
        <div className="mx-auto grid max-w-[1200px] grid-cols-2 gap-6 px-6 md:grid-cols-4">
          {trustStats.map((stat) => (
            <div key={stat.label} className="rounded-xl bg-bg-secondary p-6 text-center">
              <div className="text-4xl font-extrabold text-text-primary md:text-[56px] md:leading-none" style={{ textShadow: "0 0 20px rgba(230, 57, 70, 0.2)" }}>
                <CountUp target={stat.value} suffix={stat.suffix || ""} />
              </div>
              <div className="mt-2 text-sm font-medium tracking-widest text-text-secondary uppercase">{stat.label}</div>
            </div>
          ))}
        </div>
      </SectionWrapper>

      {/* ───────── WHAT I DO ───────── */}
      <SectionWrapper className="py-16 md:py-24">
        <div className="mx-auto max-w-[1200px] px-6">
          <h2 className="text-center text-3xl font-bold tracking-tight text-text-primary md:text-5xl md:leading-tight">
            Three Pillars. One System.
          </h2>

          <StaggerGrid className="mt-14 grid gap-8 md:grid-cols-3" direction="up" staggerDelay={0.15}>
            <GlassCard3D>
              <Handshake className="mb-4 h-8 w-8 text-accent" />
              <h3 className="text-xl font-bold text-text-primary">Consulting &amp; Advisory</h3>
              <p className="mt-3 text-text-secondary leading-relaxed">
                Brand strategy, KOL networking, community management, and launch
                campaigns tailored to Web3 projects and personal brands.
              </p>
              <a href="/services" className="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-accent hover:text-accent-hover transition-colors">
                Learn more <ArrowRight className="h-4 w-4" />
              </a>
            </GlassCard3D>

            <GlassCard3D>
              <GraduationCap className="mb-4 h-8 w-8 text-accent" />
              <h3 className="text-xl font-bold text-text-primary">Education</h3>
              <p className="mt-3 text-text-secondary leading-relaxed">
                Structured courses on trading, airdrop farming, KOL growth, and
                crypto development. Real education that produces builders.
              </p>
              <a href="/services#education" className="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-accent hover:text-accent-hover transition-colors">
                See courses <ArrowRight className="h-4 w-4" />
              </a>
            </GlassCard3D>

            <GlassCard3D>
              <Cpu className="mb-4 h-8 w-8 text-accent" />
              <h3 className="text-xl font-bold text-text-primary">AI Products</h3>
              <p className="mt-3 text-text-secondary leading-relaxed">
                SignalOS for automated trading signals. ContentBrain for AI-powered
                content intelligence. Systems that work while you sleep.
              </p>
              <a href="/services#ai-products" className="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-accent hover:text-accent-hover transition-colors">
                Explore products <ArrowRight className="h-4 w-4" />
              </a>
            </GlassCard3D>
          </StaggerGrid>
        </div>
      </SectionWrapper>

      {/* ───────── MARQUEE BAND ───────── */}
      <Marquee
        items={marqueeItems}
        speed={25}
        className="py-8 text-2xl font-bold tracking-widest text-text-muted/30 md:text-4xl"
      />

      {/* ───────── FEATURED PRODUCTS ───────── */}
      <SectionWrapper className="py-16 md:py-24">
        <div className="mx-auto max-w-[1200px] px-6">
          <h2 className="text-center text-3xl font-bold tracking-tight text-text-primary md:text-5xl md:leading-tight">
            Products That Work While You Sleep
          </h2>

          <StaggerGrid className="mt-14 grid gap-8 md:grid-cols-3" direction="scale" staggerDelay={0.12}>
            <GlassCard3D>
              <h3 className="text-xl font-bold text-text-primary">SignalOS</h3>
              <p className="mt-3 text-text-secondary leading-relaxed">
                Automated crypto and forex signals with technical analysis, risk
                management levels, and real-time Telegram delivery.
              </p>
              <p className="mt-4 text-2xl font-extrabold text-accent">$97/mo</p>
              <a href="/services#ai-products" className="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-accent hover:text-accent-hover transition-colors">
                Get started <ArrowRight className="h-4 w-4" />
              </a>
            </GlassCard3D>

            <GlassCard3D>
              <h3 className="text-xl font-bold text-text-primary">ContentBrain</h3>
              <p className="mt-3 text-text-secondary leading-relaxed">
                AI content intelligence. Competitor analysis, trend scouting, hook
                generation, and full content calendars on autopilot.
              </p>
              <p className="mt-4 text-2xl font-extrabold text-accent">$47/mo</p>
              <a href="/services#ai-products" className="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-accent hover:text-accent-hover transition-colors">
                Get started <ArrowRight className="h-4 w-4" />
              </a>
            </GlassCard3D>

            <GlassCard3D>
              <h3 className="text-xl font-bold text-text-primary">Quivira OS Bundle</h3>
              <p className="mt-3 text-text-secondary leading-relaxed">
                SignalOS + ContentBrain + priority support. The full operating
                system for builders who want everything in one layer.
              </p>
              <p className="mt-4 text-2xl font-extrabold text-accent">$297/mo</p>
              <a href="/services#ai-products" className="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-accent hover:text-accent-hover transition-colors">
                Get the bundle <ArrowRight className="h-4 w-4" />
              </a>
            </GlassCard3D>
          </StaggerGrid>
        </div>
      </SectionWrapper>

      {/* ───────── RESULTS / SOCIAL PROOF ───────── */}
      <SectionWrapper className="py-16 md:py-24">
        <div className="mx-auto max-w-[1200px] px-6">
          <h2 className="text-center text-3xl font-bold tracking-tight text-text-primary md:text-5xl md:leading-tight">
            Proof. Not Promises.
          </h2>

          <div className="mt-14 grid grid-cols-2 gap-6 md:grid-cols-4">
            {resultStats.map((stat) => (
              <div key={stat.label} className="rounded-xl bg-bg-secondary p-6 text-center">
                <div className="text-4xl font-extrabold text-text-primary md:text-[56px] md:leading-none" style={{ textShadow: "0 0 20px rgba(230, 57, 70, 0.2)" }}>
                  <CountUp target={stat.value} suffix={stat.suffix || ""} />
                </div>
                <div className="mt-2 text-sm font-medium tracking-widest text-text-secondary uppercase">{stat.label}</div>
              </div>
            ))}
          </div>

          <h3 className="mt-16 mb-10 text-center text-2xl font-bold tracking-tight text-text-primary md:text-3xl">
            What People Say
          </h3>
          <div className="grid gap-8 md:grid-cols-3">
            {testimonials.map((t) => (
              <TestimonialCard key={t.attribution} quote={t.quote} attribution={t.attribution} images={t.allImages} rating={t.rating} avatar={t.avatar} />
            ))}
          </div>
        </div>
      </SectionWrapper>

      {/* ───────── CTA BANNER ───────── */}
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
