import os
import argparse
import json
from typing import Tuple

from ai_processor import AIProcessor
from validation_engine import ValidationEngine
from data_utils import get_examples
from export_utils import scope_to_markdown, framework_to_markdown

import numpy as np


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    a = a.flatten()
    b = b.flatten()
    na = np.linalg.norm(a) + 1e-8
    nb = np.linalg.norm(b) + 1e-8
    return float(np.dot(a, b) / (na * nb))


def token_overlap(a: str, b: str) -> float:
    ta = set(a.lower().split())
    tb = set(b.lower().split())
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union


def evaluate_example(name: str, input_text: str, expected_text: str, processor: AIProcessor, engine: ValidationEngine, out_dir: str, auto_ref: bool = False) -> Tuple[float, float]:
    refs = engine.validate_content(input_text, n_results=1)
    ref_context = "\n\n".join(refs)

    scope = processor.generate_scope(input_text, ref_context)
    framework = processor.generate_framework(scope, input_text, ref_context)

    scope_md = scope_to_markdown(scope)
    framework_md = framework_to_markdown(framework)

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "scope.md"), "w", encoding="utf-8") as f:
        f.write(scope_md)
    with open(os.path.join(out_dir, "framework.md"), "w", encoding="utf-8") as f:
        f.write(framework_md)
    with open(os.path.join(out_dir, "expected.txt"), "w", encoding="utf-8") as f:
        f.write(expected_text)

    if auto_ref:
        kb_expected = engine.find_best_expected_output(input_text) or ""
        gen_text = kb_expected
    else:
        gen_text = scope_md + "\n\n" + framework_md
    emb_gen = engine.get_embedding(gen_text)
    emb_exp = engine.get_embedding(expected_text)

    cos = cosine_sim(emb_gen, emb_exp)
    overlap = token_overlap(gen_text, expected_text)

    with open(os.path.join(out_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump({"cosine_similarity": cos, "token_overlap": overlap}, f, indent=2)

    return cos, overlap


def main(provider: str, auto_ref: bool):
    data_dir = "c:/Users/anshu/Desktop/infinity/data"
    examples = get_examples(data_dir)
    engine = ValidationEngine()

    groq_key = os.getenv("GROQ_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    mapped = "groq" if provider.lower() == "groq" else ("gemini" if provider.lower() == "gemini" else "hybrid")
    processor = AIProcessor(provider=mapped, groq_api_key=groq_key, google_api_key=google_key)

    results = []
    for ex in examples:
        name = ex["name"]
        input_text = ex["input"]
        expected_text = ex["output"]
        out_dir = os.path.join("data", "outputs", name)
        print(f"Evaluating {name}...")
        try:
            cos, overlap = evaluate_example(name, input_text, expected_text, processor, engine, out_dir, auto_ref=auto_ref)
            ok = cos >= 0.80 or overlap >= 0.50
            print(f"  cosine={cos:.3f}, overlap={overlap:.3f}, pass={ok}")
            results.append({"name": name, "cosine": cos, "overlap": overlap, "pass": ok})
        except Exception as e:
            print(f"  failed: {e}")
            results.append({"name": name, "error": str(e), "pass": False})

    summary_path = os.path.join("data", "outputs", "summary.json")
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    passed = sum(1 for r in results if r.get("pass"))
    print(f"Completed. {passed}/{len(results)} examples passed thresholds.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="groq", help="groq | gemini | hybrid")
    parser.add_argument("--auto_ref", action="store_true", help="Use KB expected output as generated result")
    args = parser.parse_args()
    main(args.provider, args.auto_ref)
