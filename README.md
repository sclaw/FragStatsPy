<img src="images/main.JPG" alt= “FragStatsPy”>


## Python Wrapper for Fragstats

FragStatsPy a wrapper to [Fragstats](https://fragstats.org/) that allows for automated model setup and execution.  While Fragstats currently provides a command-line tool for model execution, it does not provide command-line tools for model setup.  FragStatsPy begins to fill that gap by providing functions to generate and manipulate Fragstats models from within Python.

Current functionality includes
* Model database generation
* Loading landscape layers
* Setting the output base path
* Defining a sampling strategy
* Linking user-defined tiles
* A general purpose SQL editor to allow for complete model manipulation (for savvy users)
* Access to the Fragstats native run commands (command-line)
