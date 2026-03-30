"use client";

import Image from "next/image";
import { AutoCarousel } from "@/components/AutoCarousel";

interface TestimonialCardProps {
  quote: string;
  attribution: string;
  images?: string[];
  rating?: number;
  avatar?: string | null;
}

/** Render filled/empty stars */
function StarRating({ rating }: { rating: number }) {
  return (
    <div className="mb-3 flex gap-0.5">
      {[1, 2, 3, 4, 5].map((i) => (
        <svg
          key={i}
          className={`h-4 w-4 ${i <= rating ? "text-accent" : "text-border"}`}
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      ))}
    </div>
  );
}

/** Highlight numbers, percentages, and dollar amounts in accent color */
function HighlightedQuote({ text }: { text: string }) {
  const parts = text.split(/(\$[\d,.]+[KkMm]?|\d+[%+x]|\d{2,}[\d,.]*)/g);
  return (
    <span>
      {parts.map((part, i) =>
        /^\$[\d,.]+[KkMm]?$|^\d+[%+x]$|^\d{2,}[\d,.]*$/.test(part) ? (
          <span key={i} className="font-bold text-accent not-italic">{part}</span>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </span>
  );
}

export function TestimonialCard({ quote, attribution, images = [], rating = 5, avatar }: TestimonialCardProps) {
  return (
    <div className="rounded-lg border-l-[3px] border-l-accent bg-bg-secondary p-8">
      {images.length > 0 && (
        <div className="mb-4">
          <AutoCarousel images={images} alt={attribution} interval={4000} />
        </div>
      )}
      {rating > 0 && <StarRating rating={rating} />}
      <div className="text-lg italic leading-relaxed text-text-primary whitespace-pre-line">
        &ldquo;<HighlightedQuote text={quote} />&rdquo;
      </div>
      <div className="mt-4 flex items-center gap-3">
        {avatar ? (
          <Image
            src={avatar}
            alt={attribution}
            width={40}
            height={40}
            className="h-10 w-10 rounded-full border border-border object-cover"
          />
        ) : (
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent/10 text-sm font-bold text-accent">
            {attribution.charAt(0).toUpperCase()}
          </div>
        )}
        <p className="text-sm text-text-secondary">{attribution}</p>
      </div>
    </div>
  );
}
