# tiles/warrows700: Wind arrows 700hPa

Mixer: **default**

## Inputs

* **uv700**:
    * **Preprocessing**: cat
    * **Inputs**: u700, v700
* **u700**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,33;level:GRIB1,100,700`
        * **grib_filter matcher**: `centre != 98 and shortName is "u" and levelType == 100 and level == 700 and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,131;level:GRIB1,100,700`
        * **grib_filter matcher**: `centre == 98 and shortName is "u" and levelType == 100 and level == 700`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,002,002,,;level:GRIB2S,100,000,0000070000`
        * **grib_filter matcher**: `centre != 98 and shortName is "u" and typeOfLevel is "isobaricInhPa" and level == 700 and editionNumber == 2`
* **v700**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,34;level:GRIB1,100,700`
        * **grib_filter matcher**: `centre != 98 and shortName is "v" and levelType == 100 and level == 700 and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,132;level:GRIB1,100,700`
        * **grib_filter matcher**: `centre == 98 and shortName is "v" and levelType == 100 and level == 700`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,,002,003,,;level:GRIB2S,100,000,0000070000`
        * **grib_filter matcher**: `centre != 98 and shortName is "v" and typeOfLevel is "isobaricInhPa" and level == 700 and editionNumber == 2`

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
  "grib": "uv700"
}
```

### add_wind

Add wind flag rendering of the previous data

With arguments:
```
{
  "params": {
    "wind_arrow_colour": "black",
    "wind_arrow_thickness": 2,
    "wind_field_type": "arrows",
    "wind_flag_cross_boundary": false,
    "wind_arrow_unit_velocity": 25.0,
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

