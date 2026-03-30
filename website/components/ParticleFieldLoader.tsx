"use client";

import dynamic from "next/dynamic";

const ParticleField = dynamic(
  () => import("@/components/ParticleField").then((mod) => ({ default: mod.ParticleField })),
  { ssr: false }
);

export function ParticleFieldLoader() {
  return <ParticleField />;
}
