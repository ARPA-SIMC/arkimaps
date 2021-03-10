# mcc: Medium Cloud Cover

Mixer: **default**

## Inputs

* **mcc**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,74`
        * **grib_filter matcher**: `shortName is "clcm"`
        * **mgrib {k}**: `False`
        * **mgrib {k}**: `0.08`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,,2,74`
        * **grib_filter matcher**: `shortName is "clcm"`
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
  "name": "mcc"
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
    "contour_min_level": 3.0,
    "contour_max_level": 8.0,
    "contour_level_selection_type": "level_list",
    "contour_shade": true,
    "contour_shade_max_level_colour": "rgba(0,0,255,0.4)",
    "contour_shade_min_level_colour": "rgba(0,0,255,0.0)",
    "contour_shade_method": "area_fill",
    "contour_interpolation_ceiling": 7.99,
    "legend": true,
    "legend_title": true,
    "legend_title_text": "Medium cloud cover [okta]"
  }
}
```

### add_coastlines_fg

Add foreground coastlines


### add_grid

Add a coordinates grid


### add_boundaries

Add political boundaries


