import argparse
import os

def generate(input):
    command = f"""PYTHONPATH=$(pwd) python ../Grover/sample/contextual_generate.py -model_config_fn ../Grover/lm/configs/base.json -model_ckpt ../Grover/models/base/model.ckpt -metadata_fn encode{input} -out_fn decode{input}"""
    os.system(command)


def main():
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, help="requires path to .jsonl file in /encode")
    args = parser.parse_args()

    # execute Grover generation
    generate(f"{args.path}.jsonl")


if __name__ == "__main__":
    main()
