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

A named set of default arguments for `steps <step_>`.

Specifying different sets of default arguments can be useful for rendering the
same recipes, for example, on different areas, or with different branding or
graphic layouts.


.. _input:

Input
=====

Input data (usually in `GRIB <https://en.wikipedia.org/wiki/GRIB>` format) that
can be used by a step_ of a recipe_.


.. _mixer:

Mixer
=====

A repository of `steps <step_>` that can be executed by a recipe_.

It is defined in arkimaps' code. Currently only one mixer is provided called
``default``, in ``arkimapslib/mixers.py``.


.. _product:

Product
=======

An image file produced by a recipe_.


.. _recipe:

Recipe
======

Defines what is needed to turn `inputs <input_>` into a product_.

It can contain:

* Zero or more `inputs <input_>`
* The name of the mixer_ to use for processing `inputs <input_>` (by default:
  ``default``)
* A set of `steps <step_>` to perform with the mixer_ on the `inputs <input_>`
* Zero or more `flavors <flavor_>` that define set of default parameters for
  recipe `steps <step_>`.

To allow to define only once some elements common to multiple recipes, there
can be recipes that only define inputs or flavours for reuse by other recipes,
but provide no sequence of steps themselves.


.. _step:

Step
====

One processing element on a recipe_. Each step has a name and optional
arguments.

The set of available step names are defined by the mixer_ used for processing.

Arguments for steps that are not explicitly provided by recipes can be provided
by `flavours <flavour_>`.
