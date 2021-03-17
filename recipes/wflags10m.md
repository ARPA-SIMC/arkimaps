# wflags10m: Wind flags 10m

Mixer: **default**

## Inputs

* **uv10m**:
    * **Preprocessing**: cat
    * **Inputs**: u10m, v10m
* **u10m**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,33;level:GRIB1,105,10`
        * **grib_filter matcher**: `shortName is "10u"`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,,2,33;level:GRIB1,105,10`
        * **grib_filter matcher**: `shortName is "10u"`
* **v10m**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,34;level:GRIB1,105,10`
        * **grib_filter matcher**: `shortName is "10v"`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,,2,34;level:GRIB1,105,10`
        * **grib_filter matcher**: `shortName is "10v"`

## Steps

### add_basemap

Add a base map


### add_coastlines_bg

Add background coastlines

With arguments:
```
{
  "params": {
    "map_coastline_general_style": "background"
  }
}
```

### add_grib

Add a grib file

With arguments:
```
{
  "grib": "uv10m"
}
```

### add_wind

Add wind flag rendering of the previous data

With arguments:
```
{
  "params": {
    "wind_field_type": "flags",
    "wind_flag_colour": "black",
    "wind_flag_length": 0.8,
    "wind_flag_origin_marker": false,
    "wind_flag_cross_boundary": true,
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
    "map_coastline_resolution": "medium"
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

