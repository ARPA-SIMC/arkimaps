# tp24h: Total precipitation 24h

Mixer: **default**

## Inputs

* **tp**:
    * **Option 1**:
        * **Preprocessing**: decumulation
        * **Arkimet matcher**: `product:GRIB1,,2,61`
        * **grib_filter matcher**: `shortName is "tp"`
    * **Option 2**:
        * **Preprocessing**: decumulation
        * **Arkimet matcher**: `product:GRIB1,,2,61`
        * **grib_filter matcher**: `shortName is "tp"`

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
  "name": "tp"
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
    "contour_label": "off",
    "contour_level_selection_type": "level_list",
    "contour_shade": "on",
    "contour_shade_colour_method": "list",
    "contour_shade_method": "area_fill",
    "contour_shade_min_level": 0.5,
    "contour_level_list": [
      1.0,
      2.0,
      5.0,
      10.0,
      20.0,
      30.0,
      50.0,
      70.0,
      100.0,
      150.0,
      200.0,
      300.0,
      500.0
    ],
    "contour_shade_colour_list": [
      "rgb( 0.686,1.000,1.000)",
      "rgb( 0.000,1.000,1.000)",
      "rgb( 0.447,0.639,1.000)",
      "rgb( 0.000,0.498,1.000)",
      "rgb( 0.145,0.000,1.000)",
      "rgb( 0.145,0.435,0.435)",
      "rgb( 1.000,1.000,0.000)",
      "rgb( 1.000,0.498,0.000)",
      "rgb( 1.000,0.000,0.000)",
      "rgb(1.000,0.000,1.000)",
      "rgb(0.615,0.403,0.937)",
      "rgb(0.5,0.,0.5)"
    ],
    "legend": true,
    "legend_display_type": "continuous",
    "legend_title": true,
    "legend_title_text": "Precipitation [mm]",
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


