import argparse
import os
import pandas as pd
import csv
import string
import re
import requests
import json
import html

from bs4 import BeautifulSoup
from warcio.archiveiterator import ArchiveIterator
from urllib.parse import urlparse
from datetime import datetime
from collections import defaultdict
from collections import Counter

from annotations import preprocess
from parse import wp_parse, fn_parse, hp_parse, bb_parse
from parse import title_from_html, publish_date_from_html, raw_from_html

# path and dates configuration
path = os.path.dirname(os.path.abspath(__file__))
info_path = path + "/info"
warc_path = path + "/warc_files"

# import the common crawl database dates
with open(f"{path}/info/dates.json") as f:
    cc_dates = json.load(f)

# create date checklist
def create_checklist(start_year, end_year, num_samples):
    # make sure num_samples is divisible by input years
    year_dif = (end_year + 1) - start_year
    if year_dif % num_samples != 0:
        print("Number of samples is not evenly divisible across input years")
        return False
    
    # create checklist
    iter_sample = int(year_dif/num_samples)
    date_dict = Counter()
    for i in range(start_year, end_year + 1):
        date_dict[str(i)] = iter_sample
    return date_dict

# read WARC file
def read_warc(warc_file, url):
    with open(warc_file, "rb") as stream:
        for record in ArchiveIterator(stream):
            if record.rec_type == "response":
                warc_target_uri = record.rec_headers.get_header("WARC-Target-URI")
                if url == warc_target_uri:
                    status = record.http_headers.statusline
                    if status != "200 OK":
                        return False
                    else:
                        return record.content_stream().read()

# delete all WARC files
def delete_warc_files():
    for warc_file in os.listdir(warc_path):
        os.remove(f"{warc_path}/{warc_file}")

# obtain digest and warc files from cdx-server
def cc_collect(news_source, num_samples, start_year, end_year):
    # create dates checklist
    date_dict = create_checklist(start_year, end_year, num_samples)
    if date_dict == False:
        return

    # upload the ml regex
    def regex_setup():
        regex_marijuana = []
        with open(f"{info_path}/regex/ml_regex.txt") as f:
            for line in f:
                regex_marijuana.append(re.compile(line.lower().strip()))
        return regex_marijuana

    # check for relevant urls
    def relevant_url(url):
        if any(not exp.search(url.lower()) is None for exp in regex_marijuana):
            return True
        else:
            return False

    # update the history logs
    def update_seen(url, csv_file):
        df1 = pd.DataFrame([[url]], columns=["SEEN"])
        df2 = pd.read_csv(f"history/{csv_file}.csv")
        df = df1.append(df2)
        df.to_csv(f"history/{csv_file}.csv", index=False)

    # set up the ml regex
    regex_marijuana = regex_setup()

    # begin collecting data
    data = defaultdict(dict)
    sample_count = 0
    while sample_count < num_samples:
        print("Samples:", sample_count)

        # loop through cc dates and ids
        for year, ids in cc_dates.items():
            if sample_count == num_samples:
                break
            for id in ids:
                if sample_count == num_samples:
                    break

                # go to cc url
                cc_date = f"{year}-{id}"
                print("Date:", cc_date)
                cc_idx_url = f"http://localhost:8080/CC-MAIN-{cc_date}-index?url={news_source}.com/*"
                records = requests.get(url=cc_idx_url).text.strip().split("\n")

                # loop through data records
                for record in records:
                    if sample_count == num_samples:
                        break

                    # parsing out eligible records
                    if record.startswith(f"com,{news_source}"):
                        start, end = record.find("{"), record.find("}") + 1
                        try:
                            cc_dict = json.loads(record[start:end])
                        except:
                            print("JSON formatting error")
                        
                        # check for a url and status in dictionary
                        if "url" in cc_dict.keys() and "status" in cc_dict.keys():
                            cc_url = cc_dict["url"]
                            cc_status = cc_dict["status"]

                            # check if cc url is relevant and status is OK
                            if relevant_url(cc_url) and cc_status == "200":

                                # check if this url is not a bad url
                                if any(bad_url in cc_url for bad_url in ["ABjfuEJ_category"]):
                                    update_seen(cc_url, "news_bad_urls")
                                    
                                else:
                                    # upload the bad/good url history logs
                                    bad_url_history = list(csv.reader(open(f"{path}/history/news_bad_urls.csv", "r")))
                                    good_url_history = list(csv.reader(open(f"{path}/history/news_good_urls.csv", "r")))

                                    # cross reference the cc url against bad/good url history log
                                    o = urlparse(cc_url)
                                    url_cleaned = f"{o.scheme}:{o.netloc}{o.path}"
                                    if [url_cleaned] in bad_url_history or [url_cleaned] in good_url_history:
                                        continue
                                    
                                    # check if publish date is in date checklist
                                    success = False
                                    for yr in o.path.split("/"):
                                        if yr in date_dict.keys():
                                            success = True
                                            date_dict[yr] -= 1
                                            # delete key if iter_sample is collected
                                            if date_dict[yr] == 0:
                                                date_dict.pop(yr)
                                    if success == False:
                                        continue

                                    # obtain warc file from aws
                                    warc_filename = cc_dict["filename"]
                                    aws = f"https://commoncrawl.s3.amazonaws.com/{warc_filename}"
                                    warc_filename = warc_filename.split("/")[-1]
                                    warc_file = f"warc_files/{warc_filename}"
                                    os.system(f"curl {aws} --output {warc_file}")

                                    # read the warc file
                                    content = read_warc(warc_file, cc_url)

                                    # save to data dictionary if successful
                                    if content != False:
                                        soup = BeautifulSoup(content, "html.parser")
                                        data[cc_date][cc_url] = soup
                                        update_seen(url_cleaned, "news_good_urls")
                                        sample_count += 1
    delete_warc_files()
    return data


