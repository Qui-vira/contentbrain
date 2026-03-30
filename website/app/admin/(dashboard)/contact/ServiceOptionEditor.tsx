"use client";

import { EditableList } from "../EditableList";
import { AdminInput } from "../components";

interface ServiceOptionData {
  id: number;
  name: string;
  sortOrder: number;
}

export function ServiceOptionEditor({
  options,
  upsertAction,
  deleteAction,
}: {
  options: ServiceOptionData[];
  upsertAction: (prev: unknown, formData: FormData) => Promise<string>;
  deleteAction: (id: number) => Promise<void>;
}) {
  const fields = (opt?: ServiceOptionData) => (
    <div className="grid gap-4 md:grid-cols-2">
      <AdminInput label="Option Name" name="name" required defaultValue={opt?.name || ""} />
      <AdminInput label="Sort Order" name="sortOrder" type="number" defaultValue={opt ? String(opt.sortOrder) : "0"} />
    </div>
  );

  return (
    <EditableList
      items={options}
      getId={(opt) => opt.id}
      renderSummary={(opt: ServiceOptionData) => (
        <span className="text-sm text-white">{opt.name}</span>
      )}
      renderEditForm={(opt: ServiceOptionData) => fields(opt)}
      renderAddForm={() => fields()}
      upsertAction={upsertAction}
      deleteAction={deleteAction}
      addTitle="Add Service Option"
    />
  );
}
