import docx
import pandas as pd
import os

import PyPDF2

def read_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

def read_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def read_xlsx(file_path):
    xl = pd.ExcelFile(file_path)
    combined_text = []
    for sheet_name in xl.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        combined_text.append(f"--- Sheet: {sheet_name} ---\n{df.to_string()}")
    return "\n\n".join(combined_text)

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

def get_example_paths(data_dir):
    out = []
    for item in os.listdir(data_dir):
        item_path = os.path.join(data_dir, item)
        if os.path.isdir(item_path) and item.startswith("Example"):
            input_dir = os.path.join(item_path, "input")
            output_dir = os.path.join(item_path, "output")
            input_files = []
            output_files = []
            if os.path.exists(input_dir):
                for f in os.listdir(input_dir):
                    input_files.append(os.path.join(input_dir, f))
            if os.path.exists(output_dir):
                for f in os.listdir(output_dir):
                    output_files.append(os.path.join(output_dir, f))
            out.append({
                "name": item,
                "input_files": input_files,
                "output_files": output_files
            })
    return out
