# thetae925: Theta-e at 925 hPa

Mixer: **default**

## Inputs

* **thetae925**:
    * **vg6d_transform arguments**: --output-variable-list=B12193
    * **Preprocessing**: vg6d_transform
    * **Inputs**: t925, q925, p925
* **t925**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,11;level:GRIB1,100,925`
        * **grib_filter matcher**: `centre != 98 and shortName is "t" and levelType == 100 and level == 925 and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,130;level:GRIB1,100,925`
        * **grib_filter matcher**: `centre == 98 and shortName is "t" and levelType == 100 and level == 925`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,000,000,,;level:GRIB2S,100,000,0000092500`
        * **grib_filter matcher**: `centre != 98 and shortName is "t" and levelType == 100 and level == 925 and editionNumber == 2`
* **q925**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,51;level:GRIB1,100,925`
        * **grib_filter matcher**: `centre != 98 and shortName is "q" and levelType == 100 and level == 925 and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,133;level:GRIB1,100,925`
        * **grib_filter matcher**: `centre == 98 and shortName is "q" and levelType == 100 and level == 925`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,001,000,,;level:GRIB2S,100,000,0000092500`
        * **grib_filter matcher**: `centre != 98 and shortName is "q" and levelType == 100 and level == 925 and editionNumber == 2`
* **p925**:
    * **vg6d_transform arguments**: --comp-var-from-lev --trans-level-type=100
    * **Preprocessing**: vg6d_transform
    * **Inputs**: t925, q925

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
  "grib": "thetae925"
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
      "rgb(0.702,0.502,0.992)",
      "rgb(0.545,0.235,0.992)",
      "rgb(0.400,0.055,0.941)",
      "rgb(0.286,0.031,0.690)",
      "rgb(0.149,0.051,0.682)",
      "rgb(0.075,0.098,0.671)",
      "rgb(0.094,0.247,0.643)",
      "rgb(0.114,0.388,0.647)",
      "rgb(0.133,0.506,0.631)",
      "rgb(0.161,0.608,0.616)",
      "rgb(0.192,0.600,0.192)",
      "rgb(0.086,0.820,0.788)",
      "rgb(0.000,0.914,0.733)",
      "rgb(0.000,0.706,0.008)",
      "rgb(0.247,0.796,0.086)",
      "rgb(0.600,0.898,0.102)",
      "rgb(1.000,0.992,0.486)",
      "rgb(0.992,0.988,0.118)",
      "rgb(0.961,0.808,0.090)",
      "rgb(0.925,0.635,0.063)",
      "rgb(0.894,0.467,0.039)",
      "rgb(0.859,0.282,0.016)",
      "rgb(0.824,0.118,0.008)",
      "rgb(0.780,0.008,0.055)",
      "rgb(0.710,0.008,0.251)",
      "rgb(0.643,0.016,0.412)",
      "rgb(0.678,0.027,0.533)",
      "rgb(0.886,0.078,0.616)",
      "rgb(0.910,0.290,0.643)",
      "rgb(0.910,0.541,0.710)",
      "rgb(0.937,0.769,0.827)"
    ],
    "contour_level_list": [
      271,
      274,
      277,
      280,
      283,
      286,
      289,
      292,
      295,
      298,
      301,
      304,
      307,
      310,
      313,
      316,
      319,
      322,
      325,
      328,
      331,
      334,
      337,
      340,
      343,
      346,
      349,
      352
    ],
    "contour_highlight": false,
    "contour_hilo": false,
    "legend": true,
    "legend_title": true,
    "legend_display_type": "continuous",
    "legend_text_font_size": 0.4,
    "legend_title_text": "Theta-e at 925 hPa [\u00b0K]",
    "legend_text_colour": "black",
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

