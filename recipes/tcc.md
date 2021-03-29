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
    "map_coastline_general_style": "background",
    "map_coastline_resolution": "high"
  }
}
```

### add_grib

Add a grib file

With arguments:
```
{
  "grib": "tcc"
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
    "legend_text_colour": "black",
    "legend_text_font_size": 0.4,
    "legend_title_font_size": 0.5,
    "legend_automatic_position": "right",
    "legend_title_text": "Total cloud cover [okta]"
  }
}
```

### add_coastlines_fg

Add foreground coastlines

With arguments:
```
{
  "params": {
    "map_coastline_sea_shade_colour": "#f2f2f2",
    "map_grid": "off",
    "map_coastline_sea_shade": "off",
    "map_label": "off",
    "map_coastline_colour": "#000000",
    "map_coastline_resolution": "high"
  }
}
```

### add_grid

Add a coordinates grid

With arguments:
```
{
  "params": {
    "map_coastline_general_style": "grid"
  }
}
```

### add_boundaries

Add political boundaries

With arguments:
```
{
  "params": {
    "map_boundaries": "on",
    "map_boundaries_colour": "#504040",
    "map_administrative_boundaries_countries_list": [
      "ITA"
    ],
    "map_administrative_boundaries_colour": "#504040",
    "map_administrative_boundaries_style": "solid",
    "map_administrative_boundaries": "on"
  }
}
```

### add_user_boundaries

Add user-defined boundaries from a shapefile


### add_geopoints

Add geopoints


### add_symbols

Add symbols settings

With arguments:
```
{
  "params": {
    "symbol_type": "marker",
    "symbol_marker_index": 15,
    "legend": "off",
    "symbol_colour": "black",
    "symbol_height": 0.28
  }
}
```

