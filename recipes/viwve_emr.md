# viwve_emr: Vertical integral of eastward water vapour flux

Mixer: **default**

## Inputs

* **viwve**:
    * **Arkimet matcher**: `product:GRIB2,98,192,162,71,5`
    * **grib_filter matcher**: `shortName is "viwve"`
* **mslp**:
    * **Arkimet matcher**: `product:GRIB1,98,128,151 or GRIB1,,2,2`
    * **grib_filter matcher**: `shortName is "pmsl" or shortName is "msl"`

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
    "subpage_lower_left_longitude": 9.0,
    "subpage_lower_left_latitude": 43.4,
    "subpage_upper_right_longitude": 13.2,
    "subpage_upper_right_latitude": 45.2,
    "subpage_map_vertical_longitude": 11.0,
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


### add_grib

Add a grib file

With arguments:
```
{
  "name": "viwve"
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
      -1100.0,
      -700.0,
      -500.0,
      -300.0,
      -100.0,
      100.0,
      300.0,
      500.0,
      700.0,
      1100.0
    ],
    "contour_shade_colour_method": "list",
    "contour_shade_colour_list": [
      "#FF00FB",
      "#3300F9",
      "#72A1FB",
      "#00FFFE",
      "#FFFFFF",
      "#FFB12F",
      "#FF4F21",
      "#F8241D",
      "#9D1513"
    ],
    "contour_highlight": false,
    "contour_hilo": false,
    "legend": true,
    "legend_title": true,
    "legend_title_text": "Vertical integral of eastward water vapour flux",
    "legend_display_type": "continuous",
    "legend_automatic_position": "right",
    "legend_text_colour": "black",
    "legend_title_font_size": 0.8
  }
}
```

### add_grib

Add a grib file

With arguments:
```
{
  "name": "mslp",
  "params": {
    "grib_automatic_scaling": false,
    "grib_scaling_factor": 0.01
  }
}
```

### add_contour

Add contouring of the previous data

With arguments:
```
{
  "params": {
    "contour_shade": false,
    "contour": true,
    "contour_level_selection_type": "interval",
    "contour_interval": 4,
    "contour_line_colour": "black",
    "contour_line_thickness": 2,
    "contour_highlight": false,
    "contour_label": true,
    "contour_label_height": 0.4,
    "contour_label_frequency": 2,
    "contour_label_blanking": true,
    "contour_label_colour": "navy",
    "legend": false
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

