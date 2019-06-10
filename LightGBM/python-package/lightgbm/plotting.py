# coding: utf-8
# pylint: disable = C0103
"""Plotting library."""
from __future__ import absolute_import

import warnings
from copy import deepcopy
from io import BytesIO

import numpy as np

from .basic import Booster
from .compat import (MATPLOTLIB_INSTALLED, GRAPHVIZ_INSTALLED, LGBMDeprecationWarning,
                     range_, zip_, string_type)
from .sklearn import LGBMModel


def _check_not_tuple_of_2_elements(obj, obj_name='obj'):
    """Check object is not tuple or does not have 2 elements."""
    if not isinstance(obj, tuple) or len(obj) != 2:
        raise TypeError('%s must be a tuple of 2 elements.' % obj_name)


def _float2str(value, precision=None):
    return ("{0:.{1}f}".format(value, precision)
            if precision is not None and not isinstance(value, string_type)
            else str(value))


def plot_importance(booster, ax=None, height=0.2,
                    xlim=None, ylim=None, title='Feature importance',
                    xlabel='Feature importance', ylabel='Features',
                    importance_type='split', max_num_features=None,
                    ignore_zero=True, figsize=None, grid=True,
                    precision=None, **kwargs):
    """Plot model's feature importances.

    Parameters
    ----------
    booster : Booster or LGBMModel
        Booster or LGBMModel instance which feature importance should be plotted.
    ax : matplotlib.axes.Axes or None, optional (default=None)
        Target axes instance.
        If None, new figure and axes will be created.
    height : float, optional (default=0.2)
        Bar height, passed to ``ax.barh()``.
    xlim : tuple of 2 elements or None, optional (default=None)
        Tuple passed to ``ax.xlim()``.
    ylim : tuple of 2 elements or None, optional (default=None)
        Tuple passed to ``ax.ylim()``.
    title : string or None, optional (default="Feature importance")
        Axes title.
        If None, title is disabled.
    xlabel : string or None, optional (default="Feature importance")
        X-axis title label.
        If None, title is disabled.
    ylabel : string or None, optional (default="Features")
        Y-axis title label.
        If None, title is disabled.
    importance_type : string, optional (default="split")
        How the importance is calculated.
        If "split", result contains numbers of times the feature is used in a model.
        If "gain", result contains total gains of splits which use the feature.
    max_num_features : int or None, optional (default=None)
        Max number of top features displayed on plot.
        If None or <1, all features will be displayed.
    ignore_zero : bool, optional (default=True)
        Whether to ignore features with zero importance.
    figsize : tuple of 2 elements or None, optional (default=None)
        Figure size.
    grid : bool, optional (default=True)
        Whether to add a grid for axes.
    precision : int or None, optional (default=None)
        Used to restrict the display of floating point values to a certain precision.
    **kwargs
        Other parameters passed to ``ax.barh()``.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The plot with model's feature importances.
    """
    if MATPLOTLIB_INSTALLED:
        import matplotlib.pyplot as plt
    else:
        raise ImportError('You must install matplotlib to plot importance.')

    if isinstance(booster, LGBMModel):
        booster = booster.booster_
    elif not isinstance(booster, Booster):
        raise TypeError('booster must be Booster or LGBMModel.')

    importance = booster.feature_importance(importance_type=importance_type)
    feature_name = booster.feature_name()

    if not len(importance):
        raise ValueError("Booster's feature_importance is empty.")

    tuples = sorted(zip_(feature_name, importance), key=lambda x: x[1])
    if ignore_zero:
        tuples = [x for x in tuples if x[1] > 0]
    if max_num_features is not None and max_num_features > 0:
        tuples = tuples[-max_num_features:]
    labels, values = zip_(*tuples)

    if ax is None:
        if figsize is not None:
            _check_not_tuple_of_2_elements(figsize, 'figsize')
        _, ax = plt.subplots(1, 1, figsize=figsize)

    ylocs = np.arange(len(values))
    ax.barh(ylocs, values, align='center', height=height, **kwargs)

    for x, y in zip_(values, ylocs):
        ax.text(x + 1, y,
                _float2str(x, precision) if importance_type == 'gain' else x,
                va='center')

    ax.set_yticks(ylocs)
    ax.set_yticklabels(labels)

    if xlim is not None:
        _check_not_tuple_of_2_elements(xlim, 'xlim')
    else:
        xlim = (0, max(values) * 1.1)
    ax.set_xlim(xlim)

    if ylim is not None:
        _check_not_tuple_of_2_elements(ylim, 'ylim')
    else:
        ylim = (-1, len(values))
    ax.set_ylim(ylim)

    if title is not None:
        ax.set_title(title)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    ax.grid(grid)
    return ax


