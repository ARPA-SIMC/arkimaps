# vis: Visibility

Mixer: **default**

## Inputs

* **vis**:
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,3,20`
        * **grib_filter matcher**: `shortName is "vis"`
    * Model **cosmo**:
        * **vg6d_transform arguments**: --output-variable-list=B20001
        * **Preprocessing**: vg6d_transform
        * **Inputs**: t2m, 2d
    * Model **icon**:
        * **vg6d_transform arguments**: --output-variable-list=B20001
        * **Preprocessing**: vg6d_transform
        * **Inputs**: t2m, 2d

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
  "grib": "vis"
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
    "contour_interpolation_floor": 0.0,
    "contour_shade_colour_list": [
      "rgb(0.004,0.129,0.800)",
      "rgb(0.000,0.671,1.000)",
      "rgb(0.000,0.776,1.000)",
      "rgb(0.000,1.000,0.992)",
      "rgb(0.000,0.996,1.000)",
      "rgb(0.106,0.996,0.573)",
      "rgb(0.420,0.996,0.098)",
      "rgb(0.604,0.996,0.000)",
      "rgb(0.992,0.827,0.110)",
      "rgb(0.996,0.898,0.294)",
      "rgb(1.000,0.965,0.490)",
      "rgb(1.000,1.000,1.000)"
    ],
    "contour_level_list": [
      0,
      50,
      100,
      150,
      200,
      350,
      600,
      800,
      1500,
      3000,
      5000,
      8000,
      10000
    ],
    "legend": true,
    "legend_display_type": "continuous",
    "legend_title": true,
    "legend_title_text": "Visibility [m]",
    "legend_text_colour": "black",
    "legend_text_font_size": 0.4,
    "legend_title_font_size": 0.5,
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

