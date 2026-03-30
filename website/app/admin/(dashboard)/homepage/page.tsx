import { getStats, getTestimonials } from "@/lib/queries";
import { upsertStat, deleteStat, upsertTestimonial, deleteTestimonial } from "../../actions/homepage";
import { AdminCard } from "../components";
import { StatEditor } from "./StatEditor";
import { TestimonialEditor } from "./TestimonialEditor";

export default async function HomepagePage() {
  const [trustStats, resultStats, homeTestimonials] = await Promise.all([
    getStats("home_trust"),
    getStats("home_results"),
    getTestimonials("home"),
  ]);

  const serializedTrust = trustStats.map((s) => ({ ...s }));
  const serializedResults = resultStats.map((s) => ({ ...s }));
  const serializedTestimonials = homeTestimonials.map((t) => ({ ...t }));

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-white">Homepage</h1>

      <AdminCard title="Trust Bar Stats">
        <StatEditor
          stats={serializedTrust}
          page="home_trust"
          upsertAction={upsertStat}
          deleteAction={deleteStat}
        />
      </AdminCard>

      <AdminCard title="Results Section Stats">
        <StatEditor
          stats={serializedResults}
          page="home_results"
          upsertAction={upsertStat}
          deleteAction={deleteStat}
        />
      </AdminCard>

      <AdminCard title="Homepage Testimonials">
        <TestimonialEditor
          testimonials={serializedTestimonials}
          page="home"
          upsertAction={upsertTestimonial}
          deleteAction={deleteTestimonial}
        />
      </AdminCard>
    </div>
  );
}