def plot_split_value_histogram(booster, feature, bins=None, ax=None, width_coef=0.8,
                               xlim=None, ylim=None,
                               title='Split value histogram for feature with @index/name@ @feature@',
                               xlabel='Feature split value', ylabel='Count',
                               figsize=None, grid=True, **kwargs):
    """Plot split value histogram for the specified feature of the model.

    Parameters
    ----------
    booster : Booster or LGBMModel
        Booster or LGBMModel instance of which feature split value histogram should be plotted.
    feature : int or string
        The feature name or index the histogram is plotted for.
        If int, interpreted as index.
        If string, interpreted as name.
    bins : int, string or None, optional (default=None)
        The maximum number of bins.
        If None, the number of bins equals number of unique split values.
        If string, it should be one from the list of the supported values by ``numpy.histogram()`` function.
    ax : matplotlib.axes.Axes or None, optional (default=None)
        Target axes instance.
        If None, new figure and axes will be created.
    width_coef : float, optional (default=0.8)
        Coefficient for histogram bar width.
    xlim : tuple of 2 elements or None, optional (default=None)
        Tuple passed to ``ax.xlim()``.
    ylim : tuple of 2 elements or None, optional (default=None)
        Tuple passed to ``ax.ylim()``.
    title : string or None, optional (default="Split value histogram for feature with @index/name@ @feature@")
        Axes title.
        If None, title is disabled.
        @feature@ placeholder can be used, and it will be replaced with the value of ``feature`` parameter.
        @index/name@ placeholder can be used,
        and it will be replaced with ``index`` word in case of ``int`` type ``feature`` parameter
        or ``name`` word in case of ``string`` type ``feature`` parameter.
    xlabel : string or None, optional (default="Feature split value")
        X-axis title label.
        If None, title is disabled.
    ylabel : string or None, optional (default="Count")
        Y-axis title label.
        If None, title is disabled.
    figsize : tuple of 2 elements or None, optional (default=None)
        Figure size.
    grid : bool, optional (default=True)
        Whether to add a grid for axes.
    **kwargs
        Other parameters passed to ``ax.bar()``.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The plot with specified model's feature split value histogram.
    """
    if MATPLOTLIB_INSTALLED:
        import matplotlib.pyplot as plt
        from matplotlib.ticker import MaxNLocator
    else:
        raise ImportError('You must install matplotlib to plot split value histogram.')

    if isinstance(booster, LGBMModel):
        booster = booster.booster_
    elif not isinstance(booster, Booster):
        raise TypeError('booster must be Booster or LGBMModel.')

    hist, bins = booster.get_split_value_histogram(feature=feature, bins=bins, xgboost_style=False)
    if np.count_nonzero(hist) == 0:
        raise ValueError('Cannot plot split value histogram, '
                         'because feature {} was not used in splitting'.format(feature))
    width = width_coef * (bins[1] - bins[0])
    centred = (bins[:-1] + bins[1:]) / 2

    if ax is None:
        if figsize is not None:
            _check_not_tuple_of_2_elements(figsize, 'figsize')
        _, ax = plt.subplots(1, 1, figsize=figsize)

    ax.bar(centred, hist, align='center', width=width, **kwargs)

    if xlim is not None:
        _check_not_tuple_of_2_elements(xlim, 'xlim')
    else:
        range_result = bins[-1] - bins[0]
        xlim = (bins[0] - range_result * 0.2, bins[-1] + range_result * 0.2)
    ax.set_xlim(xlim)

    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    if ylim is not None:
        _check_not_tuple_of_2_elements(ylim, 'ylim')
    else:
        ylim = (0, max(hist) * 1.1)
    ax.set_ylim(ylim)

    if title is not None:
        title = title.replace('@feature@', str(feature))
        title = title.replace('@index/name@', ('name' if isinstance(feature, string_type) else 'index'))
        ax.set_title(title)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    ax.grid(grid)
    return ax


