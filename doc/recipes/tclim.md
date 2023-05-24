# tclim: Temperature at 2 metres

Mixer: **default**

## Inputs

* **tclim**:
    * **Arkimet matcher**: `skip`
    * **grib_filter matcher**: `parameterCategory == 0 and discipline == 0 and (parameterNumber == 0 or parameterNumber == 4 or parameterNumber == 5) and typeOfStatisticalProcessing != 11`
    * **mgrib {k}**: `False`
    * **mgrib {k}**: `-273.15`

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
  "grib": "tclim"
}
```

### add_contour

Add contouring of the previous data

With arguments:
```
{
  "params": {
    "contour": "off",
    "contour_highlight": "off",
    "contour_hilo": "off",
    "contour_label": "on",
    "contour_label_frequency": 1,
    "contour_level_selection_type": "level_list",
    "contour_shade": "on",
    "contour_shade_colour_method": "list",
    "contour_shade_method": "area_fill",
    "contour_shade_min_level": -30.0,
    "contour_level_list": [
      -30.0,
      -29.0,
      -28.0,
      -27.0,
      -26.0,
      -25.0,
      -24.0,
      -23.0,
      -22.0,
      -21.0,
      -20.0,
      -19.0,
      -18.0,
      -17.0,
      -16.0,
      -15.0,
      -14.0,
      -13.0,
      -12.0,
      -11.0,
      -10.0,
      -9.0,
      -8.0,
      -7.0,
      -6.0,
      -5.0,
      -4.0,
      -3.0,
      -2.0,
      -1.0,
      0.0,
      1.0,
      2.0,
      3.0,
      4.0,
      5.0,
      6.0,
      7.0,
      8.0,
      9.0,
      10.0,
      11.0,
      12.0,
      13.0,
      14.0,
      15.0,
      16.0,
      17.0,
      18.0,
      19.0,
      20.0,
      21.0,
      22.0,
      23.0,
      24.0,
      25.0,
      26.0,
      27.0,
      28.0,
      29.0,
      30.0,
      31.0,
      32.0,
      33.0,
      34.0,
      35.0,
      36.0,
      37.0,
      38.0,
      39.0,
      40.0,
      41.0,
      42.0,
      60.0
    ],
    "contour_shade_colour_list": [
      "rgb(1,0.8,0)",
      "rgb(1,0.698,0)",
      "rgb(1,0.6,0)",
      "rgb(1,0.498,0)",
      "rgb(1,0.4,0)",
      "rgb(1,0.2,0)",
      "rgb(1,0,0)",
      "rgb(0.898,0,0)",
      "rgb(0.8,0,0)",
      "rgb(0.698,0,0)",
      "rgb(0.6,0,0)",
      "rgb(0.498,0,0)",
      "rgb(0.4,0,0)",
      "rgb(0.4,0,0.2)",
      "rgb(0.4,0,0.4)",
      "rgb(0.498,0,0.498)",
      "rgb(0.6,0,0.6)",
      "rgb(0.698,0,0.698)",
      "rgb(0.8,0,0.8)",
      "rgb(0.898,0,0.898)",
      "rgb(1,0,1)",
      "rgb(0.875,0,1)",
      "rgb(0.749,0,1)",
      "rgb(0.596,0,1)",
      "rgb(0.447,0,1)",
      "rgb(0.224,0,1)",
      "rgb(0,0,1)",
      "rgb(0,0.173,1)",
      "rgb(0,0.349,1)",
      "rgb(0,0.447,1)",
      "rgb(0,0.549,1)",
      "rgb(0,0.647,1)",
      "rgb(0,0.749,1)",
      "rgb(0,0.875,1)",
      "rgb(0,1,1)",
      "rgb(0,0.949,0.898)",
      "rgb(0,0.898,0.8)",
      "rgb(0,0.847,0.647)",
      "rgb(0,0.8,0.498)",
      "rgb(0,0.749,0.247)",
      "rgb(0,0.698,0)",
      "rgb(0.247,0.749,0)",
      "rgb(0.498,0.8,0)",
      "rgb(0.647,0.847,0)",
      "rgb(0.8,0.898,0)",
      "rgb(0.898,0.949,0)",
      "rgb(1,1,0)",
      "rgb(1,0.898,0)",
      "rgb(1,0.8,0)",
      "rgb(1,0.698,0)",
      "rgb(1,0.6,0)",
      "rgb(1,0.498,0)",
      "rgb(1,0.4,0)",
      "rgb(1,0.2,0)",
      "rgb(1,0,0)",
      "rgb(0.898,0,0)",
      "rgb(0.8,0,0)",
      "rgb(0.698,0,0)",
      "rgb(0.6,0,0)",
      "rgb(0.498,0,0)",
      "rgb(0.4,0,0)",
      "rgb(0.4,0,0.2)",
      "rgb(0.4,0,0.4)",
      "rgb(0.498,0,0.498)",
      "rgb(0.6,0,0.6)",
      "rgb(0.698,0,0.698)",
      "rgb(0.8,0,0.8)",
      "rgb(0.898,0,0.898)",
      "rgb(1,0,1)",
      "rgb(0.875,0,1)",
      "rgb(0.749,0,1)",
      "rgb(0.596,0,1)",
      "rgb(0.447,0,1)"
    ],
    "legend": true,
    "legend_display_type": "continuous",
    "legend_title": true,
    "legend_title_text": "Temperature at 2m [\u00b0C]",
    "legend_text_colour": "black",
    "legend_text_font_size": 0.4,
    "legend_title_font_size": 0.5,
    "legend_automatic_position": "right"
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

