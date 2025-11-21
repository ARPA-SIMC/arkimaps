# standalone/w10mbeaufort: Wind at 10 metres Beaufort scale

Mixer: **default**

## Inputs

* **wspeed10m**:
    * **vg6d_transform arguments**: --output-variable-list=B11002
    * **Preprocessing**: vg6d_transform
    * **Inputs**: u10m, v10m
* **u10m**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,33;level:GRIB1,105,10`
        * **grib_filter matcher**: `centre != 98 and shortName is "10u" and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,165`
        * **grib_filter matcher**: `centre == 98 and shortName is "10u"`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,002,002,,;level:GRIB2S,103,000,0000000010`
        * **grib_filter matcher**: `centre != 98 and shortName is "10u" and editionNumber == 2`
* **v10m**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,34;level:GRIB1,105,10`
        * **grib_filter matcher**: `centre != 98 and shortName is "10v" and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,166`
        * **grib_filter matcher**: `centre == 98 and shortName is "10v"`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,002,003,,;level:GRIB2S,103,000,0000000010`
        * **grib_filter matcher**: `centre != 98 and shortName is "10v" and editionNumber == 2`
* **uv10m**:
    * Model **cosmo**:
        * **Preprocessing**: cat
        * **Inputs**: u10m, v10m
    * Model **ifs**:
        * **Preprocessing**: cat
        * **Inputs**: u10m, v10m
    * Model **erg5**:
        * **Preprocessing**: cat
        * **Inputs**: ws10m, wdir10m
        * **mgrib {k}**: `sd`
    * Model **icon**:
        * **Preprocessing**: cat
        * **Inputs**: u10m, v10m
* **ws10m**:
    * **Arkimet matcher**: `product:GRIB2,00200,000,002,001,004,;level:GRIB2S,103,003,0000010000`
    * **grib_filter matcher**: `shortName is "ws" and level == 10`
* **wdir10m**:
    * **Arkimet matcher**: `product:GRIB2,00200,000,002,000,004,;level:GRIB2S,103,003,0000010000`
    * **grib_filter matcher**: `shortName is "wdir" and level == 10`

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
  "grib": "wspeed10m"
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
    "contour_shade_colour_list": [
      "white",
      "cyan",
      "turquoise",
      "green",
      "avocado",
      "kelly_green",
      "yellow",
      "orange",
      "red",
      "gold",
      "magenta",
      "violet",
      "black"
    ],
    "contour_level_list": [
      0.0,
      0.3,
      1.6,
      3.4,
      5.5,
      8.0,
      10.8,
      13.9,
      17.2,
      20.8,
      24.5,
      28.5,
      32.7,
      100.0
    ],
    "contour_highlight": false,
    "contour_hilo": false,
    "legend": true,
    "legend_text_colour": "black",
    "legend_title": false,
    "legend_text_composition": "user_text_only",
    "legend_user_lines": [
      "0 calma",
      "1 bava di  vento",
      "2 brezza leggera",
      "3 brezza tesa",
      "4 vento moderato",
      "5 vento teso",
      "6 vento fresco",
      "7 vento forte",
      "8 burrasca",
      "9 burrasca forte",
      "10 tempesta",
      "11 tempesta violenta",
      "12 uragano"
    ],
    "legend_display_type": "disjoint",
    "legend_automatic_position": "right",
    "legend_entry_plot_orientation": "top_bottom",
    "legend_text_font_size": 0.4,
    "legend_text_orientation": 0
  }
}
```

### add_grib

Add a grib file

With arguments:
```
{
  "grib": "uv10m"
}
```

### add_wind

Add wind flag rendering of the previous data

With arguments:
```
{
  "params": {
    "wind_arrow_colour": "navy",
    "wind_arrow_thickness": 2,
    "wind_field_type": "arrows",
    "wind_flag_cross_boundary": false,
    "wind_arrow_unit_velocity": 12.5,
    "wind_arrow_calm_indicator": false,
    "wind_thinning_factor": 1,
    "wind_thinning_method": "automatic"
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

