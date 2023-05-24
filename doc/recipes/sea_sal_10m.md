# sea_sal_10m: Salinity at -10m

Mixer: **default**

## Inputs

* **salinity10m**:
    * **Arkimet matcher**: `product:GRIB2,,,004,021,,;level:GRIB2S,160,002,0000001000`
    * **grib_filter matcher**: `editionNumber == 2 and parameterCategory == 4 and parameterNumber == 21 and typeOfFirstFixedSurface == 160 and level == 10`

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
  "grib": "salinity10m"
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
    "contour_label_height": 0.4,
    "contour_label_colour": "navy",
    "contour_label_frequency": 1,
    "contour_label_blanking": false,
    "contour_shade": true,
    "contour_level_list": [
      10.0,
      15.0,
      20.0,
      25.0,
      30.0,
      35.0,
      36.0,
      37.0,
      38.0,
      39.0,
      40.0
    ],
    "contour_level_selection_type": "list",
    "contour_shade_colour_list": [
      "#2a2f9e",
      "#4055b9",
      "#587cd2",
      "#469be6",
      "#2ec0fa",
      "#a0e13c",
      "#d8e219",
      "#fdf925",
      "#fdd525",
      "#fd9935"
    ],
    "contour_shade_colour_method": "list",
    "contour_shade_method": "area_fill",
    "legend": true,
    "legend_display_type": "continuous",
    "legend_title": true,
    "legend_title_text": "Salinity at -10m [psu]",
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

