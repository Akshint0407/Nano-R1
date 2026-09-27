"""GRPO fine-tuning of Qwen2.5-3B-Instruct on GSM8K.

This is the original nano_r1_model.py logic, unchanged in substance,
reorganized so it can be run as a script:

    python -m train.train_grpo --max-steps 150 --output-dir grpo_saved_lora

The resulting adapter directory is what apps/inference/app/model.py loads
via LORA_ADAPTER_PATH.
"""

import argparse
import re

from datasets import Dataset, load_dataset

SYSTEM_PROMPT = """
Respond in the following format:
<reasoning>
...
</reasoning>
<answer>
...
</answer>
"""

XML_COT_FORMAT = """\
<reasoning>
{reasoning}
</reasoning>
<answer>
{answer}
</answer>
"""


def extract_xml_answer(text: str) -> str:
    answer = text.split("<answer>")[-1]
    answer = answer.split("</answer>")[0]
    return answer.strip()


def extract_hash_answer(text: str) -> str | None:
    if "####" not in text:
        return None
    return text.split("####")[1].strip()


def get_gsm8k_questions(split: str = "train") -> Dataset:
    data = load_dataset("openai/gsm8k", "main")[split]
    data = data.map(
        lambda x: {
            "prompt": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": x["question"]},
            ],
            "answer": extract_hash_answer(x["answer"]),
        }
    )
    return data


# --- Reward functions (unchanged from the original script) ---

def correctness_reward_func(prompts, completions, answer, **kwargs) -> list[float]:
    responses = [completion[0]["content"] for completion in completions]
    extracted_responses = [extract_xml_answer(r) for r in responses]
    return [2.0 if r == a else 0.0 for r, a in zip(extracted_responses, answer)]


def int_reward_func(completions, **kwargs) -> list[float]:
    responses = [completion[0]["content"] for completion in completions]
    extracted_responses = [extract_xml_answer(r) for r in responses]
    return [0.5 if r.isdigit() else 0.0 for r in extracted_responses]


def strict_format_reward_func(completions, **kwargs) -> list[float]:
    pattern = r"^<reasoning>\n.*?\n</reasoning>\n<answer>\n.*?\n</answer>\n$"
    responses = [completion[0]["content"] for completion in completions]
    matches = [re.match(pattern, r) for r in responses]
    return [0.5 if match else 0.0 for match in matches]


def soft_format_reward_func(completions, **kwargs) -> list[float]:
    pattern = r"<reasoning>.*?</reasoning>\s*<answer>.*?</answer>"
    responses = [completion[0]["content"] for completion in completions]
    matches = [re.match(pattern, r) for r in responses]
    return [0.5 if match else 0.0 for match in matches]


def count_xml(text) -> float:
    count = 0.0
    if text.count("<reasoning>\n") == 1:
        count += 0.125
    if text.count("\n</reasoning>\n") == 1:
        count += 0.125
    if text.count("\n<answer>\n") == 1:
        count += 0.125
        count -= len(text.split("\n</answer>\n")[-1]) * 0.001
    if text.count("\n</answer>") == 1:
        count += 0.125
        count -= (len(text.split("\n</answer>")[-1]) - 1) * 0.001
    return count


def xmlcount_reward_func(completions, **kwargs) -> list[float]:
    contents = [completion[0]["content"] for completion in completions]
    return [count_xml(c) for c in contents]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", default="Qwen/Qwen2.5-3B-Instruct")
    parser.add_argument("--max-seq-length", type=int, default=1024)
    parser.add_argument("--lora-rank", type=int, default=64)
    parser.add_argument("--max-steps", type=int, default=150)
    parser.add_argument("--output-dir", default="grpo_saved_lora")
    parser.add_argument("--push-to-hub", default=None, help="e.g. your-username/grpo-lora-model")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Imported lazily: these are heavy, GPU-only dependencies, and importing them
    # at module level would break `--help` and any non-GPU tooling that imports
    # this module for its constants/reward functions.
    import torch
    from trl import GRPOConfig, GRPOTrainer
    from unsloth import FastLanguageModel, PatchFastRL, is_bfloat16_supported

    PatchFastRL("GRPO", FastLanguageModel)

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model_name,
        max_seq_length=args.max_seq_length,
        load_in_4bit=True,
        fast_inference=True,
        max_lora_rank=args.lora_rank,
        gpu_memory_utilization=0.5,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=args.lora_rank,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        lora_alpha=args.lora_rank,
        use_gradient_checkpointing="unsloth",
        random_state=3407,
    )

    dataset = get_gsm8k_questions()

    training_args = GRPOConfig(
        use_vllm=True,
        learning_rate=5e-6,
        adam_beta1=0.9,
        adam_beta2=0.99,
        weight_decay=0.1,
        warmup_ratio=0.1,
        lr_scheduler_type="cosine",
        optim="adamw_8bit",
        logging_steps=1,
        bf16=is_bfloat16_supported(),
        fp16=not is_bfloat16_supported(),
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1,
        num_generations=8,
        max_prompt_length=256,
        max_completion_length=200,
        max_steps=args.max_steps,
        save_steps=args.max_steps,
        max_grad_norm=0.1,
        report_to="none",
        output_dir="outputs",
    )

    trainer = GRPOTrainer(
        model=model,
        processing_class=tokenizer,
        reward_funcs=[
            xmlcount_reward_func,
            soft_format_reward_func,
            strict_format_reward_func,
            int_reward_func,
            correctness_reward_func,
        ],
        args=training_args,
        train_dataset=dataset,
    )
    trainer.train()

    model.save_lora(args.output_dir)
    print(f"Saved LoRA adapter to {args.output_dir}")

    if args.push_to_hub:
        model.push_to_hub(args.push_to_hub)
        tokenizer.push_to_hub(args.push_to_hub)
        print(f"Pushed to hub: {args.push_to_hub}")


if __name__ == "__main__":
    main()
