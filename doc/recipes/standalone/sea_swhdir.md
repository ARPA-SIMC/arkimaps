# standalone/sea_swhdir: Significant wave height (m) and direction

Mixer: **default**

## Inputs

* **swh**:
    * Model **swan**:
        * **Arkimet matcher**: `product:GRIB1,,140,229`
        * **grib_filter matcher**: `shortName is "swh" and editionNumber == 1`
    * Model **adriac**:
        * **Arkimet matcher**: `product:GRIB2,,,000,003,,`
        * **grib_filter matcher**: `shortName is "swh" and editionNumber == 2`
* **seaswhdir**:
    * **Preprocessing**: cat
    * **Inputs**: swh, wvdir
    * **mgrib {k}**: `sd`
* **wvdir**:
    * Model **swan**:
        * **Arkimet matcher**: `product:GRIB1,,140,230`
        * **grib_filter matcher**: `shortName is "mwd" and editionNumber == 1`
    * Model **adriac**:
        * **Arkimet matcher**: `product:GRIB2,,,000,004,,`
        * **grib_filter matcher**: `shortName is "wvdir" and editionNumber == 2`

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
  "grib": "swh"
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
      "rgb(0.753,0.945,0.976)",
      "rgb(0.451,0.639,1.000)",
      "rgb(0.000,0.502,1.000)",
      "rgb(0.259,0.710,0.651)",
      "rgb(0.639,0.949,0.565)",
      "rgb(0.000,1.000,0.000)",
      "rgb(1.000,1.000,0.000)",
      "rgb(1.000,0.690,0.000)",
      "rgb(1.000,0.502,0.000)",
      "rgb(1.000,0.000,0.082)",
      "rgb(0.859,0.000,0.118)",
      "rgb(0.722,0.000,0.039)",
      "rgb(0.608,0.000,0.024)"
    ],
    "contour_level_list": [
      0.0,
      0.1,
      0.5,
      0.8,
      1.25,
      1.8,
      2.5,
      3.2,
      4.0,
      5.0,
      6.0,
      7.0,
      9.0,
      14.0
    ],
    "contour_highlight": false,
    "contour_hilo": false,
    "legend": true,
    "legend_text_colour": "black",
    "legend_title": true,
    "legend_title_text": "Significant wave height [m]",
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
  "grib": "seaswhdir"
}
```

### add_wind

Add wind flag rendering of the previous data

With arguments:
```
{
  "params": {
    "wind_arrow_colour": "black",
    "wind_arrow_thickness": 1,
    "wind_field_type": "arrows",
    "wind_flag_cross_boundary": false,
    "wind_arrow_unit_velocity": 2.5,
    "wind_arrow_calm_indicator": false,
    "wind_thinning_method": "automatic",
    "wind_thinning_factor": 1
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

