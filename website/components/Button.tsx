"use client";

import { ArrowRight } from "lucide-react";

interface ButtonProps {
  children: React.ReactNode;
  variant?: "primary" | "secondary";
  href?: string;
  onClick?: () => void;
  className?: string;
  showArrow?: boolean;
}

export function Button({
  children,
  variant = "primary",
  href,
  onClick,
  className = "",
  showArrow = true,
}: ButtonProps) {
  const baseStyles =
    "inline-flex items-center gap-2 rounded-lg px-7 py-3.5 text-base font-semibold tracking-wide transition-all duration-200 cursor-pointer";
  const primaryStyles =
    "bg-gradient-to-br from-accent to-[#FF6B6B] text-white hover:scale-[1.02] hover:shadow-[0_4px_20px_rgba(230,57,70,0.3)]";
  const secondaryStyles =
    "border border-border text-text-primary hover:border-border-hover hover:bg-bg-tertiary";

  const styles = `${baseStyles} ${variant === "primary" ? primaryStyles : secondaryStyles} ${className}`;

  if (href) {
    return (
      <a href={href} className={styles}>
        {children}
        {showArrow && <ArrowRight className="h-4 w-4" />}
      </a>
    );
  }

  return (
    <button onClick={onClick} className={styles}>
      {children}
      {showArrow && <ArrowRight className="h-4 w-4" />}
    </button>
  );
}
