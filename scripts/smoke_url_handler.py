import json
from src.url_parsers.url_type_handler import handle_url

#code_url, dataset_url, model_url
models = {
    "0": ["", "", "https://huggingface.co/facebook/bart-base"],
    "1": ["https://github.com/huggingface/transformers", "", "https://huggingface.co/google-bert/bert-base-uncased"],
    "2": ["", "https://huggingface.co/datasets/glue", "https://huggingface.co/roberta-base"]
}

out = handle_url(models)
print(json.dumps(out, indent=2))
print("\nFilled links back into input (for sanity check):")
print(models)