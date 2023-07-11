import argparse
import copy

import torch
import torch.nn as nn
# from transformers import (
#     AutoModelForCausalLM,
#     AutoTokenizer,
#     DataCollatorForLanguageModeling,
#     TrainingArguments,
#     Trainer,
# )
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    LlamaTokenizer,
    LlamaForCausalLM,
    DataCollatorForLanguageModeling,
    TrainingArguments,
    Trainer,
    pipeline,
    AutoConfig,
)
from datasets import load_dataset
from quant import BinaryLinear, IrBinaryLinear, FdaBinaryLinear, XnorBinaryLinear
from utils import *
import torch.nn.functional as F
from evaluate import evaluate_model


def main(model_id, dataset_name):

    if args.load_checkpoint:
        print('loading quantized checkpoint!!!')
        tokenizer = LlamaTokenizer.from_pretrained(args.model_id)
        model = LlamaForCausalLM.from_pretrained(
            args.checkpoint_dir, torch_dtype=torch.float16, device_map='auto',
        )
        model.eval()
        evaluate_model(model, tokenizer, args.model_id, args.tasks, limit=args.eval_limit, batch_size=args.eval_batch_size, num_fewshot=args.eval_num_fewshot)

    else:
        print('not loading checkpoint!!!')
        # CUDA_VISIBLE_DEVICES=0 XDG_CACHE_HOME=/data/shangyuzhang python bnn_eval.py --tasks=mmlu --eval_limit=-1 --model_id 'huggyllama/llama-7b'
        tokenizer = AutoTokenizer.from_pretrained(args.model_id)
        model = AutoModelForCausalLM.from_pretrained(args.model_id, torch_dtype=torch.float16,  device_map={"": 0})
        model.eval()
        evaluate_model(model, tokenizer, args.model_id, args.tasks, limit=args.eval_limit, batch_size=args.eval_batch_size, num_fewshot=args.eval_num_fewshot)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Model Training Script")
    parser.add_argument(
        "--model_id", type=str, default="huggyllama/llama-7b", help="Pretrained model ID, huggyllama/llama-7b, openlm-research/open_llama_7b"
    )
    parser.add_argument(
        "--dataset", type=str, default="Abirate/english_quotes", help="Dataset name"
    )
    parser.add_argument(
        "--tasks",
        type=str,
        default="boolq",
        help="evaluate tasks name, can be tasks separated by , lambada_openai,piqa,arc_easy,arc_challenge,openbookqa, boolq",
    )
    parser.add_argument(
        "--eval_limit",
        default=-1,
        type=int,
        help="number of test samples for debug, set to -1 is no limit",
    )
    parser.add_argument(
        "--eval_batch_size",
        default=2,
        type=int,
        help="eval batch size, default is 2",
    )
    parser.add_argument(
        "--eval_num_fewshot",
        default=5,
        type=int,
        help="mmlu eval number of few-shot, default is 5",
    )
    parser.add_argument(
        "--load_checkpoint",
        action="store_true",
        help="loading checkpoint or not"
    )
    parser.add_argument(
        "--checkpoint_dir", type=str, default='/data/shangyuzhang/BinaryLLM/checkpoints/', help="to-be-evaluated checkpoint dir"
    )
    args = parser.parse_args()

    main(args.model_id, args.dataset)
