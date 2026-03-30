"use client";

import { EditableList } from "../EditableList";
import { AdminInput } from "../components";

interface SocialLinkData {
  id: number;
  name: string;
  href: string;
  sortOrder: number;
}

export function SocialLinkEditor({
  links,
  upsertAction,
  deleteAction,
}: {
  links: SocialLinkData[];
  upsertAction: (prev: unknown, formData: FormData) => Promise<string>;
  deleteAction: (id: number) => Promise<void>;
}) {
  const fields = (l?: SocialLinkData) => (
    <div className="grid gap-4 md:grid-cols-3">
      <AdminInput label="Name" name="name" required placeholder="e.g. X (Twitter)" defaultValue={l?.name || ""} />
      <AdminInput label="URL" name="href" required placeholder="https://..." defaultValue={l?.href || ""} />
      <AdminInput label="Sort Order" name="sortOrder" type="number" defaultValue={l ? String(l.sortOrder) : "0"} />
    </div>
  );

  return (
    <EditableList
      items={links}
      getId={(l) => l.id}
      renderSummary={(l: SocialLinkData) => (
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-white">{l.name}</span>
          <span className="text-xs text-[#666]">{l.href}</span>
        </div>
      )}
      renderEditForm={(l: SocialLinkData) => fields(l)}
      renderAddForm={() => fields()}
      upsertAction={upsertAction}
      deleteAction={deleteAction}
      addTitle="Add Social Link"
    />
  );
}
