import { getCaseStudies, getTestimonials, getClientLogos, getStats } from "@/lib/queries";
import { upsertCaseStudy, deleteCaseStudy } from "../../actions/portfolio";
import { upsertTestimonial, deleteTestimonial, upsertStat, deleteStat } from "../../actions/homepage";
import { upsertClientLogo, deleteClientLogo } from "../../actions/logos";
import { AdminCard } from "../components";
import { CaseStudyEditor } from "./CaseStudyEditor";
import { ClientLogoEditor } from "./ClientLogoEditor";
import { TestimonialEditor } from "../homepage/TestimonialEditor";
import { StatEditor } from "../homepage/StatEditor";

export default async function PortfolioPage() {
  const [studies, portfolioTestimonials, logos, portfolioStats] = await Promise.all([
    getCaseStudies(),
    getTestimonials("portfolio"),
    getClientLogos(),
    getStats("portfolio"),
  ]);

  const serializedStudies = studies.map((cs) => ({ ...cs }));
  const serializedTestimonials = portfolioTestimonials.map((t) => ({ ...t }));
  const serializedLogos = logos.map((l) => ({ ...l }));
  const serializedStats = portfolioStats.map((s) => ({ ...s }));

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-white">Portfolio</h1>

      <AdminCard title="Case Studies">
        <CaseStudyEditor
          studies={serializedStudies}
          upsertAction={upsertCaseStudy}
          deleteAction={deleteCaseStudy}
        />
      </AdminCard>

      <AdminCard title="Portfolio Testimonials">
        <TestimonialEditor
          testimonials={serializedTestimonials}
          page="portfolio"
          upsertAction={upsertTestimonial}
          deleteAction={deleteTestimonial}
        />
      </AdminCard>

      <AdminCard title="Portfolio Stats">
        <StatEditor
          stats={serializedStats}
          page="portfolio"
          upsertAction={upsertStat}
          deleteAction={deleteStat}
        />
      </AdminCard>

      <AdminCard title="Client Logos">
        <ClientLogoEditor
          logos={serializedLogos}
          upsertAction={upsertClientLogo}
          deleteAction={deleteClientLogo}
        />
      </AdminCard>
    </div>
  );
}
