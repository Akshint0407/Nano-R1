import type { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

// This file runs server-side (inside the web container), so it must use the
// Docker network address for the API, not the browser-facing localhost URL.
const API_URL = process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const authOptions: NextAuthOptions = {
  session: { strategy: "jwt" },
  pages: { signIn: "/login" },
  providers: [
    CredentialsProvider({
      name: "Email and password",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null;

        const res = await fetch(`${API_URL}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: credentials.email,
            password: credentials.password,
          }),
        });
        if (!res.ok) return null;

        const data = await res.json();
        // The backend only returns a token; decode nothing else client-side.
        return { id: credentials.email, email: credentials.email, accessToken: data.access_token };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        // @ts-expect-error - accessToken added in authorize()
        token.accessToken = user.accessToken;
      }
      return token;
    },
    async session({ session, token }) {
      // @ts-expect-error - extending the default session shape
      session.accessToken = token.accessToken;
      return session;
    },
  },
};
