"use client";

import React from "react";

interface GlobeHeroProps {
  children?: React.ReactNode;
  className?: string;
}

export function GlobeHero({ children, className = "" }: GlobeHeroProps) {
  return (
    <div className={`relative w-full min-h-screen overflow-hidden ${className}`}>
      <div className="relative z-10 flex items-center min-h-screen">
        {children}
      </div>
      {/* Lightweight CSS globe replacement — no Three.js */}
      <div className="absolute inset-0 z-0 pointer-events-none flex items-center justify-center">
        <div className="globe-orb" />
        <div className="globe-orb globe-orb-outer" />
      </div>
      <style jsx>{`
        .globe-orb {
          position: absolute;
          width: 500px;
          height: 500px;
          border-radius: 50%;
          border: 1px solid rgba(230, 57, 70, 0.12);
          animation: globe-spin 20s linear infinite;
          box-shadow: inset 0 0 80px rgba(230, 57, 70, 0.04);
        }
        .globe-orb::before,
        .globe-orb::after {
          content: "";
          position: absolute;
          inset: 0;
          border-radius: 50%;
          border: 1px solid rgba(230, 57, 70, 0.08);
        }
        .globe-orb::before {
          transform: rotateX(60deg);
        }
        .globe-orb::after {
          transform: rotateY(60deg);
        }
        .globe-orb-outer {
          width: 600px;
          height: 600px;
          opacity: 0.5;
          animation-duration: 30s;
          animation-direction: reverse;
        }
        @keyframes globe-spin {
          from { transform: rotateY(0deg) rotateX(15deg); }
          to { transform: rotateY(360deg) rotateX(15deg); }
        }
      `}</style>
    </div>
  );
}
