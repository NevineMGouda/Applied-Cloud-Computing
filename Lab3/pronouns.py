import re
import json
import glob
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def remove_punctuation(tweet):
    clean = re.sub(r"[,.;@#?%!&$]+\ *", " ", tweet)
    return clean


def count_pronouns(file_names=None):
    c = 0
    lookup_dic = {"den": 0, "denna": 0, "denne": 0, "det": 0, "han": 0, "hen":0, "hon": 0}
    unique_tweets = 0
    if file_names is None:
        file_names = glob.glob('data/*')
    for swed_fname in file_names:
        try:
            swedish_words_file = open(swed_fname)
            logger.info("__ACC__: Successfully loaded the data from: " + swed_fname)

        except:
            logger.error("__ACC__: Something went wrong while importing from: " + swed_fname)
            continue
        lines = swedish_words_file.readlines()
        for line in lines:
            c += 1
            # remove leading and trailing whitespace
            line = line.strip()
            # skip empty lines
            if len(line) == 0:
                continue
            # load json to a python dictionary
            tweet_dic = json.loads(line)
            if "retweeted_status" in tweet_dic:
                continue
            tweet_text = tweet_dic["text"].strip().lower()
            tweet_text = remove_punctuation(tweet_text)
            # tokenize the tweet text into a list of words by splitting with whitespace
            tweet_token = tweet_text.split()
            # This will map the total number of unique tweets available
            unique_tweets += 1

            # This will accumulate the counts for each pronoun
            for word in tweet_token:
                if word in lookup_dic:
                    lookup_dic[word] += 1
        return str(lookup_dic)