# Extending an existing recipe

You can create a recipe that builds on an existing recipe, applying only a few changes.

Suppose you want to extend this recipe, changing the colour list:

```yaml
# kindex.yaml
---
description: K-index
inputs:
  kindex:
    type: expr
    inputs: [t500, t700, t850, td700, td850]
    expr: kindex = t850 - t500 + td850 - (t700 - td700)
recipe:
 - step: add_basemap
 - step: add_coastlines_bg
 - step: add_grib
   id: source
   grib: kindex
 - step: add_contour
   params:
    contour: off
    contour_shade: on
    contour_level_selection_type: list
    contour_shade_colour_method: list
    contour_shade_method: area_fill
    contour_shade_colour_list: [ "cyan", "green", "yellow", "red" ]
    contour_level_list: [ 25, 30, 35, 40, 60 ]
    contour_highlight: off
    contour_hilo: off
    legend: on
    legend_title: on
    legend_text_font_size: 0.4
    legend_title_text: "K index [n]"
    legend_text_colour: black
    legend_title_font_size: 0.5
    legend_automatic_position: right
 - step: add_coastlines_fg
 - step: add_grid
 - step: add_boundaries
 - step: add_user_boundaries
 - step: add_geopoints
 - step: add_symbols
```

First, you need to give an ID to its `add_contour` step, so it can be referenced later:

```yaml
# …
 - step: add_contour
   id: contour
   params:
    contour: off
# …
```

Then you can create a new recipe like this:

```yaml
# kindex-gray
description: Grayscale K-index
extends: kindex
change:
  # The ID of the step to change
  source:
    # Replace the value of 'grib'
    grib: kindex1
  # The ID of the step to change
  contour:
    # For 'params', there is another step of merging
    params:
      # Change the value of a key
      contour_shade_colour_list: [ "#ffffff", "#bbbbbb", "#777777", "#333333" ]
      # Remove a key (a value of None is interpreted as intention to remove)
      contour_highlight:
```

Currently only 'change' is supported, but more extension methods can be added
if needed.

Note that the ID defaults to the step name (like `add_contour` in this case),
which can be enough if there is only one step with the given name. If there are
multiple ones, changes only apply to the first one.


# How 'change' works

Given two dictionaries:

* If a key is given that matches a key in the original, it is replaced.
* If a key is given that does not match any in the original, it is added.
* If a key is given with an empty value, the original, if present, is
  discarded.

This is applied twice:

* In the original set of keys, except for `params`
* In the value of `params`
