"use client";

import Link from "next/link";
import { useSession, signOut } from "next-auth/react";

export default function Navbar() {
  const { data: session, status } = useSession();

  return (
    <header className="border-b border-rule">
      <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-4">
        <Link href="/" className="font-serif text-lg tracking-tight">
          Nano-R1
        </Link>
        <nav className="flex items-center gap-5 text-sm">
          <Link href="/solve" className="hover:text-accent">
            Solve
          </Link>
          {status === "authenticated" && (
            <Link href="/history" className="hover:text-accent">
              History
            </Link>
          )}
          {status === "authenticated" ? (
            <button onClick={() => signOut({ callbackUrl: "/" })} className="hover:text-accent">
              Sign out
            </button>
          ) : (
            <Link href="/login" className="hover:text-accent">
              Sign in
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
