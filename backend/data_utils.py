import docx
import pandas as pd
import os

def read_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

def read_xlsx(file_path):
    df = pd.read_excel(file_path)
    # Convert dataframe to a string representation for the LLM
    return df.to_string()

def get_examples(data_dir):
    examples = []
    for item in os.listdir(data_dir):
        item_path = os.path.join(data_dir, item)
        if os.path.isdir(item_path) and item.startswith("Example"):
            input_dir = os.path.join(item_path, "input")
            output_dir = os.path.join(item_path, "output")
            
            input_texts = []
            if os.path.exists(input_dir):
                for f in os.listdir(input_dir):
                    if f.endswith(".docx"):
                        input_texts.append(read_docx(os.path.join(input_dir, f)))
                    elif f.endswith(".txt"):
                        with open(os.path.join(input_dir, f), 'r') as file:
                            input_texts.append(file.read())
            
            output_texts = []
            if os.path.exists(output_dir):
                for f in os.listdir(output_dir):
                    if f.endswith(".xlsx"):
                        output_texts.append(read_xlsx(os.path.join(output_dir, f)))
                    elif f.endswith(".docx"):
                        output_texts.append(read_docx(os.path.join(output_dir, f)))
            
            examples.append({
                "name": item,
                "input": "\n---\n".join(input_texts),
                "output": "\n---\n".join(output_texts)
            })
    return examples
