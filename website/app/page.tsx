import { getStats, getTestimonials, getMarqueeItems, getCtaBanner, getSetting } from "@/lib/queries";
import { HomeClient } from "@/components/HomeClient";
import { resolveHref } from "@/lib/resolve-href";

export const revalidate = 60;

export default async function Home() {
  const [trustStats, resultStats, testimonials, marqueeItems, cta, calendlyUrl, heroTagline, heroSubtitle] =
    await Promise.all([
      getStats("home_trust"),
      getStats("home_results"),
      getTestimonials("home"),
      getMarqueeItems("home"),
      getCtaBanner("home"),
      getSetting("calendly_url"),
      getSetting("hero_tagline"),
      getSetting("hero_subtitle"),
    ]);

  const resolvedCta = cta
    ? {
        ...cta,
        buttonHref: await resolveHref(cta.buttonHref),
      }
    : null;

  return (
    <HomeClient
      calendlyUrl={calendlyUrl}
      heroTagline={heroTagline}
      heroSubtitle={heroSubtitle}
      trustStats={trustStats}
      resultStats={resultStats}
      testimonials={testimonials}
      marqueeItems={marqueeItems}
      cta={resolvedCta}
    />
  );
}
