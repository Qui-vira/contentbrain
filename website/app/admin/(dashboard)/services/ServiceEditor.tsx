"use client";

import { useState } from "react";
import { EditableList } from "../EditableList";
import { AdminInput, AdminTextarea } from "../components";
import { CTA_OPTIONS } from "@/lib/resolve-href";

interface ServiceData {
  id: number;
  category: string;
  title: string;
  description: string;
  price: string | null;
  priceDetail: string | null;
  icon: string | null;
  ctaText: string | null;
  ctaHref: string | null;
  sortOrder: number;
}

function CtaHrefField({ defaultValue }: { defaultValue: string }) {
  const isPreset = CTA_OPTIONS.some((o) => o.value === defaultValue && o.value !== "__custom");
  const [mode, setMode] = useState<string>(
    !defaultValue ? "" : isPreset ? defaultValue : "__custom"
  );
  const [customUrl, setCustomUrl] = useState(isPreset ? "" : defaultValue);

  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs font-medium text-[#999]">CTA Href</label>
      <select
        className="rounded-lg border border-[#333] bg-[#111] px-3 py-2 text-sm text-white focus:border-[#E63946] focus:outline-none"
        value={mode}
        onChange={(e) => setMode(e.target.value)}
      >
        {CTA_OPTIONS.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
      {mode === "__custom" && (
        <input
          className="mt-1 rounded-lg border border-[#333] bg-[#111] px-3 py-2 text-sm text-white placeholder-[#555] focus:border-[#E63946] focus:outline-none"
          placeholder="https://... or /path"
          value={customUrl}
          onChange={(e) => setCustomUrl(e.target.value)}
        />
      )}
      {/* Hidden input sends the actual value to the form */}
      <input type="hidden" name="ctaHref" value={mode === "__custom" ? customUrl : mode} />
    </div>
  );
}

export function ServiceEditor({
  services,
  category,
  upsertAction,
  deleteAction,
}: {
  services: ServiceData[];
  category: string;
  upsertAction: (prev: unknown, formData: FormData) => Promise<string>;
  deleteAction: (id: number) => Promise<void>;
}) {
  const fields = (s?: ServiceData) => (
    <>
      <div className="grid gap-4 md:grid-cols-2">
        <AdminInput label="Title" name="title" required defaultValue={s?.title || ""} />
        <AdminInput label="Icon (Lucide name)" name="icon" placeholder="e.g. Eye, Users, Zap" defaultValue={s?.icon || ""} />
        <AdminInput label="Price" name="price" placeholder="e.g. $97/mo" defaultValue={s?.price || ""} />
        <AdminInput label="Price Detail" name="priceDetail" placeholder="e.g. per cohort" defaultValue={s?.priceDetail || ""} />
        <AdminInput label="CTA Text" name="ctaText" placeholder="e.g. Get SignalOS" defaultValue={s?.ctaText || ""} />
        <CtaHrefField defaultValue={s?.ctaHref || ""} />
        <AdminInput label="Sort Order" name="sortOrder" type="number" defaultValue={s ? String(s.sortOrder) : "0"} />
      </div>
      <AdminTextarea label="Description" name="description" required rows={3} defaultValue={s?.description || ""} />
    </>
  );

  return (
    <EditableList
      items={services}
      getId={(s) => s.id}
      renderSummary={(s: ServiceData) => (
        <div>
          <span className="text-sm font-medium text-white">{s.title}</span>
          {s.price && <span className="ml-2 text-sm text-[#E63946]">{s.price}</span>}
          <p className="mt-1 text-xs text-[#666] line-clamp-2">{s.description}</p>
        </div>
      )}
      renderEditForm={(s: ServiceData) => fields(s)}
      renderAddForm={() => fields()}
      upsertAction={upsertAction}
      deleteAction={deleteAction}
      hiddenFields={{ category }}
      addTitle="Add Service"
    />
  );
}
