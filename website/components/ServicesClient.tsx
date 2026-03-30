"use client";

import { GlassCard3D } from "@/components/GlassCard3D";
import { MagneticButton } from "@/components/MagneticButton";
import { TextReveal } from "@/components/TextReveal";
import { StaggerGrid } from "@/components/StaggerGrid";
import { Marquee } from "@/components/Marquee";
import { ParallaxSection } from "@/components/ParallaxSection";
import { CTABanner } from "@/components/CTABanner";
import { SectionWrapper } from "@/components/SectionWrapper";
import { getIcon } from "@/lib/icons";

interface Service {
  id: number;
  title: string;
  description: string;
  icon: string | null;
  price: string | null;
  priceDetail: string | null;
  ctaText: string | null;
  ctaHref: string | null;
}

interface ServicesClientProps {
  consulting: Service[];
  education: Service[];
  aiProducts: Service[];
  marqueeItems: string[];
  cta: { headline: string; subtext: string; buttonText: string; buttonHref: string } | null;
}

function ServiceCard({ service }: { service: Service }) {
  const Icon = getIcon(service.icon || "Zap");
  const href = service.ctaHref;

  return (
    <GlassCard3D>
      <Icon className="mb-4 h-8 w-8 text-accent" />
      <h3 className="text-xl font-bold text-text-primary">{service.title}</h3>
      <p className="mt-3 text-text-secondary leading-relaxed whitespace-pre-line">{service.description}</p>
      {service.price && (
        <p className="mt-4 text-2xl font-extrabold text-accent">
          {service.price}
          {service.priceDetail && (
            <span className="text-base font-medium text-text-muted"> | {service.priceDetail}</span>
          )}
        </p>
      )}
      {service.ctaText && href && (
        <div className="mt-5">
          <MagneticButton href={href}>{service.ctaText}</MagneticButton>
        </div>
      )}
    </GlassCard3D>
  );
}

export function ServicesClient({
  consulting,
  education,
  aiProducts,
  marqueeItems,
  cta,
}: ServicesClientProps) {
  return (
    <main>
      {/* ───────── HERO ───────── */}
      <section className="pt-16 py-32 md:py-40">
        <div className="mx-auto max-w-[1200px] px-6 text-center">
          <TextReveal as="h1" mode="words" className="text-5xl font-extrabold leading-[1.08] tracking-tight text-text-primary md:text-7xl">
            Services
          </TextReveal>
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-text-secondary">
            Consulting, education, and AI products built for builders in Web3, trading, and content.
          </p>
        </div>
      </section>

      {/* ───────── CONSULTING ───────── */}
      <SectionWrapper className="py-16 md:py-24">
        <div className="mx-auto max-w-[1200px] px-6">
          <TextReveal as="h2" mode="words" className="text-center text-3xl font-bold tracking-tight text-text-primary md:text-5xl md:leading-tight">
            Done-With-You Services
          </TextReveal>
          <StaggerGrid className="mt-14 grid gap-8 md:grid-cols-3" direction="up" staggerDelay={0.15}>
            {consulting.map((s) => (
              <ServiceCard key={s.id} service={s} />
            ))}
          </StaggerGrid>
        </div>
      </SectionWrapper>

      {/* ───────── MARQUEE BAND ───────── */}
      <Marquee
        items={marqueeItems}
        speed={25}
        className="py-8 text-2xl font-bold tracking-widest text-text-muted/30 md:text-4xl"
      />

      {/* ───────── EDUCATION ───────── */}
      <SectionWrapper id="education" className="py-16 md:py-24">
        <div className="mx-auto max-w-[1200px] px-6">
          <TextReveal as="h2" mode="words" className="text-center text-3xl font-bold tracking-tight text-text-primary md:text-5xl md:leading-tight">
            Learn. Build. Earn.
          </TextReveal>
          <StaggerGrid className="mt-14 grid gap-8 md:grid-cols-3" direction="left" staggerDelay={0.12}>
            {education.map((s) => (
              <ServiceCard key={s.id} service={s} />
            ))}
          </StaggerGrid>
        </div>
      </SectionWrapper>

      {/* ───────── AI PRODUCTS ───────── */}
      <ParallaxSection speed={0.15}>
        <SectionWrapper id="ai-products" className="py-16 md:py-24">
          <div className="mx-auto max-w-[1200px] px-6">
            <TextReveal as="h2" mode="words" className="text-center text-3xl font-bold tracking-tight text-text-primary md:text-5xl md:leading-tight">
              The Builder&apos;s Operating System
            </TextReveal>
            <p className="mx-auto mt-4 max-w-xl text-center text-lg text-text-secondary">
              Three systems. One operating layer. Fully automated.
            </p>
            <StaggerGrid className="mt-14 grid gap-8 md:grid-cols-3" direction="scale" staggerDelay={0.12}>
              {aiProducts.map((s) => {
                const Icon = getIcon(s.icon || "Zap");
                const href = s.ctaHref;
                return (
                  <GlassCard3D key={s.id} className="md:p-10">
                    <Icon className="mb-4 h-10 w-10 text-accent" />
                    <h3 className="text-2xl font-bold text-text-primary">{s.title}</h3>
                    <p className="mt-3 text-text-secondary leading-relaxed whitespace-pre-line">{s.description}</p>
                    {s.price && <p className="mt-6 text-3xl font-extrabold text-accent">{s.price}</p>}
                    {s.ctaText && href && (
                      <div className="mt-6">
                        <MagneticButton href={href}>{s.ctaText}</MagneticButton>
                      </div>
                    )}
                  </GlassCard3D>
                );
              })}
            </StaggerGrid>
          </div>
        </SectionWrapper>
      </ParallaxSection>

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
