"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";

interface TextRevealProps {
  children: string;
  className?: string;
  as?: "h1" | "h2" | "h3" | "p" | "span";
  mode?: "words" | "chars";
  staggerDelay?: number;
  once?: boolean;
}

export function TextReveal({
  children,
  className = "",
  as: Tag = "h2",
  mode = "words",
  staggerDelay = 0.03,
  once = true,
}: TextRevealProps) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once, margin: "-10% 0px" });

  const units = mode === "words" ? children.split(" ") : children.split("");

  return (
    <Tag ref={ref} className={`overflow-hidden ${className}`}>
      {units.map((unit, i) => (
        <motion.span
          key={i}
          className="inline-block"
          initial={{ y: "100%", opacity: 0 }}
          animate={isInView ? { y: 0, opacity: 1 } : {}}
          transition={{
            duration: 0.5,
            delay: i * staggerDelay,
            ease: [0.16, 1, 0.3, 1],
          }}
        >
          {unit}
          {mode === "words" && i < units.length - 1 ? "\u00A0" : ""}
        </motion.span>
      ))}
    </Tag>
  );
}
