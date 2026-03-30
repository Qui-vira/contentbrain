"use client";

import { EditableList } from "../EditableList";
import { AdminInput } from "../components";

interface TierData {
  id: number;
  product: string;
  productTitle: string;
  productSubtitle: string;
  tierKey: string;
  tierLabel: string;
  tierPrice: string;
  sortOrder: number;
}

export function PricingTierEditor({
  tiers,
  product,
  upsertAction,
  deleteAction,
}: {
  tiers: TierData[];
  product: string;
  upsertAction: (prev: unknown, formData: FormData) => Promise<string>;
  deleteAction: (id: number) => Promise<void>;
}) {
  const fields = (t?: TierData) => (
    <div className="grid gap-4 md:grid-cols-3">
      <AdminInput label="Product Title" name="productTitle" required defaultValue={t?.productTitle || ""} />
      <AdminInput label="Product Subtitle" name="productSubtitle" required defaultValue={t?.productSubtitle || ""} />
      <AdminInput label="Tier Key" name="tierKey" required placeholder="starter, pro, premium" defaultValue={t?.tierKey || ""} />
      <AdminInput label="Tier Label" name="tierLabel" required defaultValue={t?.tierLabel || ""} />
      <AdminInput label="Tier Price" name="tierPrice" required defaultValue={t?.tierPrice || ""} />
      <AdminInput label="Sort Order" name="sortOrder" type="number" defaultValue={t ? String(t.sortOrder) : "0"} />
    </div>
  );

  return (
    <EditableList
      items={tiers}
      getId={(t) => t.id}
      renderSummary={(t: TierData) => (
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-white">{t.tierLabel}</span>
          <span className="text-sm text-[#E63946]">{t.tierPrice}</span>
        </div>
      )}
      renderEditForm={(t: TierData) => fields(t)}
      renderAddForm={() => fields()}
      upsertAction={upsertAction}
      deleteAction={deleteAction}
      hiddenFields={{ product }}
      addTitle="Add Tier"
    />
  );
}
