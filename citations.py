import json
import os
import itertools

import networkx as nx

import commons

LOG = commons.make_log(__name__)

class CitationInterface:
    def __init__(self, limit=None):
        self.limit=limit
        
    def paper_iter(self):
        dir_ = commons.settings['data']['semanticscholar']
        count = itertools.count()
        with open(os.path.join(dir_, 'papers-2017-10-30.json')) as fp:
            for line in fp:
                yield json.loads(line)
                i = count.__next__()
                if i == 10**4:
                    LOG.info('{:,} papers read'.format(i))
                if i % 10**6 == 0 and i != 0:
                    LOG.info('{:,} papers read'.format(i))
                if i == self.limit:
                    LOG.info('limit of {} reached'.format(self.limit))
                    break

    def colored_graph(self, color_edges=False):
        '''Iterator for the list of edges'''
        def get_authors(paper):
            authors = []
            for author in paper['authors']:
                if len(author['ids']) == 0:
                    continue
                assert len(author['ids']) == 1, author
                authors.append(author['ids'][0])
            return authors

        bad = 0  # number of papers discarded or some reason
        for paper in self.paper_iter():
            id = paper['id']
            authors = get_authors(paper)
            in_citations = paper['inCitations']
            out_citations = paper['outCitations']

            if authors is None or len(authors) == 0:
                bad += 1
                continue

            for author in authors:
                if color_edges:
                    yield (author, id, 1)
                else:
                    yield (author, id)
            for citation in in_citations:
                if color_edges:
                    yield (id, citation, 2)
                else:
                    yield (id, citation)

        LOG.info('Discarded {:,} papers'.format(bad))

