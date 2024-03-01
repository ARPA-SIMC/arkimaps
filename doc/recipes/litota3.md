# litota3: Averaged total lightning flash density in the last 3 hours

Mixer: **default**

## Inputs

* **litota3**:
    * **Arkimet matcher**: `product:GRIB2,,000,017,004,,; timerange:Timedef,,0,3h`
    * **grib_filter matcher**: `shortName is "litota3"`

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
  "grib": "litota3"
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
    "contour_shade_method": "area_fill",
    "contour_level_selection_type": "level_list",
    "contour_level_list": [
      0.1,
      0.5,
      1.0,
      2.0,
      5.0,
      10.0,
      20.0,
      50.0,
      100.0
    ],
    "contour_shade_colour_method": "list",
    "contour_shade_colour_list": [
      "#CC97A1",
      "#610B1D",
      "#A90528",
      "#FF032F",
      "#FF7126",
      "#FFA12D",
      "#FFDA37",
      "#FDFC3F"
    ],
    "contour_highlight": false,
    "contour_hilo": false,
    "legend": true,
    "legend_display_type": "continuous",
    "legend_title": true,
    "legend_title_text": "Averaged total lightning in the last 3h",
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

