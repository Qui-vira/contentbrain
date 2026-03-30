"use client";

import { useState } from "react";
import { SectionWrapper } from "@/components/SectionWrapper";
import { FAQAccordion } from "@/components/FAQAccordion";
import { CTABanner } from "@/components/CTABanner";
import { GlassCard3D } from "@/components/GlassCard3D";
import { TextReveal } from "@/components/TextReveal";
import { StaggerGrid } from "@/components/StaggerGrid";
import { Marquee } from "@/components/Marquee";
import { PaymentModal } from "@/components/PaymentModal";
import { resolveHrefSync } from "@/lib/resolve-href";
import { Check, Minus, ExternalLink } from "lucide-react";

interface PersonalService {
  id: number;
  name: string;
  price: string;
  detail: string;
  ctaText: string | null;
  ctaHref: string | null;
  sortOrder: number;
}

interface PricingTier {
  tierKey: string;
  tierLabel: string;
  tierPrice: string;
}

interface PricingFeature {
  featureName: string;
  starter: string;
  pro: string;
  premium: string;
}

interface ProductData {
  productKey: string;
  productTitle: string;
  productSubtitle: string;
  tiers: PricingTier[];
  features: PricingFeature[];
}

interface FaqItem {
  question: string;
  answer: string;
}

interface PricingClientProps {
  personalServices: PersonalService[];
  products: ProductData[];
  faqItems: FaqItem[];
  marqueeItems: string[];
  settings: Record<string, string>;
  cta: { headline: string; subtext: string; buttonText: string; buttonHref: string } | null;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function FeatureValue({ value }: { value: string }) {
  if (value === "true") return <Check className="mx-auto h-5 w-5 text-accent" />;
  if (value === "false") return <Minus className="mx-auto h-5 w-5 text-text-muted" />;
  return <span className="text-sm text-text-primary">{value}</span>;
}

/** Extract the first numeric value from a price string like "$3,000" or "$97/mo" */
function parseNumericPrice(price: string): number | null {
  const digits = price.replace(/[$,]/g, "").match(/\d+(\.\d+)?/);
  return digits ? parseFloat(digits[0]) : null;
}

// ─── PaymentTriggerButton ─────────────────────────────────────────────────────

function PaymentTriggerButton({
  serviceName,
  amount,
  label,
  settings,
  className,
}: {
  serviceName: string;
  amount: number;
  label?: string;
  settings: Record<string, string>;
  className?: string;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const calPaidUrl = settings.cal_paid_url || "";

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className={
          className ||
          "rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-accent/90 cursor-pointer whitespace-nowrap"
        }
      >
        {label || "Pay Now"}
      </button>
      <PaymentModal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        serviceName={serviceName}
        amount={amount}
        calPaidUrl={calPaidUrl}
      />
    </>
  );
}

// ─── TierComparison ───────────────────────────────────────────────────────────

function TierComparison({
  product,
  settings,
}: {
  product: ProductData;
  settings: Record<string, string>;
}) {
  const isProtocol = product.productKey === "quivira_protocol";

  return (
    <div className="mt-10">
      <h3 className="text-2xl font-bold text-text-primary">
        {product.productTitle}
        <span className="ml-3 text-lg font-normal text-text-secondary">
          — {product.productSubtitle}
        </span>
      </h3>

      {/* Quivira Protocol positioning hook */}
      {isProtocol && (
        <p className="mt-3 max-w-2xl text-text-secondary">
          The all-in-one high-ticket mentorship for builders who want clarity, execution, and real
          results in Web3. Limited seats per cohort.
        </p>
      )}

      <StaggerGrid className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-3">
        {product.tiers.map((tier) => {
          const isProTier = tier.tierKey === "pro";
          const numericPrice = parseNumericPrice(tier.tierPrice);

          return (
            <GlassCard3D
              key={tier.tierKey}
              className={isProTier ? "border-accent" : ""}
            >
              {/* "Most Chosen" badge for Protocol Pro tier */}
              {isProtocol && isProTier && (
                <div className="mb-3 inline-block rounded-full bg-accent/10 px-3 py-1 text-xs font-bold uppercase tracking-widest text-accent">
                  Most Chosen
                </div>
              )}

              <div className="mb-1 text-sm font-medium uppercase tracking-widest text-text-secondary">
                {tier.tierLabel}
              </div>
              <div className="text-3xl font-extrabold text-text-primary">{tier.tierPrice}</div>

              <div className="mt-6 space-y-4">
                {product.features.map((f) => (
                  <div key={f.featureName} className="flex items-center justify-between text-sm">
                    <span className="text-text-secondary">{f.featureName}</span>
                    <FeatureValue value={f[tier.tierKey as "starter" | "pro" | "premium"]} />
                  </div>
                ))}
              </div>

              {/* Payment CTA */}
              <div className="mt-6">
                {numericPrice ? (
                  <PaymentTriggerButton
                    serviceName={`${product.productTitle} — ${tier.tierLabel}`}
                    amount={numericPrice}
                    label="Get Started"
                    settings={settings}
                    className="w-full rounded-lg bg-accent px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-accent/90 cursor-pointer"
                  />
                ) : (
                  <a
                    href="/contact"
                    className="block w-full rounded-lg border border-border px-4 py-2.5 text-center text-sm font-semibold text-text-secondary transition-colors hover:border-accent hover:text-accent"
                  >
                    Contact Us
                  </a>
                )}
              </div>
            </GlassCard3D>
          );
        })}
      </StaggerGrid>
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

export function PricingClient({
  personalServices,
  products,
  faqItems,
  marqueeItems,
  settings,
  cta,
}: PricingClientProps) {
  return (
    <main className="min-h-screen bg-bg-primary">
      {/* Hero */}
      <SectionWrapper className="pt-32 pb-16 md:pt-40">
        <div className="mx-auto max-w-[1200px] px-6 text-center">
          <TextReveal
            as="h1"
            mode="words"
            className="text-4xl font-bold tracking-tight text-text-primary md:text-6xl md:leading-tight"
          >
            Simple pricing. Real value.
          </TextReveal>
          <p className="mx-auto mt-4 max-w-xl text-lg text-text-secondary">
            No hidden fees. No lock-in contracts. Start with what fits. Upgrade when ready.
          </p>
        </div>
      </SectionWrapper>

      {/* Consulting & Education table */}
      <SectionWrapper className="py-16 md:py-24">
        <div className="mx-auto max-w-[1200px] px-6">
          <TextReveal
            as="h2"
            mode="words"
            className="text-3xl font-bold tracking-tight text-text-primary md:text-4xl"
          >
            Consulting &amp; Education
          </TextReveal>
          <div className="mt-8 overflow-x-auto rounded-xl border border-border">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-border bg-bg-tertiary">
                  <th className="px-6 py-4 text-sm font-semibold uppercase tracking-widest text-text-secondary">
                    Service
                  </th>
                  <th className="px-6 py-4 text-sm font-semibold uppercase tracking-widest text-text-secondary">
                    Price
                  </th>
                  <th className="px-6 py-4 text-sm font-semibold uppercase tracking-widest text-text-secondary">
                    Details
                  </th>
                  <th className="px-6 py-4 text-sm font-semibold uppercase tracking-widest text-text-secondary">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody>
                {personalServices.map((s, i) => {
                  const rowClass = `border-b border-border bg-bg-secondary ${i % 2 === 1 ? "bg-bg-tertiary/50" : ""}`;
                  const isContactPrice = s.price.toLowerCase().includes("contact");

                  // Resolve the action cell
                  let actionCell: React.ReactNode;
                  if (s.ctaHref) {
                    const href = resolveHrefSync(s.ctaHref, settings);
                    actionCell = (
                      <a
                        href={href}
                        target={href.startsWith("http") ? "_blank" : undefined}
                        rel={href.startsWith("http") ? "noopener noreferrer" : undefined}
                        className="inline-flex items-center gap-1 rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-accent/90 whitespace-nowrap"
                      >
                        {s.ctaText || "Book Now"}
                        {href.startsWith("http") && <ExternalLink className="h-3 w-3" />}
                      </a>
                    );
                  } else if (isContactPrice) {
                    actionCell = (
                      <a
                        href="/contact"
                        className="inline-block rounded-lg border border-border px-4 py-2 text-sm font-semibold text-text-secondary transition-colors hover:border-accent hover:text-accent whitespace-nowrap"
                      >
                        Get in Touch
                      </a>
                    );
                  } else {
                    const amount = parseNumericPrice(s.price) ?? 0;
                    actionCell = (
                      <PaymentTriggerButton
                        serviceName={s.name}
                        amount={amount}
                        label={s.ctaText || "Pay Now"}
                        settings={settings}
                      />
                    );
                  }

                  return (
                    <tr key={s.id} className={rowClass}>
                      <td className="px-6 py-4 font-medium text-text-primary">{s.name}</td>
                      <td className="px-6 py-4 font-semibold text-accent">{s.price}</td>
                      <td className="px-6 py-4 text-text-secondary whitespace-pre-line">{s.detail}</td>
                      <td className="px-6 py-4">{actionCell}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </SectionWrapper>

      {/* Product Tiers */}
      <SectionWrapper className="py-16 md:py-24">
        <div className="mx-auto max-w-[1200px] px-6">
          <TextReveal
            as="h2"
            mode="words"
            className="text-3xl font-bold tracking-tight text-text-primary md:text-4xl"
          >
            Quivira OS Products
          </TextReveal>
          {products.map((product) => (
            <TierComparison key={product.productKey} product={product} settings={settings} />
          ))}
        </div>
      </SectionWrapper>

      {/* Marquee */}
      <Marquee
        items={marqueeItems}
        className="py-8 text-lg font-bold tracking-widest text-text-secondary/50"
      />

      {/* FAQ */}
      <SectionWrapper className="py-16 md:py-24">
        <div className="mx-auto max-w-[800px] px-6">
          <TextReveal
            as="h2"
            mode="words"
            className="mb-8 text-3xl font-bold tracking-tight text-text-primary md:text-4xl"
          >
            Common Questions
          </TextReveal>
          <FAQAccordion items={faqItems} />
        </div>
      </SectionWrapper>

      {/* CTA */}
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
