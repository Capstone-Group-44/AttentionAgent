// app/_components/auth-required.tsx
"use client";
import Link from "next/link";

export function AuthRequired({ message = "Please log in to view this page." }) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center px-6 text-center">
      <h2 className="text-xl font-semibold">{message}</h2>
      <div className="mt-6 flex gap-3">
        <Link
          href="/login"
          className="rounded-lg bg-slate-900 px-5 py-2 text-sm font-medium text-white hover:bg-slate-800"
        >
          Log in
        </Link>
        <Link
          href="/register"
          className="rounded-lg border border-slate-300 px-5 py-2 text-sm font-medium hover:bg-slate-100"
        >
          Create account
        </Link>
      </div>
    </div>
  );
}