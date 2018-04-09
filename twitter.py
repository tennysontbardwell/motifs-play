import glob
import re
from datetime import datetime
import commons
import collections
import itertools


LOG = commons.make_log(__name__)


def twitter_tweet_iter(one_month=False):
    dir_ = commons.settings['data']['twitter']
    files = sorted(glob.glob(dir_ + '/tweets*.txt'))
    count = itertools.count()
    for file_ in files:
        with open(file_) as fp:
            fp.readline()
            try:
                while True:
                    line = fp.readline()
                    if len(line) < 3:
                        # for EOF testing
                        break
                    time = re.match(r'T\t(.*)$', line)[1]
                    time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                    user = re.match(r'U\t(.*)$', fp.readline())[1]
                    content = re.match(r'W\t(.*)$', fp.readline())[1]
                    fp.readline()

                    at = re.findall(r'@(\w{1,15})(?:\W|$)', content)
                    hashtags = re.findall(r'#([a-zA-Z0-9]*)(?:\W|$)', content)

                    yield {
                        'time': time,
                        'timestamp': int(time.timestamp()),
                        'user': user,
                        'content': content,
                        'at': at,
                        'hashtags': hashtags
                    }
                    i = count.__next__()
                    if i % 10**6 == 0:
                        LOG.info('{:,} tweets read'.format(i))
                    
            except EOFError:
                pass

        if one_month:
            break


class TwitterInterface:
    def __init__(self):
        self.one_month=False

    def twitter_at(self):
        for tweet in twitter_tweet_iter(one_month=self.one_month):
            for at in tweet['at']:
                yield tweet['user'], at, tweet['timestamp']

    def twitter_at_by_hashtag(self):
        '''Same as twitter_at, but in the format (hashtag,
        (source,target,time)). Only returns edges that belong to a hashtag, and
        will return edges multiple times if the same hashtag is used multiple
        times'''
        for tweet in twitter_tweet_iter(one_month=self.one_month):
            for at in tweet['at']:
                for hashtag in tweet['hashtags']:
                    yield hashtag, (tweet['user'], at, tweet['timestamp'])

    def twitter_hashtag_segregate(self):
        hashtag_lists = collections.defaultdict(list)
        for hashtag, edge in self.twitter_at_by_hashtag():
            hashtag_lists[hashtag].append(edge)
        return hashtag_lists.items()

