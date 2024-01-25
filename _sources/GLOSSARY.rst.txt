=================
arkimaps glossary
=================

Arkimaps processing uses terminology taken from a metaphore of cooking.

While the cooking metaphore makes the terminology mostly intuitive, it might be
useful to have exact definitions of the terms used by arkimaps in the context
of arkimaps.

Those are provided in this file.


.. _flavor:

Flavor
======

A named set of default arguments for `recipe steps`_.

Specifying different sets of default arguments can be useful for rendering the
same recipes, for example, on different areas, or with different branding or
graphic layouts.


.. _input:

Input
=====

Input data (usually in `GRIB <https://en.wikipedia.org/wiki/GRIB>`_ format) that
can be used by a `recipe step`_.


.. _mixer:

Mixer
=====

A repository of `recipe steps`_ that can be executed by a recipe_.

It is defined in arkimaps' code. Currently only one mixer is provided called
``default``, in ``arkimapslib/mixers.py``.


.. _`model step`:

Model step
==========

A step in the output of a forecast model, defined in hours from the reference
time of a model run.


.. _order:

Order
=====

An order is a collection of all the data needed to generate one single
product_.

Typically, for each recipe_ there is an order for each `model step`_ for which
all required input_ data are available.


.. _pantry:

Pantry
======

Repository of input_ data available to `recipe steps`_.


.. _product:

Product
=======

An image file produced by a recipe_.


.. _recipe:

Recipe
======

Defines what is needed to turn inputs_ into a product_.

It can contain:

* Zero or more inputs_
* The name of the mixer_ to use for processing inputs_ (by default:
  ``default``)
* A set of `recipe steps`_ to perform with the mixer_ on the inputs_
* Zero or more flavors_ that define set of default parameters for
  recipe `recipe steps`_.

To allow to define only once some elements common to multiple recipes, there
can be recipes that only define inputs or flavours for reuse by other recipes,
but provide no sequence of steps themselves.


.. _`recipe step`:

Recipe step
===========

One processing element on a recipe_. Each step has a name and optional
arguments.

The set of available step names are defined by the mixer_ used for processing.

Arguments for steps that are not explicitly provided by recipes can be provided
by flavors_.



.. _flavors: `flavor`_
.. _inputs: `input`_
.. _recipes: `recipe`_
.. _`recipe steps`: `recipe step`_
