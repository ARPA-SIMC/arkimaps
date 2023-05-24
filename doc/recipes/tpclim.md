# tpclim: Total precipitation (climate elaboration)

Mixer: **default**

## Inputs

* **tpclim**:
    * **Arkimet matcher**: `product:GRIB2,,,001,008,,;timerange:Timedef,0s,11,,`
    * **grib_filter matcher**: `parameterCategory == 1 and parameterNumber == 8 and discipline == 0 and typeOfStatisticalProcessing != 10 and indicatorOfUnitOfTimeRange == 2`

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
  "grib": "tpclim"
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
    "contour_shade_min_level": 0.0,
    "contour_level_list": [
      0.0,
      1.0,
      5.0,
      10.0,
      20.0,
      30.0,
      40.0,
      50.0,
      75.0,
      100.0,
      150.0,
      200.0,
      250.0,
      300.0,
      400.0,
      500.0,
      600.0,
      700.0,
      800.0,
      1000.0,
      1200.0,
      1400.0,
      1600.0,
      1800.0,
      2000,
      2500
    ],
    "contour_shade_colour_list": [
      "rgb(1,1,1)",
      "rgb(0.831,1,1)",
      "rgb(0.667,1,1)",
      "rgb(0,1,1)",
      "rgb(0,0.875,1)",
      "rgb(0,0.749,1)",
      "rgb(0,0.647,1)",
      "rgb(0,0.549,1)",
      "rgb(0,0.447,1)",
      "rgb(0,0.349,1)",
      "rgb(0,0.173,1)",
      "rgb(0,0,1)",
      "rgb(0.224,0,1)",
      "rgb(0.447,0,1)",
      "rgb(0.596,0,1)",
      "rgb(0.749,0,1)",
      "rgb(0.875,0,1)",
      "rgb(1,0,1)",
      "rgb(0.898,0,0.898)",
      "rgb(0.8,0,0.8)",
      "rgb(0.698,0,0.698)",
      "rgb(0.6,0,0.6)",
      "rgb(0.498,0,0.498)",
      "rgb(0.4,0,0.4)",
      "rgb(0.4,0,0.2)"
    ],
    "legend": true,
    "legend_display_type": "continuous",
    "legend_title": true,
    "legend_text_colour": "black",
    "legend_text_font_size": 0.4,
    "legend_title_font_size": 0.5,
    "legend_title_text": "Total precipitation [mm]",
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

