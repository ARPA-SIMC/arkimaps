# rh2m: Relative humidity at 2 metres

Mixer: **default**

## Inputs

* **rh2m**:
    * Model **cosmo**:
        * **vg6d_transform arguments**: --output-variable-list=B13003
        * **Preprocessing**: vg6d_transform
        * **Inputs**: t2m, 2d
    * Model **ifs**:
        * **vg6d_transform arguments**: --output-variable-list=B13003
        * **Preprocessing**: vg6d_transform
        * **Inputs**: t2m, 2d
    * Model **erg5**:
        * **Arkimet matcher**: `product:GRIB2,00200,000,001,001,004,000;level:GRIB2S,103,003,0000001800`
        * **grib_filter matcher**: `shortName is "r" and level == 2`
    * Model **icon**:
        * **vg6d_transform arguments**: --output-variable-list=B13003
        * **Preprocessing**: vg6d_transform
        * **Inputs**: t2m, 2d
* **t2m**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,11;level:GRIB1,105,2`
        * **grib_filter matcher**: `centre != 98 and shortName is "2t" and levelType == 105 and timeRangeIndicator == 0 and level == 2 and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,167;level:GRIB1,1`
        * **grib_filter matcher**: `centre == 98 and shortName is "2t" and levelType == 1 and level == 0 and timeRangeIndicator == 0`
    * Model **erg5**:
        * **Arkimet matcher**: `product:GRIB2,00200,000,000,000,004,000;level:GRIB2S,103,003,0000001800`
        * **grib_filter matcher**: `shortName is "t" and level == 2`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,000,000,000,015,001;level:GRIB2S,103,000,0000000002`
        * **grib_filter matcher**: `centre != 98 and shortName is "2t" and level == 2 and editionNumber == 2`
* **2d**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,17`
        * **grib_filter matcher**: `centre != 98 and shortName is "2d" and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,168`
        * **grib_filter matcher**: `centre == 98 and shortName is "2d"`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,000,000,006,015,001`
        * **grib_filter matcher**: `centre != 98 and shortName is "2d" and editionNumber == 2`

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
  "grib": "rh2m"
}
```

### add_contour

Add contouring of the previous data

With arguments:
```
{
  "params": {
    "contour_shade": true,
    "contour_shade_method": "area_fill",
    "contour_level_selection_type": "level_list",
    "contour_shade_colour_method": "list",
    "contour_level_list": [
      0.0,
      20.0,
      40.0,
      60.0,
      80.0,
      90.0,
      100.0
    ],
    "legend": true,
    "legend_display_type": "continuous",
    "legend_title": true,
    "legend_text_colour": "black",
    "legend_text_font_size": 0.4,
    "legend_title_text": "Relative Humidity at 2m [%]",
    "legend_title_font_size": 0.5,
    "legend_automatic_position": "right",
    "contour_highlight": false,
    "contour_label": false,
    "contour_hilo": false,
    "contour": false,
    "contour_shade_colour_list": [
      "red",
      "orange",
      "yellow",
      "green",
      "cyan",
      "blue"
    ]
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

