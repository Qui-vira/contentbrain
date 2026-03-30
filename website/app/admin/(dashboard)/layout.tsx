import Link from "next/link";
import { verifySession, destroySession } from "@/lib/auth";
import { redirect } from "next/navigation";
import {
  LayoutDashboard,
  Settings,
  Home,
  Briefcase,
  DollarSign,
  FolderOpen,
  User,
  MessageCircle,
  LogOut,
} from "lucide-react";

const navItems = [
  { href: "/admin", label: "Dashboard", icon: LayoutDashboard },
  { href: "/admin/settings", label: "Settings", icon: Settings },
  { href: "/admin/homepage", label: "Homepage", icon: Home },
  { href: "/admin/services", label: "Services", icon: Briefcase },
  { href: "/admin/pricing", label: "Pricing", icon: DollarSign },
  { href: "/admin/portfolio", label: "Portfolio", icon: FolderOpen },
  { href: "/admin/about", label: "About", icon: User },
  { href: "/admin/contact", label: "Contact", icon: MessageCircle },
];

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await verifySession();
  if (!session) redirect("/admin/login");

  async function logout() {
    "use server";
    await destroySession();
    redirect("/admin/login");
  }

  return (
    <div className="flex min-h-screen bg-[#0d0d0d]">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 z-40 flex h-screen w-56 flex-col border-r border-[#222] bg-[#111]">
        <div className="flex h-14 items-center px-5">
          <Link href="/admin" className="text-lg font-bold text-white">
            Quivira <span className="text-xs font-normal text-[#666]">Admin</span>
          </Link>
        </div>

        <nav className="flex-1 space-y-0.5 px-3 py-4">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-[#aaa] transition-colors hover:bg-[#1a1a1a] hover:text-white"
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="border-t border-[#222] p-3">
          <form action={logout}>
            <button
              type="submit"
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-[#666] transition-colors hover:bg-[#1a1a1a] hover:text-white cursor-pointer"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </form>
          <Link
            href="/"
            className="mt-1 flex items-center gap-3 rounded-lg px-3 py-2.5 text-xs text-[#444] transition-colors hover:text-[#888]"
          >
            View live site &rarr;
          </Link>
        </div>
      </aside>

      {/* Main content */}
      <main className="ml-56 flex-1 p-8">
        {children}
      </main>
    </div>
  );
}
