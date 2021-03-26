# warrows925: Wind arrows 925hPa

Mixer: **default**

## Inputs

* **uv925**:
    * **Preprocessing**: cat
    * **Inputs**: u925, v925
* **u925**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,33;level:GRIB1,100,925`
        * **grib_filter matcher**: `shortName is "u" and indicatorOfTypeOfLevel == 100 and level == 925`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,,2,33;level:GRIB1,100,925`
        * **grib_filter matcher**: `shortName is "u" and indicatorOfTypeOfLevel == 100 and level == 925`
* **v925**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,34;level:GRIB1,100,925`
        * **grib_filter matcher**: `shortName is "v" and indicatorOfTypeOfLevel == 100 and level == 925`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,,2,34;level:GRIB1,100,925`
        * **grib_filter matcher**: `shortName is "v" and indicatorOfTypeOfLevel == 100 and level == 925`

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
  "grib": "uv925"
}
```

### add_wind

Add wind flag rendering of the previous data

With arguments:
```
{
  "params": {
    "wind_arrow_colour": "black",
    "wind_arrow_thickness": "thick",
    "wind_field_type": "arrows",
    "wind_flag_cross_boundary": false,
    "wind_arrow_unit_velocity": 12.5,
    "wind_arrow_calm_indicator": false,
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

