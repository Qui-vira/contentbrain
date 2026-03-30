"use client";

import { usePathname } from "next/navigation";
import { Navbar } from "./Navbar";

export function PublicNavbar() {
  const pathname = usePathname();
  if (pathname.startsWith("/admin")) return null;
  return <Navbar />;
}

export function PublicWrapper({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  if (pathname.startsWith("/admin")) return null;
  return <>{children}</>;
}
