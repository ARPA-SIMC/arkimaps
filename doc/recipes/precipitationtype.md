# precipitationtype: Precipitation types

Mixer: **default**

## Inputs

* **precitype**:
    * **Arkimet matcher**: `product:GRIB2,98,0,1,19,,`
    * **grib_filter matcher**: `shortName is "ptype"`

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
  "grib": "precitype"
}
```

### add_symbols

Add symbols settings

With arguments:
```
{
  "params": {
    "symbol_type": "marker",
    "symbol_table_mode": "on",
    "symbol_min_table": [
      1,
      3,
      5,
      6,
      8,
      9,
      12
    ],
    "symbol_max_table": [
      2,
      4,
      6,
      7,
      9,
      10,
      13
    ],
    "symbol_marker_table": [
      18,
      18,
      18,
      18,
      18,
      18
    ],
    "symbol_colour_table": [
      "GREEN",
      "RED",
      "BLUE",
      "YELLOW",
      "TURQUOISE",
      "YELLOWISH_ORANGE",
      "ochre"
    ],
    "symbol_height_table": [
      0.6,
      0.6,
      0.6,
      0.6,
      0.6,
      0.6
    ],
    "legend": "on",
    "legend_title": true,
    "legend_text_colour": "black",
    "legend_text_font_size": 0.56,
    "legend_title_font_size": 0.8,
    "legend_title_text": "Precipitation types",
    "legend_text_composition": "user_text_only",
    "legend_user_lines": [
      "pioggia",
      "gelicidio FZRA",
      "neve",
      "neve bagnata",
      "mista",
      "neve tonda",
      "gelicidio FZDZ"
    ],
    "legend_display_type": "disjoint",
    "legend_entry_text_width": 80.0,
    "legend_symbol_height_factor": 1.4
  },
  "skip": true
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

