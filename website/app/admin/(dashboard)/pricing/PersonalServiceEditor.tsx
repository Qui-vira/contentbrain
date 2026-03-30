"use client";

import { EditableList } from "../EditableList";
import { AdminInput } from "../components";

interface PersonalServiceData {
  id: number;
  name: string;
  price: string;
  detail: string;
  ctaText: string | null;
  ctaHref: string | null;
  sortOrder: number;
}

export function PersonalServiceEditor({
  services,
  upsertAction,
  deleteAction,
}: {
  services: PersonalServiceData[];
  upsertAction: (prev: unknown, formData: FormData) => Promise<string>;
  deleteAction: (id: number) => Promise<void>;
}) {
  const fields = (ps?: PersonalServiceData) => (
    <div className="grid gap-4 md:grid-cols-2">
      <AdminInput label="Name" name="name" required defaultValue={ps?.name || ""} />
      <AdminInput label="Price" name="price" required defaultValue={ps?.price || ""} />
      <AdminInput label="Detail" name="detail" required defaultValue={ps?.detail || ""} />
      <AdminInput label="Sort Order" name="sortOrder" type="number" defaultValue={ps ? String(ps.sortOrder) : "0"} />
      <AdminInput
        label="CTA Text (optional)"
        name="ctaText"
        placeholder="e.g. Pay Now, Book Session"
        defaultValue={ps?.ctaText || ""}
      />
      <AdminInput
        label="CTA Link (optional — blank = payment modal)"
        name="ctaHref"
        placeholder="calendly_free, calendly, /contact, or full URL"
        defaultValue={ps?.ctaHref || ""}
      />
    </div>
  );

  return (
    <EditableList
      items={services}
      getId={(ps) => ps.id}
      renderSummary={(ps: PersonalServiceData) => (
        <div className="flex items-center gap-3">
          <span className="text-sm text-white">{ps.name}</span>
          <span className="text-sm text-[#E63946]">{ps.price}</span>
          <span className="text-xs text-[#666]">{ps.detail}</span>
          {ps.ctaText && (
            <span className="rounded-full bg-[#1a1a1a] px-2 py-0.5 text-xs text-[#888]">
              CTA: {ps.ctaText}
            </span>
          )}
        </div>
      )}
      renderEditForm={(ps: PersonalServiceData) => fields(ps)}
      renderAddForm={() => fields()}
      upsertAction={upsertAction}
      deleteAction={deleteAction}
      addTitle="Add Service"
    />
  );
}
