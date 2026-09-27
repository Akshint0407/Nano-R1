"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import Link from "next/link";
import { api, type Conversation } from "@/lib/api";

export default function HistoryPage() {
  const { data: session, status } = useSession();
  const accessToken = (session as unknown as { accessToken?: string } | null)?.accessToken;
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!accessToken) return;
    api
      .listConversations(accessToken)
      .then(setConversations)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load history."));
  }, [accessToken]);

  if (status === "loading") return null;

  if (status !== "authenticated") {
    return (
      <p className="text-ink/70">
        <Link href="/login" className="text-accent underline">
          Sign in
        </Link>{" "}
        to see your solved problems.
      </p>
    );
  }

  return (
    <div>
      <h1 className="font-serif text-2xl">History</h1>
      {error && <p className="mt-4 text-sm text-red-700">{error}</p>}
      {conversations.length === 0 && !error && (
        <p className="mt-4 text-ink/60">Nothing solved yet.</p>
      )}
      <ul className="mt-6 divide-y divide-rule border-t border-rule">
        {conversations.map((c) => (
          <li key={c.id}>
            <Link href={`/history/${c.id}`} className="block py-3 hover:text-accent">
              {c.title}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
