"use client";

import { EditableList } from "../EditableList";
import { AdminInput } from "../components";

interface FeatureData {
  id: number;
  product: string;
  featureName: string;
  starter: string;
  pro: string;
  premium: string;
  sortOrder: number;
}

export function PricingFeatureEditor({
  features,
  product,
  upsertAction,
  deleteAction,
}: {
  features: FeatureData[];
  product: string;
  upsertAction: (prev: unknown, formData: FormData) => Promise<string>;
  deleteAction: (id: number) => Promise<void>;
}) {
  const fields = (f?: FeatureData) => (
    <div className="grid gap-4 md:grid-cols-3">
      <AdminInput label="Feature Name" name="featureName" required defaultValue={f?.featureName || ""} />
      <AdminInput label="Starter Value" name="starter" required placeholder="true, false, or text" defaultValue={f?.starter || ""} />
      <AdminInput label="Pro Value" name="pro" required defaultValue={f?.pro || ""} />
      <AdminInput label="Premium Value" name="premium" required defaultValue={f?.premium || ""} />
      <AdminInput label="Sort Order" name="sortOrder" type="number" defaultValue={f ? String(f.sortOrder) : "0"} />
    </div>
  );

  return (
    <EditableList
      items={features}
      getId={(f) => f.id}
      renderSummary={(f: FeatureData) => (
        <div className="flex items-center gap-2 text-xs">
          <span className="w-1/4 text-sm text-[#ccc]">{f.featureName}</span>
          <span className="text-[#888]">S: {f.starter}</span>
          <span className="text-[#888]">P: {f.pro}</span>
          <span className="text-[#888]">Pr: {f.premium}</span>
        </div>
      )}
      renderEditForm={(f: FeatureData) => fields(f)}
      renderAddForm={() => fields()}
      upsertAction={upsertAction}
      deleteAction={deleteAction}
      hiddenFields={{ product }}
      addTitle="Add Feature"
    />
  );
}
