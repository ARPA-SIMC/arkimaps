# tiles/wspeed500: Wind speed at 500hPa

Mixer: **default**

## Inputs

* **wspeed500**:
    * **vg6d_transform arguments**: --output-variable-list=B11002
    * **Preprocessing**: vg6d_transform
    * **Inputs**: u500, v500
* **u500**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,33;level:GRIB1,100,500`
        * **grib_filter matcher**: `centre != 98 and shortName is "u" and levelType == 100 and level == 500`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,131;level:GRIB1,100,500`
        * **grib_filter matcher**: `centre == 98 and shortName is "u" and levelType == 100 and level == 500`
* **v500**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,34;level:GRIB1,100,500`
        * **grib_filter matcher**: `centre != 98 and shortName is "v" and levelType == 100 and level == 500`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,132;level:GRIB1,100,500`
        * **grib_filter matcher**: `centre == 98 and shortName is "v" and levelType == 100 and level == 500`

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
  "grib": "wspeed500"
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
      "#ffff66",
      "#d9ff00",
      "#93ff00",
      "#6ba531",
      "#00724b",
      "#005447",
      "#004247",
      "#003370",
      "#0033a3"
    ],
    "contour_level_list": [
      10.0,
      15.0,
      20.0,
      25.0,
      30.0,
      40.0,
      50.0,
      60.0,
      80.0,
      100.0
    ],
    "contour_highlight": false,
    "contour_hilo": false,
    "legend": true,
    "legend_text_colour": "black",
    "legend_title": true,
    "legend_title_text": "Wind speed at 500hPa [m/s]",
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

