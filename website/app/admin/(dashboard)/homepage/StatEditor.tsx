"use client";

import { EditableList } from "../EditableList";
import { AdminInput, AdminSelect } from "../components";

interface StatData {
  id: number;
  page: string;
  label: string;
  value: number;
  suffix: string | null;
  sortOrder: number;
}

export function StatEditor({
  stats,
  page,
  upsertAction,
  deleteAction,
}: {
  stats: StatData[];
  page: string;
  upsertAction: (prev: unknown, formData: FormData) => Promise<string>;
  deleteAction: (id: number) => Promise<void>;
}) {
  const fields = (stat?: StatData) => (
    <div className="grid gap-4 md:grid-cols-4">
      <AdminInput label="Label" name="label" required placeholder="e.g. Community Members" defaultValue={stat?.label || ""} />
      <AdminInput label="Value" name="value" type="number" required defaultValue={stat ? String(stat.value) : ""} />
      <AdminInput label="Suffix" name="suffix" placeholder="e.g. +, %+" defaultValue={stat?.suffix || ""} />
      <AdminInput label="Sort Order" name="sortOrder" type="number" defaultValue={stat ? String(stat.sortOrder) : "0"} />
    </div>
  );

  return (
    <EditableList
      items={stats}
      getId={(s) => s.id}
      renderSummary={(s: StatData) => (
        <div className="flex items-center gap-3">
          <span className="text-2xl font-bold text-white">{s.value}{s.suffix}</span>
          <span className="text-sm text-[#888]">{s.label}</span>
        </div>
      )}
      renderEditForm={(s: StatData) => fields(s)}
      renderAddForm={() => fields()}
      upsertAction={upsertAction}
      deleteAction={deleteAction}
      hiddenFields={{ page }}
      addTitle="Add Stat"
    />
  );
}
