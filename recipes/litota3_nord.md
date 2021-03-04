# litota3_nord: Averaged total lightning flash density in the last 3 hours

Mixer: **default**

## Inputs

* **litota3_nord**:
    * **Arkimet matcher**: `product:GRIB2,98,0,17,4,5`
    * **grib_filter matcher**: `shortName is "litota3"`

## Steps

### add_basemap

Add a base map

With arguments:
```
{
  "params": {
    "page_id_line": false,
    "output_width": 900,
    "page_y_length": 19.0,
    "subpage_map_projection": "polar_stereographic",
    "subpage_lower_left_longitude": 6.0,
    "subpage_lower_left_latitude": 42.5,
    "subpage_upper_right_longitude": 18.0,
    "subpage_upper_right_latitude": 48.0,
    "subpage_map_vertical_longitude": 10.3,
    "map_grid": true,
    "map_grid_latitude_reference": 45.0,
    "map_grid_longitude_reference": 0.0,
    "map_grid_longitude_increment": 1.0,
    "map_grid_latitude_increment": 1.0,
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


### add_grib

Add a grib file

With arguments:
```
{
  "name": "litota3_nord"
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
    "contour_shade_method": "area_fill",
    "contour_level_selection_type": "level_list",
    "contour_level_list": [
      0.1,
      0.5,
      1.0,
      2.0,
      5.0,
      10.0,
      20.0,
      50.0,
      100.0
    ],
    "contour_shade_colour_method": "list",
    "contour_shade_colour_list": [
      "#CC97A1",
      "#610B1D",
      "#A90528",
      "#FF032F",
      "#FF7126",
      "#FFA12D",
      "#FFDA37",
      "#FDFC3F"
    ],
    "contour_highlight": false,
    "contour_hilo": false,
    "legend": true,
    "legend_title": true,
    "legend_title_text": "Averaged total lightning in the last 3h",
    "legend_display_type": "continuous",
    "legend_automatic_position": "right",
    "legend_text_colour": "black",
    "legend_title_font_size": 0.5
  }
}
```

### add_coastlines_fg

Add foreground coastlines


### add_grid

Add a coordinates grid


### add_boundaries

Add a coordinates grid

With arguments:
```
{
  "params": {
    "map_user_layer": true,
    "map_user_layer_name": "/usr/local/share/libsim-1.1/Sottozone_allerta_ER",
    "map_user_layer_colour": "blue"
  }
}
```

### add_geopoints

Add geopoint file

With arguments:
```
{
  "params": {
    "geo_input_file_name": "/tmp/puntiCitta.geo"
  }
}
```

### add_symbols

Add symbols settings


