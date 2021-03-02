# viwvn_ita: Vertical integral of northward water vapour flux

Mixer: **default**

## Inputs

* **viwvn**:
    * **Arkimet matcher**: `product:GRIB2,98,192,162,72,6`
    * **grib_filter matcher**: `shortName is "viwvn"`
* **mslp**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,2`
        * **grib_filter matcher**: `shortName is "pmsl"`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,,2,2`
        * **grib_filter matcher**: `shortName is "pmsl"`

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
  "name": "viwvn"
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
    "legend_title_text": "Vertical integral of northward water vapour flux",
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


