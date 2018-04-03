from data_set import TxtWriter
from commons import settings
from os import path
import twitter


def main():
    path_ = path.join(settings['build_dir'],
                      'twitter/one_month/twitter_at/at_graph.txt')
    TxtWriter.edges_to_txt(path_, twitter.twitter_at(one_month=True))

    path_ = path.join(settings['build_dir'],
                      'twitter/all/twitter_at/at_graph.txt')
    TxtWriter.edges_to_txt(path_, twitter.twitter_at())

    path_ = path.join(settings['build_dir'],
                      'twitter/all/twitter_at/hashtags/')
    TxtWriter
    
    


if __name__ == '__main__':
    main()
