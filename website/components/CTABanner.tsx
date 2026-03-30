"use client";

import { MagneticButton } from "./MagneticButton";
import { ParallaxSection } from "./ParallaxSection";
import { TextReveal } from "./TextReveal";

interface CTABannerProps {
  headline: string;
  subtext: string;
  buttonText: string;
  buttonHref: string;
}

export function CTABanner({ headline, subtext, buttonText, buttonHref }: CTABannerProps) {
  return (
    <section className="py-16 md:py-24">
      <div className="mx-auto max-w-[1200px] px-6">
        <div className="rounded-2xl bg-bg-secondary p-12 text-center md:p-16">
          <ParallaxSection speed={0.1}>
            <div className="mx-auto mb-6 h-[3px] w-20 bg-accent" />
            <TextReveal as="h2" mode="words" className="text-3xl font-bold tracking-tight text-text-primary md:text-5xl md:leading-tight">
              {headline}
            </TextReveal>
            <p className="mx-auto mt-4 max-w-xl text-lg text-text-secondary whitespace-pre-line">
              {subtext}
            </p>
            <div className="mt-8">
              <MagneticButton href={buttonHref}>{buttonText}</MagneticButton>
            </div>
          </ParallaxSection>
        </div>
      </div>
    </section>
  );
}