def plot_metric(booster, metric=None, dataset_names=None,
                ax=None, xlim=None, ylim=None,
                title='Metric during training',
                xlabel='Iterations', ylabel='auto',
                figsize=None, grid=True):
    """Plot one metric during training.

    Parameters
    ----------
    booster : dict or LGBMModel
        Dictionary returned from ``lightgbm.train()`` or LGBMModel instance.
    metric : string or None, optional (default=None)
        The metric name to plot.
        Only one metric supported because different metrics have various scales.
        If None, first metric picked from dictionary (according to hashcode).
    dataset_names : list of strings or None, optional (default=None)
        List of the dataset names which are used to calculate metric to plot.
        If None, all datasets are used.
    ax : matplotlib.axes.Axes or None, optional (default=None)
        Target axes instance.
        If None, new figure and axes will be created.
    xlim : tuple of 2 elements or None, optional (default=None)
        Tuple passed to ``ax.xlim()``.
    ylim : tuple of 2 elements or None, optional (default=None)
        Tuple passed to ``ax.ylim()``.
    title : string or None, optional (default="Metric during training")
        Axes title.
        If None, title is disabled.
    xlabel : string or None, optional (default="Iterations")
        X-axis title label.
        If None, title is disabled.
    ylabel : string or None, optional (default="auto")
        Y-axis title label.
        If 'auto', metric name is used.
        If None, title is disabled.
    figsize : tuple of 2 elements or None, optional (default=None)
        Figure size.
    grid : bool, optional (default=True)
        Whether to add a grid for axes.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The plot with metric's history over the training.
    """
    if MATPLOTLIB_INSTALLED:
        import matplotlib.pyplot as plt
    else:
        raise ImportError('You must install matplotlib to plot metric.')

    if isinstance(booster, LGBMModel):
        eval_results = deepcopy(booster.evals_result_)
    elif isinstance(booster, dict):
        eval_results = deepcopy(booster)
    else:
        raise TypeError('booster must be dict or LGBMModel.')

    num_data = len(eval_results)

    if not num_data:
        raise ValueError('eval results cannot be empty.')

    if ax is None:
        if figsize is not None:
            _check_not_tuple_of_2_elements(figsize, 'figsize')
        _, ax = plt.subplots(1, 1, figsize=figsize)

    if dataset_names is None:
        dataset_names = iter(eval_results.keys())
    elif not isinstance(dataset_names, (list, tuple, set)) or not dataset_names:
        raise ValueError('dataset_names should be iterable and cannot be empty')
    else:
        dataset_names = iter(dataset_names)

    name = next(dataset_names)  # take one as sample
    metrics_for_one = eval_results[name]
    num_metric = len(metrics_for_one)
    if metric is None:
        if num_metric > 1:
            msg = """more than one metric available, picking one to plot."""
            warnings.warn(msg, stacklevel=2)
        metric, results = metrics_for_one.popitem()
    else:
        if metric not in metrics_for_one:
            raise KeyError('No given metric in eval results.')
        results = metrics_for_one[metric]
    num_iteration, max_result, min_result = len(results), max(results), min(results)
    x_ = range_(num_iteration)
    ax.plot(x_, results, label=name)

    for name in dataset_names:
        metrics_for_one = eval_results[name]
        results = metrics_for_one[metric]
        max_result, min_result = max(max(results), max_result), min(min(results), min_result)
        ax.plot(x_, results, label=name)

    ax.legend(loc='best')

    if xlim is not None:
        _check_not_tuple_of_2_elements(xlim, 'xlim')
    else:
        xlim = (0, num_iteration)
    ax.set_xlim(xlim)

    if ylim is not None:
        _check_not_tuple_of_2_elements(ylim, 'ylim')
    else:
        range_result = max_result - min_result
        ylim = (min_result - range_result * 0.2, max_result + range_result * 0.2)
    ax.set_ylim(ylim)

    if ylabel == 'auto':
        ylabel = metric

    if title is not None:
        ax.set_title(title)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    ax.grid(grid)
    return ax


