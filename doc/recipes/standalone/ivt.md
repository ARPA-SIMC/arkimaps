# standalone/ivt: Integrated Vapour Transport

Mixer: **default**

## Inputs

* **twflux**:
    * **Preprocessing**: expr
    * **Inputs**: viwve, viwvn
* **viwve**:
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB2,98,192,162,71,5`
        * **grib_filter matcher**: `shortName is "viwve" and editionNumber == 1`
    * Model **ifs_g2**:
        * **Arkimet matcher**: `product:GRIB2,98,0,1,150;level:GRIB2D,1,,,`
        * **grib_filter matcher**: `shortName is "viwve" and editionNumber == 2`
* **viwvn**:
    * Model **any**:
        * **Arkimet matcher**: `product:GRIB2,98,192,162,72,5`
        * **grib_filter matcher**: `shortName is "viwvn" and editionNumber == 1`
    * Model **ifs_g2**:
        * **Arkimet matcher**: `product:GRIB2,98,0,1,151;level:GRIB2D,1,,,`
        * **grib_filter matcher**: `shortName is "viwvn" and editionNumber == 2`
* **mslp**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,2`
        * **grib_filter matcher**: `shortName is "pmsl" and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,151`
        * **grib_filter matcher**: `shortName is "msl"`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,003,001,,;level:GRIB2S,101,000,0000000000`
        * **grib_filter matcher**: `( shortName is "pmsl" or shortName is "prmsl" ) and editionNumber == 2`
* **uv950**:
    * **Preprocessing**: cat
    * **Inputs**: u950, v950
* **u950**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,33;level:GRIB1,100,950`
        * **grib_filter matcher**: `centre != 98 and shortName is "u" and levelType == 100 and level == 950 and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,131;level:GRIB1,100,950`
        * **grib_filter matcher**: `centre == 98 and shortName is "u" and levelType == 100 and level == 950`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,002,002,,;level:GRIB2S,100,000,0000095000`
        * **grib_filter matcher**: `centre != 98 and shortName is "u" and typeOfLevel is "isobaricInhPa" and level == 950 and editionNumber == 2`
* **v950**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,34;level:GRIB1,100,950`
        * **grib_filter matcher**: `centre != 98 and shortName is "v" and levelType == 100 and level == 950 and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,132;level:GRIB1,100,950`
        * **grib_filter matcher**: `centre == 98 and shortName is "v" and levelType == 100 and level == 950`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,002,003,,;level:GRIB2S,100,000,0000095000`
        * **grib_filter matcher**: `centre != 98 and shortName is "v" and typeOfLevel is "isobaricInhPa" and level == 950 and editionNumber == 2`

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
  "grib": "twflux"
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
      250,
      300,
      350,
      400,
      450,
      500,
      600,
      700,
      800,
      900,
      1000,
      1250,
      2000
    ],
    "contour_shade_colour_method": "list",
    "contour_shade_colour_list": [
      "#a6bddb",
      "#74a9cf",
      "#3690c0",
      "#a3a891",
      "#bebd65",
      "#d8d239",
      "#f3e70b",
      "#f4c60a",
      "#f88406",
      "#fb4103",
      "#ff0000",
      "#6e3715"
    ],
    "contour_highlight": false,
    "contour_hilo": false,
    "legend": true,
    "legend_title": true,
    "legend_title_text": "Integrated Vapour Transport (kg/ms)",
    "legend_display_type": "continuous",
    "legend_automatic_position": "right",
    "legend_text_colour": "black",
    "legend_text_font_size": 0.5,
    "legend_title_font_size": 0.5
  }
}
```

### add_grib

Add a grib file

With arguments:
```
{
  "grib": "mslp",
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
    "contour_interval": 2,
    "contour_line_style": "solid",
    "contour_line_colour": "black",
    "contour_reference_level": 1000,
    "contour_line_thickness": 2,
    "contour_hilo": true,
    "contour_hilo_type": "text",
    "contour_lo_colour": "blue",
    "contour_hi_colour": "red",
    "contour_hilo_window_size": 5,
    "contour_highlight_frequency": 100,
    "contour_highlight_colour": "blue",
    "contour_label": true,
    "contour_label_height": 0.4,
    "contour_label_frequency": 2,
    "legend": false
  }
}
```

### add_grib

Add a grib file

With arguments:
```
{
  "grib": "uv950"
}
```

### add_wind

Add wind flag rendering of the previous data

With arguments:
```
{
  "params": {
    "wind_field_type": "arrows",
    "wind_arrow_colour": "black",
    "wind_arrow_head_shape": 0,
    "wind_arrow_head_ratio": 0.6,
    "wind_arrow_unit_velocity": 25,
    "wind_flag_origin_marker": false,
    "wind_flag_cross_boundary": true,
    "wind_thinning_method": "automatic",
    "wind_thinning_factor": 1,
    "legend": true,
    "legend_title": true,
    "legend_title_text": "Integrated Vapour Transport (kg/ms)",
    "legend_display_type": "continuous",
    "legend_automatic_position": "right",
    "legend_text_colour": "black",
    "legend_text_font_size": 0.5,
    "legend_title_font_size": 0.5
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

