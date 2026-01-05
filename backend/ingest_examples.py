import os
from data_utils import get_examples
from validation_engine import ValidationEngine

import argparse

def populate_db(api_key: str):
    data_dir = "c:/Users/anshu/Desktop/infinity/data"
    engine = ValidationEngine(api_key=api_key)
    
    examples = get_examples(data_dir)
    print(f"Found {len(examples)} examples.")
    
    for ex in examples:
        print(f"Indexing {ex['name']}...")
        content = f"INPUT:\n{ex['input']}\n\nEXPECTED_OUTPUT:\n{ex['output']}"
        engine.add_reference_doc(
            doc_id=ex['name'],
            content=content,
            metadata={"type": "example", "client": ex['name']}
        )
    print("Indexing complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", help="Google API Key (optional if in .env)")
    args = parser.parse_args()
    populate_db(args.api_key)