def _to_graphviz(tree_info, show_info, feature_names, precision=None, **kwargs):
    """Convert specified tree to graphviz instance.

    See:
      - https://graphviz.readthedocs.io/en/stable/api.html#digraph
    """
    if GRAPHVIZ_INSTALLED:
        from graphviz import Digraph
    else:
        raise ImportError('You must install graphviz to plot tree.')

    def add(root, parent=None, decision=None):
        """Recursively add node or edge."""
        if 'split_index' in root:  # non-leaf
            name = 'split{0}'.format(root['split_index'])
            if feature_names is not None:
                label = 'split_feature_name: {0}'.format(feature_names[root['split_feature']])
            else:
                label = 'split_feature_index: {0}'.format(root['split_feature'])
            label += r'\nthreshold: {0}'.format(_float2str(root['threshold'], precision))
            for info in show_info:
                if info in {'split_gain', 'internal_value'}:
                    label += r'\n{0}: {1}'.format(info, _float2str(root[info], precision))
                elif info == 'internal_count':
                    label += r'\n{0}: {1}'.format(info, root[info])
            graph.node(name, label=label)
            if root['decision_type'] == '<=':
                l_dec, r_dec = '<=', '>'
            elif root['decision_type'] == '==':
                l_dec, r_dec = 'is', "isn't"
            else:
                raise ValueError('Invalid decision type in tree model.')
            add(root['left_child'], name, l_dec)
            add(root['right_child'], name, r_dec)
        else:  # leaf
            name = 'leaf{0}'.format(root['leaf_index'])
            label = 'leaf_index: {0}'.format(root['leaf_index'])
            label += r'\nleaf_value: {0}'.format(_float2str(root['leaf_value'], precision))
            if 'leaf_count' in show_info:
                label += r'\nleaf_count: {0}'.format(root['leaf_count'])
            graph.node(name, label=label)
        if parent is not None:
            graph.edge(parent, name, decision)

    graph = Digraph(**kwargs)
    add(tree_info['tree_structure'])

    return graph


