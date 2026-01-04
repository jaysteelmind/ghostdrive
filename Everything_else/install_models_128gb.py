import os
import time
import requests
from tqdm import tqdm

# Optional: Ensure PySide6 and core GUI wheels are installed
def ensure_pyside6_installed():
    try:
        import PySide6
        return
    except ImportError:
        print("📦 Installing PySide6 from local wheels...")
        wheels = [
            "dependencies\\pyside6-6.10.0-cp39-abi3-win_amd64.whl",
            "dependencies\\pyside6_addons-6.10.0-cp39-abi3-win_amd64.whl",
            "dependencies\\pyside6_essentials-6.10.0-cp39-abi3-win_amd64.whl"
        ]
        for wheel in wheels:
            os.system(f"pip install --no-deps --no-index \"{wheel}\"")

ensure_pyside6_installed()

# Target folder
model_dir = os.path.join("Everything_else", "models")
os.makedirs(model_dir, exist_ok=True)

# Hugging Face direct model download URLs and their target filenames
models = {
    # 🧠 Summarizer / Judge / Logic baseline
    "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf":
        "mistral-7b-instruct-v0.2.Q4_K_M.gguf",

    # 🧠 Emotion Expert - DeepSeek R1
    "https://huggingface.co/mradermacher/DeepSeek-R1-Distill-Llama-8B-GGUF/resolve/main/DeepSeek-R1-Distill-Llama-8B.Q4_K_M.gguf":
        "DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf", 

    # 🧠 Survival Expert - DarkIdol
    "https://huggingface.co/QuantFactory/DarkIdol-Llama-3.1-8B-Instruct-1.2-Uncensored-GGUF/resolve/main/DarkIdol-Llama-3.1-8B-Instruct-1.2-Uncensored.Q4_K_M.gguf":
        "DarkIdol-Llama-3.1-8B-Instruct-1.2-Uncensored.Q4_K_M.gguf",

    # 🧠 Math Expert - WizardMath
    "https://huggingface.co/mradermacher/WizardMath-7B-V1.0-i1-GGUF/resolve/main/WizardMath-7B-V1.0.i1-Q4_K_M.gguf":
        "WizardMath-7B-V1.0.i1-Q4_K_M.gguf",

    # 🧠 Coding Expert - Lily
    "https://huggingface.co/QuantFactory/Lily-Cybersecurity-7B-v0.2-GGUF/resolve/main/Lily-Cybersecurity-7B-v0.2.Q4_K_M.gguf":
        "Lily-Cybersecurity-7B-v0.2.Q4_K_M.gguf",

    # 🧠 Finance Expert
    "https://huggingface.co/mradermacher/SuryaNarayanan-BUSINESS-LAW-MATH-GGUF/resolve/main/SuryaNarayanan-BUSINESS-LAW-MATH.Q4_K_M.gguf":
        "SuryaNarayanan-BUSINESS-LAW-MATH.Q4_K_M.gguf",

    # 🧠 Medical Expert
    "https://huggingface.co/mradermacher/DeepSeek-R1-Distill-Llama-8B-Medical-Expert-GGUF/resolve/main/DeepSeek-R1-Distill-Llama-8B-Medical-Expert.Q4_K_M.gguf":
        "DeepSeek-R1-Distill-Llama-8B-Medical-Expert.Q4_K_M.gguf",

    # 🧠 Psychology Expert
    "https://huggingface.co/mradermacher/Llama-3-Mopeyfied-Psychology-8B-GGUF/resolve/main/Llama-3-Mopeyfied-Psychology-8B.Q4_K_M.gguf":
        "Llama-3-Mopeyfied-Psychology-8B.Q4_K_M.gguf",

    # 🧠 Mental Health Expert
    "https://huggingface.co/QuantFactory/Mental-Health-FineTuned-Mistral-7B-Instruct-v0.2-GGUF/resolve/main/Mental-Health-FineTuned-Mistral-7B-Instruct-v0.2.Q4_K_M.gguf":
        "Mental-Health-FineTuned-Mistral-7B-Instruct-v0.2.Q4_K_M.gguf",

    # 🧠 History Expert
    "https://huggingface.co/mradermacher/llama3-secret-history-GGUF/resolve/main/llama3-secret-history.Q4_K_M.gguf":
        "llama3-secret-history.Q4_K_M.gguf",

    # 🧠 Political Expert
    "https://huggingface.co/mradermacher/DevilsAdvocate-8B-GGUF/resolve/main/DevilsAdvocate-8B.Q4_K_M.gguf":
        "DevilsAdvocate-7B-i1.Q4_K_M.gguf",

    # 🧠 Sarcasm / People Expert
    "https://huggingface.co/mradermacher/Mistral-7B-Instruct-v0.1-Sarcasm-i1-GGUF/resolve/main/Mistral-7B-Instruct-v0.1-Sarcasm.i1-Q4_K_M.gguf":
        "Mistral-7B-Instruct-v0.1-Sarcasm-i1.Q4_K_M.gguf",

    # 🧠 Conspiracy Expert
    "https://huggingface.co/DavidAU/L3.2-Rogue-Creative-Instruct-Uncensored-Abliterated-7B-GGUF/resolve/main/L3.2-Rogue-Creative-Instruct-Uncensored-Abliterated-7B-D_AU-Q4_k_m.gguf":
        "L3.2-Rogue-Creative-Instruct-Uncensored-Abliterated-7B.Q4_K_M.gguf"
}

print("📦 Downloading models from Hugging Face...\n")


def download_with_progress(url, dest):
    """Download file with progress bar + retries."""
    CHUNK = 1024 * 1024  # 1 MB

    for attempt in range(1, 4):
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total = int(response.headers.get('content-length', 0))

            # Configure tqdm progress bar
            progress = tqdm(
                total=total,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=os.path.basename(dest),
                ascii=True,
            )

            with open(dest, "wb") as f:
                for chunk in response.iter_content(CHUNK):
                    if chunk:
                        f.write(chunk)
                        progress.update(len(chunk))

            progress.close()

            # Verify file was fully written
            if total != 0 and os.path.getsize(dest) < total:
                raise Exception("Downloaded file is incomplete.")

            return True

        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
            time.sleep(3)

    return False


# Main download loop
for url, filename in models.items():
    dest = os.path.join(model_dir, filename)

    if os.path.exists(dest):
        print(f"⏩ Skipping {filename}, already exists.\n")
        continue

    print(f"→ Downloading: {filename}")
    success = download_with_progress(url, dest)

    if success:
        print(f"✓ Saved to: {dest}\n")
    else:
        print(f"❌ Failed to download {filename} after 3 attempts.\n")

print("✅ All downloads attempted.")
