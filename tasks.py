from data_set import TxtWriter
from commons import settings
import commons
import os
import pickle

import twitter
import citations


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


@commons.file_cached
def citation_graph(path, color_edges=False):
    cit = citations.CitationInterface()
    with open(path, 'w') as fp:
        first = True
        for edge in cit.colored_graph(color_edges=color_edges):
            if not first:
                fp.write('\n')
            else:
                first = False
            if color_edges:
                fp.write('{} {} {}'.format(*edge))
            else:
                fp.write('{} {}'.format(*edge))

    
def main():
    # twitter_task()
    path = os.path.join(settings['build_dir'],
                      'citations/colored_graph.csv')
    citation_graph(path)
    path = os.path.join(settings['build_dir'],
                      'citations/colored_graph_signed.csv')
    citation_graph(path, color_edges=True)


if __name__ == '__main__':
    main()
