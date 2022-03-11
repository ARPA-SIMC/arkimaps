# standalone/jet: Wind, Wind speed  and Geopotential at 250hPa

Mixer: **default**

## Inputs

* **wspeed250**:
    * **vg6d_transform arguments**: --output-variable-list=B11002
    * **Preprocessing**: vg6d_transform
    * **Inputs**: u250, v250
* **u250**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,33;level:GRIB1,100,250`
        * **grib_filter matcher**: `shortName is "u" and indicatorOfTypeOfLevel == 100 and level == 250`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,131;level:GRIB1,100,250`
        * **grib_filter matcher**: `shortName is "u" and indicatorOfTypeOfLevel == 100 and level == 250`
* **v250**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,34;level:GRIB1,100,250`
        * **grib_filter matcher**: `shortName is "v" and indicatorOfTypeOfLevel == 100 and level == 250`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,132;level:GRIB1,100,250`
        * **grib_filter matcher**: `shortName is "v" and indicatorOfTypeOfLevel == 100 and level == 250`
* **z250**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,6; level:GRIB1,100,250`
        * **grib_filter matcher**: `shortName is "z" and indicatorOfTypeOfLevel == 100 and level == 250 and centre != 98`
        * **mgrib {k}**: `False`
        * **mgrib {k}**: `0.01`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,156; level:GRIB1,100,250`
        * **grib_filter matcher**: `shortName is "gh" and indicatorOfTypeOfLevel == 100 and level == 250 and centre == 98`
        * **mgrib {k}**: `False`
        * **mgrib {k}**: `0.1`
* **uv250**:
    * **Preprocessing**: cat
    * **Inputs**: u250, v250

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
      "yellow",
      "beige",
      "gold",
      "khaki"
    ],
    "contour_level_list": [
      35.0,
      45.0,
      55.0,
      65.0,
      150.0
    ],
    "contour_highlight": false,
    "contour_hilo": false,
    "legend": true,
    "legend_title": true,
    "legend_title_text": "Maximum wind gust speed [m/s]",
    "legend_display_type": "continuous",
    "legend_automatic_position": "right"
  }
}
```

### add_grib

Add a grib file

With arguments:
```
{
  "grib": "z250"
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
    "contour_interval": 4,
    "contour_line_colour": "black",
    "contour_line_thickness": 3,
    "contour_highlight": false,
    "contour_label": true,
    "contour_label_height": 0.6,
    "contour_label_frequency": 2,
    "contour_label_blanking": true,
    "contour_label_colour": "navy",
    "legend": false
  }
}
```

### add_grib

Add a grib file

With arguments:
```
{
  "grib": "uv250"
}
```

### add_wind

Add wind flag rendering of the previous data

With arguments:
```
{
  "params": {
    "wind_arrow_colour": "blue",
    "wind_arrow_thickness": 1,
    "wind_arrow_min_speed": 15.0,
    "wind_field_type": "arrows",
    "wind_flag_cross_boundary": false,
    "wind_arrow_unit_velocity": 12.5,
    "wind_arrow_calm_indicator": false,
    "wind_thinning_factor": 10
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

