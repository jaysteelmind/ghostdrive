# ============================================================
#   model_registry.py — Sequential Model Loader (No Caching)
# ============================================================

import os
import gc
import yaml
import time
from llama_cpp import Llama

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_YAML_PATH = os.path.join(SCRIPT_DIR, "models", "models.yaml")

with open(MODELS_YAML_PATH, "r") as f:
    MODEL_CONFIGS = yaml.safe_load(f)["models"]

# Active model pointer so we can unload safely
ACTIVE_LLM = None


# ------------------------------------------------------------
# 1. Fetch model config from YAML
# ------------------------------------------------------------
def get_model_config(model_id):
    if model_id not in MODEL_CONFIGS:
        raise ValueError(f"Model ID '{model_id}' not found in models.yaml")
    return MODEL_CONFIGS[model_id]


# ------------------------------------------------------------
# 2. Unload previous model (VRAM + RAM + context)
# ------------------------------------------------------------
def unload_previous_model():
    """Close the currently loaded llama model and free VRAM."""
    global ACTIVE_LLM

    if ACTIVE_LLM is not None:
        try:
            ACTIVE_LLM.close()
            print("[Jynx] Previous model successfully unloaded.")
        except Exception as e:
            print(f"[Jynx] Warning: error while closing model: {e}")
        ACTIVE_LLM = None

    collected = gc.collect()
    print(f"[Jynx] Garbage collected: {collected} objects")
    time.sleep(0.05)




# ------------------------------------------------------------
# 3. Prompt formatting helpers
# ------------------------------------------------------------
def format_prompt(prompt: str, model_id: str, system_prompt: str = "You are a helpful assistant.") -> str:
    """
    Clean prompt format — avoids infinite Q&A loops and trigger words.
    """

    model = model_id.lower()

    # QWEN = ChatML
    if "qwen" in model:
        return (
            f"<|im_start|>system\n{system_prompt.strip()}\n<|im_end|>\n"
            f"<|im_start|>user\n{prompt.strip()}\n<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

    # LLAMA / MISTRAL = OpenInstruct format
    if "mistral" in model or "llama" in model or "wizard" in model:
        return (
            f"<s>[INST] {system_prompt.strip()} [/INST]\n"
            f"[INST] {prompt.strip()} [/INST]"
        )

    # Fallback: NO "Answer:"
    return f"{system_prompt.strip()}\n\n{prompt.strip()}"




def get_stop_sequence(model_id):
    """
    Universal safety stop sequences.
    Prevents:
    - multi‑turn hallucination ("User:", "Assistant:")
    - infinite Q&A loops
    - repeating system tags
    - runaway streaming
    """

    base_stops = [
        "</s>",
        "<|im_end|>",
        
        # Prevent hallucinated turns
        "User:",
        "user:",
        "Assistant:",
        "assistant:",
        "System:",
        "system:",
        "Human:",
        "human:",
        "AI:",
        "ai:",

        # Prevent Summarizer Hallucinations
        "User Prompt:",
        "***Task Summary***",
        "***Experts***",
        
        # Prevent new turn introductions
        "\nUser:",
        "\nAssistant:",
        "\nSystem:",
        "\nHuman:",
        "\nAI:",
    ]

    model = model_id.lower()

    # Qwen is ChatML → also break on special tokens
    if "qwen" in model:
        base_stops.extend([
            "<|im_start|>",
        ])

    # Llama/Mistral usually need EOS explicitly
    if "llama" in model or "mistral" in model:
        base_stops.extend([
            "[INST]",
            "</INST>",
        ])

    # Remove duplicates, preserve order
    seen = set()
    cleaned = []
    for s in base_stops:
        if s not in seen:
            cleaned.append(s)
            seen.add(s)

    return cleaned



# ------------------------------------------------------------
# 4. Load model SEQUENTIALLY with zero caching
# ------------------------------------------------------------
def load_model_from_config(model_id):
    """Load a model fresh, after unloading any previous model."""
    global ACTIVE_LLM

    config = get_model_config(model_id)
    abs_path = os.path.join(SCRIPT_DIR, "models", config["path"])


    print(f"[Jynx] Loading {model_id} from: {abs_path}")

    # 🔥 Completely unload any existing model first
    unload_previous_model()

    # Load fresh model
    try:
        llm = Llama(
            model_path=abs_path,
            n_ctx=config.get("max_tokens", 2048),
            n_threads=config.get("n_threads", os.cpu_count()),
            n_batch=128,
            n_gpu_layers=config.get("n_gpu_layers", -1),
            use_mlock=config.get("use_mlock", False),
        )
    except Exception as e:
        print(f"[Jynx] Failed to load model '{model_id}': {e}")
        raise RuntimeError(f"Failed to load model from file: {abs_path}") from e

    # Store active model reference
    ACTIVE_LLM = llm

    # --------------------------------------------------------
    # 5. Unified call() wrapper for inference
    # --------------------------------------------------------
    def call(prompt, stream_override=None, max_tokens=None, temperature=None, stop=None):
        stream_enabled = config.get("stream", False) if stream_override is None else stream_override
        is_qwen = "qwen" in model_id.lower()

        # ---------------- QWEN MODELS -----------------
        if is_qwen:
            system_prompt = config.get("system_prompt", "You are a helpful assistant.")
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]

            chat_args = {
                "messages": messages,
                "temperature": temperature or config.get("temperature", 0.7),
                "max_tokens": max_tokens or config.get("max_tokens", 256),
                "stop": stop or get_stop_sequence(model_id),
            }

            try:
                return llm.create_chat_completion(stream=stream_enabled, **chat_args)
            except Exception as e:
                print(f"[Jynx] Error during Qwen inference: {e}")
                return iter([])

        # ---------------- MISTRAL / LLAMA MODELS -----------------
        formatted_prompt = format_prompt(
            prompt,
            model_id=model_id,
            system_prompt=config.get("system_prompt", "You are a helpful assistant.")
        )

        args = {
            "prompt": formatted_prompt,
            "temperature": temperature or config.get("temperature", 0.7),
            "max_tokens": max_tokens or config.get("max_tokens", 256),
            "stop": stop or get_stop_sequence(model_id),
        }

        try:
            return llm(**args, stream=stream_enabled)
        except Exception as e:
            print(f"[Jynx] Error during inference for model {model_id}: {e}")
            return iter([])

    return call, config
