"use client";

import { useActionState, useState, useRef, type ReactNode } from "react";

// Shared admin UI components

export function AdminInput({
  label,
  name,
  defaultValue = "",
  type = "text",
  required = false,
  placeholder,
}: {
  label: string;
  name: string;
  defaultValue?: string;
  type?: string;
  required?: boolean;
  placeholder?: string;
}) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-[#888]">{label}</label>
      <input
        name={name}
        type={type}
        defaultValue={defaultValue}
        required={required}
        placeholder={placeholder}
        className="w-full rounded-lg border border-[#333] bg-[#1a1a1a] px-3 py-2 text-sm text-white placeholder:text-[#555] focus:border-[#E63946] focus:outline-none"
      />
    </div>
  );
}

export function AdminTextarea({
  label,
  name,
  defaultValue = "",
  rows = 3,
  required = false,
}: {
  label: string;
  name: string;
  defaultValue?: string;
  rows?: number;
  required?: boolean;
}) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-[#888]">{label}</label>
      <textarea
        name={name}
        defaultValue={defaultValue}
        rows={rows}
        required={required}
        className="w-full rounded-lg border border-[#333] bg-[#1a1a1a] px-3 py-2 text-sm text-white placeholder:text-[#555] focus:border-[#E63946] focus:outline-none resize-none"
      />
    </div>
  );
}

export function AdminSelect({
  label,
  name,
  defaultValue = "",
  options,
  required = false,
}: {
  label: string;
  name: string;
  defaultValue?: string;
  options: { value: string; label: string }[];
  required?: boolean;
}) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-[#888]">{label}</label>
      <select
        name={name}
        defaultValue={defaultValue}
        required={required}
        className="w-full rounded-lg border border-[#333] bg-[#1a1a1a] px-3 py-2 text-sm text-white focus:border-[#E63946] focus:outline-none"
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  );
}

