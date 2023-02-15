# standalone/cc: Cloud Cover Layers

Mixer: **default**

## Inputs

* **lcc**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,73`
        * **grib_filter matcher**: `shortName is "clcl"`
        * **mgrib {k}**: `False`
        * **mgrib {k}**: `0.08`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,006,022,,;level:GRIB2D,100,000,0000080000,001,000,0000000000`
        * **grib_filter matcher**: `shortName is "ccl" and scaledValueOfFirstFixedSurface == 80000 and scaledValueOfSecondFixedSurface == 0 and editionNumber == 2`
        * **mgrib {k}**: `False`
        * **mgrib {k}**: `0.08`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,186`
        * **grib_filter matcher**: `shortName is "lcc"`
        * **mgrib {k}**: `False`
        * **mgrib {k}**: `8`
* **mcc**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,74`
        * **grib_filter matcher**: `shortName is "clcm"`
        * **mgrib {k}**: `False`
        * **mgrib {k}**: `0.08`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,006,022,,;level:GRIB2D,100,000,0000040000,100,000,0000080000`
        * **grib_filter matcher**: `shortName is "ccl" and scaledValueOfFirstFixedSurface == 40000 and scaledValueOfSecondFixedSurface == 80000 and editionNumber == 2`
        * **mgrib {k}**: `False`
        * **mgrib {k}**: `0.08`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,187`
        * **grib_filter matcher**: `shortName is "mcc"`
        * **mgrib {k}**: `False`
        * **mgrib {k}**: `8`
* **hcc**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,75`
        * **grib_filter matcher**: `shortName is "clch"`
        * **mgrib {k}**: `False`
        * **mgrib {k}**: `0.08`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,006,022,,;level:GRIB2D,100,000,0000000000,100,000,0000040000`
        * **grib_filter matcher**: `shortName is "ccl" and scaledValueOfFirstFixedSurface == 0 and scaledValueOfSecondFixedSurface == 40000 and editionNumber == 2`
        * **mgrib {k}**: `False`
        * **mgrib {k}**: `0.08`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,188`
        * **grib_filter matcher**: `shortName is "hcc"`
        * **mgrib {k}**: `False`
        * **mgrib {k}**: `8`

## Steps

### add_basemap

Add a base map


### add_coastlines_bg

Add background coastlines

With arguments:
```
{
  "params": {
    "map_coastline_sea_shade_colour": "black",
    "map_coastline_sea_shade": true,
    "map_coastline_land_shade_colour": "black",
    "map_coastline_land_shade": true
  }
}
```

### add_grib

Add a grib file

With arguments:
```
{
  "grib": "lcc"
}
```

### add_contour

Add contouring of the previous data

With arguments:
```
{
  "params": {
    "contour": true,
    "contour_level_selection_type": "interval",
    "contour_interval": 1.0,
    "contour_shade": true,
    "contour_shade_method": "dot",
    "contour_shade_dot_size": 0.01,
    "contour_shade_min_level": 2.0,
    "contour_shade_max_level": 8.0,
    "contour_shade_min_level_colour": "red",
    "contour_shade_max_level_colour": "red",
    "contour_shade_min_level_density": 1.0,
    "contour_shade_max_level_density": 90,
    "contour_line_colour": "red",
    "contour_highlight": false,
    "contour_label": false,
    "contour_hilo": false,
    "legend": true,
    "legend_title": true,
    "legend_text_font_size": 0.4,
    "legend_title_text": "nubi per strati [ottavi]",
    "legend_automatic_position": "right",
    "legend_entry_plot_orientation": "top_bottom"
  }
}
```

### add_grib

Add a grib file

With arguments:
```
{
  "grib": "mcc"
}
```

### add_contour

Add contouring of the previous data

With arguments:
```
{
  "params": {
    "contour": true,
    "contour_level_selection_type": "interval",
    "contour_interval": 1.0,
    "contour_shade": true,
    "contour_shade_method": "dot",
    "contour_shade_dot_size": 0.01,
    "contour_shade_min_level": 3.0,
    "contour_shade_max_level": 8.0,
    "contour_shade_min_level_colour": "green",
    "contour_shade_max_level_colour": "green",
    "contour_shade_min_level_density": 1.0,
    "contour_shade_max_level_density": 70,
    "contour_line_colour": "green",
    "contour_highlight": false,
    "contour_label": false,
    "contour_hilo": false,
    "legend": true,
    "legend_title": true,
    "legend_text_font_size": 0.4,
    "legend_title_text": "nubi per strati [ottavi]",
    "legend_automatic_position": "right",
    "legend_entry_plot_orientation": "top_bottom"
  }
}
```

### add_grib

Add a grib file

With arguments:
```
{
  "grib": "hcc"
}
```

### add_contour

Add contouring of the previous data

With arguments:
```
{
  "params": {
    "contour": true,
    "contour_level_selection_type": "interval",
    "contour_interval": 1.0,
    "contour_shade": true,
    "contour_shade_method": "dot",
    "contour_shade_dot_size": 0.01,
    "contour_shade_min_level": 4.0,
    "contour_shade_max_level": 8.0,
    "contour_shade_min_level_colour": "cyan",
    "contour_shade_max_level_colour": "cyan",
    "contour_shade_min_level_density": 1.0,
    "contour_shade_max_level_density": 50,
    "contour_line_colour": "cyan",
    "contour_highlight": false,
    "contour_label": false,
    "contour_hilo": false,
    "legend": true,
    "legend_title": true,
    "legend_text_font_size": 0.4,
    "legend_title_text": "nubi per strati [ottavi]",
    "legend_automatic_position": "right",
    "legend_entry_plot_orientation": "top_bottom"
  }
}
```

### add_coastlines_fg

Add foreground coastlines

With arguments:
```
{
  "params": {
    "map_coastline_colour": "white",
    "map_coastline_thickness": 3
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
    "map_boundaries_colour": "white",
    "map_administrative_boundaries_countries_list": [
      "ITA"
    ],
    "map_administrative_boundaries_style": "solid",
    "map_administrative_boundaries": true,
    "map_administrative_boundaries_colour": "white"
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

