"use client";

import { useState } from "react";
import { FormWithStatus, DeleteButton } from "./components";

interface EditableListProps {
  /* eslint-disable @typescript-eslint/no-explicit-any */
  items: any[];
  getId: (item: any) => number;
  renderSummary: (item: any) => React.ReactNode;
  renderEditForm: (item: any) => React.ReactNode;
  renderAddForm: () => React.ReactNode;
  /* eslint-enable @typescript-eslint/no-explicit-any */
  upsertAction: (prev: unknown, formData: FormData) => Promise<string>;
  deleteAction: (id: number) => Promise<void>;
  addTitle?: string;
  /** Extra hidden fields to include in every form (e.g. page="home") */
  hiddenFields?: Record<string, string>;
}

export function EditableList({
  items,
  getId,
  renderSummary,
  renderEditForm,
  renderAddForm,
  upsertAction,
  deleteAction,
  addTitle = "Add New",
  hiddenFields,
}: EditableListProps) {
  const [editingId, setEditingId] = useState<number | null>(null);

  return (
    <div>
      {items.length > 0 && (
        <div className="space-y-3">
          {items.map((item) => {
            const id = getId(item);
            const isEditing = editingId === id;

            return (
              <div key={id} className="rounded-lg bg-[#1a1a1a] p-4">
                {/* Summary row */}
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">{renderSummary(item)}</div>
                  <div className="flex shrink-0 gap-3">
                    <button
                      type="button"
                      onClick={() => setEditingId(isEditing ? null : id)}
                      className="text-xs text-blue-400 hover:text-blue-300 transition-colors cursor-pointer"
                    >
                      {isEditing ? "Close" : "Edit"}
                    </button>
                    <DeleteButton action={async () => { await deleteAction(id); }} />
                  </div>
                </div>

                {/* Inline edit form */}
                {isEditing && (
                  <div className="mt-4 border-t border-[#333] pt-4">
                    <FormWithStatus action={upsertAction} buttonText="Save Changes">
                      <input type="hidden" name="id" value={id} />
                      {hiddenFields && Object.entries(hiddenFields).map(([k, v]) => (
                        <input key={k} type="hidden" name={k} value={v} />
                      ))}
                      {renderEditForm(item)}
                    </FormWithStatus>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Add new form */}
      <div className="mt-6 border-t border-[#222] pt-6">
        <h4 className="mb-3 text-sm font-semibold text-[#aaa]">{addTitle}</h4>
        <FormWithStatus action={upsertAction} buttonText="Add">
          <input type="hidden" name="id" value="" />
          {hiddenFields && Object.entries(hiddenFields).map(([k, v]) => (
            <input key={k} type="hidden" name={k} value={v} />
          ))}
          {renderAddForm()}
        </FormWithStatus>
      </div>
    </div>
  );
}
