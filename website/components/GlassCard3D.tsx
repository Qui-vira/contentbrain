"use client";

import React, { useRef, useState } from "react";

interface GlassCard3DProps {
  children: React.ReactNode;
  className?: string;
}

export function GlassCard3D({ children, className = "" }: GlassCard3DProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [transform, setTransform] = useState({ rotateX: 0, rotateY: 0 });

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    const rotateX = (y / rect.height) * -12;
    const rotateY = (x / rect.width) * 12;
    setTransform({ rotateX, rotateY });
  };

  const handleMouseLeave = () => {
    setTransform({ rotateX: 0, rotateY: 0 });
  };

  return (
    <div
      className="group"
      style={{ perspective: "1000px" }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <div
        ref={cardRef}
        className={`relative rounded-xl border border-border bg-bg-secondary/80 backdrop-blur-xl p-8 transition-all duration-300 ease-out hover:border-accent/30 hover:shadow-[0_8px_32px_rgba(230,57,70,0.15)] ${className}`}
        style={{
          transform: `rotateX(${transform.rotateX}deg) rotateY(${transform.rotateY}deg) translateZ(0)`,
          transformStyle: "preserve-3d",
        }}
      >
        {/* Glow overlay on hover */}
        <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-accent/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

        {/* Content layer - pushed forward in 3D space */}
        <div
          style={{
            transform: "translateZ(20px)",
            transformStyle: "preserve-3d",
          }}
        >
          {children}
        </div>
      </div>
    </div>
  );
}
