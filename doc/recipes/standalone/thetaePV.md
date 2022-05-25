# standalone/thetaePV: Theta-e at potential vorticity surface

Mixer: **default**

## Inputs

* **thetaePV**:
    * **Arkimet matcher**: `product:GRIB1,98,128,3;level:GRIB1,117,2000`
    * **grib_filter matcher**: `centre == 98 and shortName is "pt" and indicatorOfTypeOfLevel == 117 and level == 2000`
* **uvpv**:
    * **Preprocessing**: cat
    * **Inputs**: upv, vpv
* **upv**:
    * **Arkimet matcher**: `product:GRIB1,98,128,131;level:GRIB1,117,2000`
    * **grib_filter matcher**: `centre == 98 and shortName is "u" and indicatorOfTypeOfLevel == 117 and level == 2000`
* **vpv**:
    * **Arkimet matcher**: `product:GRIB1,98,128,132;level:GRIB1,117,2000`
    * **grib_filter matcher**: `centre == 98 and shortName is "v" and indicatorOfTypeOfLevel == 117 and level == 2000`
* **mslp**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,2`
        * **grib_filter matcher**: `shortName is "pmsl" and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,151`
        * **grib_filter matcher**: `shortName is "msl"`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,00080,000,003,001,015,001;level:GRIB2S,101,000,0000000000`
        * **grib_filter matcher**: `shortName is "pmsl" and editionNumber == 2`

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
  "grib": "thetaePV"
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
      "rgb(0.07451,0.00000,0.48235)",
      "rgb(0.05882,0.14510,0.55294)",
      "rgb(0.04314,0.28235,0.61176)",
      "rgb(0.02745,0.41961,0.67843)",
      "rgb(0.00784,0.55686,0.74510)",
      "rgb(0.00392,0.61569,0.71373)",
      "rgb(0.00392,0.59608,0.58824)",
      "rgb(0.00000,0.58431,0.46667)",
      "rgb(0.00392,0.54902,0.33725)",
      "rgb(0.00000,0.52941,0.21569)",
      "rgb(0.22353,0.63922,0.16863)",
      "rgb(0.44314,0.74118,0.12157)",
      "rgb(0.66667,0.84314,0.07451)",
      "rgb(0.89020,0.94902,0.02353)",
      "rgb(1.00000,0.89020,0.00000)",
      "rgb(1.00000,0.66667,0.00000)",
      "rgb(1.00000,0.44314,0.00000)",
      "rgb(1.00000,0.22353,0.00000)",
      "rgb(1.00000,0.00000,0.00000)"
    ],
    "contour_level_list": [
      270,
      295,
      300,
      305,
      310,
      315,
      320,
      325,
      330,
      335,
      340,
      345,
      350,
      355,
      360,
      365,
      370,
      375,
      380,
      440
    ],
    "contour_highlight": false,
    "contour_hilo": false,
    "legend": true,
    "legend_title": true,
    "legend_display_type": "continuous",
    "legend_text_font_size": 0.4,
    "legend_title_text": "Theta-e at PV surface [\u00b0K]",
    "legend_text_colour": "black",
    "legend_title_font_size": 0.5,
    "legend_automatic_position": "right"
  }
}
```

### add_grib

Add a grib file

With arguments:
```
{
  "grib": "uvpv"
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
    "wind_field_type": "arrows",
    "wind_flag_cross_boundary": false,
    "wind_arrow_unit_velocity": 25.0,
    "wind_arrow_min_speed": 15.0,
    "wind_arrow_calm_indicator": false,
    "wind_thinning_factor": 1,
    "wind_thinning_method": "automatic"
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
    "contour_line_thickness": 3,
    "contour_highlight": false,
    "contour_label": true,
    "contour_label_height": 0.5,
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