export function AdminButton({
  children,
  variant = "primary",
  type = "submit",
  onClick,
}: {
  children: React.ReactNode;
  variant?: "primary" | "danger" | "secondary";
  type?: "submit" | "button";
  onClick?: () => void;
}) {
  const colors = {
    primary: "bg-[#E63946] hover:bg-[#FF4D5A] text-white",
    danger: "bg-transparent border border-red-800 hover:bg-red-900/30 text-red-400",
    secondary: "bg-[#222] hover:bg-[#333] text-[#ccc]",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors cursor-pointer ${colors[variant]}`}
    >
      {children}
    </button>
  );
}

export function AdminCard({ children, title }: { children: React.ReactNode; title?: string }) {
  return (
    <div className="rounded-xl border border-[#222] bg-[#111] p-6">
      {title && <h3 className="mb-4 text-lg font-semibold text-white">{title}</h3>}
      {children}
    </div>
  );
}

export function FormWithStatus({
  action,
  children,
  buttonText = "Save",
}: {
  action: (prev: unknown, formData: FormData) => Promise<string>;
  children: React.ReactNode;
  buttonText?: string;
}) {
  const [message, formAction, isPending] = useActionState(action, null);

  return (
    <form action={formAction} className="space-y-4">
      {children}
      <div className="flex items-center gap-3">
        <AdminButton>{isPending ? "Saving..." : buttonText}</AdminButton>
        {message && <span className="text-sm text-green-400">{message}</span>}
      </div>
    </form>
  );
}

export function DeleteButton({
  action,
  label = "Delete",
}: {
  action: () => Promise<void>;
  label?: string;
}) {
  return (
    <form action={action}>
      <button
        type="submit"
        className="text-xs text-red-400 hover:text-red-300 transition-colors cursor-pointer"
      >
        {label}
      </button>
    </form>
  );
}

export function ImageUpload({
  label,
  name,
  defaultValue = "",
}: {
  label: string;
  name: string;
  defaultValue?: string;
}) {
  const [url, setUrl] = useState(defaultValue);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch("/api/upload", { method: "POST", body: formData });
      const data = await res.json();
      if (data.url) {
        setUrl(data.url);
      } else {
        alert(data.error || "Upload failed");
      }
    } catch {
      alert("Upload failed. Check if Blob storage is configured.");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-[#888]">{label}</label>
      {/* Hidden input that carries the URL value into the form */}
      <input type="hidden" name={name} value={url} />

      <div className="flex gap-3">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Upload an image or paste a URL"
          className="flex-1 rounded-lg border border-[#333] bg-[#1a1a1a] px-3 py-2 text-sm text-white placeholder:text-[#555] focus:border-[#E63946] focus:outline-none"
        />
        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          disabled={uploading}
          className="shrink-0 rounded-lg bg-[#222] px-4 py-2 text-sm font-medium text-[#ccc] transition-colors hover:bg-[#333] disabled:opacity-50 cursor-pointer"
        >
          {uploading ? "Uploading..." : "Upload"}
        </button>
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          onChange={handleUpload}
          className="hidden"
        />
      </div>

      {url && (
        <div className="mt-2 flex items-start gap-3">
          <div className="h-20 w-32 shrink-0 overflow-hidden rounded-lg border border-[#333]">
            <img src={url} alt="Preview" className="h-full w-full object-cover" />
          </div>
          <button
            type="button"
            onClick={() => setUrl("")}
            className="text-xs text-red-400 hover:text-red-300 cursor-pointer"
          >
            Remove
          </button>
        </div>
      )}
    </div>
  );
}

export function MediaUpload({
  label,
  name,
  defaultValue = "",
  accept = "image/*,video/*",
}: {
  label: string;
  name: string;
  defaultValue?: string;
  accept?: string;
}) {
  const [url, setUrl] = useState(defaultValue);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const isVideo = url && (url.includes("video") || /\.(mp4|webm|mov|avi)$/i.test(url));

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch("/api/upload", { method: "POST", body: formData });
      const data = await res.json();
      if (data.url) {
        setUrl(data.url);
      } else {
        alert(data.error || "Upload failed");
      }
    } catch {
      alert("Upload failed.");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-[#888]">{label}</label>
      <input type="hidden" name={name} value={url} />
      <div className="flex gap-3">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Upload or paste a URL"
          className="flex-1 rounded-lg border border-[#333] bg-[#1a1a1a] px-3 py-2 text-sm text-white placeholder:text-[#555] focus:border-[#E63946] focus:outline-none"
        />
        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          disabled={uploading}
          className="shrink-0 rounded-lg bg-[#222] px-4 py-2 text-sm font-medium text-[#ccc] transition-colors hover:bg-[#333] disabled:opacity-50 cursor-pointer"
        >
          {uploading ? "Uploading..." : "Upload"}
        </button>
        <input ref={fileRef} type="file" accept={accept} onChange={handleUpload} className="hidden" />
      </div>
      {url && (
        <div className="mt-2 flex items-start gap-3">
          <div className="h-20 w-32 shrink-0 overflow-hidden rounded-lg border border-[#333]">
            {isVideo ? (
              <video src={url} className="h-full w-full object-cover" muted />
            ) : (
              <img src={url} alt="Preview" className="h-full w-full object-cover" />
            )}
          </div>
          <button type="button" onClick={() => setUrl("")} className="text-xs text-red-400 hover:text-red-300 cursor-pointer">
            Remove
          </button>
        </div>
      )}
    </div>
  );
}

export function MultiMediaFields({
  defaultImages = [],
  defaultVideos = [],
  maxImages = 5,
  maxVideos = 5,
  imagePrefix = "image",
  videoPrefix = "video",
}: {
  defaultImages?: string[];
  defaultVideos?: string[];
  maxImages?: number;
  maxVideos?: number;
  imagePrefix?: string;
  videoPrefix?: string;
}) {
  const [imgCount, setImgCount] = useState(Math.max(defaultImages.length, 1));
  const [vidCount, setVidCount] = useState(Math.max(defaultVideos.length, 0));

  return (
    <div className="space-y-4">
      {/* Images */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs font-medium text-[#888]">Images (up to {maxImages})</label>
          {imgCount < maxImages && (
            <button
              type="button"
              onClick={() => setImgCount((c) => Math.min(c + 1, maxImages))}
              className="text-xs text-[#E63946] hover:text-[#FF4D5A] transition-colors cursor-pointer"
            >
              + Add Image
            </button>
          )}
        </div>
        {Array.from({ length: imgCount }).map((_, i) => (
          <ImageUpload key={i} label={`Image ${i + 1}`} name={`${imagePrefix}_${i}`} defaultValue={defaultImages[i] || ""} />
        ))}
      </div>

      {/* Videos */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs font-medium text-[#888]">Videos (up to {maxVideos})</label>
          {vidCount < maxVideos && (
            <button
              type="button"
              onClick={() => setVidCount((c) => Math.min(c + 1, maxVideos))}
              className="text-xs text-[#E63946] hover:text-[#FF4D5A] transition-colors cursor-pointer"
            >
              + Add Video
            </button>
          )}
        </div>
        {Array.from({ length: vidCount }).map((_, i) => (
          <MediaUpload key={i} label={`Video ${i + 1}`} name={`${videoPrefix}_${i}`} defaultValue={defaultVideos[i] || ""} accept="video/*" />
        ))}
      </div>
    </div>
  );
}
