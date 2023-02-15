# tiles/wspeed250: Wind speed at 250hPa

Mixer: **default**

## Inputs

* **wspeed250**:
    * **vg6d_transform arguments**: --output-variable-list=B11002
    * **Preprocessing**: vg6d_transform
    * **Inputs**: u250, v250
* **u250**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,33;level:GRIB1,100,250`
        * **grib_filter matcher**: `centre != 98 and shortName is "u" and levelType == 100 and level == 250`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,131;level:GRIB1,100,250`
        * **grib_filter matcher**: `centre == 98 and shortName is "u" and levelType == 100 and level == 250`
* **v250**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,34;level:GRIB1,100,250`
        * **grib_filter matcher**: `centre != 98 and shortName is "v" and levelType == 100 and level == 250`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,132;level:GRIB1,100,250`
        * **grib_filter matcher**: `centre == 98 and shortName is "v" and levelType == 100 and level == 250`

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
  "grib": "wspeed250"
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
      "#ffff00",
      "#a7e700",
      "#5dd000",
      "#1fb800",
      "#00a110",
      "#008a34",
      "#00724b"
    ],
    "contour_level_list": [
      30.0,
      40.0,
      50.0,
      60.0,
      70.0,
      80.0,
      90.0,
      100.0
    ],
    "contour_highlight": false,
    "contour_hilo": false,
    "legend": true,
    "legend_text_colour": "black",
    "legend_title": true,
    "legend_title_text": "Wind speed at 250hPa [m/s]",
    "legend_display_type": "continuous",
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

