import { db } from "@/lib/db";
import { asc } from "drizzle-orm";
import * as s from "@/lib/schema";
import { getPersonalServices, getFaqItems } from "@/lib/queries";
import {
  upsertPricingTier,
  deletePricingTier,
  upsertPricingFeature,
  deletePricingFeature,
  upsertFaqItem,
  deleteFaqItem,
  upsertPersonalService,
  deletePersonalService,
} from "../../actions/pricing";
import { AdminCard } from "../components";
import { PersonalServiceEditor } from "./PersonalServiceEditor";
import { PricingTierEditor } from "./PricingTierEditor";
import { PricingFeatureEditor } from "./PricingFeatureEditor";
import { FaqEditor } from "./FaqEditor";

export default async function PricingPage() {
  const [personalSvcs, tiers, features, faq] = await Promise.all([
    getPersonalServices(),
    db.select().from(s.pricingTiers).orderBy(asc(s.pricingTiers.product), asc(s.pricingTiers.sortOrder)),
    db.select().from(s.pricingFeatures).orderBy(asc(s.pricingFeatures.product), asc(s.pricingFeatures.sortOrder)),
    getFaqItems(),
  ]);

  const products = ["signalos", "contentbrain", "quivira_os", "quivira_protocol"];

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-white">Pricing</h1>

      <AdminCard title="Consulting & Education Table">
        <PersonalServiceEditor
          services={personalSvcs.map((ps) => ({ ...ps }))}
          upsertAction={upsertPersonalService}
          deleteAction={deletePersonalService}
        />
      </AdminCard>

      {products.map((product) => {
        const productTiers = tiers.filter((t) => t.product === product).map((t) => ({ ...t }));
        const productFeatures = features.filter((f) => f.product === product).map((f) => ({ ...f }));
        const title = productTiers[0]?.productTitle || product;

        return (
          <div key={product} className="space-y-4">
            <AdminCard title={`${title} — Tiers`}>
              <PricingTierEditor
                tiers={productTiers}
                product={product}
                upsertAction={upsertPricingTier}
                deleteAction={deletePricingTier}
              />
            </AdminCard>

            <AdminCard title={`${title} — Features`}>
              <PricingFeatureEditor
                features={productFeatures}
                product={product}
                upsertAction={upsertPricingFeature}
                deleteAction={deletePricingFeature}
              />
            </AdminCard>
          </div>
        );
      })}

      <AdminCard title="FAQ Items">
        <FaqEditor
          items={faq.map((f) => ({ ...f }))}
          upsertAction={upsertFaqItem}
          deleteAction={deleteFaqItem}
        />
      </AdminCard>
    </div>
  );
}
