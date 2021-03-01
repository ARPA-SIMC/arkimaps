# rh2m: Relative humidity at 2 metres

Mixer: **default**

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
  "name": "rh2m"
}
```

### add_contour

Add contouring of the previous data

With arguments:
```
{
  "params": {
    "contour_shade": true,
    "contour_shade_method": "area_fill",
    "contour_level_selection_type": "level_list",
    "contour_shade_colour_method": "list",
    "contour_level_list": [
      0.0,
      20.0,
      40.0,
      60.0,
      80.0,
      90.0,
      100.0
    ],
    "legend": true,
    "contour_highlight": false,
    "contour_label": false,
    "contour_hilo": false,
    "contour": false,
    "contour_shade_colour_list": [
      "red",
      "orange",
      "yellow",
      "green",
      "cyan",
      "blue"
    ]
  }
}
```

### add_coastlines_fg

Add foreground coastlines


### add_grid

Add a coordinates grid


### add_boundaries

Add a coordinates grid


