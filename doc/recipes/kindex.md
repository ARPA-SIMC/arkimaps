# kindex: K-index

Mixer: **default**

## Inputs

* **kindex**:
    * **Preprocessing**: expr
    * **Inputs**: t500, t700, t850, td700, td850
* **t500**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,11;level:GRIB1,100,500`
        * **grib_filter matcher**: `centre != 98 and shortName is "t" and levelType == 100 and level == 500 and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,130;level:GRIB1,100,500`
        * **grib_filter matcher**: `centre == 98 and shortName is "t" and levelType == 100 and level == 500`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,000,000,,;level:GRIB2S,100,000,0000050000;timerange:Timedef,,254,`
        * **grib_filter matcher**: `centre != 98 and shortName is "t" and levelType == 100 and level == 500 and editionNumber == 2`
* **t700**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,11;level:GRIB1,100,700`
        * **grib_filter matcher**: `centre != 98 and shortName is "t" and levelType == 100 and level == 700 and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,130;level:GRIB1,100,700`
        * **grib_filter matcher**: `centre == 98 and shortName is "t" and levelType == 100 and level == 700`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,000,000,,;level:GRIB2S,100,000,0000070000;timerange:Timedef,,254,`
        * **grib_filter matcher**: `centre != 98 and shortName is "t" and levelType == 100 and level == 700 and editionNumber == 2`
* **t850**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,11;level:GRIB1,100,850`
        * **grib_filter matcher**: `centre != 98 and shortName is "t" and levelType == 100 and level == 850 and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,130;level:GRIB1,100,850`
        * **grib_filter matcher**: `centre == 98 and shortName is "t" and levelType == 100 and level == 850`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,000,000,,;level:GRIB2S,100,000,0000085000;timerange:Timedef,,254,`
        * **grib_filter matcher**: `centre != 98 and shortName is "t" and levelType == 100 and level == 850 and editionNumber == 2`
* **td700**:
    * **vg6d_transform arguments**: --output-variable-list=B12103
    * **Preprocessing**: vg6d_transform
    * **Inputs**: t700, q700, p700
* **q700**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,51;level:GRIB1,100,700`
        * **grib_filter matcher**: `centre != 98 and shortName is "q" and levelType == 100 and level == 700 and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,133;level:GRIB1,100,700`
        * **grib_filter matcher**: `centre == 98 and shortName is "q" and levelType == 100 and level == 700`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,001,000,,;level:GRIB2S,100,000,0000070000`
        * **grib_filter matcher**: `centre != 98 and shortName is "q" and levelType == 100 and level == 700 and editionNumber == 2`
* **p700**:
    * **vg6d_transform arguments**: --comp-var-from-lev --trans-level-type=100
    * **Preprocessing**: vg6d_transform
    * **Inputs**: t700, q700
* **td850**:
    * **vg6d_transform arguments**: --output-variable-list=B12103
    * **Preprocessing**: vg6d_transform
    * **Inputs**: t850, q850, p850
* **q850**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,51;level:GRIB1,100,850`
        * **grib_filter matcher**: `centre != 98 and shortName is "q" and levelType == 100 and level == 850 and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,133;level:GRIB1,100,850`
        * **grib_filter matcher**: `centre == 98 and shortName is "q" and levelType == 100 and level == 850`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,001,000,,;level:GRIB2S,100,000,0000085000`
        * **grib_filter matcher**: `centre != 98 and shortName is "q" and levelType == 100 and level == 850 and editionNumber == 2`
* **p850**:
    * **vg6d_transform arguments**: --comp-var-from-lev --trans-level-type=100
    * **Preprocessing**: vg6d_transform
    * **Inputs**: t850, q850

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
  "grib": "kindex"
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
      "cyan",
      "green",
      "yellow",
      "red"
    ],
    "contour_level_list": [
      25,
      30,
      35,
      40,
      60
    ],
    "contour_highlight": false,
    "contour_hilo": false,
    "legend": true,
    "legend_title": true,
    "legend_text_font_size": 0.4,
    "legend_title_text": "K index [n]",
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

