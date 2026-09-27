import os
from functools import lru_cache


class Settings:
    """Runtime configuration for the inference service, all overridable via env vars."""

    base_model_name: str = os.getenv("BASE_MODEL_NAME", "Qwen/Qwen2.5-3B-Instruct")
    # Path or HF repo id of the GRPO LoRA adapter produced by train/train_grpo.py
    lora_adapter_path: str = os.getenv("LORA_ADAPTER_PATH", "grpo_saved_lora")
    max_seq_length: int = int(os.getenv("MAX_SEQ_LENGTH", "1024"))
    max_new_tokens: int = int(os.getenv("MAX_NEW_TOKENS", "512"))
    load_in_4bit: bool = os.getenv("LOAD_IN_4BIT", "true").lower() == "true"
    gpu_memory_utilization: float = float(os.getenv("GPU_MEMORY_UTILIZATION", "0.5"))
    # When true, the service loads the real model. When false (default off-GPU dev
    # boxes / CI), it returns a canned response so the rest of the stack is testable
    # without a GPU.
    use_stub_model: bool = os.getenv("USE_STUB_MODEL", "false").lower() == "true"
    # CPU-friendly path: run a quantized GGUF build via llama.cpp instead of the
    # GPU-only unsloth/vllm path. No CUDA required — this is what runs on a laptop.
    # Ignored if use_stub_model is true.
    use_llama_cpp: bool = os.getenv("USE_LLAMA_CPP", "false").lower() == "true"
    # HF repo id + filename of the GGUF build to download/cache locally (used only
    # when use_llama_cpp is true). Defaults to a small instruct model that's usable
    # on a CPU-only machine; swap for a 3B build if your machine can handle it.
    llama_cpp_repo_id: str = os.getenv("LLAMA_CPP_REPO_ID", "Qwen/Qwen2.5-1.5B-Instruct-GGUF")
    llama_cpp_filename: str = os.getenv("LLAMA_CPP_FILENAME", "qwen2.5-1.5b-instruct-q4_k_m.gguf")
    llama_cpp_n_ctx: int = int(os.getenv("LLAMA_CPP_N_CTX", "2048"))
    llama_cpp_n_threads: int = int(os.getenv("LLAMA_CPP_N_THREADS", str(os.cpu_count() or 4)))
    api_key: str | None = os.getenv("INFERENCE_API_KEY")  # shared secret with apps/api
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8001"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
