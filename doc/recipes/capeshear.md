# capeshear: Convective available potential energy shear (m**2 s**-2)

Mixer: **default**

## Inputs

* **capeshear**:
    * **Arkimet matcher**: `product:GRIB1,98,228,44`
    * **grib_filter matcher**: `centre == 98 and shortName is "capes"`

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
  "grib": "capeshear"
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
    "contour_level_selection_type": "level_list",
    "contour_shade_colour_method": "list",
    "contour_shade_method": "area_fill",
    "contour_shade_colour_list": [
      "#bcbdef",
      "#7778ef",
      "#0178ff",
      "#02bcff",
      "#04fdef",
      "#01acac",
      "#00781d",
      "#06fb2f",
      "#cefb02",
      "#ff9a00",
      "#ff1e00",
      "#ac1a77",
      "#fe38ff",
      "#7730ff"
    ],
    "contour_level_list": [
      10,
      50,
      100,
      200,
      300,
      400,
      500,
      600,
      800,
      1000,
      1250,
      1500,
      1750,
      2000,
      4000
    ],
    "contour_highlight": false,
    "contour_hilo": false,
    "contour_label": false,
    "legend": true,
    "legend_title": true,
    "legend_text_font_size": 0.4,
    "legend_title_text": "Cape Shear [m**2/s**2]",
    "legend_text_colour": "black",
    "legend_title_font_size": 0.5,
    "legend_automatic_position": "right",
    "legend_display_type": "continuous"
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

