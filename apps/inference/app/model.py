"""Thin wrapper around the GRPO-tuned Qwen2.5 model for serving.

This reuses the exact system prompt and XML parsing from the original
nano_r1_model.py training script so a model trained with that script
produces output this service can parse correctly.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass

from .config import get_settings

logger = logging.getLogger("nano_r1.inference")

# --- Same contract the GRPO reward functions were trained against ---
SYSTEM_PROMPT = """
Respond in the following format:
<reasoning>
...
</reasoning>
<answer>
...
</answer>
"""


def extract_xml_answer(text: str) -> str:
    answer = text.split("<answer>")[-1]
    answer = answer.split("</answer>")[0]
    return answer.strip()


def extract_xml_reasoning(text: str) -> str:
    if "<reasoning>" not in text:
        return ""
    reasoning = text.split("<reasoning>")[-1]
    reasoning = reasoning.split("</reasoning>")[0]
    return reasoning.strip()


@dataclass
class GenerationResult:
    raw_completion: str
    reasoning: str
    answer: str


class ModelRunner:
    """Loads the base model + LoRA adapter once and serves generations.

    Lazy-loaded and guarded by a lock so concurrent requests during the
    (slow) first load don't each try to load the model.
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._model = None
        self._tokenizer = None
        self._lock = threading.Lock()
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def _load(self) -> None:
        if self._loaded:
            return
        with self._lock:
            if self._loaded:  # re-check inside the lock
                return

            if self._settings.use_stub_model:
                logger.warning("USE_STUB_MODEL=true — serving canned responses, no GPU/model loaded.")
                self._loaded = True
                return

            if self._settings.use_llama_cpp:
                logger.info(
                    "USE_LLAMA_CPP=true — loading %s/%s via llama.cpp (CPU, no GPU/LoRA adapter).",
                    self._settings.llama_cpp_repo_id,
                    self._settings.llama_cpp_filename,
                )
                from llama_cpp import Llama  # imported lazily: not needed on the GPU path

                self._model = Llama.from_pretrained(
                    repo_id=self._settings.llama_cpp_repo_id,
                    filename=self._settings.llama_cpp_filename,
                    n_ctx=self._settings.llama_cpp_n_ctx,
                    n_threads=self._settings.llama_cpp_n_threads,
                    verbose=False,
                )
                self._loaded = True
                logger.info("llama.cpp model loaded (CPU).")
                return

            logger.info("Loading base model %s ...", self._settings.base_model_name)
            from unsloth import FastLanguageModel  # imported lazily: heavy + GPU-only

            self._model, self._tokenizer = FastLanguageModel.from_pretrained(
                model_name=self._settings.base_model_name,
                max_seq_length=self._settings.max_seq_length,
                load_in_4bit=self._settings.load_in_4bit,
                fast_inference=True,
                gpu_memory_utilization=self._settings.gpu_memory_utilization,
            )
            self._model.load_lora(self._settings.lora_adapter_path)
            FastLanguageModel.for_inference(self._model)
            self._loaded = True
            logger.info("Model + LoRA adapter loaded.")

    def generate(self, question: str, max_new_tokens: int | None = None) -> GenerationResult:
        self._load()

        if self._settings.use_stub_model:
            return self._stub_generate(question)

        if self._settings.use_llama_cpp:
            return self._llama_cpp_generate(question, max_new_tokens)

        max_new_tokens = max_new_tokens or self._settings.max_new_tokens
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]
        prompt = self._tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        from vllm import SamplingParams

        sampling_params = SamplingParams(
            temperature=0.7,
            top_p=0.9,
            max_tokens=max_new_tokens,
        )
        output = self._model.fast_generate(
            [prompt],
            sampling_params=sampling_params,
            lora_request=self._model.load_lora(self._settings.lora_adapter_path),
        )
        completion = output[0].outputs[0].text
        return GenerationResult(
            raw_completion=completion,
            reasoning=extract_xml_reasoning(completion),
            answer=extract_xml_answer(completion),
        )

    def _llama_cpp_generate(self, question: str, max_new_tokens: int | None) -> GenerationResult:
        """CPU path via llama.cpp. This is a plain (non-GRPO-tuned) instruct model, so
        it follows the <reasoning>/<answer> format because it's a decent instruction
        follower, not because it was RL-trained on it like the LoRA adapter path."""
        max_new_tokens = max_new_tokens or self._settings.max_new_tokens
        output = self._model.create_chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            max_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.9,
        )
        completion = output["choices"][0]["message"]["content"] or ""
        return GenerationResult(
            raw_completion=completion,
            reasoning=extract_xml_reasoning(completion),
            answer=extract_xml_answer(completion),
        )

    @staticmethod
    def _stub_generate(question: str) -> GenerationResult:
        """Deterministic canned output so apps/api and apps/web are testable without a GPU."""
        time.sleep(0.3)
        reasoning = f"(stub) Working through: {question[:120]}"
        answer = "42"
        raw = f"<reasoning>\n{reasoning}\n</reasoning>\n<answer>\n{answer}\n</answer>\n"
        return GenerationResult(raw_completion=raw, reasoning=reasoning, answer=answer)


runner = ModelRunner()
