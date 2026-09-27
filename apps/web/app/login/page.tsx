"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    const result = await signIn("credentials", {
      email,
      password,
      redirect: false,
    });

    setSubmitting(false);
    if (result?.error) {
      setError("Incorrect email or password.");
      return;
    }
    router.push("/solve");
  }

  return (
    <div className="max-w-sm">
      <h1 className="font-serif text-2xl">Sign in</h1>
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
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full border border-rule bg-transparent px-3 py-2"
          />
        </div>
        {error && <p className="text-sm text-red-700">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="border border-ink bg-ink px-5 py-2 text-paper hover:bg-accent hover:border-accent disabled:opacity-50"
        >
          {submitting ? "Signing in…" : "Sign in"}
        </button>
      </form>
      <p className="mt-4 text-sm text-ink/60">
        No account?{" "}
        <Link href="/register" className="text-accent underline">
          Register
        </Link>
      </p>
    </div>
  );
}
