import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
import bitsandbytes as bnb

PATH = "C:/Users/Arpit/Desktop/samsung/LLMs-Perplexity/llama-3.2-1b"
tokenizer = AutoTokenizer.from_pretrained(PATH, local_files_only=True, load_in_4bit=True)
model = AutoModelForCausalLM.from_pretrained(PATH, local_files_only=True)
test = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
# test = {"text":["Hello there how are you"]}
encodings = tokenizer("\n\n".join(test["text"]), return_tensors="pt")

print(model.config)

max_length = model.config.max_length
stride = 512
seq_len = encodings.input_ids.size(1)
device = "cpu"

nlls = []
prev_end_loc = 0
for begin_loc in tqdm(range(0, seq_len, stride)):
    end_loc = min(begin_loc + max_length, seq_len)
    trg_len = end_loc - prev_end_loc  # may be different from stride on last loop
    input_ids = encodings.input_ids[:, begin_loc:end_loc].to(device)
    target_ids = input_ids.clone()
    target_ids[:, :-trg_len] = -100

    with torch.no_grad():
        outputs = model(input_ids, labels=target_ids)

        # loss is calculated using CrossEntropyLoss which averages over valid labels
        # N.B. the model only calculates loss over trg_len - 1 labels, because it internally shifts the labels
        # to the left by 1.
        neg_log_likelihood = outputs.loss

    nlls.append(neg_log_likelihood)

    prev_end_loc = end_loc
    if end_loc == seq_len:
        break

ppl = torch.exp(torch.stack(nlls).mean())

print(f"The perplexity is :: {ppl}")