"use client";

export default function FeedbackButtons({
  rating,
  onRate,
}: {
  rating: number | null;
  onRate: (rating: 1 | -1) => void;
}) {
  return (
    <div className="flex items-center gap-2 text-sm">
      <button
        aria-label="This reasoning was correct"
        onClick={() => onRate(1)}
        className={`border px-2 py-1 ${
          rating === 1 ? "border-accent bg-accentSoft" : "border-rule hover:border-accent"
        }`}
      >
        Correct
      </button>
      <button
        aria-label="This reasoning was wrong"
        onClick={() => onRate(-1)}
        className={`border px-2 py-1 ${
          rating === -1 ? "border-accent bg-accentSoft" : "border-rule hover:border-accent"
        }`}
      >
        Wrong
      </button>
    </div>
  );
}
