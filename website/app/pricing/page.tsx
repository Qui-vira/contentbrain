import { getPersonalServices, getPricingTiers, getPricingFeatures, getFaqItems, getMarqueeItems, getCtaBanner, getSettings } from "@/lib/queries";
import { PricingClient } from "@/components/PricingClient";
import { resolveHref } from "@/lib/resolve-href";

export const revalidate = 60;

export default async function PricingPage() {
  const productKeys = ["signalos", "contentbrain", "quivira_os", "quivira_protocol"];

  const [personalServices, faqItems, marqueeItems, cta, settings, ...tierAndFeatures] = await Promise.all([
    getPersonalServices(),
    getFaqItems(),
    getMarqueeItems("pricing"),
    getCtaBanner("pricing"),
    getSettings(),
    ...productKeys.flatMap((p) => [getPricingTiers(p), getPricingFeatures(p)]),
  ]);

  const products = productKeys.map((key, i) => {
    const tiers = tierAndFeatures[i * 2] as Awaited<ReturnType<typeof getPricingTiers>>;
    const features = tierAndFeatures[i * 2 + 1] as Awaited<ReturnType<typeof getPricingFeatures>>;
    return {
      productKey: key,
      productTitle: tiers[0]?.productTitle || "",
      productSubtitle: tiers[0]?.productSubtitle || "",
      tiers: tiers.map((t) => ({ tierKey: t.tierKey, tierLabel: t.tierLabel, tierPrice: t.tierPrice })),
      features: features.map((f) => ({ featureName: f.featureName, starter: f.starter, pro: f.pro, premium: f.premium })),
    };
  });

  return (
    <PricingClient
      personalServices={personalServices}
      products={products}
      faqItems={faqItems}
      marqueeItems={marqueeItems}
      settings={settings as Record<string, string>}
      cta={cta ? { ...cta, buttonHref: await resolveHref(cta.buttonHref) } : null}
    />
  );
}
