import { getServices, getMarqueeItems, getCtaBanner } from "@/lib/queries";
import { ServicesClient } from "@/components/ServicesClient";
import { resolveHref } from "@/lib/resolve-href";

export const revalidate = 60;

async function resolveServices(services: Awaited<ReturnType<typeof getServices>>) {
  return Promise.all(
    services.map(async (s) => ({
      ...s,
      ctaHref: s.ctaHref ? await resolveHref(s.ctaHref) : null,
    }))
  );
}

export default async function ServicesPage() {
  const [consulting, education, aiProducts, marqueeItems, cta] =
    await Promise.all([
      getServices("consulting"),
      getServices("education"),
      getServices("ai_products"),
      getMarqueeItems("services"),
      getCtaBanner("services"),
    ]);

  const [resolvedConsulting, resolvedEducation, resolvedAiProducts] = await Promise.all([
    resolveServices(consulting),
    resolveServices(education),
    resolveServices(aiProducts),
  ]);

  const resolvedCta = cta
    ? {
        ...cta,
        buttonHref: await resolveHref(cta.buttonHref),
      }
    : null;

  return (
    <ServicesClient
      consulting={resolvedConsulting}
      education={resolvedEducation}
      aiProducts={resolvedAiProducts}
      marqueeItems={marqueeItems}
      cta={resolvedCta}
    />
  );
}