# update document history
def update_history(dataset):
    # news.csv configuration
    df = [["EXTRACTED", "ON", datetime.date(datetime.now())]]
    for date, info in dataset.items():
        for url in info.keys():
            date_components = date.split("-")
            year = int(date_components[0])
            id = int(date_components[1])
            df.append([year, id, url])

    # update news.csv
    df1 = pd.DataFrame(df, columns=["year", "id", "url"])
    df2 = pd.read_csv(f"{path}/history/news.csv")
    df = df1.append(df2)
    df.to_csv(f"{path}/history/news.csv", index=False)


# parse author and text information from raw text
def parse(raw_text, news_source):
    # preprocess text
    pp_text = preprocess(raw_text)

    # parse raw text based on news source
    if news_source == "washingtonpost":
        author, text = wp_parse(pp_text)
    elif news_source == "foxnews":
        author, text = fn_parse(pp_text)
    elif news_source == "huffingtonpost" or news_source == "huffpost":
        author, text = hp_parse(pp_text)
    elif news_source == "breitbart":
        author, text = bb_parse(pp_text)

    return author, text

# convert dataset to csv
def convert(dataset, news_source, name):
    # obtain data for dataframe
    df = []
    domain = f"{news_source}.com"
    for date, info in dataset.items():
        for url, soup in info.items():
            title = title_from_html(soup)
            publish_date = publish_date_from_html(soup, news_source)
            raw_text = raw_from_html(soup)
            author, text = parse(raw_text, news_source)
            df.append([url, domain, title, author, publish_date, "", text])

    # save dataframe as .csv file
    df = pd.DataFrame(df, columns=["url","domain","title","authors","publish_date","summary","text",])
    df.to_csv(f"{path}/data/news/{name}.csv", index=False)


def main():
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--news_source', type=str, help='requires a news source to collect data')
    parser.add_argument('--num_samples', type=int, help='requires the number of samples')
    parser.add_argument('--start_year', type=int, help='requires the start year')
    parser.add_argument('--end_year', type=int, help='requires the end year')
    parser.add_argument('--path', type=str, help='requires path to .csv file in /data/news')
    args = parser.parse_args()

    # collect data
    print('Collecting data...')
    dataset = cc_collect(args.news_source, args.num_samples, args.start_year, args.end_year)

    # update history
    print('Updating history...')
    update_history(dataset)

    # convert data to csv
    print('Writing data...')
    convert(dataset, args.news_source, args.path)


if __name__ == "__main__":
    main()