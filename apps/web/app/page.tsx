import Link from "next/link";

export default function HomePage() {
  return (
    <div className="py-10">
      <h1 className="font-serif text-4xl leading-tight">
        A model that shows its work.
      </h1>
      <p className="mt-4 max-w-xl text-ink/70">
        Nano-R1 is Qwen2.5-3B-Instruct, fine-tuned with GRPO on GSM8K math word problems.
        Every answer comes with the reasoning trace the model used to get there — and you
        can tell it when it&rsquo;s wrong, which feeds back into the next training pass.
      </p>
      <div className="mt-8 flex gap-4">
        <Link
          href="/solve"
          className="border border-ink bg-ink px-5 py-2 text-paper hover:bg-accent hover:border-accent"
        >
          Try a problem
        </Link>
        <Link href="/register" className="border border-rule px-5 py-2 hover:border-accent">
          Create an account
        </Link>
      </div>
    </div>
  );
}
