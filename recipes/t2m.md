# t2m: Temperature at 2 metres

Mixer: **default**

## Inputs

* **t2m**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,11;level:GRIB1,105,2`
        * **grib_filter matcher**: `shortName is "2t" and indicatorOfTypeOfLevel == 105 and timeRangeIndicator == 0 and level == 2`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,,2,11;level:GRIB1,105,2`
        * **grib_filter matcher**: `shortName is "2t" and indicatorOfTypeOfLevel == 105 and timeRangeIndicator == 0 and level == 2`

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
  "name": "t2m"
}
```

### add_contour

Add contouring of the previous data

With arguments:
```
{
  "params": {
    "contour": false,
    "contour_highlight_frequency": 100,
    "contour_highlight_thickness": 5,
    "contour_interval": 2.0,
    "contour_label_height": 0.4,
    "contour_label_colour": "navy",
    "contour_label_frequency": 1,
    "contour_label_blanking": false,
    "contour_level_selection_type": "interval",
    "contour_line_thickness": 3,
    "contour_shade": true,
    "contour_shade_colour_list": [
      "rgb(1,0.8,0)",
      "rgb(1,0.6,0)",
      "rgb(1,0.4,0)",
      "rgb(1,0,0)",
      "rgb(0.8,0,0)",
      "rgb(0.6,0,0)",
      "rgb(0.4,0,0)",
      "rgb(0.4,0,0.4)",
      "rgb(0.6,0,0.6)",
      "rgb(0.8,0,0.8)",
      "rgb(1,0,1)",
      "rgb(0.75,0,1)",
      "rgb(0.45,0,1)",
      "rgb(0,0,1)",
      "rgb(0,0.35,1)",
      "rgb(0,0.55,1)",
      "rgb(0,0.75,1)",
      "rgb(0,1,1)",
      "rgb(0,0.9,0.8)",
      "rgb(0,0.8,0.5)",
      "rgb(0,0.7,0.0)",
      "rgb(0.5,0.8,0.0)",
      "rgb(0.8,0.9,0.0)",
      "rgb(1,1,0)",
      "rgb(1,0.8,0)",
      "rgb(1,0.6,0)",
      "rgb(1,0.4,0)",
      "rgb(1,0,0)",
      "rgb(0.8,0,0)",
      "rgb(0.6,0,0)",
      "rgb(0.4,0,0)",
      "rgb(0.4,0,0.4)",
      "rgb(0.6,0,0.6)",
      "rgb(0.8,0,0.8)",
      "rgb(1,0,1)",
      "rgb(0.75,0,1)",
      "rgb(0.45,0,1)"
    ],
    "contour_shade_colour_method": "list",
    "contour_shade_max_level": 46.0,
    "contour_shade_method": "area_fill",
    "contour_shade_min_level": -30.0,
    "legend": true,
    "legend_display_type": "continuous",
    "legend_title": true,
    "legend_title_text": "Temperature at 2m [\u00b0C]",
    "legend_automatic_position": "right"
  }
}
```

### add_coastlines_fg

Add foreground coastlines


### add_grid

Add a coordinates grid


### add_boundaries

Add political boundaries


