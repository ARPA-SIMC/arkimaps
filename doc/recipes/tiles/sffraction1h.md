# tiles/sffraction1h: Snow fraction 1h

Mixer: **default**

## Inputs

* **sffraction1h**:
    * **Preprocessing**: sffraction
    * **Inputs**: tpdec1h, snowdec1h
* **tpdec1h**:
    * **Decumulation step**: 1
    * **Preprocessing**: decumulate
    * **Inputs**: tp
* **tp**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,61`
        * **grib_filter matcher**: `centre != 98 and shortName is "tp" and editionNumber == 1`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,98,128,228`
        * **grib_filter matcher**: `centre == 98 and shortName is "tp"`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,000,001,052,015,001`
        * **grib_filter matcher**: `centre != 98 and shortName is "tp" and editionNumber == 2`
* **snowdec1h**:
    * Model **cosmo**:
        * **Decumulation step**: 1
        * **Preprocessing**: decumulate
        * **Inputs**: snowcosmo
    * Model **icon**:
        * **Decumulation step**: 1
        * **Preprocessing**: decumulate
        * **Inputs**: snowcosmo
    * Model **ifs**:
        * **Decumulation step**: 1
        * **Preprocessing**: decumulate
        * **Inputs**: sf
* **snowcosmo**:
    * Model **cosmo**:
        * **Preprocessing**: or
        * **Inputs**: snowsum, snowgsp
    * Model **icon**:
        * **Preprocessing**: or
        * **Inputs**: snowsum, snowgsp
* **snowsum**:
    * Model **cosmo**:
        * **vg6d_transform arguments**: --output-variable-list=B13205
        * **Preprocessing**: vg6d_transform
        * **Inputs**: snowcon, snowgsp
    * Model **icon**:
        * **vg6d_transform arguments**: --output-variable-list=B13205
        * **Preprocessing**: vg6d_transform
        * **Inputs**: snowcon, snowgsp
* **snowcon**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,78`
        * **grib_filter matcher**: `( shortName is "snoc" or shortName is "snow_con" ) and editionNumber == 1`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,000,001,055,015,001`
        * **grib_filter matcher**: `shortName is "snow_con" and editionNumber == 2`
* **snowgsp**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,79`
        * **grib_filter matcher**: `( shortName is "lssf" or shortName is "snow_gsp" ) and editionNumber == 1`
    * Model **icon**:
        * **Arkimet matcher**: `product:GRIB2,,000,001,056,015,001`
        * **grib_filter matcher**: `shortName is "snow_gsp" and editionNumber == 2`

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
  "grib": "sffraction1h",
  "params": {
    "grib_automatic_scaling": false
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
    "contour_line_colour": "red",
    "contour_line_style": "dot",
    "contour_line_thickness": 2,
    "contour_label_height": 0.4,
    "contour_highlight": false,
    "contour_label": true,
    "contour_min_level": 25.0,
    "contour_max_level": 100.0,
    "contour_interval": 25.0,
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

