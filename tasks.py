#!/usr/bin/env python3
from data_set import TxtWriter
from commons import settings
import commons
import os
import pickle
import collections
import math

import numpy as np

import twitter
import citations
import visualize
import multilayer


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
def citations_tasks(path, journal1, journal2):
    c = CitationInterface(journal_filter=[journal1, journal2])

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


def citation_test():
    # journals = ['Nanoscale', 'Neurosurgery']
    journals = ['The Journal of nutrition',
                "The American journal of clinical nutrition"]
    cit = citations.CitationInterface(journal_filter=journals)
    dir_ = os.path.join(commons.settings['build_dir'], 'citations',
                      'journals__{}__{}'.format(journals[0], journals[1]))
    path = os.path.join(dir_, 'multilayer.json')
    graph = cit.colored_graph(path)

    path = os.path.join(dir_, 'multilayer_graph.tsv')
    graph.directed_graph_file(path)

    path = os.path.join(dir_, 'multilayer_graph_named.tsv')
    graph.directed_graph_file(path, names=True)

    m_path = os.path.join(dir_, 'motifs.json')
    graph.count_motifs(m_path, m4=True)
    m1_path = os.path.join(dir_, 'motifs__{}.json'.format(journals[0]))
    graph.set_filters(node_labels=[None, journals[0]])
    graph.count_motifs(m1_path, m4=True)
    m2_path = os.path.join(dir_, 'motifs__{}.json'.format(journals[1]))
    graph.set_filters(node_labels=[None, journals[1]])
    graph.count_motifs(m2_path, m4=True)

    o_path = os.path.join(dir_, 'motifs_comparison.html')
    visualize.motif_count(o_path, [m_path, m1_path, m2_path])  # 

    cluster = multilayer.Cluster(graph)
    cluster.get_cluster_accuracy(cluster.cluster(2))


def citation_misc():
    authors = []
    def get_authors(paper):
        authors = []
        for author in paper['authors']:
            if len(author['ids']) == 0:
                continue
            assert len(author['ids']) == 1, author
            authors.append(author['ids'][0])
        return authors
    cite = citations.CitationInterface()
    # cite.limit = 10**6
    for paper in cite.paper_iter():
        authors += get_authors(paper)
    authors = collections.Counter(authors)
    counts = collections.Counter(authors.values())
    path = os.path.join(settings['build_dir'],
                      'citations/author_dist.html')
    visualize.plot_dist(path, list(authors.values()), 'Papers Authored')


def citation_misc2():
    authors = collections.defaultdict(list)
    def get_authors(paper):
        authors = []
        for author in paper['authors']:
            if len(author['ids']) == 0:
                continue
            assert len(author['ids']) == 1, author
            authors.append(author['ids'][0])
        return authors
    cite = citations.CitationInterface()
    # cite.limit = 10**4
    for paper in cite.paper_iter():
        for author in get_authors(paper):
            authors[author].append(paper['journalName'])

    res = []
    for _, papers in authors.items():
        c = collections.Counter(papers)
        fst = c.most_common(2)[0][1] / len(papers)
        try:
            snd = c.most_common(2)[1][1] / len(papers)
        except IndexError:
            snd = 0
        res.append((fst,snd))

    matrix = np.zeros((20,20), dtype=int)
    for fst,snd in res:
        fst_index = math.floor(fst*20)
        if fst_index == 20:
            fst_index = 19
        snd_index = math.floor(snd*20)
        if snd_index == 20:
            snd_index = 19
        matrix[fst_index][snd_index] += 1
    path = os.path.join(settings['build_dir'],
                      'citations/author_dist_2d.png')
    visualize.hist_2d(path, matrix)


def main():
    # twitter_task()
    # path = os.path.join(settings['build_dir'],
    #                   'citations/colored_graph.csv')
    # citation_graph(path)
    # path = os.path.join(settings['build_dir'],
    #                   'citations/colored_graph_signed.csv')
    # citation_graph(path, color_edges=True)
    citation_misc2()


if __name__ == '__main__':
    main()
