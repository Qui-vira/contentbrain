"use client";

import { useActionState } from "react";
import { login } from "../actions/auth";

export default function LoginPage() {
  const [error, formAction, isPending] = useActionState(login, null);

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#0a0a0a]">
      <div className="w-full max-w-sm rounded-xl border border-[#222] bg-[#111] p-8">
        <h1 className="mb-6 text-center text-xl font-bold text-white">
          Admin Login
        </h1>

        <form action={formAction} className="space-y-4">
          <div>
            <label htmlFor="username" className="mb-1 block text-sm text-[#888]">
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              required
              className="w-full rounded-lg border border-[#333] bg-[#1a1a1a] px-4 py-2.5 text-white placeholder:text-[#555] focus:border-[#E63946] focus:outline-none"
              placeholder="admin"
            />
          </div>

          <div>
            <label htmlFor="password" className="mb-1 block text-sm text-[#888]">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              className="w-full rounded-lg border border-[#333] bg-[#1a1a1a] px-4 py-2.5 text-white placeholder:text-[#555] focus:border-[#E63946] focus:outline-none"
            />
          </div>

          {error && (
            <p className="text-sm text-[#E63946]">{error}</p>
          )}

          <button
            type="submit"
            disabled={isPending}
            className="w-full rounded-lg bg-[#E63946] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#FF4D5A] disabled:opacity-50 cursor-pointer"
          >
            {isPending ? "Signing in..." : "Sign In"}
          </button>
        </form>
      </div>
    </div>
  );
}
