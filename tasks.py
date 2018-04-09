from data_set import TxtWriter
from commons import settings
import commons
import os
import twitter


@commons.file_cached
def twitter_hashtags(path, one_month=False):
    twitter_interface = twitter.TwitterInterface()
    twitter_interface.one_month = one_month

    for hashtag, edge_list in twitter_interface.twitter_hashtag_segregate():
        if len(edge_list) < 500:
            continue
        TxtWriter.edges_to_txt(os.path.join(path, hashtag), edge_list)


def twitter_task():
    twitter_all = twitter.TwitterInterface()
    twitter_month = twitter.TwitterInterface()
    twitter_month.one_month = True

    path = os.path.join(settings['build_dir'],
                      'twitter/one_month/twitter_at/at_graph.txt')
    TxtWriter.edges_to_txt(path, twitter_month.twitter_at())

    path = os.path.join(settings['build_dir'],
                      'twitter/all/twitter_at/at_graph.txt')
    TxtWriter.edges_to_txt(path, twitter_all.twitter_at())

    path = os.path.join(settings['build_dir'],
                      'twitter/one_month/twitter_at/hashtags')
    twitter_hashtags(path, True)

    path = os.path.join(settings['build_dir'],
                      'twitter/all/twitter_at/hashtags')
    twitter_hashtags(path, False)

    
    
def main():
    twitter_task()


if __name__ == '__main__':
    main()
