# tiles/wflags850: Wind flags 850hPa

Mixer: **default**

## Inputs

* **uv850**:
    * **Preprocessing**: cat
    * **Inputs**: u850, v850
* **u850**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,33;level:GRIB1,100,850`
        * **grib_filter matcher**: `centre != 98 and shortName is "u" and levelType == 100 and level == 850 and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,131;level:GRIB1,100,850`
        * **grib_filter matcher**: `centre == 98 and shortName is "u" and levelType == 100 and level == 850`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,002,002,,;level:GRIB2S,100,000,0000085000`
        * **grib_filter matcher**: `centre != 98 and shortName is "u" and typeOfLevel is "isobaricInhPa" and level == 850 and editionNumber == 2`
* **v850**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,34;level:GRIB1,100,850`
        * **grib_filter matcher**: `centre != 98 and shortName is "v" and levelType == 100 and level == 850 and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,132;level:GRIB1,100,850`
        * **grib_filter matcher**: `centre == 98 and shortName is "v" and levelType == 100 and level == 850`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,002,003,,;level:GRIB2S,100,000,0000085000`
        * **grib_filter matcher**: `centre != 98 and shortName is "v" and typeOfLevel is "isobaricInhPa" and level == 850 and editionNumber == 2`

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
  "grib": "uv850"
}
```

### add_wind

Add wind flag rendering of the previous data

With arguments:
```
{
  "params": {
    "wind_field_type": "flags",
    "wind_flag_colour": "evergreen",
    "wind_flag_length": 0.8,
    "wind_flag_origin_marker": false,
    "wind_flag_cross_boundary": true,
    "wind_thinning_method": "automatic",
    "wind_thinning_factor": 2
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

