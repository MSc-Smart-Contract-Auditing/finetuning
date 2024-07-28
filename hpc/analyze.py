from unsloth import FastLanguageModel
from datasets import load_dataset
import pandas as pd
from tqdm import tqdm
import csv
import re

model_name = "unsloth/llama-3-13b-Instruct-bnb-4bit"
model_alias = "0-shot-13b-instruct"

results = pd.read_csv(f"{model_alias}-descriptions.csv")
results.loc[results["real"].isnull(), "real"] = "There is no vulnearbility"

max_seq_length = 20  # Choose any! We auto support RoPE Scaling internally!
dtype = (
    None  # None for auto detection. Float16 for Tesla T4, V100, Bfloat16 for Ampere+
)
load_in_4bit = True  # Use 4bit quantization to reduce memory usage. Can be False.

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=model_name,
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
)

FastLanguageModel.for_inference(model)

test_dataset = load_dataset(
    "msc-smart-contract-audition/audits-with-reasons", split="test"
)

results = pd.read_csv(f"{model_alias}-descriptions.csv")
results.loc[results["real"].isnull(), "real"] = "There is no vulnearbility"

comparison_query_template = """
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
Below is text comprehension task. Output a score based on the specification below.

<|start_header_id|>user<|end_header_id|>

Below are two audits for a piece of solidity code.
You are a security auditor and your task is to mark an audit written by a student based on 3 critera.

First reason about whether each criterion is met or not.
If criteria are not fully satisifed, determine which is the more appropriate label from "PASS" or "FAIL" (nothing else is allowed).
Only after you have explained the reasoning behind each criterion, output a list labeling each criterion with either "PASS" or "FAIL".

Reason about wether the student's description satisfies the following criteria:
Criterion 1: Fulfilled if the two audits describe an identical vulnerability. This is about the nature of vulnerability and how it affects the contract, rather than the specifics of the code.
Criterion 2: Fulfilled if the student describes the same code scope or a subset of yours. In other words partial scope is also acceptable. Otherwise, this criterion is not met.
Criterion 3: Fulfilled if the two audits describe identical attacking strategy. The description does NOT need to be identical just the idea for the attack.

Only once you have deliberated on the criteria, output EXACTLY 3 criteria with a status of either "PASS" or "FAIL".
Example: Criterion 1: PASS

Do not output anything else like clarifications or other remarks after the list of criteria.

Your audit:
{}<|eot_id|>

Student's audit:
{}<|eot_id|>

<|start_header_id|>assistant<|end_header_id|>
My reasoning about the criteria:
"""


def run_query(data, query, show_tqdm=True):
    queries = data.apply(
        lambda row: query.format(
            row["real"].replace("\\n", "\n"),
            row["output"].replace("\\n", "\n"),
        ),
        axis=1,
    )

    if show_tqdm:
        iterator = tqdm(enumerate(queries), total=len(queries))
    else:
        iterator = enumerate(queries)

    for idx, query in iterator:
        real_contains_vuln = data.iloc[idx]["real"] != "There is no vulnearbility"
        output_contains_vuln = data.iloc[idx]["output"] != "There is no vulnearbility"

        if real_contains_vuln != output_contains_vuln:
            yield [
                "FAIL",
                "FAIL",
                "FAIL",
                "FAIL",
                "Criterion 0: FAIL\\n One of the descriptions does not contain a vulnerability.",
            ]
            continue

        if not real_contains_vuln and not output_contains_vuln:
            yield ["PASS", "PASS", "PASS", "PASS", "No vulnerabilities to compare."]
            continue

        inputs = tokenizer(query, return_tensors="pt", truncation=True).to("cuda")
        output_tokens = model.generate(
            **inputs, max_new_tokens=512, pad_token_id=tokenizer.pad_token_id
        )
        decoded_output = tokenizer.decode(
            output_tokens[0],
            skip_special_tokens=True,
            pad_token_id=tokenizer.pad_token_id,
        )

        result = decoded_output.split("My reasoning about the criteria:\n")[1].strip()
        pattern = re.compile(r"Criterion \d+: (PASS|FAIL)")
        criteria = ["PASS"] + pattern.findall(result)[
            -3:
        ]  # Add a pass for the 0th criterion

        yield criteria + [result.replace("\n", "\\n")]


with open(f"{model_alias}-descriptions-results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["cr0", "cr1", "cr2", "cr3", "description"])
    for result in run_query(results, comparison_query_template):
        writer.writerow(result)
