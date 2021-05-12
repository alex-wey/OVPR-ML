# About
Hi there - welcome to the OVPR-ML repository. Over the past year, I have been building a pipeline that captures data focused on marijuana legalization from Common Crawl and Reddit. This data is stored, processed, and fed into the [Grover](https://github.com/rowanz/grover) model to generate synthetic texts. The human and computer-generated texts are annotated by researchers to be used for building a computation model of social and political narratives underlying online discourse.

# Setup

## Grover
1. Download the [Grover](https://github.com/rowanz/grover) repository
2. Follow the "Quickstart: setting up Grover for generation!"
3. Make sure that you adjust the paths in `generate.py` respective to the Grover repository

## Common Crawl
1. Download the [CC Index Server](https://github.com/ikreymer/cc-index-server) repository
2. Follow the "Usage & Installation"
3. When scraping Common Crawl, `cd cc-index-server` and run `cdx-server`

## Reddit
1. Go to Babak Hemmatian's [Reddit Marijuana Legalization Corpus: Full Data Cleaned (8.5.2020)](https://drive.google.com/drive/u/1/folders/1yx2lmbrbHr0uAA8zLj-TbHaXqOrcNhw6)
2. Download `author`, `original_comm`, and `subreddit` folders into this repository's `data` folder
3. You may delete the `author`, `original_comm`, and `subreddit` files that exist in these folders, respectively

# Codebase

## Setup

1. Make sure `python` or `python3` is installed correctly
2. Install `requirements.txt`

## Scraping

For scraping data from Common Crawl, refer to `news.py`, which requires as input:
- News source
- Number of samples to be collected
- Start year for publish date
- End year for publish date
- Path to save the `.csv` file in `/data/news`

IMPORTANT: `parse.py` is curated to process HTML sourced from The Washington Post, Fox News, The Huffinton Post, and Breitbart. If the user intends to sample from other news sources, separate parse functions will have to be written into `parse.py` and added to the `parse` function in `news.py`. Note that HTML is quite finicky to parse, so the current parse functions in `parse.py` are not fully robust and may require additional changes.

ADDITIONALLY: `parse.py` contains a function called `publish_date_from_html`. The output is not consistent across all news sources (i.e. The Washington Post yields "month day, year" while Fox News yields "year-month-day"). Even HTML from the same news source do not contain consistent date formatting. This requires the user to manually change the `publish_date` format in the `.csv` file in `/data/{source}`, which should be "day-month-year" numerically.

For scraping data from Reddit, refer to `reddit.py`, which requires as input:
- Number of samples to be collected
- Boolean indicating whether to sample from 2008 - 2014
- Boolean indicating whether to sample from 2015 - 2019
- Path to save the `.csv` file in `/data/reddit`

## Encoding

For encoding the data, refer to `encode.py`, which requires as input:
- Path to `.csv` file from `/data/{source}`

## Generating

For generating synthetic texts, refer to `generate.py`, which requires as input:
- Path to `.jsonl` file from `/encode/{source}`

## Decoding

For decoding the data, refer to `decode.py`, which requires as input:
- Path to `.jsonl` file from `/decode/{source}`
- Results are stored in `/results/{source}`

# Research

Please