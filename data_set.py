import luigi
import commons
from os import path


class TxtWriter:
    '''Writes txt formats of graphs, which are source_id, target_id, value\n
    '''
    def __init__(self, fp):
        self.mapping = mapping = defaultdict(count().__next__)
        self.fp = fp
        self.first = True

    def add_edge(source, target, time):
        if not self.first:
            self.fp.write('\n')
        else:
            self.first = False
        fp.write('{} {} {}'.format(
            self.mapping[source], self.mapping[target], time))

    def add_edges(self, edges):
        for edge in edges:
            self.add_edge(edge)


class Dataset(luigi.Task):
    '''
    file_formats:
    jsonlines: dicts with keys: [source, target, value], one per line
    json: same as jsonlines but all in one json
    txt: source_id target_id value\n
    '''
    dataset = luigi.Parameter()
    file_format = luigi.Parameter()

    def output(self):
        path = path.join(commons['build_dir'], dataset, 'graph.' + file_format)
        return luigi.LocalTarget(path)

    def run(self):
        if dataset == 'twitter_at':
            import twitter
            edges = twitter.twitter_at()
        else:
            raise ValueError('invalid dataset')

        if file_format == 'txt':
            with self.output().open('w') as fp:
                txt_writer = IdBuilder(fp)
                txt_writer.add_edges(edges)
        elif file_format == 'jsonlines':
            raise NotImplemented()
        else:
            raise ValueError('invalid format')

