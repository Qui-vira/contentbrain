"use client";

import { EditableList } from "../EditableList";
import { AdminInput, ImageUpload } from "../components";

interface LogoData {
  id: number;
  name: string;
  image: string;
  sortOrder: number;
}

export function ClientLogoEditor({
  logos,
  upsertAction,
  deleteAction,
}: {
  logos: LogoData[];
  upsertAction: (prev: unknown, formData: FormData) => Promise<string>;
  deleteAction: (id: number) => Promise<void>;
}) {
  const fields = (l?: LogoData) => (
    <>
      <div className="grid gap-4 md:grid-cols-2">
        <AdminInput label="Client Name" name="name" required defaultValue={l?.name || ""} />
        <AdminInput label="Sort Order" name="sortOrder" type="number" defaultValue={l ? String(l.sortOrder) : "0"} />
      </div>
      <ImageUpload label="Logo Image" name="image" defaultValue={l?.image || ""} />
    </>
  );

  return (
    <EditableList
      items={logos}
      getId={(l) => l.id}
      renderSummary={(l: LogoData) => (
        <div className="flex items-center gap-3">
          {l.image && (
            <div className="h-10 w-20 shrink-0 overflow-hidden rounded border border-[#333] bg-white p-1">
              <img src={l.image} alt={l.name} className="h-full w-full object-contain" />
            </div>
          )}
          <span className="text-sm text-[#ccc]">{l.name}</span>
        </div>
      )}
      renderEditForm={(l: LogoData) => fields(l)}
      renderAddForm={() => fields()}
      upsertAction={upsertAction}
      deleteAction={deleteAction}
      addTitle="Add Client Logo"
    />
  );
}
