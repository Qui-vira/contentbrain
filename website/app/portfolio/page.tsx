import { getCaseStudies, getTestimonials, getCtaBanner, getStats, getClientLogos } from "@/lib/queries";
import { PortfolioClient } from "@/components/PortfolioClient";

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
      cta={cta}
    />
  );
}
