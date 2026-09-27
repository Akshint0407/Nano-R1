"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useSession } from "next-auth/react";
import { api, type ConversationDetail, type Message } from "@/lib/api";
import WorkedProblem from "@/components/WorkedProblem";

export default function HistoryDetailPage() {
  const params = useParams<{ id: string }>();
  const { data: session, status } = useSession();
  const accessToken = (session as unknown as { accessToken?: string } | null)?.accessToken;
  const [conversation, setConversation] = useState<ConversationDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!accessToken || !params.id) return;
    api
      .getConversation(accessToken, params.id)
      .then(setConversation)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load."));
  }, [accessToken, params.id]);

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

  if (status === "loading") return null;
  if (status !== "authenticated") return <p className="text-ink/70">Sign in to view this.</p>;
  if (error) return <p className="text-sm text-red-700">{error}</p>;
  if (!conversation) return null;

  return (
    <div>
      <h1 className="font-serif text-2xl">{conversation.title}</h1>
      <div className="mt-6">
        {conversation.messages.map((message) => (
          <WorkedProblem
            key={message.id}
            message={message}
            onRate={(rating) => handleRate(message, rating)}
          />
        ))}
      </div>
    </div>
  );
}
