# tiles/mcc: Cloud cover, medium level

Mixer: **default**

## Inputs

* **mcc**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,74`
        * **grib_filter matcher**: `shortName is "clcm"`
        * **mgrib {k}**: `False`
        * **mgrib {k}**: `0.08`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,006,022,,;level:GRIB2D,100,000,0000040000,100,000,0000080000`
        * **grib_filter matcher**: `shortName is "ccl" and scaledValueOfFirstFixedSurface == 40000 and scaledValueOfSecondFixedSurface == 80000 and editionNumber == 2`
        * **mgrib {k}**: `False`
        * **mgrib {k}**: `0.08`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,187`
        * **grib_filter matcher**: `shortName is "mcc"`
        * **mgrib {k}**: `False`
        * **mgrib {k}**: `8`

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
  "grib": "mcc"
}
```

### add_contour

Add contouring of the previous data

With arguments:
```
{
  "params": {
    "contour": false,
    "contour_highlight": false,
    "contour_hilo": false,
    "contour_label": false,
    "contour_level_list": [
      1.0,
      2.0,
      3.0,
      4.0,
      5.0,
      6.0,
      7.0,
      8.0
    ],
    "contour_min_level": 3.0,
    "contour_max_level": 8.0,
    "contour_level_selection_type": "level_list",
    "contour_shade": true,
    "contour_shade_max_level_colour": "rgba(0,0,255,0.4)",
    "contour_shade_min_level_colour": "rgba(0,0,255,0.0)",
    "contour_shade_method": "area_fill",
    "contour_interpolation_ceiling": 7.99,
    "legend": true,
    "legend_title": true,
    "legend_text_colour": "black",
    "legend_text_font_size": 0.4,
    "legend_title_font_size": 0.5,
    "legend_automatic_position": "right",
    "legend_title_text": "Medium cloud cover [okta]"
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

