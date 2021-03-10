# tcc: Total cloud cover

Mixer: **default**

## Inputs

* **tcc**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,71`
        * **grib_filter matcher**: `shortName is "clct"`
        * **mgrib {k}**: `False`
        * **mgrib {k}**: `0.08`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,,2,71`
        * **grib_filter matcher**: `shortName is "clct"`
        * **mgrib {k}**: `False`
        * **mgrib {k}**: `0.08`

## Steps

### add_basemap

Add a base map


### add_coastlines_bg

Add background coastlines

With arguments:
```
{
  "params": {
    "map_coastline_general_style": "background"
  }
}
```

### add_grib

Add a grib file

With arguments:
```
{
  "name": "tcc"
}
```

### add_contour

Add contouring of the previous data

With arguments:
```
{
  "params": {
    "contour": false,
    "contour_highlight": false,
    "contour_hilo": false,
    "contour_label": false,
    "contour_level_list": [
      1.0,
      2.0,
      3.0,
      4.0,
      5.0,
      6.0,
      7.0,
      8.0
    ],
    "contour_level_selection_type": "list",
    "contour_shade": true,
    "contour_shade_colour_list": [
      "rgb(0.96,0.96,1.0)",
      "rgb(0.88,0.89,0.95)",
      "rgb(0.8,0.83,0.9)",
      "rgb(0.72,0.76,0.86)",
      "rgb(0.64,0.69,0.81)",
      "rgb(0.56,0.62,0.76)",
      "rgb(0.49,0.56,0.71)"
    ],
    "contour_shade_colour_method": "list",
    "contour_shade_method": "area_fill",
    "contour_interpolation_ceiling": 7.99,
    "legend": true,
    "legend_title": true,
    "legend_title_text": "Total cloud cover [okta]"
  }
}
```

### add_coastlines_fg

Add foreground coastlines


### add_grid

Add a coordinates grid


### add_boundaries

Add political boundaries


