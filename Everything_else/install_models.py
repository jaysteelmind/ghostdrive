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
    # 🧠 Logic Expert - DarkIdol
    "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf":
        "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
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
