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
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,002,002,,;level:GRIB2S,100,000,0000025000`
        * **grib_filter matcher**: `centre != 98 and shortName is "u" and typeOfLevel is "isobaricInhPa" and level == 250`
* **v250**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,34;level:GRIB1,100,250`
        * **grib_filter matcher**: `centre != 98 and shortName is "v" and levelType == 100 and level == 250`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,132;level:GRIB1,100,250`
        * **grib_filter matcher**: `centre == 98 and shortName is "v" and levelType == 100 and level == 250`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,002,003,,;level:GRIB2S,100,000,0000025000`
        * **grib_filter matcher**: `centre != 98 and shortName is "v" and typeOfLevel is "isobaricInhPa" and level == 250`

## Steps

### add_basemap

Add a base map

With arguments:
```
{
  "params": {
    "page_id_line": false,
    "output_width": 1280,
    "subpage_map_projection": "cylindrical",
    "subpage_lower_left_longitude": 2.5,
    "subpage_lower_left_latitude": 35.0,
    "subpage_upper_right_longitude": 20.0,
    "subpage_upper_right_latitude": 50.0,
    "page_x_length": 38,
    "page_y_length": 31,
    "super_page_x_length": 40,
    "super_page_y_length": 32,
    "subpage_x_length": 34,
    "subpage_y_length": 30,
    "subpage_x_position": 2,
    "subpage_y_position": 1,
    "map_grid": true,
    "map_grid_latitude_reference": 45.0,
    "map_grid_longitude_reference": 0.0,
    "map_grid_longitude_increment": 2.5,
    "map_grid_latitude_increment": 2.5,
    "map_grid_colour": "grey",
    "map_grid_line_style": "dash",
    "map_label_colour": "black",
    "map_label_height": 0.4,
    "map_label_latitude_frequency": 1
  }
}
```

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
    "map_boundaries": true,
    "map_boundaries_colour": "#000000",
    "map_administrative_boundaries_countries_list": [
      "ITA"
    ],
    "map_administrative_boundaries_colour": "#000000",
    "map_administrative_boundaries_style": "solid",
    "map_administrative_boundaries": true,
    "map_coastline_thickness": 2
  }
}
```

### add_user_boundaries

Add user-defined boundaries from a shapefile

With arguments:
```
{
  "skip": true,
  "params": {
    "map_user_layer": "on",
    "map_user_layer_colour": "blue"
  }
}
```

### add_geopoints

Add geopoints

With arguments:
```
{
  "skip": true
}
```

### add_symbols

Add symbols settings

With arguments:
```
{
  "skip": true,
  "params": {
    "symbol_type": "marker",
    "symbol_marker_index": 15,
    "legend": "off",
    "symbol_colour": "black",
    "symbol_height": 0.28
  }
}
```

