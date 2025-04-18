# cape: C.A.P.E.

Mixer: **default**

## Inputs

* **cape**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,201,145`
        * **grib_filter matcher**: `centre != 98 and shortName is "cape_ml" and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,59`
        * **grib_filter matcher**: `centre == 98 and shortName is "cape"`
    * Model **ifs_g2**:
        * **Arkimet matcher**: `product:GRIB2,98,0,7,6`
        * **grib_filter matcher**: `centre == 98 and shortName is "mucape"`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,000,007,006,,`
        * **grib_filter matcher**: `centre != 98 and shortName is "cape" and editionNumber == 2`

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
  "grib": "cape"
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
    "contour_level_selection_type": "level_list",
    "contour_shade_colour_method": "calculate",
    "contour_shade_method": "area_fill",
    "contour_shade_colour_list": [
      "rgb(1.00,0.35,0.00)",
      "rgb(1.00,0.55,0.00)",
      "rgb(1.00,0.67,0.00)",
      "rgb(1.00,0.78,0.00)",
      "rgb(1.00,0.89,0.00)",
      "rgb(1.00,1.00,0.00)",
      "rgb(0.75,0.98,0.00)",
      "rgb(0.60,0.86,0.10)",
      "rgb(0.43,0.77,0.20)",
      "rgb(0.30,0.68,0.40)",
      "rgb(0.50,0.90,1.00)",
      "rgb(0.50,0.70,1.00)",
      "rgb(0.37,0.50,1.00)",
      "rgb(0.20,0.30,0.90)",
      "rgb(0.10,0.15,0.75)",
      "rgb(0.00,0.05,0.55)"
    ],
    "contour_shade_max_level": 4200.0,
    "contour_shade_min_level": 100.0,
    "contour_level_list": [
      100.0,
      200.0,
      300.0,
      500.0,
      750.0,
      1000.0,
      1250.0,
      1500.0,
      1750.0,
      2000.0,
      2250.0,
      2500.0,
      2750.0,
      3000.0,
      3500.0,
      4000.0,
      4500.0
    ],
    "contour_highlight": false,
    "contour_hilo": false,
    "contour_label": false,
    "legend": true,
    "legend_title": true,
    "legend_text_font_size": 0.4,
    "legend_title_text": "C.A.P.E. [J/kg]",
    "legend_text_colour": "black",
    "legend_title_font_size": 0.5,
    "legend_automatic_position": "right",
    "legend_display_type": "continuous"
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

