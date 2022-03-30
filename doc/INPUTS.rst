==================
Recipe input types
==================

Input types are defined in ``arkimapslib/inputs.py``, and this is their
reference manual.

When defined in ``yaml`` recipes, an input can a dict defining the input for
all models, or a list of dict defining the input differently depending on the
model.

Input types such as ``cat`` can be derived from one or more other inputs by
computation, and Arkimaps will handle the chain of dependencies correctly.

Inputs can be defined anywhere in the recipe directory, and dependencies
between them will be handled correctly.


Input type reference
====================


``default``
-----------

A GRIB matched from the stream of data to be processed. The ``arkimet`` keyword
defines an arkimet matcher, and the ``eccodes`` keyword defines a
``grib_filter`` expression, that select data from a stream of model output.

Example::

 t2m:
  - model: cosmo
    arkimet: product:GRIB1,,2,11;level:GRIB1,105,2
    eccodes: centre != 98 and shortName is "2t" and indicatorOfTypeOfLevel == 105 and timeRangeIndicator == 0 and level == 2
  - model: ifs 
    arkimet: product:GRIB1,98,128,167;level:GRIB1,1
    eccodes: centre == 98 and shortName is "2t" and indicatorOfTypeOfLevel == 1 and level == 0 and timeRangeIndicator == 0
  - model: erg5
    arkimet: product:GRIB2,00200,000,000,000,004,000;level:GRIB2S,103,003,0000001800
    eccodes: shortName is "t" and level == 2

If you define inputs differently depending on models, please make sure that the
filter expression can discriminate the model. In the example above, if you
defined ``eccodess`` simply as ``shortname is "2t"`` for both Cosmo and IFS,
then you might end up with a temperature from IFS that is postprocessed using
the Cosmo postprocessing.


``static``
----------

References a file distributed with Arkimaps.

Example::

  puntiCitta:
    type: static
    path: puntiCitta.geo


``shape``
---------

References a shapefile distributed with Arkimaps.

Example::

  sottozoneAllertaER:
    type: shape
    path: shapes/Sottozone_allerta_ER

One cannot use ``static`` for shapefiles, because shapefiles are actually directories.


``cat``
-------

For each level for which all inputs are available, it creates a new GRIB by
concatenating the GRIB data listed as inputs.

Example::

 uv10m:
   type: cat
   inputs: [u10m, v10m]


``decumulate``
--------------

Performs decumulation using vg6d_transform_.

The output of vg6d_transform_is split by step using ecCodes_' ``endStep``, and
stored in the pantry as ``$name+$step.grib``.

Example::

  inputs:
   tp:
     - model: cosmo
       arkimet: product:GRIB1,,2,61
       eccodes: centre != 98 and shortName is "tp"
     - model: ifs
       arkimet: product:GRIB1,98,128,228
       eccodes: centre == 98 and shortName is "tp"
   tpdec1h:
     - type: decumulate
       step: 1
       inputs: tp
   tpdec3h:
     - type: decumulate
       step: 3
       inputs: tp


``vg6d_transform``
------------------

Runs vg6d_transform_ run on another input, with arguments taken from the input
definition.

The output of vg6d_transform_is split by step using ecCodes_' ``endStep``, and
stored in the pantry as ``$name+$step.grib``.

Example::

 wspeed10m:
   type: vg6d_transform
   args: ["--output-variable-list=B11002"]
   inputs: [u10m, v10m]


``or``
------

Choose the first available in a list of possible inputs. This can be used to
implement values that can be computed in different ways depending on available
input values.

Example::

 snowcon:
   - model: cosmo
     arkimet: product:GRIB1,,2,78
     eccodes: shortName is "snow_con" or shortName is "snoc"
 snowgsp:
   - model: cosmo
     arkimet: product:GRIB1,,2,79
     eccodes: shortName is "snow_gsp" or shortName is "lssf"
 snowsum:
   - model: cosmo
     type: vg6d_transform
     args: ["--output-variable-list=B13205"]
     inputs: [snowcon, snowgsp]
 snowcosmo:
   - model: cosmo
     type: or
     inputs: [snowsum, snowgsp]

In this case, if convective snow has been computed, it is added to large scale.
Otherwise, just large scale is used.


``groundtomsl``
---------------

Given two inputs, assume that:

* the first is ground geopotential, and that it is only computed for step 0
* the second is a value computed for all step and measured as height above
  ground

The two values are combined to convert the second value to a value above mean
sea level.

``grib_set`` is applied if present.

Example::

  - model: ifs
    type: groundtomsl
    inputs: [z, alt0ground]                                                
    invalid: -999
    grib_set:
      shortName: deg0l

.. TODO invalid becomes clip


``ratio``
---------

given two inputs, generate a new input dividing the first by the
  second, and optionally applying a multiplication factor

``grib_set`` is applied if present.


Reference of arguments shared by at least two input types
=========================================================

``inputs``
----------

Lists the source inputs that are used to compute this input.

Order can matter: for example, ``cat`` will concate inputs in the order they
are listed.


``grib_set``
~~~~~~~~~~~~

In these input types, you can optionally add a ``grib_set`` dictionary
argument, which is a set of ``key=value`` assignments done via eccodes on the
resulting grib before writing it out.

This can be used to correct the GRIB metadata after processing.


``clip`` argument to groundtomsl and ratio
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In these input types, you can optionally add a ``clip`` expression as a string.

The expression is a Python expression that can use as variables the names of
the source inputs, as well as the name of the current input. The variables will
be numpy arrays. The goal is to change the array named as the current input, to
postprocess it before writing it out.

For example, one can clip like this::

   example:
      type: groundtomsl
      inputs: [z, val]
      clip: example[example < 0] = -999



.. _shapefile: https://en.wikipedia.org/wiki/Shapefile
.. _vg6d_transform: https://github.com/ARPA-SIMC/libsim
.. _ecCodes: https://confluence.ecmwf.int/display/ECC/ecCodes+Home
