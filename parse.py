import json
import bs4
from bs4.element import Comment

# washington post parse function
def wp_parse(raw_text):
    # split text
    split_text = raw_text.split()

    # information setup
    author_found = False
    author = None
    end_idx_found = False
    start_idx = 0
    end_idx = 0

    # text end words
    end_words = ["Comments", "Read", "Sign"]

    # loop through words for author
    for i, word in enumerate(split_text):
        # get author
        if author_found == False and word == "By":
            author_found = True
            author = split_text[i+1] + " " + split_text[i+2]
            start_idx = i+3
    
    # loop through words for text
    for i, word in enumerate(split_text[start_idx:]):
        # get text
        if end_idx_found == False and word in end_words:
            end_idx_found = True
            end_idx = i + start_idx
    text = " ".join(split_text[start_idx:end_idx])

    return author, text


# fox news parse function
def fn_parse(raw_text):
    # split text
    split_text = raw_text.split()

    # information setup
    start_idx_found = False
    start_idx = 0
    end_idx_found = False
    end_idx = 0

    # text end words
    end_words = ["Advertisement", "Trending"]

    # loop through words for author
    for i, word in enumerate(split_text):
        # get start index
        if start_idx_found == False and word == "Print":
            start_idx_found = True
            start_idx = i+1
    
    # loop through words for text
    for i, word in enumerate(split_text[start_idx:]):
        # get text
        if end_idx_found == False and word in end_words:
            end_idx_found = True
            end_idx = i + start_idx
    text = " ".join(split_text[start_idx:end_idx])

    return None, text # cannot find author in just text


# huffington post parse function
def hp_parse(raw_text):
    # split text
    split_text = raw_text.split()

    # information setup
    author_found = False
    author = None
    end_idx_found = False
    start_idx = 0
    end_idx = 0

    # text end words
    end_words = ["Related", "Suggest"]

    # loop through words for author
    for i, word in enumerate(split_text):
        # get author
        if author_found == False and word == "By":
            author_found = True
            author = split_text[i+1] + " " + split_text[i+2]
            start_idx = i+6
    
    # loop through words for text
    for i, word in enumerate(split_text[start_idx:]):
        # get text
        if end_idx_found == False and word in end_words:
            end_idx_found = True
            end_idx = i + start_idx
    text = " ".join(split_text[start_idx:end_idx])

    return author, text


# breitbart parse function
def bb_parse(raw_text):
    # split text
    split_text = raw_text.split()

    # information setup
    author_found = False
    author = None
    end_idx_found = False
    start_idx = 0
    end_idx = 0

    # text end words
    end_words = ["Comments"]

    # loop through words for author
    for i, word in enumerate(split_text):
        # get author
        if author_found == False and word == "by":
            author_found = True
            author = split_text[i+1] + " " + split_text[i+2]
            start_idx = i+9
    
    # loop through words for text
    for i, word in enumerate(split_text[start_idx:]):
        # get text
        if end_idx_found == False and word in end_words:
            end_idx_found = True
            end_idx = i + start_idx
    text = " ".join(split_text[start_idx:end_idx])

    return author, text


# get title from html
def title_from_html(soup):
    return soup.title.string.strip()


# get publish date from html
def publish_date_from_html(soup, news_source):
    # WASHINGTON POST
    if news_source == "washingtonpost":
        for tag in soup.find_all('script'):
            if tag.get('type', None) == 'application/ld+json':
                try:
                    metadata = json.loads(tag.contents[0])
                    publish_date = metadata['datePublished']
                    return publish_date
                except:
                    temp = str(tag.contents[0])
                    date_idx = temp.find('datePublished')
                    publish_date = temp[date_idx+16:date_idx+21]
                    return publish_date

        for tag in soup.find_all('span'):
            if tag.get('itemprop', None) == 'datePublished':
                publish_date = tag.contents[0]
                return publish_date # returns "month day, year"
    
    # FOX NEWS
    elif news_source == "foxnews":
        for tag in soup.find_all('meta'):
            if tag.get('name', None) == 'dc.date':
                publish_date = tag.get('content', None)
                return publish_date # returns "year-month-day"

    # HUFFINTON POST
    elif news_source == "huffingtonpost" or news_source == "huffpost":
        for tag in soup.find_all('meta'):
            if tag.get('property', None) == 'article:published_time':
                publish_date = tag.get('content', None)
                return publish_date

            if tag.get('name', None) == 'sailthru.date':
                publish_date = tag.get('content', None).split()
                return publish_date # returns "year-month-day"

    # BREITBART
    elif news_source == "breitbart":
        for tag in soup.find_all('span', {'class':'story-time'}):
            publish_date = tag.text
            return publish_date # returns "day-month-year"


# get raw text from html
def raw_from_html(soup):
    def tag_visible(element):
        if element.parent.name in ["style","script","head","title","meta","[document]",]:
            return False
        if isinstance(element, Comment):
            return False
        return True

    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return " ".join(t.strip() for t in visible_texts)