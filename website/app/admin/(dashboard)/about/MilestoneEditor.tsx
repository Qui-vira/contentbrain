"use client";

import { useState } from "react";
import { AdminInput, AdminTextarea, FormWithStatus, DeleteButton, ImageUpload } from "../components";

interface MilestoneData {
  id: number;
  year: string;
  title: string;
  text: string;
  image: string | null;
  images: string | null;
  imageLayout: string | null;
  sortOrder: number;
}

function parseImages(m: MilestoneData): string[] {
  try {
    if (m.images) return JSON.parse(m.images);
  } catch {}
  return m.image ? [m.image] : [];
}

export function MilestoneEditor({
  milestones,
  upsertAction,
  deleteAction,
}: {
  milestones: MilestoneData[];
  upsertAction: (prev: unknown, formData: FormData) => Promise<string>;
  deleteAction: (id: number) => Promise<void>;
}) {
  const [editingId, setEditingId] = useState<number | null>(null);

  return (
    <div>
      <p className="mb-4 text-xs text-[#666]">
        Click &quot;Edit&quot; to modify a milestone. Each milestone can have up to 5 images displayed as a carousel or grid.
      </p>

      <div className="space-y-3">
        {milestones.map((m) => {
          const imgs = parseImages(m);
          const isEditing = editingId === m.id;

          return (
            <div key={m.id} className="rounded-lg bg-[#1a1a1a] p-4">
              {/* Summary row */}
              <div className="flex items-start justify-between">
                <div className="flex gap-4">
                  {imgs[0] && (
                    <div className="h-16 w-24 shrink-0 overflow-hidden rounded-lg border border-[#333]">
                      <img src={imgs[0]} alt={m.title} className="h-full w-full object-cover" />
                    </div>
                  )}
                  <div>
                    <span className="inline-block rounded bg-[#E63946]/20 px-2 py-0.5 text-xs font-bold text-[#E63946]">{m.year}</span>
                    <span className="ml-2 text-sm font-medium text-white">{m.title}</span>
                    <p className="mt-1 text-xs text-[#666] line-clamp-2">{m.text}</p>
                    {imgs.length > 1 && (
                      <p className="mt-1 text-[10px] text-[#555]">{imgs.length} images ({m.imageLayout || "carousel"})</p>
                    )}
                  </div>
                </div>
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setEditingId(isEditing ? null : m.id)}
                    className="text-xs text-blue-400 hover:text-blue-300 transition-colors cursor-pointer"
                  >
                    {isEditing ? "Close" : "Edit"}
                  </button>
                  <DeleteButton action={async () => { await deleteAction(m.id); }} />
                </div>
              </div>

              {/* Edit form */}
              {isEditing && (
                <div className="mt-4 border-t border-[#333] pt-4">
                  <FormWithStatus action={upsertAction} buttonText="Save Changes">
                    <input type="hidden" name="id" value={m.id} />
                    <div className="grid gap-4 md:grid-cols-3">
                      <AdminInput label="Year" name="year" required defaultValue={m.year} placeholder="e.g. 2019, Now" />
                      <AdminInput label="Title" name="title" required defaultValue={m.title} />
                      <AdminInput label="Sort Order" name="sortOrder" type="number" defaultValue={String(m.sortOrder)} />
                    </div>
                    <AdminTextarea label="Text (use blank lines for paragraphs)" name="text" required rows={6} defaultValue={m.text} />
                    <div>
                      <label className="mb-1 block text-xs font-medium text-[#888]">Image Layout</label>
                      <select
                        name="imageLayout"
                        defaultValue={m.imageLayout || "carousel"}
                        className="w-full rounded-lg border border-[#333] bg-[#1a1a1a] px-3 py-2 text-sm text-white focus:border-[#E63946] focus:outline-none"
                      >
                        <option value="carousel">Carousel (swipeable)</option>
                        <option value="grid">Grid (2-column)</option>
                      </select>
                    </div>
                    <MultiImageFields defaultImages={imgs} />
                  </FormWithStatus>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Add new milestone */}
      <div className="mt-6 border-t border-[#222] pt-6">
        <h4 className="mb-3 text-sm font-semibold text-[#aaa]">Add New Milestone</h4>
        <FormWithStatus action={upsertAction} buttonText="Add Milestone">
          <input type="hidden" name="id" value="" />
          <div className="grid gap-4 md:grid-cols-3">
            <AdminInput label="Year" name="year" required placeholder="e.g. 2019, Now" />
            <AdminInput label="Title" name="title" required placeholder="e.g. The Beginning" />
            <AdminInput label="Sort Order" name="sortOrder" type="number" defaultValue="0" />
          </div>
          <AdminTextarea label="Text (use blank lines for paragraphs)" name="text" required rows={4} />
          <div>
            <label className="mb-1 block text-xs font-medium text-[#888]">Image Layout</label>
            <select
              name="imageLayout"
              defaultValue="carousel"
              className="w-full rounded-lg border border-[#333] bg-[#1a1a1a] px-3 py-2 text-sm text-white focus:border-[#E63946] focus:outline-none"
            >
              <option value="carousel">Carousel (swipeable)</option>
              <option value="grid">Grid (2-column)</option>
            </select>
          </div>
          <MultiImageFields defaultImages={[]} />
        </FormWithStatus>
      </div>
    </div>
  );
}

function MultiImageFields({ defaultImages }: { defaultImages: string[] }) {
  const [count, setCount] = useState(Math.max(defaultImages.length, 1));

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
            + Add Image Slot
          </button>
        )}
      </div>
      {Array.from({ length: count }).map((_, i) => (
        <ImageUpload
          key={i}
          label={`Image ${i + 1}`}
          name={`image_${i}`}
          defaultValue={defaultImages[i] || ""}
        />
      ))}
    </div>
  );
}
