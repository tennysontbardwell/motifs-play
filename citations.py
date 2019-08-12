import json
import os
import itertools
import collections

import networkx as nx

import commons
from multilayer import Multilayer

LOG = commons.make_log(__name__)


class PaperLookup:
    def __init__(self, key):
        self.key = key
        self.path = os.path.join(commons.settings['build_dir'], 'citations',
                                'paper_lookup_key__{}.json'.format(key))

    @commons.file_cached_class
    def _build_lookup(self, path):
        c = CitationInterface()
        # paper_id : str -> value_id : int
        paper_map = {}
        # value_id_map_rev = value : str -> value_id : int
        value_id_map_rev = collections.defaultdict(itertools.count().__next__)
        for paper in c.paper_iter():
            id_ = paper['id']
            value = paper[self.key]
            value_id = value_id_map_rev[value]
            paper_map[id_] = value_id

        # value_id_map = value_id : int -> value : str
        value_id_map = {v: k for k, v in value_id_map_rev.items()}
        data = {
            'paper_map': paper_map,
            'value_id_map': value_id_map
        }
        with open(path, 'w') as fp:
            json.dump(data, fp)

    def load_lookup(self):
        self._build_lookup(self.path)
        with open(self.path) as fp:
            data = json.load(fp)
        self.paper_map = data['paper_map']
        self.value_id_map = data['value_id_map']

    def lookup_paper(self, paper_id: int):
        value_id = self.paper_map.get(paper_id, None)
        if value_id == None:
            return None
        value_id = str(value_id)  # json keys are str
        return self.value_id_map[value_id]


class CitationInterface:
    def __init__(self, limit=None, journal_filter=None):
        self.limit=limit
        self.journal_filter = journal_filter
        if journal_filter is not None:
            self.journal_lookup = PaperLookup('journalName')
            self.journal_lookup.load_lookup()

    def filter_paper_id(self, paper_id):
        '''Returns True if this paper_id should be kept'''
        if self.journal_filter is None:
            return True
        else:
            journal = self.journal_lookup.lookup_paper(paper_id)
            return journal in self.journal_filter
    
    def paper_iter(self):
        dir_ = commons.settings['data']['semanticscholar']
        count = itertools.count()
        with open(os.path.join(dir_, 'papers-2017-10-30.json')) as fp:
            for line in fp:
                j = json.loads(line)
                if not self.filter_paper_id(j['id']):
                    continue

                i = count.__next__()
                if i == 10**4:
                    LOG.info('{:,} papers read'.format(i))
                if i % 10**6 == 0 and i != 0:
                    LOG.info('{:,} papers read'.format(i))
                if i+1 == self.limit:
                    LOG.info('limit of {} reached'.format(self.limit))
                    break

                yield j

    def colored_graph(self, path) -> Multilayer:
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

        g = Multilayer(path)
        if g.loaded:
            LOG.info('Graph cached at {}'.format(path))
            return g

        for paper in self.paper_iter():
            id_ = paper['id']
            journal = paper['journalName']
            authors = get_authors(paper)
            in_citations = paper['inCitations']
            out_citations = paper['outCitations']

            if authors is None or len(authors) == 0:
                bad += 1
                continue

            g.add_node(id_, journal, 'paper')
            for author in authors:
                g.add_node(author, None, 'author')
                g.add_edge(author, id_, 'authorship')
            for citation in in_citations:
                if not self.filter_paper_id(citation):
                    bad += 1
                    continue
                citation_journal = self.journal_lookup.lookup_paper(citation)
                g.add_node(citation, citation_journal, 'paper')
                g.add_edge(id_, citation, 'citation')

        LOG.info('Discarded {:,} papers'.format(bad))
        g.write()
        return g

