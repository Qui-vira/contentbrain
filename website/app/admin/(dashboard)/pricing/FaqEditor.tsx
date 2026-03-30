"use client";

import { EditableList } from "../EditableList";
import { AdminInput, AdminTextarea } from "../components";

interface FaqData {
  id: number;
  question: string;
  answer: string;
  sortOrder: number;
}

export function FaqEditor({
  items,
  upsertAction,
  deleteAction,
}: {
  items: FaqData[];
  upsertAction: (prev: unknown, formData: FormData) => Promise<string>;
  deleteAction: (id: number) => Promise<void>;
}) {
  const fields = (f?: FaqData) => (
    <>
      <div className="grid gap-4 md:grid-cols-2">
        <AdminInput label="Question" name="question" required defaultValue={f?.question || ""} />
        <AdminInput label="Sort Order" name="sortOrder" type="number" defaultValue={f ? String(f.sortOrder) : "0"} />
      </div>
      <AdminTextarea label="Answer" name="answer" required rows={3} defaultValue={f?.answer || ""} />
    </>
  );

  return (
    <EditableList
      items={items}
      getId={(f) => f.id}
      renderSummary={(f: FaqData) => (
        <div>
          <p className="text-sm font-medium text-white">{f.question}</p>
          <p className="mt-1 text-xs text-[#666] line-clamp-2">{f.answer}</p>
        </div>
      )}
      renderEditForm={(f: FaqData) => fields(f)}
      renderAddForm={() => fields()}
      upsertAction={upsertAction}
      deleteAction={deleteAction}
      addTitle="Add FAQ"
    />
  );
}
