# cp3h: Convective precipitation 3h

Mixer: **default**

## Inputs

* **cpdec3h**:
    * **Decumulation step**: 3
    * **Preprocessing**: decumulate
    * **Inputs**: cp
* **cp**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,201,113`
        * **grib_filter matcher**: `shortName is "rain_con"`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,143`
        * **grib_filter matcher**: `shortName is "cp"`

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
  "grib": "cpdec3h"
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
    "legend_title_text": "Convective precipitation [mm]",
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

