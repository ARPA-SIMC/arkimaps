[![Build Status](https://simc.arpae.it/moncic-ci/arkimaps/centos8.png)](https://simc.arpae.it/moncic-ci/arkimaps/)
[![Build Status](https://simc.arpae.it/moncic-ci/arkimaps/fedora34.png)](https://simc.arpae.it/moncic-ci/arkimaps/)
[![Build Status](https://copr.fedorainfracloud.org/coprs/simc/stable/package/arkimaps/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/simc/stable/package/arkimaps/)

# arkimaps

[Italian README](README_it.md).

Automated framework to render GRIB1/2 data with ECMWF's Magics, using a repository of simple YAML recipes

Supported models:
 * COSMO-LAMI
 * IFS-ECMWF
 * ERG5 (https://dati.arpae.it/dataset/erg5-interpolazione-su-griglia-di-dati-meteo)

Arkimaps works both as a standalone program and as a postprocessor for https://github.com/ARPA-SIMC/arkimet


## Requirements

 - python3 >= 3.7
 - python3-magics
 - eccodes

optional requirements:
 
 - https://github.com/ARPA-SIMC/libsim (for some specific preprocessing, i.e.: accumulated precipitation, relative humidity, wind speed)
 - https://github.com/ARPA-SIMC/arkimet

## Quick start

### Generate plots from a grib file

```
./arkimaps process -o out.tar --grib < test_data.grib
```

### Generate plots from an arkimet query

```
# t2m example:
arki-query --inline 'Reftime:=today 00:00;product:GRIB1,80,2,11;level:g02' http://arkimet.metarpa:8090/dataset/cosmo_5M_ita > test_data.arkimet
./arkimaps process -o out.tar < test_data.arkimet
```

To obtain the parameters need for an arki-query for all available recipes:

```
./arkimaps print-arki-query
```

### Output

The output is a `tar` file containing one directory for each recipe
name; inside every directory there's a plot for each forecast step.

To dinamically unpack the `tar` file:
```
./arkimaps process --filter=eccodes < test.arkimet |tar -xf - -C out/
```

#### Cropping

The `--flavours` option can be used to specify different output
possibilities.

For example, for plots tailored on Emilia-Romagna:
```
./arkimaps process --filter=eccodes --flavours=emro < test.arkimet
```

The full list of implemented areas is available in the directory
[doc/prodotti](../master/doc/prodotti/README.md).

To add new areas it's possibile to add files to the
[flavour directory](../master/recipes/flavours/) (see below at the
section "Creating new flavours for rendering".

### Specifying output products

arkimaps produces by default every possibile output with the input
data. To reduce the number of products there are two ways:
 * copying a subset of recipes from the `recipes` directory in a custom
 path and pointing arkimaps to it with the `--recipes` option
 * filtering the products using a "flavour" (see below at the
section "Creating new flavours for rendering")

Example:
```
./arkimaps process --filter=eccodes --recipes /tmp/temprecipes < test.arkimet
```

## Documentation

 * Informations on implemented products andareas (in Italian only): [doc/prodotti/README.md](../master/doc/prodotti/README.md)
 * [Glossary](../master/doc/GLOSSARY.rst)
 * [Recipe inputs](../master/doc/INPUTS.rst)
 * [Steps for creating new recipes](../master/doc/new_recipe.md)
 * Description on how data are processed from a recipe to the desired output: [Recipe workflow](../master/doc/RECIPE_WORKFLOW.rst).

For a description of all available subcommands:
```
./arkimaps -h
```

For a description of each subcommand:
```
./arkimaps process -h
```

## Informations about recipes

Inputs defined in a recipe are common to all the recipes.
The same input name defined in more recipes results in an error.
It's possible to create recipes without steps just for input definition.

## Debugging and troubleshooting

To speed up debugging, there are some `arkimaps` subcommands:

 * `./arkimaps --debug dispatch workdir` to organize input data in a defined
   work directory
 * `./arkimaps --debug preview workdir t2m+000` to preview a single output from
   a pre-organized work directory

The preview opens `xdg-open`, that usses the predefined system application to open
the resulting image.

If the recipe is nested in a subdirectory, the subdirectory must be specified:
e.g.  `./arkimaps --debug preview workdir standalone/jet+000` (v. #99).

It's possible to specify the reference time using `--date`. The syntax is the same
of the `date --date=` command.


## Creating new flavours for rendering

In the `.yaml` files contained in the `recipes` directory is possible to add a
`flavours` sections that adds rendering variants.
The `arkimaps` rendering subcommands have a `--flavours` option that allows to
choose which variant to use.

The structure of a "flavour" contains:

* `name`: variant name
* `recipes_filter`: list of products (recipes name). If present, only the listed
  recipes would be plotted. Allowed globs (e.g.: `tp*`)
* `steps`: configurations for single steps

The configuration of a "step" may have:

* `skip: yes`: ignore a given step
* `params`: default `params` value if not specified in the single recipe

To generate tiling output, it's possible to add a `tile` keyword containing:

* `zoom_min: Int = 3`: minimum zoom level
* `zoom_max: Int = 5`: maximum zoom level
* `lat_min: Float`: minimum latitude
* `lat_max: Float`: maximum latitude
* `lon_min: Float`: minimum longitude
* `lon_max: Float`: maximum longitude

## Contact and copyright information

arkimaps is Copyright (C) 2020-2022 ARPAE-SIMC <urpsim@arpae.it>

arkimaps is Free Software, licensed under the terms of the GNU General Public
License version 2.
