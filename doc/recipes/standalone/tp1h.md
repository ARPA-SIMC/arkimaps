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
        * **Arkimet matcher**: `product:GRIB2,,,001,052,,`
        * **grib_filter matcher**: `centre != 98 and shortName is "tp" and editionNumber == 2`
* **sffraction1h**:
    * **Preprocessing**: sffraction
    * **Inputs**: tpdec1h, snowdec1h
* **snowdec1h**:
    * **Decumulation step**: 1
    * **Preprocessing**: decumulate
    * **Inputs**: snow
* **snow**:
    * **Preprocessing**: or
    * **Inputs**: sf, snowsum, snowgsp
* **sf**:
    * **Arkimet matcher**: `product:GRIB1,98,128,144`
    * **grib_filter matcher**: `shortName is "sf"`
* **snowsum**:
    * **vg6d_transform arguments**: --output-variable-list=B13205
    * **Preprocessing**: vg6d_transform
    * **Inputs**: snowcon, snowgsp
* **snowcon**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,78`
        * **grib_filter matcher**: `( shortName is "snoc" or shortName is "snow_con" ) and editionNumber == 1`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,001,055,,`
        * **grib_filter matcher**: `shortName is "snow_con" and editionNumber == 2`
* **snowgsp**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,79`
        * **grib_filter matcher**: `( shortName is "lssf" or shortName is "snow_gsp" ) and editionNumber == 1`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,001,056,,`
        * **grib_filter matcher**: `shortName is "snow_gsp" and editionNumber == 2`
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
    "contour_shade_min_level": 0.5,
    "contour_level_list": [
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
    "map_boundaries": "on",
    "map_boundaries_colour": "#504040",
    "map_administrative_boundaries_countries_list": [
      "ITA"
    ],
    "map_administrative_boundaries_colour": "#504040",
    "map_administrative_boundaries_style": "solid",
    "map_administrative_boundaries": "on"
  }
}
```

### add_user_boundaries

Add user-defined boundaries from a shapefile


### add_geopoints

Add geopoints


### add_symbols

Add symbols settings

With arguments:
```
{
  "params": {
    "symbol_type": "marker",
    "symbol_marker_index": 15,
    "legend": "off",
    "symbol_colour": "black",
    "symbol_height": 0.28
  }
}
```

