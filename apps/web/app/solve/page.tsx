"use client";

import { useState } from "react";
import { useSession } from "next-auth/react";
import { api, type ConversationDetail, type Message } from "@/lib/api";
import WorkedProblem from "@/components/WorkedProblem";

export default function SolvePage() {
  const { data: session, status } = useSession();
  const [question, setQuestion] = useState("");
  const [conversation, setConversation] = useState<ConversationDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const accessToken = (session as unknown as { accessToken?: string } | null)?.accessToken;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim()) return;
    setError(null);
    setLoading(true);

    try {
      if (!accessToken) {
        throw new Error("Sign in to solve problems and save your history.");
      }
      const updated = conversation
        ? {
            ...conversation,
            messages: [
              ...conversation.messages,
              await api.addMessage(accessToken, conversation.id, question),
            ],
          }
        : await api.startConversation(accessToken, question);
      setConversation(updated);
      setQuestion("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  async function handleRate(message: Message, rating: 1 | -1) {
    if (!accessToken || !conversation) return;
    const feedback = await api.setFeedback(accessToken, message.id, rating);
    setConversation({
      ...conversation,
      messages: conversation.messages.map((m) =>
        m.id === message.id ? { ...m, feedback } : m
      ),
    });
  }

  return (
    <div>
      <h1 className="font-serif text-2xl">Give it a problem</h1>

      <form onSubmit={handleSubmit} className="mt-6">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether?"
          rows={4}
          className="w-full resize-none border border-rule bg-transparent px-3 py-2"
        />
        <div className="mt-3 flex items-center gap-4">
          <button
            type="submit"
            disabled={loading}
            className="border border-ink bg-ink px-5 py-2 text-paper hover:bg-accent hover:border-accent disabled:opacity-50"
          >
            {loading ? "Working it out…" : "Solve"}
          </button>
          {status !== "authenticated" && (
            <p className="text-sm text-ink/50">Sign in to solve problems and save your history.</p>
          )}
        </div>
        {error && <p className="mt-2 text-sm text-red-700">{error}</p>}
      </form>

      {conversation && (
        <div className="mt-10">
          {conversation.messages.map((message) => (
            <WorkedProblem
              key={message.id}
              message={message}
              onRate={accessToken ? (rating) => handleRate(message, rating) : undefined}
            />
          ))}
        </div>
      )}
    </div>
  );
}
