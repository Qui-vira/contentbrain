import { getAllServices } from "@/lib/queries";
import { upsertService, deleteService } from "../../actions/services";
import { AdminCard } from "../components";
import { ServiceEditor } from "./ServiceEditor";

const categories = [
  { value: "consulting", label: "Consulting" },
  { value: "education", label: "Education" },
  { value: "ai_products", label: "AI Products" },
];

export default async function ServicesPage() {
  const services = await getAllServices();

  const grouped = {
    consulting: services.filter((s) => s.category === "consulting").map((s) => ({ ...s })),
    education: services.filter((s) => s.category === "education").map((s) => ({ ...s })),
    ai_products: services.filter((s) => s.category === "ai_products").map((s) => ({ ...s })),
  };

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-white">Services</h1>

      {categories.map((cat) => (
        <AdminCard key={cat.value} title={cat.label}>
          <ServiceEditor
            services={grouped[cat.value as keyof typeof grouped]}
            category={cat.value}
            upsertAction={upsertService}
            deleteAction={deleteService}
          />
        </AdminCard>
      ))}
    </div>
  );
}
