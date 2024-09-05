# hzero: Height of zero degree level

Mixer: **default**

## Notes

for IFS model it needs both "deg0l" and "z" variables

## Inputs

* **hzero**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,80,201,84;level:GRIB1,4`
        * **grib_filter matcher**: `shortName is "hzerocl"`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,003,006,,;level:GRIB2D,004,000,0000000000,101,,`
        * **grib_filter matcher**: `centre != 98 and shortName is "h" and editionNumber == 2`
    * Model **ifs**:
        * **Preprocessing**: groundtomsl
        * **Inputs**: z, hzeroground

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
  "grib": "hzero"
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
    "contour_shade_colour_method": "list",
    "contour_shade_colour_list": [
      "black",
      "white",
      "mustard",
      "purple",
      "violet",
      "navy",
      "blue",
      "greenish_blue",
      "sky",
      "cyan",
      "turquoise",
      "green",
      "avocado",
      "bluish_green",
      "kelly_green",
      "olive",
      "evergreen",
      "rgb(0.,0.28,0.16)",
      "rgb(1.,1.,0.)",
      "rgb(1.,0.9,0.)",
      "rgb(1.,0.8,0.)",
      "rgb(1.,0.7,0.)",
      "rgb(1.,0.6,0.)",
      "rgb(1.,0.5,0.)",
      "rgb(1.,0.4,0.)",
      "rgb(1.,0.3,0.)",
      "rgb(1.,0.2,0.)",
      "rgb(1.,0.,0.)",
      "rgb(0.9,0.,0.)",
      "rgb(0.8,0.,0.)",
      "rgb(0.7,0.,0.)",
      "rgb(0.6,0.,0.)"
    ],
    "contour_shade_method": "area_fill",
    "contour_level_selection_type": "list",
    "contour_level_list": [
      -999,
      0,
      50,
      100,
      150,
      200,
      250,
      300,
      350,
      400,
      450,
      500,
      550,
      600,
      700,
      800,
      900,
      1000,
      1100,
      1200,
      1300,
      1400,
      1500,
      1600,
      1700,
      1800,
      1900,
      2000,
      2250,
      2500,
      3000,
      3500,
      4000
    ],
    "legend": true,
    "legend_display_type": "continuous",
    "legend_title": true,
    "legend_title_text": "Height of zero degree level (m)",
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

