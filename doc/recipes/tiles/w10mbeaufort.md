# tiles/w10mbeaufort: Wind at 10 metres Beaufort scale

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

