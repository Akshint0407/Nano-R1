# Nano-R1
# Fine-Tuning Qwen2.5-3B-Instruct with GRPO for Mathematical Reasoning

![Python](https://img.shields.io/badge/python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-Apache_2.0-red?style=for-the-badge&logo=apache&logoColor=white)
![Hugging Face](https://img.shields.io/badge/Hugging_Face-Deployed-yellow?style=for-the-badge&logo=huggingface&logoColor=yellow)


This repository contains code for fine-tuning the **Qwen2.5-3B-Instruct** model using **GRPO (Generalized Reward Policy Optimization)** on the **GSM8K** dataset. The goal is to improve the model's ability to solve mathematical reasoning problems through reinforcement learning with custom reward functions.

## 🚀 Deployment

The fine-tuned model is deployed on Hugging Face and can be accessed here:  
🔗 **[Hugging Face Model Hub](https://huggingface.co/Akshint47/Nano_R1_Model)** 

You can interact with the model directly or integrate it into your projects using the Hugging Face `transformers` library.

## ✨ Features

- **Efficient Fine-Tuning**: Uses Unsloth and LoRA for faster training with reduced GPU memory.
- **Custom Reward Engineering**:
  - Correctness (answer accuracy)
  - Format adherence (XML-structured reasoning)
  - Integer validation
  - XML completeness scoring
- **vLLM Integration**: Accelerates inference during training.
- **GSM8K Focus**: Optimized for mathematical word problems.

## 📋 Requirements

```bash
# Core packages
pip install unsloth vllm trl datasets
```
## Additional dependencies
```bash
pip install torch transformers sentence piece accelerate
```

## Hardware Recommendations:

GPU with ≥16GB VRAM (e.g., NVIDIA T4, A10G, or better)

Recommended: CUDA 12.x and cuDNN 8.6+

## 🛠️ Setup & Usage
Install dependencies:

```bash
git clone https://github.com/Akshint0407/Nano-R1.git
cd Nano-R1
pip install -r requirements.txt
```

Run the notebook:

```bash
jupyter notebook nano_r1_model.ipynb
```
Key Configuration (in notebook):
```python```
```
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "Qwen/Qwen2.5-3B-Instruct",
    max_seq_length = 1024,
    load_in_4bit = True,
    max_lora_rank = 64
)
```

## 📊 Training Process
The GRPO trainer optimizes for:

-  Reward Maximization: Combined score from all reward functions
  
-  KL Regularization: Maintains policy stability
  
-  Efficiency: Processes 8 generations per batch
  
-  Training Progress (replace with actual metrics screenshot)

## 📜 License  
This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for full terms.  

## 🙏 Acknowledgments
- Unsloth for optimization tools

- Hugging Face for models and datasets

- vLLM for fast inference

- OpenAI for the GSM8K dataset

## 🤝 Contributing
- Contributions are welcome! Please open an issue or PR for:

- Bug fixes

- Additional reward functions

- Performance improvements

=======

Qwen2.5-3B-Instruct, fine-tuned with **GRPO** on **GSM8K** for math reasoning — now wrapped
in a full-stack app instead of a Colab notebook. Every answer comes with the reasoning
trace the model produced, and users can rate it right/wrong, which is stored as replay
data for a future GRPO reward pass.

## Architecture

```
apps/
├── web/         Next.js (TypeScript, Tailwind) — chat UI, auth, history
├── api/         FastAPI + PostgreSQL — accounts, conversations, feedback, orchestration
└── inference/   FastAPI + vLLM/Unsloth — loads the base model + GRPO LoRA adapter, generates
```

`web` never talks to `inference` directly — everything goes through `api`, which is what
writes to Postgres and enforces auth. `inference` is stateless and only knows about the
model.

## Quick start (Docker Compose)

Each app needs a `.env` file — copy the examples first:

```bash
cp apps/web/.env.example apps/web/.env
cp apps/api/.env.example apps/api/.env
cp apps/inference/.env.example apps/inference/.env
```

Then:

```bash
docker compose up --build
```

- Web: http://localhost:3000
- API: http://localhost:8000 (docs at `/docs`)
- Inference: http://localhost:8001

By default `inference` runs with `USE_STUB_MODEL=true`, so the whole stack works without a
GPU — it returns a canned reasoning/answer pair instead of running the real model. That's
enough to build and test `web` and `api` end to end.

## Running the real model

The stub is only for local dev without a GPU. To serve the actual fine-tuned model:

1. Train (or reuse your existing) LoRA adapter:
   ```bash
   cd apps/inference
   pip install -r requirements.txt
   python -m train.train_grpo --max-steps 150 --output-dir grpo_saved_lora
   ```
2. Point the inference service at it and turn off the stub, in `apps/inference/.env`:
   ```
   LORA_ADAPTER_PATH=grpo_saved_lora
   USE_STUB_MODEL=false
   ```
3. Run `apps/inference` on a machine with a GPU (≥16GB VRAM) — either directly
   (`uvicorn app.main:app`) or via its Dockerfile with `--build-arg INSTALL_GPU_DEPS=true`
   on a CUDA base image.

## Local development (without Docker)

**inference** (needs a GPU for real generation, or leave `USE_STUB_MODEL=true`):
```bash
cd apps/inference
pip install fastapi "uvicorn[standard]" pydantic
uvicorn app.main:app --reload --port 8001
```

**api** (needs Postgres running — `docker compose up postgres` is the easy way):
```bash
cd apps/api
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**web**:
```bash
cd apps/web
npm install
npm run dev
```

## Data model

- `users` — accounts (email + hashed password)
- `conversations` — one per problem-solving session
- `messages` — each question + the model's `reasoning` and `answer`
- `feedback` — a user's rating (+1 / -1) on one message, the signal that can seed a future
  reward pass on top of the existing GRPO reward functions

## What's unchanged from the original script

`apps/inference/train/train_grpo.py` is the original `nano_r1_model.py` logic, reorganized
into a callable script — same system prompt, same reward functions
(`correctness_reward_func`, `int_reward_func`, `strict_format_reward_func`,
`soft_format_reward_func`, `xmlcount_reward_func`), same GRPO config. A LoRA adapter you've
already trained with the old script drops straight into `LORA_ADAPTER_PATH` and works with
`apps/inference` unchanged.
>>>>>>> 9720a06 (Add my files and changes)
