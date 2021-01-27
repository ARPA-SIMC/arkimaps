# wmax: Maximum wind gust speed

Mixer: **default**

## Inputs

* **mcont**:
    * **Arkimet matcher**: `product:GRIB1,98,228,28 or GRIB1,,201,187`
    * **grib_filter matcher**: `shortName is "10fg3" or shortName is "vmax_10m"`

## Steps

### add_basemap

Add a base map

With arguments:
```
{
  "params": {
    "subpage_map_projection": "cylindrical",
    "subpage_lower_left_longitude": -5.0,
    "subpage_lower_left_latitude": 30.0,
    "subpage_upper_right_longitude": 27.0,
    "subpage_upper_right_latitude": 55.0
  }
}
```

### add_coastlines_bg

Add background coastlines


### add_grib

Add a grib file

With arguments:
```
{
  "name": "mcont"
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


### add_grid

Add a coordinates grid


### add_boundaries

Add a coordinates grid


