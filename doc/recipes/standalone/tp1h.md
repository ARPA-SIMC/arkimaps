# standalone/tp1h: Total precipitation 01h + snow fraction + wind 10m

Mixer: **default**

## Inputs

* **tpdec1h**:
    * **Decumulation step**: 1
    * **Preprocessing**: decumulate
    * **Inputs**: tp
* **tp**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,61`
        * **grib_filter matcher**: `centre != 98 and shortName is "tp" and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,228`
        * **grib_filter matcher**: `centre == 98 and shortName is "tp"`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,001,052,, or GRIB2,,,001,008,,`
        * **grib_filter matcher**: `centre != 98 and shortName is "tp" and editionNumber == 2 and numberOfTimeRange == 1 and typeOfGeneratingProcess == 2`
* **sffraction1h**:
    * **Preprocessing**: sffraction
    * **Inputs**: tpdec1h, snowdec1h
* **snowdec1h**:
    * **Decumulation step**: 1
    * **Preprocessing**: decumulate
    * **Inputs**: snow
* **snow**:
    * **Preprocessing**: or
    * **Inputs**: sf, snowsumicon, snowsum, snowgsp, tsnowp
* **sf**:
    * **Arkimet matcher**: `product:GRIB1,98,128,144`
    * **grib_filter matcher**: `shortName is "sf"`
* **snowsumicon**:
    * **vg6d_transform arguments**: --output-variable-list=B13237
    * **Preprocessing**: vg6d_transform
    * **Inputs**: snowcon, snowgsp, graupel
* **snowcon**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,78`
        * **grib_filter matcher**: `( shortName is "snoc" or shortName is "snow_con" ) and editionNumber == 1`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,001,055,,`
        * **grib_filter matcher**: `shortName is "snow_con" and editionNumber == 2 and numberOfTimeRange == 1`
* **snowgsp**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,79`
        * **grib_filter matcher**: `( shortName is "lssf" or shortName is "snow_gsp" ) and editionNumber == 1`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,001,056,,`
        * **grib_filter matcher**: `shortName is "snow_gsp" and editionNumber == 2 and numberOfTimeRange == 1`
* **graupel**:
    * **Arkimet matcher**: `product:GRIB2,,,001,75,,`
    * **grib_filter matcher**: `shortName is "tgrp" and editionNumber == 2 and numberOfTimeRange == 1`
* **snowsum**:
    * **vg6d_transform arguments**: --output-variable-list=B13205
    * **Preprocessing**: vg6d_transform
    * **Inputs**: snowcon, snowgsp
* **tsnowp**:
    * **Arkimet matcher**: `PRODUCT:GRIB2,,,001,66,,`
    * **grib_filter matcher**: `shortname is "tsnowp" and editionNumber == 2`
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
  "grib": "tpdec1h"
}
```

### add_contour

Add contouring of the previous data

With arguments:
```
{
  "params": {
    "contour": "off",
    "contour_highlight": "off",
    "contour_hilo": "off",
    "contour_label": "off",
    "contour_level_selection_type": "level_list",
    "contour_shade": "on",
    "contour_shade_colour_method": "list",
    "contour_shade_method": "area_fill",
    "contour_shade_min_level": 0.1,
    "contour_level_list": [
      0.1,
      0.5,
      1.0,
      2.0,
      5.0,
      10.0,
      20.0,
      30.0,
      50.0,
      70.0,
      100.0,
      150.0,
      200.0
    ],
    "contour_shade_colour_list": [
      "rgb(0.83,0.83,0.83)",
      "rgb( 0.686,1.000,1.000)",
      "rgb( 0.000,1.000,1.000)",
      "rgb( 0.447,0.639,1.000)",
      "rgb( 0.000,0.498,1.000)",
      "rgb( 0.145,0.000,1.000)",
      "rgb( 0.145,0.435,0.435)",
      "rgb( 1.000,1.000,0.000)",
      "rgb( 1.000,0.498,0.000)",
      "rgb( 1.000,0.000,0.000)",
      "rgb(1.000,0.000,1.000)",
      "rgb(0.615,0.403,0.937)"
    ],
    "legend": true,
    "legend_display_type": "continuous",
    "legend_title": true,
    "legend_text_colour": "black",
    "legend_text_font_size": 0.4,
    "legend_title_font_size": 0.5,
    "legend_title_text": "Total precipitation [mm]",
    "legend_automatic_position": "right"
  }
}
```

### add_grib

Add a grib file

With arguments:
```
{
  "grib": "sffraction1h",
  "params": {
    "grib_automatic_scaling": false
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
    "contour_line_colour": "red",
    "contour_line_style": "dot",
    "contour_line_thickness": 2,
    "contour_label_height": 0.4,
    "contour_highlight": false,
    "contour_label": true,
    "contour_min_level": 25.0,
    "contour_max_level": 100.0,
    "contour_interval": 25.0
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
    "wind_arrow_colour": "black",
    "wind_arrow_thickness": 1,
    "wind_field_type": "arrows",
    "wind_flag_cross_boundary": false,
    "wind_arrow_unit_velocity": 12.5,
    "wind_arrow_calm_indicator": false,
    "wind_thinning_method": "automatic",
    "wind_thinning_factor": 1
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

