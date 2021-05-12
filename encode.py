import argparse
import os
import pandas as pd
import json

def encode(csv_path, output_path):
    # read data
    df = pd.read_csv(csv_path)
    records = []

    # loop through rows and parse data into dictionary
    for i, row in df.iterrows():
        data = {}
        if isinstance(row["url"], float):
            data["url"] = ""
        else:
            data["url"] = row["url"]
        data["domain"] = row["domain"]
        data["title"] = row["title"]
        if isinstance(row["authors"], float):
            data["authors"] = []
        else:
            data["authors"] = [row["authors"]]
        data["publish_date"] = row["publish_date"]
        data["text"] = row["text"]
        if isinstance(row["summary"], float):
            data["summary"] = None
        else:
            data["summary"] = row["summary"]
        records.append(data) # add data dictionary to records list

    # write all of the records to .jsonl file
    with open(f"encode{output_path}", "w") as f:
        for record in records:
            json.dump(record, f)
            f.write("\n")


def main():
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, help="requires path to .csv in /data")
    args = parser.parse_args()

    # encode data for Grover generation
    data_path = f"{os.path.dirname(os.path.abspath(__file__))}/data{args.path}.csv"
    encode(data_path, f"{args.path}.jsonl")


if __name__ == "__main__":
    main()
