tbb-fp
======

Demo project to evaluate Tor Browser's fingerprinting defense for screen resolution.

Calculates the amount of entropy reduction by the existing screen resolution countermeasure and runs simulations with different window resizing parameters. Reports the entropy of the new distribution, number of different anonymity sets and some metrics.

Computations are based on Panopticlick database dump found on [Tor Bug Tracker](https://trac.torproject.org/projects/tor/attachment/ticket/4810/panopticlick-screen-resolution-detection.txt).

## Result of simulations.
Run the tool yourself to get more detailed results.

| Countermeasure | Shannon-Entropy (bits) |Number of anonymity sets (# of bins) | Area of TBB Window / Desktop area  |
| ------------- |:-------------:|:-----:|:-----:|
| None (Original data)      | **4.68** (was 4.83 in the [original paper](https://panopticlick.eff.org/browser-uniqueness.pdf#page=17)) | 2695 | - |
| Screens above 640x480 (data used to run simulations)       | **5.14** | 2298 | - |
| Existing countermeasure (resize window to multiples 200x100px and report inner screen size as the resolution)      | **2.63**      |   43 | %57.55|
| Resize window height to multiples of 200px      | **1.79** | 28 | %52.83 |
| Enforce an aspect ratio of 1.1 for screens with chrome height > 800px      | **1.28** | 13 | %51.35 |
| Resize height to multiples of 200px + enforce aspect ratio of 1.1      | **0.37** | 9 | %45.26 |
