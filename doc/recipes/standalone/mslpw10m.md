# standalone/mslpw10m: Mean sea level pressure and wind at 10 metres

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
      "green",
      "yellow",
      "orange",
      "red"
    ],
    "contour_level_list": [
      13.9,
      17.1,
      20.6,
      24.2,
      70.0
    ],
    "contour_highlight": false,
    "contour_hilo": false,
    "legend": true,
    "legend_text_colour": "black",
    "legend_title": true,
    "legend_title_text": "Wind speed [m/s]",
    "legend_display_type": "continuous",
    "legend_automatic_position": "right"
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
    "wind_field_type": "flags",
    "wind_flag_colour": "black",
    "wind_flag_length": 0.8,
    "wind_flag_origin_marker": false,
    "wind_flag_cross_boundary": true,
    "wind_thinning_factor": 1,
    "wind_thinning_method": "automatic"
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

