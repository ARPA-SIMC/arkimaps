# mslp: Mean Sea Level Pressure

Mixer: **default**

## Inputs

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
  "name": "mslp",
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
    "contour_line_thickness": 2,
    "contour_highlight": false,
    "contour_label": true,
    "contour_label_height": 0.4,
    "contour_label_frequency": 2,
    "contour_label_blanking": true,
    "contour_label_colour": "navy",
    "legend": false
  }
}
```

### add_coastlines_fg

Add foreground coastlines


### add_grid

Add a coordinates grid


### add_boundaries

Add political boundaries


