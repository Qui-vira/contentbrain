"use client";

import { EditableList } from "../EditableList";
import { AdminInput } from "../components";

interface ContactOptionData {
  id: number;
  icon: string;
  title: string;
  description: string;
  href: string;
  sortOrder: number;
}

export function ContactOptionEditor({
  options,
  upsertAction,
  deleteAction,
}: {
  options: ContactOptionData[];
  upsertAction: (prev: unknown, formData: FormData) => Promise<string>;
  deleteAction: (id: number) => Promise<void>;
}) {
  const fields = (opt?: ContactOptionData) => (
    <>
      <div className="grid gap-4 md:grid-cols-3">
        <AdminInput label="Icon (Lucide)" name="icon" required placeholder="e.g. MessageCircle" defaultValue={opt?.icon || ""} />
        <AdminInput label="Title" name="title" required defaultValue={opt?.title || ""} />
        <AdminInput label="Description" name="description" required defaultValue={opt?.description || ""} />
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <AdminInput label="URL" name="href" required defaultValue={opt?.href || ""} />
        <AdminInput label="Sort Order" name="sortOrder" type="number" defaultValue={opt ? String(opt.sortOrder) : "0"} />
      </div>
    </>
  );

  return (
    <EditableList
      items={options}
      getId={(opt) => opt.id}
      renderSummary={(opt: ContactOptionData) => (
        <div>
          <span className="text-sm font-medium text-white">{opt.title}</span>
          <span className="ml-2 text-xs text-[#555]">({opt.icon})</span>
          <p className="text-xs text-[#666]">{opt.description}</p>
        </div>
      )}
      renderEditForm={(opt: ContactOptionData) => fields(opt)}
      renderAddForm={() => fields()}
      upsertAction={upsertAction}
      deleteAction={deleteAction}
      addTitle="Add Contact Option"
    />
  );
}
