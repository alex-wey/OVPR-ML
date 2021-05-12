import argparse
import os
import random
import pandas as pd
import nltk
import csv
import string
import math
import re

from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from annotations import preprocess

stopwords = stopwords.words("english")

# path configuration
path = os.path.dirname(os.path.abspath(__file__))
data_path = path + "/data"
original_comm_path = data_path + "/original_comm"
author_path = data_path + "/author"
subreddit_path = data_path + "/subreddit"

# randomized selection of dates (key: year, value: n random months)
def randomize(start, end):
    dates = {}
    for i in range(start, end + 1):
        dates[i] = random.sample(range(1, 13), 12)
    return dates


# update document history
def update_history(year, month, i):
    df = [[year, month, i]]
    df1 = pd.DataFrame(df, columns=["year", "month", "index"])
    df2 = pd.read_csv("history/reddit.csv")
    df = df1.append(df2)
    df.to_csv("history/reddit.csv", index=False)


# get data set for years 2015-2019
def get_data1(random_dates, num_total, cmv, uo):
    ret_data = {}
    cur_count = 0
    while cur_count != num_total:
        print("Count:", cur_count)

        for year, months in random_dates.items():
            if cur_count == num_total:
                break
            print("Year:", year)
            num_cmv, num_uo = cmv, uo

            for month in months:
                if num_cmv == 0 and num_uo == 0:
                    break
                print("Month:", month)

                # open author, subreddit, and comments
                authors = open(f"{author_path}/author-{year}-{month}").read().split("\n")
                subreddits = (open(f"{subreddit_path}/subreddit-{year}-{month}").read().split("\n"))
                comments = (open(f"{original_comm_path}/original_comm-{year}-{month}").read().split("\n"))

                # obtain random indices to loop through file entries
                random_indices = random.sample(range(len(authors)), len(authors))
                for i in random_indices:
                    if num_cmv == 0 and num_uo == 0:
                        break

                    # cross reference the history
                    history = list(csv.reader(open("history/reddit.csv", "r")))
                    if list(map(str, [year, month, i])) in history:
                        continue

                    # check entry for correct criteria
                    temp = comments[i].split()

                    if len(temp) >= 200 and len(temp) <= 400:
                        if subreddits[i] == "unpopularopinion" and num_uo != 0:
                            ret_data[f"00-{month}-{year}.{i}"] = (authors[i], subreddits[i], comments[i])
                            update_history(year, month, i)
                            num_uo -= 1
                            cur_count += 1
                            print("Num UO:", num_uo, "Count:", cur_count)

                        if subreddits[i] == "changemyview" and num_cmv != 0:
                            ret_data[f"00-{month}-{year}.{i}"] = (authors[i], subreddits[i], comments[i])
                            update_history(year, month, i)
                            num_cmv -= 1
                            cur_count += 1
                            print("Num CMV:", num_cmv, "Count:", cur_count)
    return ret_data


# configure dataset for years 2008-2014
def get_data2(random_dates, num_total):
    ret_data = {}
    cur_count = 0
    while cur_count != num_total:
        print("Count:", cur_count)

        for year, months in random_dates.items():
            if cur_count == num_total:
                break
            print("Year:", year)
            num_samples = 1

            for month in months:
                if num_samples == 0:
                    break
                
                # open author, subreddit, and comments
                authors = open(f"{author_path}/author-{year}-{month}").read().split("\n")
                subreddits = (open(f"{subreddit_path}/subreddit-{year}-{month}").read().split("\n"))
                comments = (open(f"{original_comm_path}/original_comm-{year}-{month}").read().split("\n"))

                # obtain random indices to loop through file entries
                random_indices = random.sample(range(len(authors)), len(authors))
                for i in random_indices:
                    if num_samples == 0:
                        break

                    # cross reference the history
                    history = list(csv.reader(open("history/reddit.csv", "r")))
                    if list(map(str, [year, month, i])) in history:
                        continue

                    # check entry for correct criteria
                    temp = comments[i].split()
                    if len(temp) >= 200 and len(temp) <= 400:
                        ret_data[f"00-{month}-{year}.{i}"] = (authors[i], subreddits[i], comments[i])
                        update_history(year, month, i)
                        num_samples -= 1
                        cur_count += 1
                        print("Count:", cur_count)
                        break
    return ret_data


# convert dataset to csv
def convert(dataset, name):

    def relevant_title(text):
        # load marijuana regex
        regex_marijuana = []
        with open(f"{data_path}/other/regex/ml_regex.txt") as f:
            for line in f:
                regex_marijuana.append(re.compile(line.lower().strip()))

        # obtain sentences from text
        sentences = nltk.tokenize.sent_tokenize(text)
        for i, line in enumerate(sentences):

            # check if any sentence contains words that match regex
            if any(not exp.search(line.lower()) is None for exp in regex_marijuana):
                if len(line.split(" ")) >= 45 and len(line.split(" ")) <= 50:
                    return line
                else:
                    ret_line, c = line, i + 1
                    while len(ret_line.split(" ")) < 45:
                        if c < len(sentences):
                            ret_line = ret_line + " " + sentences[c]
                            c += 1
                        else:
                            return ret_line
                    return ret_line
        return False

    def process(input):
        # remove any urls
        text = preprocess(input)

        # obtain segments in sentence
        segments, s = [], 0
        for i, c in enumerate(text):
            if c in [".", "?", "!"] and i + 1 < len(text):
                if text[i + 1].isalpha():
                    segments.append(text[s:i + 1])
                    s = i + 1
        segments.append(text[s:])
        return " ".join(segments)

    # obtain data for dataframe
    df = []
    for key, value in dataset.items():
        domain = f"reddit.com/r/{value[1]}"
        text = process(value[2])
        title = relevant_title(text)
        if not title:
            print("No title obtained for:", key)
            continue
        author = value[0]
        publish_date = key.split('.')[0]
        df.append(["", domain, title, author, publish_date, "", text])

    # save dataframe as .csv file
    df = pd.DataFrame(df, columns=["url","domain","title","authors","publish_date","summary","text",])
    df.to_csv(f"data/reddit{name}.csv", index=False)


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def main():
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_samples', type=int, help='requires the number of samples')
    parser.add_argument('--yrs_2008_2014', type=str2bool, help='gathering data for years 2008-2014')
    parser.add_argument('--yrs_2015_2019', type=str2bool, help='gathering data for years 2015-2019')
    parser.add_argument('--path', type=str, help='requires path to .csv file in /data/reddit')
    args = parser.parse_args()

    # obtain random dataset
    if args.yrs_2008_2014:
        random_dates = randomize(2008, 2014)
        dataset = get_data2(random_dates, args.num_samples)
    elif args.yrs_2015_2019:
        random_dates = randomize(2015, 2019)
        dataset = get_data1(random_dates, args.num_samples, 2, 2) # need to change num_cmv, num_uo

    # obtain dataset
    print("Data obtained...")
    for key, value in dataset.items():
        print(key, value[1])

    # convert dataset into csv
    convert(dataset, args.path)


if __name__ == "__main__":
    main()