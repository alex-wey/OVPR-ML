import argparse
import os
import pandas as pd
import json
import csv
import time
import random
import re

from itertools import combinations
from datetime import datetime

path = os.path.dirname(os.path.abspath(__file__))

def preprocess(input):
    # remove links
    text = re.sub(
        r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|
        (\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""",
        "",
        input,
        )

    # convert to ascii
    text = text.encode("ascii", "ignore").decode()
    return text

# collect the original and grover texts from the results
def annotations(decode_path, num_annotators):
    # gather corresponding texts and ids
    ids_texts = []

    # info.csv configuration
    df = [["COLLECTED", "ON", datetime.date(datetime.now()), None, None]]
    d = json.JSONDecoder()
    with open(decode_path, "r") as f:
        for i, line in enumerate(f):
            record = d.decode(line)
            domain = None
            publish_date = None
            for key, value in record.items():
                id = datetime.now().strftime("%d%m%y%H%M%S")
                if key == "domain":
                    domain = value
                elif key == "publish_date":
                    publish_date = value
                elif key == "text":
                    text = preprocess(value)
                    ids_texts.append((id, text))
                    df.append([id, publish_date, i, "original", domain])
                elif key == "gens_article":
                    text = preprocess(value[0])
                    ids_texts.append((id, text))
                    df.append([id, publish_date, i, "grover", domain])
                time.sleep(1)
            print(i)

    # update info.csv
    df1 = pd.DataFrame(df, columns=["id", "publish_date", "index", "type", "domain"])
    df2 = pd.read_csv(f"{path}/info/info.csv")
    df = df1.append(df2)
    df.to_csv(f"{path}/info/info.csv", index=False)

    # distrubute texts for annotators
    distribute(ids_texts, num_annotators)

def distribute(ids_texts, num_annotators):

    def write_share(first, second, id):
        f = open(f"{path}/info/share.txt", "a")
        f.write(f"a{str(first)}: {id}.txt\n")
        f.write(f"a{str(second)}: {id}.txt\n\n")
        f.close

    def write_txt(i, id, text):
        f = open(f"{path}/annotations/a{str(i)}/5_4_21/{id}.txt", "w")
        f.write(text)
        f.close()

    # shuffle the data
    random.shuffle(ids_texts)

    # sample num_annotators texts to share
    ids_texts_share = ids_texts[:num_annotators]
    combs = list(combinations(range(num_annotators), 2))
    for tup, comb in zip(ids_texts_share, combs):
        id, text = tup
        write_txt(comb[0], id, text)
        write_txt(comb[1], id, text)
        write_share(comb[0], comb[1], id)

    # divide the data by num_annotators
    ids_texts = ids_texts[num_annotators:]
    sample_len = int(len(ids_texts)/num_annotators)
    for i in range(num_annotators):
        for j in range(sample_len):
            id, text = ids_texts.pop()
            write_txt(i, id, text)


def main():
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, help="requires path to .jsonl from /decode")
    parser.add_argument("--num_annotators", type=int, help="requires number of annotators")
    args = parser.parse_args()

    # annotations function
    annotations(f"{os.path.dirname(os.path.abspath(__file__))}/decode{args.path}.jsonl", args.num_annotators)

if __name__ == "__main__":
    main()