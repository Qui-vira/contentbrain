"use client";

/**
 * Renders text with line-break awareness.
 * - Double newlines become separate paragraphs with spacing
 * - Single newlines become <br /> within a paragraph
 * - Single-line text renders as a plain <p>
 */
export function TextBlock({
  text,
  className = "",
}: {
  text: string;
  className?: string;
}) {
  if (!text) return null;

  // Split on double newlines for paragraphs
  const paragraphs = text.split(/\n\s*\n/).filter((p) => p.trim());

  if (paragraphs.length <= 1 && !text.includes("\n")) {
    return <p className={className}>{text}</p>;
  }

  return (
    <div className={className}>
      {paragraphs.map((para, i) => {
        const lines = para.split("\n").filter((l) => l.trim());
        return (
          <p key={i} className="mb-4 last:mb-0">
            {lines.map((line, j) => (
              <span key={j}>
                {line.trim()}
                {j < lines.length - 1 && <br />}
              </span>
            ))}
          </p>
        );
      })}
    </div>
  );
}
