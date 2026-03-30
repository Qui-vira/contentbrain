"use client";

import { useRef, useState } from "react";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

interface MagneticButtonProps {
  children: React.ReactNode;
  href?: string;
  variant?: "primary" | "secondary";
  className?: string;
  showArrow?: boolean;
  strength?: number;
}

export function MagneticButton({
  children,
  href,
  variant = "primary",
  className = "",
  showArrow = true,
  strength = 0.3,
}: MagneticButtonProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const x = (e.clientX - rect.left - rect.width / 2) * strength;
    const y = (e.clientY - rect.top - rect.height / 2) * strength;
    setPosition({ x, y });
  };

  const handleMouseLeave = () => {
    setPosition({ x: 0, y: 0 });
  };

  const baseStyles =
    "inline-flex items-center gap-2 rounded-lg px-7 py-3.5 text-base font-semibold tracking-wide cursor-pointer";
  const primaryStyles =
    "bg-gradient-to-br from-accent to-[#FF6B6B] text-white shadow-[0_0_0_0_rgba(230,57,70,0)] hover:shadow-[0_4px_30px_rgba(230,57,70,0.4)]";
  const secondaryStyles =
    "border border-border text-text-primary hover:border-accent/50 hover:bg-bg-tertiary";

  const styles = `${baseStyles} ${variant === "primary" ? primaryStyles : secondaryStyles} ${className}`;

  const Tag = href ? "a" : "button";

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      animate={{ x: position.x, y: position.y }}
      transition={{ type: "spring", stiffness: 150, damping: 15, mass: 0.1 }}
      className="inline-block"
    >
      <Tag href={href} className={styles}>
        <motion.span
          animate={{ x: position.x * 0.3, y: position.y * 0.3 }}
          transition={{ type: "spring", stiffness: 150, damping: 15 }}
          className="inline-flex items-center gap-2"
        >
          {children}
          {showArrow && <ArrowRight className="h-4 w-4" />}
        </motion.span>
      </Tag>
    </motion.div>
  );
}
