"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      await api.register(email, password);
      const result = await signIn("credentials", { email, password, redirect: false });
      if (result?.error) throw new Error("Registered, but sign-in failed — try logging in.");
      router.push("/solve");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-sm">
      <h1 className="font-serif text-2xl">Create an account</h1>
      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm text-ink/70">
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full border border-rule bg-transparent px-3 py-2"
          />
        </div>
        <div>
          <label htmlFor="password" className="block text-sm text-ink/70">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full border border-rule bg-transparent px-3 py-2"
          />
          <p className="mt-1 text-xs text-ink/50">At least 8 characters.</p>
        </div>
        {error && <p className="text-sm text-red-700">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="border border-ink bg-ink px-5 py-2 text-paper hover:bg-accent hover:border-accent disabled:opacity-50"
        >
          {submitting ? "Creating…" : "Create account"}
        </button>
      </form>
    </div>
  );
}
