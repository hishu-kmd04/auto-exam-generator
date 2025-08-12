import os
import subprocess
import time
import json
import sys

# ====== CONFIG ======
INPUT_DOCX = "input/base_questions.docx"
PARSED_JSON = "output/parsed.json"
QUESTIONS_JSON = "output/questions.json"
IMAGES_DIR = "output/images"
FINAL_DOCX = "output/result.docx"

# ANSI Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"

def run_step(description, command, skip_if_exists=None):
    """Run a shell command with timing and optional skipping."""
    if skip_if_exists and os.path.exists(skip_if_exists):
        choice = input(f"{YELLOW}⚠ {skip_if_exists} already exists. Skip {description}? (y/n): {RESET}").strip().lower()
        if choice == "y":
            print(f"{CYAN}⏭ Skipped: {description}{RESET}")
            return True

    print(f"{CYAN}▶ Starting: {description}{RESET}")
    start = time.time()
    result = subprocess.run(command, shell=True)
    elapsed = time.time() - start

    if result.returncode != 0:
        print(f"{RED}✖ Error during: {description}{RESET}")
        sys.exit(1)

    print(f"{GREEN}✔ Completed: {description} in {elapsed:.2f}s{RESET}")
    return True

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def safe_remove(path):
    """Remove file safely."""
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"{YELLOW}⚠ Removed old file: {path}{RESET}")
        except PermissionError:
            print(f"{RED}✖ Please close the file before running again: {path}{RESET}")
            sys.exit(1)

def summary_report():
    print(f"\n{GREEN}====== SUMMARY ======{RESET}")
    if os.path.exists(PARSED_JSON):
        with open(PARSED_JSON, "r", encoding="utf-8") as f:
            parsed_data = json.load(f)
            print(f"{CYAN}Parsed Questions:{RESET} {len(parsed_data.get('questions', []))}")
    if os.path.exists(QUESTIONS_JSON):
        with open(QUESTIONS_JSON, "r", encoding="utf-8") as f:
            q_data = json.load(f)
            print(f"{CYAN}Generated Questions:{RESET} {len(q_data.get('questions', []))}")
    if os.path.exists(IMAGES_DIR):
        images = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        print(f"{CYAN}Generated Images:{RESET} {len(images)}")
    if os.path.exists(FINAL_DOCX):
        print(f"{CYAN}Final Document:{RESET} {FINAL_DOCX}")
    print(f"{GREEN}======================{RESET}\n")

if __name__ == "__main__":
    ensure_dir("output")

    # Step 1: Parse DOCX
    run_step(
        "Parsing base_questions.docx",
        f'python src/parse_doc.py --input "{INPUT_DOCX}" --out "{PARSED_JSON}"',
        skip_if_exists=PARSED_JSON
    )

    # Step 2: Generate Questions
    run_step(
        "Generating questions.json (template mode)",
        f'python src/generator.py --mode template --input "{PARSED_JSON}" --out "{QUESTIONS_JSON}"',
        skip_if_exists=QUESTIONS_JSON
    )

    # Step 3: Generate Images
    ensure_dir(IMAGES_DIR)
    run_step(
        "Generating images from questions.json",
        f'python src/image_gen.py --input "{QUESTIONS_JSON}" --out "{IMAGES_DIR}"',
        skip_if_exists=None  # Always re-run in case images changed
    )

    # Step 4: Build Final DOCX
    safe_remove(FINAL_DOCX)
    run_step(
        "Building final result.docx",
        f'python src/build_doc.py --input "{QUESTIONS_JSON}" --images "{IMAGES_DIR}" --out "{FINAL_DOCX}"',
        skip_if_exists=None
    )

    # Show summary
    summary_report()
