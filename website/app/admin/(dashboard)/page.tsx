import { db } from "@/lib/db";
import { count } from "drizzle-orm";
import * as s from "@/lib/schema";

async function getCount(table: Parameters<typeof count>[0] extends undefined ? never : any) {
  const [row] = await db.select({ count: count() }).from(table);
  return row.count;
}

export default async function AdminDashboard() {
  const [
    servicesCount,
    testimonialsCount,
    faqCount,
    caseStudiesCount,
    socialLinksCount,
    statsCount,
  ] = await Promise.all([
    getCount(s.services),
    getCount(s.testimonials),
    getCount(s.faqItems),
    getCount(s.caseStudies),
    getCount(s.socialLinks),
    getCount(s.stats),
  ]);

  const cards = [
    { label: "Services", count: servicesCount, href: "/admin/services" },
    { label: "Testimonials", count: testimonialsCount, href: "/admin/portfolio" },
    { label: "FAQ Items", count: faqCount, href: "/admin/pricing" },
    { label: "Case Studies", count: caseStudiesCount, href: "/admin/portfolio" },
    { label: "Social Links", count: socialLinksCount, href: "/admin/settings" },
    { label: "Stats", count: statsCount, href: "/admin/homepage" },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-white">Dashboard</h1>
      <p className="mt-1 text-sm text-[#888]">
        Overview of all content on bigquivdigitals.com
      </p>

      <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-3">
        {cards.map((card) => (
          <a
            key={card.label}
            href={card.href}
            className="rounded-xl border border-[#222] bg-[#111] p-6 transition-colors hover:border-[#333]"
          >
            <div className="text-3xl font-bold text-white">{card.count}</div>
            <div className="mt-1 text-sm text-[#888]">{card.label}</div>
          </a>
        ))}
      </div>
    </div>
  );
}
