"use client";

import { useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";

const keywords = ["Trading", "AI", "Web3", "Education"];

export function KeywordRotator() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % keywords.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <span className="relative inline-block h-[1.1em] overflow-hidden align-bottom">
      <AnimatePresence mode="wait">
        <motion.span
          key={keywords[index]}
          initial={{ y: "100%", opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: "-100%", opacity: 0 }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
          className="inline-block text-accent"
        >
          {keywords[index]}
        </motion.span>
      </AnimatePresence>
    </span>
  );
}
