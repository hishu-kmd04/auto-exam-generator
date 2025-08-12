# generator.py
"""
Two generation modes:
 - 'llm' : uses OpenAI ChatCompletion to generate questions in the required format
 - 'template' : deterministic, offline transformations to create similar questions

Usage:
  python generator.py --mode template --input output/parsed.json --out output/questions.json
  python generator.py --mode llm --input output/parsed.json --out output/questions.json
"""
import argparse
import os
import json
import random
from utils import load_json, save_json
from typing import Dict

# optionally import openai if llm mode used
try:
    import openai
except Exception:
    openai = None

def template_transform_uniform(q_text):
    """
    Example: transform the uniform color-of-shirt/pants question to a new variant.
    This will detect shirt/pants lists and shuffle / modify counts.
    """
    # Basic heuristic: if the text mentions "uniform" and a table of colors, create a new similar problem
    # We produce an output dict in target format.
    title = "Uniform Color Combinations"
    description = "Compute the number of different uniform combinations from given options."
    # Create a new variant: change items (e.g. shirts: 4 colors, pants: 3 colors)
    shirts = ["Blue", "Green", "Gray", "White"]
    pants = ["Black", "Khaki", "Navy"]
    # create options and answer
    total = len(shirts) * len(pants)
    options = [str(total), str(total-1), str(total+1), str(total*2)]
    correct = str(total)
    question = f"Each student must wear one shirt and one pair of pants. There are {len(shirts)} shirt colors: {', '.join(shirts)} and {len(pants)} pants colors: {', '.join(pants)}. How many different uniforms are possible?"
    out = {
        "title": title,
        "description": description,
        "question": question,
        "instruction": "Select the best answer.",
        "difficulty": "easy",
        "order": 1,
        "options": options,
        "correct_answer": correct,
        "explanation": f"Number of combinations = {len(shirts)} * {len(pants)} = {total}.",
        "subject": "Quantitative Math",
        "unit": "Numbers and Operations",
        "topic": "Computation with Whole Numbers",
        "plusmarks": 1
    }
    return out

def template_transform_packed_balls(q_text):
    # Produce a variant: change radius or number of balls arrangement
    title = "Packed Spheres in a Rectangular Box"
    description = "Find the dimensions of a rectangular box tightly holding a pack of spheres."
    radius = 3  # cm
    # Suppose 6 balls arranged 2 x 3 grid => width = 2*radius*2? We'll create an option set
    # We'll produce numeric choices similar to original style:
    opts = [
        f"{2} \\times {3} \\times {6}",
        f"{2*radius} \\times {4*radius} \\times {6*radius}",
        f"{2} \\times {4} \\times {6}",
        f"{4*radius} \\times {8*radius} \\times {12*radius}",
        f"{6*radius} \\times {8*radius} \\times {12*radius}",
    ]
    # Create a clear question with LaTeX preservation.
    question = (
        "The top view of a rectangular package of 6 tightly packed balls is shown. "
        f"If each ball has a radius of {radius} centimeters, which of the following are closest to the dimensions, in centimeters, of the rectangular package?"
    )
    out = {
        "title": title,
        "description": description,
        "question": question,
        "instruction": "Choose the best option.",
        "difficulty": "moderate",
        "order": 2,
        "options": opts,
        "correct_answer": opts[1],
        "explanation": "Constructed variant; the arrangement chosen gives the corresponding bounding box dimensions.",
        "subject": "Quantitative Math",
        "unit": "Geometry and Measurement",
        "topic": "Packing / Coordinate Geometry",
        "plusmarks": 1
    }
    return out

def generate_template(parsed):
    questions = []
    raw_list = parsed.get("questions", [])
    # For each base question, map to a template generator
    for i, q in enumerate(raw_list):
        lower = q.lower()
        if "uniform" in lower or "shirt" in lower:
            qnew = template_transform_uniform(q)
            qnew["order"] = i+1
            questions.append(qnew)
        elif "balls" in lower or "radius" in lower or "pack" in lower:
            qnew = template_transform_packed_balls(q)
            qnew["order"] = i+1
            questions.append(qnew)
        else:
            # fallback: simple paraphrase + options
            title = f"Autogen Question {i+1}"
            qnew = {
                "title": title,
                "description": "Auto-generated problem from template fallback.",
                "question": q[:600],
                "instruction": "Answer the following.",
                "difficulty": "moderate",
                "order": i+1,
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Fallback explanation.",
                "subject": "Quantitative Math",
                "unit": "Problem Solving",
                "topic": "Word Problems",
                "plusmarks": 1
            }
            questions.append(qnew)
    return {"questions": questions}

# --- LLM mode ---
def generate_with_openai(parsed, openai_api_key: str, model="gpt-4o-mini"):
    if openai is None:
        raise RuntimeError("openai package not installed. pip install openai")
    openai.api_key = openai_api_key

    questions_out = []
    for i, base in enumerate(parsed.get("questions", [])):
        prompt = (
            "You are a helpful question-writer. Produce ONE new multiple-choice math question "
            "that is similar to this base problem while preserving any LaTeX math using $...$ or $$...$$. "
            "Also produce 4 options and mark which is correct. Output strictly as JSON with fields:\n"
            '{"title","description","question","instruction","difficulty","order","options","correct_answer","explanation","subject","unit","topic","plusmarks"}\n'
            "Base problem (do not include original in output):\n"
            + base[:1200]
        )
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700
        )
        # parse assistant message as JSON
        content = resp["choices"][0]["message"]["content"]
        try:
            obj = json.loads(content)
        except Exception:
            # if assistant included markdown or stray text, try to extract JSON block
            import re
            m = re.search(r'\{[\s\S]*\}$', content)
            if m:
                obj = json.loads(m.group(0))
            else:
                raise
        obj["order"] = i+1
        questions_out.append(obj)
    return {"questions": questions_out}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["template", "llm"], default="template")
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--openai_key", default=os.environ.get("OPENAI_API_KEY"))
    args = parser.parse_args()

    parsed = load_json(args.input)
    if args.mode == "template":
        out = generate_template(parsed)
    else:
        if not args.openai_key:
            raise RuntimeError("openai_key required for llm mode")
        out = generate_with_openai(parsed, args.openai_key)
        print("Questions generated:", out)
    save_json(out, args.out)
    print("Generated questions saved to", args.out)

if __name__ == "__main__":
    main()
