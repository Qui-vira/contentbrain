"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";

interface AutoCarouselProps {
  images?: string[];
  videos?: string[];
  alt?: string;
  interval?: number; // ms between auto-swipes
  className?: string;
}

export function AutoCarousel({
  images = [],
  videos = [],
  alt = "",
  interval = 4000,
  className = "",
}: AutoCarouselProps) {
  const media = [
    ...images.map((src) => ({ type: "image" as const, src })),
    ...videos.map((src) => ({ type: "video" as const, src })),
  ];

  const [current, setCurrent] = useState(0);
  const [direction, setDirection] = useState(1);
  const [paused, setPaused] = useState(false);
  const touchStartX = useRef(0);
  const touchEndX = useRef(0);

  const goTo = useCallback(
    (idx: number, dir?: number) => {
      setDirection(dir ?? (idx > current ? 1 : -1));
      setCurrent(idx);
    },
    [current],
  );

  const next = useCallback(() => {
    setDirection(1);
    setCurrent((c) => (c + 1) % media.length);
  }, [media.length]);

  const prev = useCallback(() => {
    setDirection(-1);
    setCurrent((c) => (c - 1 + media.length) % media.length);
  }, [media.length]);

  // Auto-advance
  useEffect(() => {
    if (media.length <= 1 || paused) return;
    const timer = setInterval(next, interval);
    return () => clearInterval(timer);
  }, [media.length, paused, next, interval]);

  // Touch/swipe handlers
  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartX.current = e.touches[0].clientX;
  };
  const handleTouchMove = (e: React.TouchEvent) => {
    touchEndX.current = e.touches[0].clientX;
  };
  const handleTouchEnd = () => {
    const diff = touchStartX.current - touchEndX.current;
    if (Math.abs(diff) > 50) {
      if (diff > 0) next();
      else prev();
    }
  };

  if (media.length === 0) return null;

  if (media.length === 1) {
    const item = media[0];
    return (
      <div className={`group relative overflow-hidden rounded-2xl border border-border ${className}`}>
        {item.type === "image" ? (
          <Image src={item.src} alt={alt} width={600} height={400} className="h-auto w-full transition-transform duration-700 group-hover:scale-105" />
        ) : (
          <video src={item.src} controls className="h-auto w-full" />
        )}
      </div>
    );
  }

  const item = media[current];

  return (
    <div
      className={`relative overflow-hidden rounded-2xl border border-border ${className}`}
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      <AnimatePresence mode="wait" custom={direction}>
        <motion.div
          key={current}
          custom={direction}
          initial={{ opacity: 0, x: direction * 60 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -direction * 60 }}
          transition={{ duration: 0.35 }}
        >
          {item.type === "image" ? (
            <Image src={item.src} alt={`${alt} ${current + 1}`} width={600} height={400} className="h-auto w-full" />
          ) : (
            <video src={item.src} controls className="h-auto w-full" />
          )}
        </motion.div>
      </AnimatePresence>

      {/* Navigation arrows */}
      <button
        onClick={prev}
        className="absolute left-2 top-1/2 -translate-y-1/2 flex h-8 w-8 items-center justify-center rounded-full bg-black/60 text-white backdrop-blur-sm transition hover:bg-black/80"
        aria-label="Previous"
      >
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
      </button>
      <button
        onClick={next}
        className="absolute right-2 top-1/2 -translate-y-1/2 flex h-8 w-8 items-center justify-center rounded-full bg-black/60 text-white backdrop-blur-sm transition hover:bg-black/80"
        aria-label="Next"
      >
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
      </button>

      {/* Dots */}
      <div className="absolute bottom-3 left-1/2 flex -translate-x-1/2 gap-1.5">
        {media.map((_, idx) => (
          <button
            key={idx}
            onClick={() => goTo(idx)}
            className={`h-1.5 rounded-full transition-all ${idx === current ? "w-6 bg-accent" : "w-1.5 bg-white/50"}`}
            aria-label={`Go to slide ${idx + 1}`}
          />
        ))}
      </div>

      {/* Auto-play indicator */}
      {!paused && (
        <div className="absolute bottom-3 right-3">
          <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent" />
        </div>
      )}
    </div>
  );
}
