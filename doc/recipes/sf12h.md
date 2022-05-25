# sf12h: Total snow fall 12h

Mixer: **default**

## Inputs

* **snowdec12h**:
    * Model **cosmo**:
        * **Decumulation step**: 12
        * **Preprocessing**: decumulate
        * **Inputs**: snowcosmo
    * Model **ifs**:
        * **Decumulation step**: 12
        * **Preprocessing**: decumulate
        * **Inputs**: sf
* **snowcosmo**:
    * **Preprocessing**: or
    * **Inputs**: snowsum, snowgsp
* **snowsum**:
    * **vg6d_transform arguments**: --output-variable-list=B13205
    * **Preprocessing**: vg6d_transform
    * **Inputs**: snowcon, snowgsp
* **snowcon**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,78`
        * **grib_filter matcher**: `( shortName is "snoc" or shortName is "snow_con" ) and editionNumber == 1`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,000,001,055,015,001`
        * **grib_filter matcher**: `shortName is "snow_con" and editionNumber == 2`
* **snowgsp**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,79`
        * **grib_filter matcher**: `( shortName is "lssf" or shortName is "snow_gsp" ) and editionNumber == 1`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,000,001,056,015,001`
        * **grib_filter matcher**: `shortName is "snow_gsp" and editionNumber == 2`

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
  "grib": "snowdec12h"
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
      200.0,
      300.0,
      500.0
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
      "rgb(0.615,0.403,0.937)",
      "rgb(0.5,0.,0.5)"
    ],
    "legend": true,
    "legend_display_type": "continuous",
    "legend_title": true,
    "legend_text_colour": "black",
    "legend_text_font_size": 0.4,
    "legend_title_font_size": 0.5,
    "legend_title_text": "Total snow fall [mm H2O equivalent]",
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

