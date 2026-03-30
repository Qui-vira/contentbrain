"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";

interface StaggerGridProps {
  children: React.ReactNode[];
  className?: string;
  staggerDelay?: number;
  direction?: "up" | "left" | "right" | "scale";
}

export function StaggerGrid({
  children,
  className = "",
  staggerDelay = 0.1,
  direction = "up",
}: StaggerGridProps) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-10% 0px" });

  const getInitial = () => {
    switch (direction) {
      case "left":
        return { opacity: 0, x: -40 };
      case "right":
        return { opacity: 0, x: 40 };
      case "scale":
        return { opacity: 0, scale: 0.8 };
      default:
        return { opacity: 0, y: 40 };
    }
  };

  const getAnimate = () => {
    switch (direction) {
      case "left":
      case "right":
        return { opacity: 1, x: 0 };
      case "scale":
        return { opacity: 1, scale: 1 };
      default:
        return { opacity: 1, y: 0 };
    }
  };

  return (
    <div ref={ref} className={className}>
      {children.map((child, i) => (
        <motion.div
          key={i}
          initial={getInitial()}
          animate={isInView ? getAnimate() : {}}
          transition={{
            duration: 0.6,
            delay: i * staggerDelay,
            ease: [0.16, 1, 0.3, 1],
          }}
        >
          {child}
        </motion.div>
      ))}
    </div>
  );
}
