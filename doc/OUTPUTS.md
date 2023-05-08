# Output files

This file docuemnts the files that can be found in the output tarball.

## `products.json`

This file contains information about generated products.

It is represented as a list of information records for each product.

Each information record is in the form:

```
{
  "flavour": {
    "name" (str): the name of the flavour used,
    "defined_in" (str): the path of the YAML file where the flavour is defined
  },
  "recipe": {
    "name" (str): the name of the recipe
    "defined_in" (str): the path of the YAML file where the recipe is defined
    "description" (str): the description from the recipe YAML file
    "info" (Any): the value of the info field in the recipe YAML file
  },
  "reftimes": {
    "YYYY-mm-dd HH:MM:SS": {
      "inputs" (list[str]): list of input names used in this product
      "steps" (dict[int, int]): number of products generated for each step
      "legend_info" (dict[str, Any]): dictionary of MAGICS parameters used to generate the legend
      "render_stats": {
          "time_ns": time it took to generate all products for this step, in nanoseconds
      },
    }
  }
}
```

## `inputs.json`

This file contains details about which inputs have been used by which recipes.

It is represented as a dictionary, whose keys are input names, and values are
statistics on the use of that input.

```
{
  "input_name" (dict): statistics about this input
}
```

The statistics in turn are dictionary with two elements:

```
{
  "used_by" (list[str]): …
  "computation" (list[tuple[int, str]]): …
}
```

* `used_by` is a list with the names of the recipes that used this input
* `computation` is a list of the computation steps that were taken to generate
  this input. Each element of the list is the elapsed time in nanosecond, and a
  description of the computation step


## `log.json`

This files contains the Python logging output generated during processing.

It is represented as a list one records, one per message, each with these
fields:

* `ts`: UNIX timestamp, floating point
* `level`: numeric log level
* `msg`: formatted log message
* `name`: name of the subsystem that generated the logging message

