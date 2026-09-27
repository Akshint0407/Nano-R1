"use client";

import { useState } from "react";
import type { Message } from "@/lib/api";
import FeedbackButtons from "@/components/FeedbackButtons";

export default function WorkedProblem({
  message,
  onRate,
}: {
  message: Message;
  onRate?: (rating: 1 | -1) => void;
}) {
  const [expanded, setExpanded] = useState(true);

  return (
    <article className="border-b border-rule py-6 last:border-b-0">
      <p className="font-serif text-lg leading-snug">{message.question}</p>

      <button
        onClick={() => setExpanded((v) => !v)}
        className="mt-3 text-xs uppercase tracking-wide text-ink/50 hover:text-accent"
      >
        {expanded ? "Hide work" : "Show work"}
      </button>

      {expanded && (
        <pre className="mt-2 whitespace-pre-wrap font-mono text-sm leading-relaxed text-ink/80">
          {message.reasoning}
        </pre>
      )}

      <div className="mt-4 flex items-center justify-between">
        <div className="inline-block border border-rule bg-accentSoft px-4 py-2">
          <span className="text-xs uppercase tracking-wide text-ink/50">Answer</span>
          <p className="font-serif text-xl">{message.answer}</p>
        </div>
        {onRate && (
          <FeedbackButtons rating={message.feedback?.rating ?? null} onRate={onRate} />
        )}
      </div>
    </article>
  );
}
