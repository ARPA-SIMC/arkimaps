# sea_dslm: Deviation of sea level from mean

Mixer: **default**

## Inputs

* **dslm**:
    * **Arkimet matcher**: `product:GRIB2,,,003,001,,;level:GRIB2S,001,,`
    * **grib_filter matcher**: `editionNumber == 2 and parameterCategory == 3 and parameterNumber == 1`

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
  "grib": "dslm"
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
    "contour_label_height": 0.4,
    "contour_label_colour": "navy",
    "contour_label_frequency": 1,
    "contour_label_blanking": false,
    "contour_shade": true,
    "contour_level_list": [
      -1.0,
      -0.8,
      -0.6,
      -0.4,
      -0.2,
      0.0,
      0.2,
      0.4,
      0.6,
      0.8,
      1.0,
      1.2,
      1.4,
      1.6,
      1.8,
      2.0
    ],
    "contour_level_selection_type": "list",
    "contour_shade_colour_list": [
      "#6600ff",
      "#0000ff",
      "#0078ff",
      "#00b4fa",
      "#00e6fa",
      "#00fcbe",
      "#deff19",
      "#ffff36",
      "#ffe600",
      "#ffb500",
      "#ff7b00",
      "#fe0000",
      "#d70000",
      "#b90000",
      "#960000"
    ],
    "contour_shade_colour_method": "list",
    "contour_shade_method": "area_fill",
    "legend": true,
    "legend_display_type": "continuous",
    "legend_title": true,
    "legend_title_text": "Deviation of sea level from mean [m]",
    "legend_text_colour": "black",
    "legend_text_font_size": 0.4,
    "legend_title_font_size": 0.5,
    "legend_automatic_position": "right"
  }
}
```

### add_contour

Add contouring of the previous data

With arguments:
```
{
  "params": {
    "contour": true,
    "contour_shade": false,
    "contour_level_selection_type": "interval",
    "contour_interval": 0.025,
    "contour_line_colour": "#222222",
    "contour_line_thickness": 1,
    "contour_highlight": true,
    "contour_highlight_frequency": 4,
    "contour_highlight_colour": "#000000",
    "contour_highlight_thickness": 2,
    "contour_label": false,
    "legend": false
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

