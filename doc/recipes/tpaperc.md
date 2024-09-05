# tpaperc: Total precipitation anomaly percentage (climate elaboration)

Mixer: **default**

## Inputs

* **tpaperc**:
    * **Arkimet matcher**: `skip`
    * **grib_filter matcher**: `discipline == 192 and parameterCategory == 171 and parameterNumber == 228 and typeOfStatisticalProcessing == 10`

## Steps

### add_basemap

Add a base map

With arguments:
```
{
  "params": {
    "page_id_line": false,
    "output_width": 1280,
    "subpage_map_projection": "cylindrical",
    "subpage_lower_left_longitude": 2.5,
    "subpage_lower_left_latitude": 35.0,
    "subpage_upper_right_longitude": 20.0,
    "subpage_upper_right_latitude": 50.0,
    "page_x_length": 38,
    "page_y_length": 31,
    "super_page_x_length": 40,
    "super_page_y_length": 32,
    "subpage_x_length": 34,
    "subpage_y_length": 30,
    "subpage_x_position": 2,
    "subpage_y_position": 1,
    "map_grid": true,
    "map_grid_latitude_reference": 45.0,
    "map_grid_longitude_reference": 0.0,
    "map_grid_longitude_increment": 2.5,
    "map_grid_latitude_increment": 2.5,
    "map_grid_colour": "grey",
    "map_grid_line_style": "dash",
    "map_label_colour": "black",
    "map_label_height": 0.4,
    "map_label_latitude_frequency": 1
  }
}
```

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
  "grib": "tpaperc"
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
    "contour_label_blanking": "off",
    "contour_label_height": 0.8,
    "contour_label_frequency": 1,
    "contour_level_selection_type": "level_list",
    "contour_shade": "on",
    "contour_shade_colour_method": "list",
    "contour_shade_method": "area_fill",
    "contour_shade_min_level": -100.0,
    "contour_level_list": [
      -100.0,
      -75.0,
      -50.0,
      -45.0,
      -40.0,
      -35.0,
      -30.0,
      -25.0,
      -20.0,
      -15.0,
      -10.0,
      -5.0,
      5.0,
      10.0,
      15.0,
      20.0,
      25.0,
      30.0,
      40.0,
      50.0,
      75.0,
      100.0,
      150.0,
      200.0,
      300.0,
      400.0,
      500.0,
      1000.0
    ],
    "contour_shade_colour_list": [
      "rgb(0.8,0,0)",
      "rgb(0.898,0,0)",
      "rgb(1,0,0)",
      "rgb(1,0.2,0)",
      "rgb(1,0.4,0)",
      "rgb(1,0.498,0)",
      "rgb(1,0.6,0)",
      "rgb(1,0.698,0)",
      "rgb(1,0.8,0)",
      "rgb(1,0.898,0)",
      "rgb(1,1,0)",
      "rgb(1,1,1)",
      "rgb(0.498,1,1)",
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
      "rgb(0.875,0,1)"
    ],
    "legend": true,
    "legend_display_type": "continuous",
    "legend_title": true,
    "legend_text_colour": "black",
    "legend_text_font_size": 0.4,
    "legend_title_font_size": 0.5,
    "legend_title_text": "Total precipitation anomaly percentage [%]",
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
    "map_boundaries": true,
    "map_boundaries_colour": "#000000",
    "map_administrative_boundaries_countries_list": [
      "ITA"
    ],
    "map_administrative_boundaries_colour": "#000000",
    "map_administrative_boundaries_style": "solid",
    "map_administrative_boundaries": true,
    "map_coastline_thickness": 2
  }
}
```

### add_user_boundaries

Add user-defined boundaries from a shapefile

With arguments:
```
{
  "skip": true,
  "params": {
    "map_user_layer": "on",
    "map_user_layer_colour": "blue"
  }
}
```

### add_geopoints

Add geopoints

With arguments:
```
{
  "skip": true
}
```

### add_symbols

Add symbols settings

With arguments:
```
{
  "skip": true,
  "params": {
    "symbol_type": "marker",
    "symbol_marker_index": 15,
    "legend": "off",
    "symbol_colour": "black",
    "symbol_height": 0.28
  }
}
```

