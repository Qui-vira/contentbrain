"use client";

import { useEffect, useState, useCallback } from "react";
import { motion, useSpring } from "framer-motion";

export function CustomCursor() {
  const [visible, setVisible] = useState(false);
  const [hovering, setHovering] = useState(false);

  const springConfig = { damping: 25, stiffness: 250 };
  const cursorX = useSpring(0, springConfig);
  const cursorY = useSpring(0, springConfig);

  const onEnter = useCallback(() => setHovering(true), []);
  const onLeave = useCallback(() => setHovering(false), []);

  useEffect(() => {
    // Only on desktop
    if (window.matchMedia("(max-width: 768px)").matches) return;
    if ("ontouchstart" in window) return;

    const onMouseMove = (e: MouseEvent) => {
      cursorX.set(e.clientX);
      cursorY.set(e.clientY);
      if (!visible) setVisible(true);
    };

    window.addEventListener("mousemove", onMouseMove, { passive: true });

    // Use event delegation instead of attaching to every element
    const onOver = (e: Event) => {
      const target = e.target as HTMLElement;
      if (target.closest("a, button, [role='button'], input, textarea, select, .cursor-pointer")) {
        setHovering(true);
      }
    };
    const onOut = (e: Event) => {
      const target = e.target as HTMLElement;
      if (target.closest("a, button, [role='button'], input, textarea, select, .cursor-pointer")) {
        setHovering(false);
      }
    };

    document.addEventListener("mouseover", onOver, { passive: true });
    document.addEventListener("mouseout", onOut, { passive: true });

    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseover", onOver);
      document.removeEventListener("mouseout", onOut);
    };
  }, [cursorX, cursorY, visible]);

  if (!visible) return null;

  return (
    <>
      <motion.div
        className="fixed top-0 left-0 z-[9999] pointer-events-none mix-blend-difference"
        style={{ x: cursorX, y: cursorY, translateX: "-50%", translateY: "-50%" }}
      >
        <motion.div
          animate={{
            width: hovering ? 48 : 32,
            height: hovering ? 48 : 32,
            borderColor: hovering ? "rgba(230, 57, 70, 0.8)" : "rgba(255,255,255,0.5)",
          }}
          transition={{ duration: 0.2 }}
          className="rounded-full border-2"
        />
      </motion.div>
      <motion.div
        className="fixed top-0 left-0 z-[9999] pointer-events-none"
        style={{ x: cursorX, y: cursorY, translateX: "-50%", translateY: "-50%" }}
      >
        <motion.div
          animate={{
            width: hovering ? 6 : 4,
            height: hovering ? 6 : 4,
            backgroundColor: hovering ? "rgba(230, 57, 70, 1)" : "rgba(255,255,255,0.9)",
          }}
          transition={{ duration: 0.15 }}
          className="rounded-full"
        />
      </motion.div>
    </>
  );
}
