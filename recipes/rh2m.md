# rh2m: Relative humidity at 2 metres

Mixer: **default**

## Inputs

* **rh2m**:
    * Model **cosmo**:
        * **vg6d_transform arguments**: --output-variable-list=B13003
        * **Preprocessing**: vg6d_transform
        * **Inputs**: t2m, 2d, mslp
    * Model **ifs**:
        * **vg6d_transform arguments**: --output-variable-list=B13003
        * **Preprocessing**: vg6d_transform
        * **Inputs**: t2m, 2d, mslp
* **t2m**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,11;level:GRIB1,105,2`
        * **grib_filter matcher**: `shortName is "2t" and indicatorOfTypeOfLevel == 105 and timeRangeIndicator == 0 and level == 2`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,,2,11;level:GRIB1,105,2`
        * **grib_filter matcher**: `shortName is "2t" and indicatorOfTypeOfLevel == 105 and timeRangeIndicator == 0 and level == 2`
* **2d**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,17`
        * **grib_filter matcher**: `shortName is "2d"`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,,2,17`
        * **grib_filter matcher**: `shortName is "2d"`
* **mslp**:
    * Model **cosmo**:
        * **Arkimet matcher**: `product:GRIB1,,2,2`
        * **grib_filter matcher**: `shortName is "pmsl"`
    * Model **ifs**:
        * **Arkimet matcher**: `product:GRIB1,,2,2`
        * **grib_filter matcher**: `shortName is "pmsl"`

## Steps

### add_basemap

Add a base map

With arguments:
```
{
  "params": {
    "subpage_map_projection": "cylindrical",
    "subpage_lower_left_longitude": -5.0,
    "subpage_lower_left_latitude": 30.0,
    "subpage_upper_right_longitude": 27.0,
    "subpage_upper_right_latitude": 55.0
  }
}
```

### add_coastlines_bg

Add background coastlines


### add_grib

Add a grib file

With arguments:
```
{
  "name": "rh2m"
}
```

### add_contour

Add contouring of the previous data

With arguments:
```
{
  "params": {
    "contour_shade": true,
    "contour_shade_method": "area_fill",
    "contour_level_selection_type": "level_list",
    "contour_shade_colour_method": "list",
    "contour_level_list": [
      0.0,
      20.0,
      40.0,
      60.0,
      80.0,
      90.0,
      100.0
    ],
    "legend": true,
    "contour_highlight": false,
    "contour_label": false,
    "contour_hilo": false,
    "contour": false,
    "contour_shade_colour_list": [
      "red",
      "orange",
      "yellow",
      "green",
      "cyan",
      "blue"
    ]
  }
}
```

### add_coastlines_fg

Add foreground coastlines


### add_grid

Add a coordinates grid


### add_boundaries

Add a coordinates grid

