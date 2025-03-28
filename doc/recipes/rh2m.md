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
        * **Arkimet matcher**: `product:GRIB2,00200,000,001,001,004,;level:GRIB2S,103,003,0000001800`
        * **grib_filter matcher**: `( shortName is "r" or shortName is "avg_r" ) and level == 2`
    * Model **icon**:
        * **vg6d_transform arguments**: --output-variable-list=B13003
        * **Preprocessing**: vg6d_transform
        * **Inputs**: t2m, 2d
* **t2m**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,11;level:GRIB1,105,2`
        * **grib_filter matcher**: `centre != 98 and (shortName is "2t" or shortName is "t_2m_cl") and levelType == 105 and level == 2 and (timeRangeIndicator == 0 or timeRangeIndicator == 3) and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,167;level:GRIB1,1`
        * **grib_filter matcher**: `centre == 98 and shortName is "2t" and levelType == 1 and level == 0 and (timeRangeIndicator == 0 or timeRangeIndicator == 1)`
    * Model **erg5**:
        * **Arkimet matcher**: `product:GRIB2,00200,000,000,000,004,;level:GRIB2S,103,003,0000001800`
        * **grib_filter matcher**: `shortName is "t" and level == 2 and typeOfProcessedData == 0 and typeOfGeneratingProcess == 8`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,000,000,000,,;level:GRIB2S,103,000,0000000002;timerange:Timedef,,254,`
        * **grib_filter matcher**: `centre != 98 and (shortName is "2t" or shortName is "t") and level == 2 and editionNumber == 2 and typeOfGeneratingProcess == 2`
* **2d**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,17`
        * **grib_filter matcher**: `centre != 98 and shortName is "2d" and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,168`
        * **grib_filter matcher**: `centre == 98 and shortName is "2d"`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,000,006,,`
        * **grib_filter matcher**: `centre != 98 and shortName is "2d" and editionNumber == 2`

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

