# vis: Visibility

Mixer: **default**

## Inputs

* **vis**:
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,3,20`
        * **grib_filter matcher**: `shortName is "vis"`
    * Model **cosmo**:
        * **vg6d_transform arguments**: --output-variable-list=B20001
        * **Preprocessing**: vg6d_transform
        * **Inputs**: t2m, 2d
    * Model **icon**:
        * **vg6d_transform arguments**: --output-variable-list=B20001
        * **Preprocessing**: vg6d_transform
        * **Inputs**: t2m, 2d

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
  "grib": "vis"
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
    "contour_interpolation_floor": 0.0,
    "contour_shade_colour_list": [
      "rgb(0.004,0.129,0.800)",
      "rgb(0.000,0.671,1.000)",
      "rgb(0.000,0.776,1.000)",
      "rgb(0.000,1.000,0.992)",
      "rgb(0.000,0.996,1.000)",
      "rgb(0.106,0.996,0.573)",
      "rgb(0.420,0.996,0.098)",
      "rgb(0.604,0.996,0.000)",
      "rgb(0.992,0.827,0.110)",
      "rgb(0.996,0.898,0.294)",
      "rgb(1.000,0.965,0.490)",
      "rgb(1.000,1.000,1.000)"
    ],
    "contour_level_list": [
      0,
      50,
      100,
      150,
      200,
      350,
      600,
      800,
      1500,
      3000,
      5000,
      8000,
      10000
    ],
    "legend": true,
    "legend_display_type": "continuous",
    "legend_title": true,
    "legend_title_text": "Visibility [m]",
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

