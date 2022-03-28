# Creating a new recipe

1. Pick a name
2. Identify inputs with arkimet and eccodes filters
3. Draft a recipe
4. Run a test dispatch to collect test samples
5. Run `arki-scan --inline` on the collected test samples to wrap them with
   arkimet metadata
6. Run [mktestsample](https://github.com/ARPA-SIMC/mktestsample/) on the
   samples to minimize them
7. Move the test samples to `testdata/$recipename`
8. Create a new test in `tests/test_$recipename.py`
9. Fine tune the recipe with `arkimaps preview`
10. Update the tests a part of the recipes become ok and move from 'prototype'
    to 'production'
