import json
import os

import pandas as pd
import plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as ff
import numpy as np
import matplotlib.pyplot as plt
import pylab

import commons


@commons.file_cached
def motif_count(path, files):
    jsons = []
    names = []
    for f in files:
        names.append(os.path.basename(f))
        with open(f) as fp:
            jsons.append(json.load(fp))

    keys = list(jsons[0].keys())

    graphs = []
    for name,j in zip(names,jsons):
        data = [j[key]["count"] for key in keys]
        graphs.append(go.Bar(
            x=keys,
            y=data,
            name=name
        ))

    layout = go.Layout(barmode='group')
    fig = go.Figure(data=graphs, layout=layout)
    py.offline.plot(fig, filename=path)


def plot_dist(path, values, label):
    trace = go.Histogram(x=values, xbins=dict(start=min(values),
                    size=0.25, end=max(values)),
                    marker=dict(color='rgb(0, 0, 100)'))

    layout = go.Layout(
        title="Histogram Frequency Counts"
    )

    fig = go.Figure(data=go.Data([trace]), layout=layout)
    py.offline.plot(fig, filename=path)

    
def hist_2d(path, matrix):
    print(matrix)
    import pdb; pdb.set_trace()
    XB = np.linspace(-0,5,100)
    YB = np.linspace(-0,5,100)
    X,Y = np.meshgrid(XB,YB)
    Z = np.exp(-(X**2+Y**2))
    # plt.savefig(path)
    # plt.imsave(path, matrix)
    plt.imshow(Z,interpolation='none')

    # n = 100000
    # x = np.random.standard_normal(n)
    # y = 2.0 + 3.0 * x + 4.0 * np.random.standard_normal(n)
    # plt.hexbin(x,y)
    # plt.savefig(path)


def bar_plot(path, data):
    graphs = []
    for name,j in zip(names,jsons):
        data = [j[key]["count"] for key in keys]
        graphs.append(go.Bar(
            x=list(range(1,len(data)+1)),
            y=data,
            name=name
        ))

    layout = go.Layout(barmode='group')
    fig = go.Figure(data=graphs, layout=layout)
    py.offline.plot(fig, filename=path)

