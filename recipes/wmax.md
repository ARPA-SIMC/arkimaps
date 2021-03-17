# wmax: Maximum wind gust speed

Mixer: **default**

## Inputs

* **wmax**:
    * **Arkimet matcher**: `product:GRIB1,98,228,28 or GRIB1,,201,187`
    * **grib_filter matcher**: `shortName is "10fg3" or shortName is "vmax_10m"`

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
  "grib": "wmax"
}
```

### add_contour

Add contouring of the previous data

With arguments:
```
{
  "params": {
    "contour": false,
    "contour_shade": true,
    "contour_level_selection_type": "list",
    "contour_shade_colour_method": "list",
    "contour_shade_method": "area_fill",
    "contour_shade_colour_list": [
      "green",
      "yellow",
      "orange",
      "red"
    ],
    "contour_level_list": [
      13.9,
      17.1,
      20.6,
      24.2,
      70.0
    ],
    "contour_highlight": false,
    "contour_hilo": false,
    "legend": true,
    "legend_title": true,
    "legend_title_text": "Maximum wind gust speed [m/s]",
    "legend_display_type": "continuous",
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
    "map_coastline_resolution": "medium"
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

