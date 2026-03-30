import { getCaseStudies, getTestimonials, getCtaBanner, getStats, getClientLogos } from "@/lib/queries";
import { PortfolioClient } from "@/components/PortfolioClient";
import { resolveHref } from "@/lib/resolve-href";

export const revalidate = 60;

export default async function PortfolioPage() {
  const [caseStudies, testimonials, cta, portfolioStats, clientLogos] = await Promise.all([
    getCaseStudies(),
    getTestimonials("portfolio"),
    getCtaBanner("portfolio"),
    getStats("portfolio"),
    getClientLogos(),
  ]);

  return (
    <PortfolioClient
      caseStudies={caseStudies}
      testimonials={testimonials}
      portfolioStats={portfolioStats}
      clientLogos={clientLogos}
      cta={cta ? { ...cta, buttonHref: await resolveHref(cta.buttonHref) } : null}
    />
  );
}
