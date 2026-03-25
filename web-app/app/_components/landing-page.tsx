"use client";

import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="flex min-h-[70vh] flex-col items-center justify-center px-6 text-center">
      <h1 className="text-3xl font-semibold tracking-tight">
        SCREEN GAZE
      </h1>

      <p className="mt-4 max-w-md text-sm text-muted-foreground">
        Track your focus sessions, monitor progress, and build better
        productivity habits over time.
      </p>

      <div className="mt-8 flex gap-4">
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