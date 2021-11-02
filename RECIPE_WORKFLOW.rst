===============
Recipe workflow
===============

Documentation of how data is processed to go from a recipe to a final product.

See ``GLOSSARY.rst`` for a detailed explanation of the terms used in arkimet.


Loading recipes
===============

Recipes are loaded by scanning the recipes directory recursively for ``.yaml`` files
(see ``arkimapslib.kitchen.Kitchen.load_recipes()``).

The ``inputs`` part of each recipe is added to a global repository of input
definitions.

The ``flavours`` part of each recipe is added to a global repository of flavour
definitions.

For each recipe which has a ``recipe`` section, a product is created with the
same name as the name of the recipe file (without ``.yaml`` extension).


Filling the pantry
==================

arkimaps is designed to process an unorganized stream of GRIB data.

The stream is processed matching each GRIB data with the filter expressions
provided in the input definitions found in recipes, storing each matched GRIB
in a directory called ``pantry`` inside the working directory.

Inside the pantry, each input found in this way is stored as
``[$model_]$name+$step.grib``, where:

* ``$model`` is the model name as found in the input definition, if the input
  definition defined filtering rules for different models
* ``$name`` is the input name
* ``$step`` is the step detected for this input: ``endStep`` is used when
  filtering using ecCodes_, and a function of the Timerange metadata is used
  when filtering using Arkimet_.

See ``EccodesPantry.fill()`` and ``ArkimetPantry.fill()`` in
``arkimapslib.pantry``.


Making orders
=============

For each flavour requested for rendering, and for each recipe that can be
rendered in that flavour, the pantry is scanned to see which inputs are
available and for which steps, and the result is used to build a list of all
products that are expected in the output.

During this process, arkimaps also computes those input data that need to be
generated as derivations of other input data.

Filtering recipes
-----------------

A flavour can optionally define a ``recipes_filter`` which limits what recipes
can be built using that flavour.

As a first step of making orders, each flavour limits the recipes built with it
to only those it allows.

See ``arkimapslib.kitchen.WorkingKitchen.make_orders()``

Postprocessing input data
-------------------------

Inputs defined in recipes have a ``type`` that defines if they correspond to
GRIB data as found in the stream to be processed, if they need to be fetched
from other locations, or if they need to be computed from other inputs.

Input types are defined in ``arkimapslib/inputs.py`` and can currently be:

* ``default``: a GRIB matched from the stream of data to be processed
* ``static``: a file distributed with Arkimaps
* ``shape``: a shapefile_ distributed with Arkimaps
* ``cat``: concatenation of two or more other inputs
* ``decumulate``: the output of decumulation of another input performed with vg6d_transform_
* ``vg6d_transform``: the output of vg6d_transform_ run on another input, with
  arguments taken from the input definition

Input types such as ``cat`` can be derived from one or more other inputs by
computation, and Arkimaps will handle the chain of dependencies correctly
regardless of where inputs are defined in the recipe directory.

The output of input postprocessors is split by step using ecCodes_'
``endStep``, and stored in the pantry as ``$name+$step.grib``.


Computing model steps for which an order can be made
----------------------------------------------------

For each recipe, arkimaps scans its recipe steps to see what inputs they use,
building a list of inputs used by the recipe.

For each input used by the recipe, arkimaps queries the pantry for the set of
model steps that are available for it, and intersects all sets found.

The result is the list of model steps that are available for all inputs of the
recipe: an order made for those steps will have all needed inputs available for
rendering.

See ``arkimapslib.flavours.Flavour.make_orders()``


Generating the orders list
--------------------------

Having computed all the inputs needed for all model step for which a product
can be computed, arkimet builds a list of orders for the renderer, one for each
product.

For each order, arkimaps also computes the list of recipe steps found in the
recipe, plus all the arguments for each step, computed taking the current
flavour into account.



Rendering orders
================

Once an order has been prepared with all its inputs, rendering it only needs
executing all recipe steps in order, and writing the resulting image to the
working directory. This is done in ``arkimapslib.orders.Order.prepare()``.

Since each order is self-contained, it can be rendered in parallel together
with all other orders. This is orchestrated by
``arkimapslib.render.Renderer.renderer``, which distributes the orders to be
rendered to a to a multiprocessing pool of simple executors.


.. _ecCodes: https://confluence.ecmwf.int/display/ECC/ecCodes+Home
.. _Arkimet: https://github.com/ARPA-SIMC/arkimet
.. _shapefile: https://en.wikipedia.org/wiki/Shapefile
.. _vg6d_transform: https://github.com/ARPA-SIMC/libsim
