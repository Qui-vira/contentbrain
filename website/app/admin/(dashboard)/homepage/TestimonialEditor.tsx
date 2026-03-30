"use client";

import { EditableList } from "../EditableList";
import { AdminInput, AdminTextarea, ImageUpload } from "../components";

interface TestimonialData {
  id: number;
  page: string;
  quote: string;
  attribution: string;
  image: string | null;
  images: string | null;
  allImages: string[];
  sortOrder: number;
  rating: number;
  avatar: string | null;
  category: string;
}

function parseImages(t: TestimonialData): string[] {
  return t.allImages || [];
}

function MultiImageFields({ defaultImages }: { defaultImages: string[] }) {
  const [count, setCount] = useState(Math.max(defaultImages.length, 0));

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-xs font-medium text-[#888]">Images (up to 5)</label>
        {count < 5 && (
          <button
            type="button"
            onClick={() => setCount((c) => Math.min(c + 1, 5))}
            className="text-xs text-[#E63946] hover:text-[#FF4D5A] transition-colors cursor-pointer"
          >
            + Add Image
          </button>
        )}
      </div>
      {Array.from({ length: count }).map((_, i) => (
        <ImageUpload key={i} label={`Image ${i + 1}`} name={`image_${i}`} defaultValue={defaultImages[i] || ""} />
      ))}
    </div>
  );
}

import { useState } from "react";

export function TestimonialEditor({
  testimonials,
  page,
  upsertAction,
  deleteAction,
}: {
  testimonials: TestimonialData[];
  page: string;
  upsertAction: (prev: unknown, formData: FormData) => Promise<string>;
  deleteAction: (id: number) => Promise<void>;
}) {
  const fields = (t?: TestimonialData) => {
    const imgs = t ? parseImages(t) : [];
    return (
      <>
        <div className="grid gap-4 md:grid-cols-2">
          <AdminTextarea label="Quote" name="quote" required rows={3} defaultValue={t?.quote || ""} />
          <div className="space-y-4">
            <AdminInput label="Attribution" name="attribution" required placeholder="e.g. Krib Member, Crypto Trader" defaultValue={t?.attribution || ""} />
            <AdminInput label="Sort Order" name="sortOrder" type="number" defaultValue={t ? String(t.sortOrder) : "0"} />
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <AdminInput label="Rating (1-5)" name="rating" type="number" defaultValue={t ? String(t.rating) : "5"} />
          <ImageUpload label="Client Avatar" name="avatar" defaultValue={t?.avatar || ""} />
          <div>
            <label className="mb-1.5 block text-xs font-medium text-[#888]">Category</label>
            <select name="category" defaultValue={t?.category || "general"} className="w-full rounded-lg border border-[#333] bg-[#111] px-4 py-2.5 text-sm text-white">
              <option value="general">General</option>
              <option value="trading">Trading Signals</option>
              <option value="content">Content Strategy</option>
              <option value="consulting">Consulting</option>
            </select>
          </div>
        </div>
        <MultiImageFields defaultImages={imgs} />
      </>
    );
  };

  return (
    <EditableList
      items={testimonials}
      getId={(t) => t.id}
      renderSummary={(t: TestimonialData) => {
        const imgs = parseImages(t);
        return (
          <div className="flex gap-3">
            {t.avatar ? (
              <div className="h-10 w-10 shrink-0 overflow-hidden rounded-full border border-[#333]">
                <img src={t.avatar} alt="" className="h-full w-full object-cover" />
              </div>
            ) : imgs[0] ? (
              <div className="h-12 w-16 shrink-0 overflow-hidden rounded border border-[#333]">
                <img src={imgs[0]} alt="" className="h-full w-full object-cover" />
              </div>
            ) : null}
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <p className="text-sm italic text-[#ccc] line-clamp-2">&ldquo;{t.quote}&rdquo;</p>
              </div>
              <div className="mt-1 flex items-center gap-2">
                <span className="text-xs text-yellow-400">{"★".repeat(t.rating || 5)}{"☆".repeat(5 - (t.rating || 5))}</span>
                <p className="text-xs text-[#666]">&mdash; {t.attribution}</p>
              </div>
            </div>
          </div>
        );
      }}
      renderEditForm={(t: TestimonialData) => fields(t)}
      renderAddForm={() => fields()}
      upsertAction={upsertAction}
      deleteAction={deleteAction}
      hiddenFields={{ page }}
      addTitle="Add Testimonial"
    />
  );
}
