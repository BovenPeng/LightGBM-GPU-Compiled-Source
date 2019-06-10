Python API
==========

Data Structure API
------------------

.. autoclass:: lightgbm.Dataset
    :members:
    :show-inheritance:

.. autoclass:: lightgbm.Booster
    :members:
    :show-inheritance:


Training API
------------

.. autofunction:: lightgbm.train

.. autofunction:: lightgbm.cv


Scikit-learn API
----------------

.. autoclass:: lightgbm.LGBMModel
    :members:
    :inherited-members:
    :show-inheritance:

.. autoclass:: lightgbm.LGBMClassifier
    :members:
    :inherited-members:
    :show-inheritance:

.. autoclass:: lightgbm.LGBMRegressor
    :members:
    :inherited-members:
    :show-inheritance:

.. autoclass:: lightgbm.LGBMRanker
    :members:
    :inherited-members:
    :show-inheritance:


Callbacks
---------

.. autofunction:: lightgbm.early_stopping

.. autofunction:: lightgbm.print_evaluation

.. autofunction:: lightgbm.record_evaluation

.. autofunction:: lightgbm.reset_parameter


Plotting
--------

.. autofunction:: lightgbm.plot_importance

.. autofunction:: lightgbm.plot_split_value_histogram

.. autofunction:: lightgbm.plot_metric

.. autofunction:: lightgbm.plot_tree

.. autofunction:: lightgbm.create_tree_digraph
