# viwve: Vertical integral of eastward water vapour flux

Mixer: **default**

## Inputs

* **viwve**:
    * **Arkimet matcher**: `product:GRIB2,98,192,162,71,5`
    * **grib_filter matcher**: `shortName is "viwve"`
* **mslp**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,2`
        * **grib_filter matcher**: `shortName is "pmsl"`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,,2,2`
        * **grib_filter matcher**: `shortName is "pmsl"`

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
  "grib": "viwve"
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
      -1100.0,
      -700.0,
      -500.0,
      -300.0,
      -100.0,
      100.0,
      300.0,
      500.0,
      700.0,
      1100.0
    ],
    "contour_shade_colour_method": "list",
    "contour_shade_colour_list": [
      "#FF00FB",
      "#3300F9",
      "#72A1FB",
      "#00FFFE",
      "#FFFFFF",
      "#FFB12F",
      "#FF4F21",
      "#F8241D",
      "#9D1513"
    ],
    "contour_highlight": false,
    "contour_hilo": false,
    "legend": true,
    "legend_title": true,
    "legend_title_text": "Vertical integral of eastward water vapour flux",
    "legend_display_type": "continuous",
    "legend_automatic_position": "right",
    "legend_text_colour": "black",
    "legend_text_font_size": 0.4,
    "legend_title_font_size": 0.5
  }
}
```

### add_grib

Add a grib file

With arguments:
```
{
  "grib": "mslp",
  "params": {
    "grib_automatic_scaling": false,
    "grib_scaling_factor": 0.01
  }
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
    "contour_line_thickness": 2,
    "contour_highlight": false,
    "contour_label": true,
    "contour_label_height": 0.4,
    "contour_label_frequency": 2,
    "contour_label_blanking": true,
    "contour_label_colour": "navy",
    "legend": false
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

