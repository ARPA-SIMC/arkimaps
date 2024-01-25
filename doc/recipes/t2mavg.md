# t2mavg: Average temperature at 2 metres

Mixer: **default**

## Inputs

* **t2mavg**:
    * **Averaging step**: 24
    * **Preprocessing**: average
    * **Inputs**: t2m
* **t2m**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,11;level:GRIB1,105,2`
        * **grib_filter matcher**: `centre != 98 and shortName is "2t" and levelType == 105 and timeRangeIndicator == 0 and level == 2 and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,167;level:GRIB1,1`
        * **grib_filter matcher**: `centre == 98 and shortName is "2t" and levelType == 1 and level == 0 and timeRangeIndicator == 0`
    * Model **erg5**:
        * **Arkimet matcher**: `product:GRIB2,00200,000,000,000,004,;level:GRIB2S,103,003,0000001800`
        * **grib_filter matcher**: `shortName is "t" and level == 2`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,000,000,000,,;level:GRIB2S,103,000,0000000002;timerange:Timedef,,254,`
        * **grib_filter matcher**: `centre != 98 and shortName is "2t" and level == 2 and editionNumber == 2`

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
  "grib": "t2mavg",
  "params": {
    "grib_automatic_scaling": false,
    "grib_scaling_offset": -273.15
  }
}
```

### add_contour

Add contouring of the previous data

With arguments:
```
{
  "params": {
    "contour": false,
    "contour_highlight_frequency": 100,
    "contour_highlight_thickness": 5,
    "contour_interval": 2.0,
    "contour_label_height": 0.4,
    "contour_label_colour": "navy",
    "contour_label_frequency": 1,
    "contour_label_blanking": false,
    "contour_level_selection_type": "interval",
    "contour_line_thickness": 3,
    "contour_shade": true,
    "contour_shade_colour_list": [
      "rgb(1,0.8,0)",
      "rgb(1,0.6,0)",
      "rgb(1,0.4,0)",
      "rgb(1,0,0)",
      "rgb(0.8,0,0)",
      "rgb(0.6,0,0)",
      "rgb(0.4,0,0)",
      "rgb(0.4,0,0.4)",
      "rgb(0.6,0,0.6)",
      "rgb(0.8,0,0.8)",
      "rgb(1,0,1)",
      "rgb(0.75,0,1)",
      "rgb(0.45,0,1)",
      "rgb(0,0,1)",
      "rgb(0,0.35,1)",
      "rgb(0,0.55,1)",
      "rgb(0,0.75,1)",
      "rgb(0,1,1)",
      "rgb(0,0.9,0.8)",
      "rgb(0,0.8,0.5)",
      "rgb(0,0.7,0.0)",
      "rgb(0.5,0.8,0.0)",
      "rgb(0.8,0.9,0.0)",
      "rgb(1,1,0)",
      "rgb(1,0.8,0)",
      "rgb(1,0.6,0)",
      "rgb(1,0.4,0)",
      "rgb(1,0,0)",
      "rgb(0.8,0,0)",
      "rgb(0.6,0,0)",
      "rgb(0.4,0,0)",
      "rgb(0.4,0,0.4)",
      "rgb(0.6,0,0.6)",
      "rgb(0.8,0,0.8)",
      "rgb(1,0,1)",
      "rgb(0.75,0,1)",
      "rgb(0.45,0,1)"
    ],
    "contour_shade_colour_method": "list",
    "contour_shade_max_level": 46.0,
    "contour_shade_method": "area_fill",
    "contour_shade_min_level": -30.0,
    "legend": true,
    "legend_display_type": "continuous",
    "legend_title": true,
    "legend_title_text": "24h Average temperature at 2m [\u00b0C]",
    "legend_text_colour": "black",
    "legend_text_font_size": 0.4,
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

