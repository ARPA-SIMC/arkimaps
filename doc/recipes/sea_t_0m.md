# sea_t_0m: Sea temperature at -0.5m

Mixer: **default**

## Inputs

* **seat0m**:
    * **Arkimet matcher**: `product:GRIB2,,,004,018,,;level:GRIB2S,160,002,0000000035`
    * **grib_filter matcher**: `editionNumber == 2 and parameterCategory == 4 and parameterNumber == 18 and typeOfFirstFixedSurface == 160 and level == 0`
    * **mgrib {k}**: `False`
    * **mgrib {k}**: `-273.15`

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
  "grib": "seat0m"
}
```

### add_contour

Add contouring of the previous data

With arguments:
```
{
  "params": {
    "contour": true,
    "contour_line_colour": "#222222",
    "contour_line_thickness": 1,
    "contour_highlight": false,
    "contour_label_height": 0.4,
    "contour_label_colour": "navy",
    "contour_label_frequency": 1,
    "contour_label_blanking": false,
    "contour_shade": true,
    "contour_level_list": [
      5.0,
      6.0,
      7.0,
      8.0,
      9.0,
      10.0,
      11.0,
      12.0,
      13.0,
      14.0,
      15.0,
      16.0,
      17.0,
      18.0,
      19.0,
      20.0,
      21.0,
      22.0,
      23.0,
      24.0,
      25.0
    ],
    "contour_level_selection_type": "list",
    "contour_shade_colour_list": [
      "#660099",
      "#3200cd",
      "#0000ff",
      "#004cd9",
      "#0078c3",
      "#00a3ae",
      "#00cf98",
      "#00fa82",
      "#cce666",
      "#eef666",
      "#ffff0f",
      "#ffe100",
      "#ffb700",
      "#ff9000",
      "#ff6900",
      "#fe0000",
      "#e30000",
      "#ca0000",
      "#ae0000",
      "#930000"
    ],
    "contour_shade_colour_method": "list",
    "contour_shade_method": "area_fill",
    "legend": true,
    "legend_display_type": "continuous",
    "legend_title": true,
    "legend_title_text": "Sea Temperature at -0.5m [\u00b0C]",
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

