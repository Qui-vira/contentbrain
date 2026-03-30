"use client";

import { useState } from "react";
import { EditableList } from "../EditableList";
import { AdminInput, AdminTextarea, ImageUpload, MediaUpload } from "../components";

interface CaseStudyData {
  id: number;
  title: string;
  stats: string[];
  allImages: string[];
  allVideos: string[];
  sortOrder: number;
}

function MediaFields({ defaultImages, defaultVideos }: { defaultImages: string[]; defaultVideos: string[] }) {
  const [imgCount, setImgCount] = useState(Math.max(defaultImages.length, 0));
  const [vidCount, setVidCount] = useState(Math.max(defaultVideos.length, 0));

  return (
    <div className="space-y-4">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs font-medium text-[#888]">Images (up to 5)</label>
          {imgCount < 5 && (
            <button type="button" onClick={() => setImgCount((c) => c + 1)} className="text-xs text-[#E63946] hover:text-[#FF4D5A] transition-colors cursor-pointer">
              + Add Image
            </button>
          )}
        </div>
        {Array.from({ length: imgCount }).map((_, i) => (
          <ImageUpload key={i} label={`Image ${i + 1}`} name={`image_${i}`} defaultValue={defaultImages[i] || ""} />
        ))}
      </div>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs font-medium text-[#888]">Videos (up to 5)</label>
          {vidCount < 5 && (
            <button type="button" onClick={() => setVidCount((c) => c + 1)} className="text-xs text-[#E63946] hover:text-[#FF4D5A] transition-colors cursor-pointer">
              + Add Video
            </button>
          )}
        </div>
        {Array.from({ length: vidCount }).map((_, i) => (
          <MediaUpload key={i} label={`Video ${i + 1}`} name={`video_${i}`} defaultValue={defaultVideos[i] || ""} accept="video/*" />
        ))}
      </div>
    </div>
  );
}

export function CaseStudyEditor({
  studies,
  upsertAction,
  deleteAction,
}: {
  studies: CaseStudyData[];
  upsertAction: (prev: unknown, formData: FormData) => Promise<string>;
  deleteAction: (id: number) => Promise<void>;
}) {
  const fields = (cs?: CaseStudyData) => (
    <>
      <div className="grid gap-4 md:grid-cols-2">
        <AdminInput label="Title" name="title" required defaultValue={cs?.title || ""} />
        <AdminInput label="Sort Order" name="sortOrder" type="number" defaultValue={cs ? String(cs.sortOrder) : "0"} />
      </div>
      <AdminTextarea label="Stats (one per line)" name="stats" required rows={5} defaultValue={cs?.stats.join("\n") || ""} />
      <MediaFields defaultImages={cs?.allImages || []} defaultVideos={cs?.allVideos || []} />
    </>
  );

  return (
    <EditableList
      items={studies}
      getId={(cs) => cs.id}
      renderSummary={(cs: CaseStudyData) => (
        <div className="flex gap-3">
          {cs.allImages[0] && (
            <div className="h-12 w-16 shrink-0 overflow-hidden rounded border border-[#333]">
              <img src={cs.allImages[0]} alt="" className="h-full w-full object-cover" />
            </div>
          )}
          <div>
            <p className="text-sm font-medium text-white">{cs.title}</p>
            <p className="mt-1 text-xs text-[#666]">{cs.stats.length} stats{cs.allImages.length > 0 ? ` · ${cs.allImages.length} images` : ""}{cs.allVideos.length > 0 ? ` · ${cs.allVideos.length} videos` : ""}</p>
          </div>
        </div>
      )}
      renderEditForm={(cs: CaseStudyData) => fields(cs)}
      renderAddForm={() => fields()}
      upsertAction={upsertAction}
      deleteAction={deleteAction}
      addTitle="Add Case Study"
    />
  );
}