def create_tree_digraph(booster, tree_index=0, show_info=None, precision=None,
                        old_name=None, old_comment=None, old_filename=None, old_directory=None,
                        old_format=None, old_engine=None, old_encoding=None, old_graph_attr=None,
                        old_node_attr=None, old_edge_attr=None, old_body=None, old_strict=False, **kwargs):
    """Create a digraph representation of specified tree.

    Note
    ----
    For more information please visit
    https://graphviz.readthedocs.io/en/stable/api.html#digraph.

    Parameters
    ----------
    booster : Booster or LGBMModel
        Booster or LGBMModel instance to be converted.
    tree_index : int, optional (default=0)
        The index of a target tree to convert.
    show_info : list of strings or None, optional (default=None)
        What information should be shown in nodes.
        Possible values of list items: 'split_gain', 'internal_value', 'internal_count', 'leaf_count'.
    precision : int or None, optional (default=None)
        Used to restrict the display of floating point values to a certain precision.
    **kwargs
        Other parameters passed to ``Digraph`` constructor.
        Check https://graphviz.readthedocs.io/en/stable/api.html#digraph for the full list of supported parameters.

    Returns
    -------
    graph : graphviz.Digraph
        The digraph representation of specified tree.
    """
    if isinstance(booster, LGBMModel):
        booster = booster.booster_
    elif not isinstance(booster, Booster):
        raise TypeError('booster must be Booster or LGBMModel.')

    for param_name in ['old_name', 'old_comment', 'old_filename', 'old_directory',
                       'old_format', 'old_engine', 'old_encoding', 'old_graph_attr',
                       'old_node_attr', 'old_edge_attr', 'old_body']:
        param = locals().get(param_name)
        if param is not None:
            warnings.warn('{0} parameter is deprecated and will be removed in 2.4 version.\n'
                          'Please use **kwargs to pass {1} parameter.'.format(param_name, param_name[4:]),
                          LGBMDeprecationWarning)
            if param_name[4:] not in kwargs:
                kwargs[param_name[4:]] = param
    if locals().get('strict'):
        warnings.warn('old_strict parameter is deprecated and will be removed in 2.4 version.\n'
                      'Please use **kwargs to pass strict parameter.',
                      LGBMDeprecationWarning)
        if 'strict' not in kwargs:
            kwargs['strict'] = True

    model = booster.dump_model()
    tree_infos = model['tree_info']
    if 'feature_names' in model:
        feature_names = model['feature_names']
    else:
        feature_names = None

    if tree_index < len(tree_infos):
        tree_info = tree_infos[tree_index]
    else:
        raise IndexError('tree_index is out of range.')

    if show_info is None:
        show_info = []

    graph = _to_graphviz(tree_info, show_info, feature_names, precision, **kwargs)

    return graph


def plot_tree(booster, ax=None, tree_index=0, figsize=None,
              old_graph_attr=None, old_node_attr=None, old_edge_attr=None,
              show_info=None, precision=None, **kwargs):
    """Plot specified tree.

    Note
    ----
    It is preferable to use ``create_tree_digraph()`` because of its lossless quality
    and returned objects can be also rendered and displayed directly inside a Jupyter notebook.

    Parameters
    ----------
    booster : Booster or LGBMModel
        Booster or LGBMModel instance to be plotted.
    ax : matplotlib.axes.Axes or None, optional (default=None)
        Target axes instance.
        If None, new figure and axes will be created.
    tree_index : int, optional (default=0)
        The index of a target tree to plot.
    figsize : tuple of 2 elements or None, optional (default=None)
        Figure size.
    show_info : list of strings or None, optional (default=None)
        What information should be shown in nodes.
        Possible values of list items: 'split_gain', 'internal_value', 'internal_count', 'leaf_count'.
    precision : int or None, optional (default=None)
        Used to restrict the display of floating point values to a certain precision.
    **kwargs
        Other parameters passed to ``Digraph`` constructor.
        Check https://graphviz.readthedocs.io/en/stable/api.html#digraph for the full list of supported parameters.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The plot with single tree.
    """
    if MATPLOTLIB_INSTALLED:
        import matplotlib.pyplot as plt
        import matplotlib.image as image
    else:
        raise ImportError('You must install matplotlib to plot tree.')

    for param_name in ['old_graph_attr', 'old_node_attr', 'old_edge_attr']:
        param = locals().get(param_name)
        if param is not None:
            warnings.warn('{0} parameter is deprecated and will be removed in 2.4 version.\n'
                          'Please use **kwargs to pass {1} parameter.'.format(param_name, param_name[4:]),
                          LGBMDeprecationWarning)
            if param_name[4:] not in kwargs:
                kwargs[param_name[4:]] = param

    if ax is None:
        if figsize is not None:
            _check_not_tuple_of_2_elements(figsize, 'figsize')
        _, ax = plt.subplots(1, 1, figsize=figsize)

    graph = create_tree_digraph(booster=booster, tree_index=tree_index,
                                show_info=show_info, precision=precision, **kwargs)

    s = BytesIO()
    s.write(graph.pipe(format='png'))
    s.seek(0)
    img = image.imread(s)

    ax.imshow(img)
    ax.axis('off')
    return ax
