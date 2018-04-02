import glob
import re
from datetime import datetime
import commons


def twitter_tweet_iter(one_month=False):
    dir_ = commons.settings['data']['twitter']
    files = sorted(glob.glob(dir_ + '/tweets*.txt'))
    for file_ in files:
        with open(file_) as fp:
            fp.readline()
            try:
                while True:
                    time = re.match(r'T\t(.*)$', fp.readline())[1]
                    time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                    user = re.match(r'U\t(.*)$', fp.readline())[1]
                    content = re.match(r'W\t(.*)$', fp.readline())[1]
                    fp.readline()

                    at = re.findall(r'@(\w{1,15})(?:\W|$)', content)
                    hashtags = re.findall(r'#([a-zA-Z0-9]*)(?:\W|$)', content)

                    yield {
                        'time': time,
                        'timestamp': time.timestamp(),
                        'user': user,
                        'content': content,
                        'at': at,
                        'hashtags': hashtags
                    }
                    
            except EOFError:
                pass

        if one_month:
            break


def twitter_at(one_month=False):
    for tweet in twitter_tweet_iter(one_month=one_month):
        for at in tweet['at']:
            yield tweet['user'], at, tweet['timestamp']

