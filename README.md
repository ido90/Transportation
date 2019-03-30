# Matching of Recorded Bus Trips to Planned Routes

Written by Ido Greenberg and Oded Shimon in 2019, as part of a Civil Hackathon of the Israeli Workshop of Public Knowledge.

## Abstract
Both data sets of planned bus routes and of actual bus trips are publicly available in Israel, allowing diagnosis of trips and comparison of their timings and routes to the plans.
However, it is suspected that the reported matching between the planned routes and the actual trips is inaccurate, making any diagnosis ineffective.

This project shows that within limited subsets of the data (that were provided in the hackathon), practically all the observed trips correctly correspond to their reported route.
It also provides general tools for detection of uncertainly-classified trips (with more than one plausible planned route) and of anomalous trips (with no plausible planned route), and convenient visualization of these anomalous trips.

The match of a trip to a planned route is essentially calculated through the distances of the observed trip locations from the route.

The complete results and a sample of figures are available in the output/ directory.

## Challenge Definition

The challenge is based on two public data sets (see references below):

1. Planned routes of bus lines - including date, **route identifier** (roughly mappable to the conventional bus line), **shape identifier** (more detailed identifier which describes the slight variants of the routes), and **the route itself** (given as hundreds of pairs of latitude and longitude coordinates).

2. GPS tracking of the actual trips of buses (ideally with frequency of 1 observation per minute) - including **trip identifier**, time of observation, **location** (given as a pair of latitude and longitude coordinates), and **route identifier** (corresponding to the planned route of the trip).
This data set can be used, for example, to compare the planned trips to the actual ones - timings, routes and even existence of trips.

Unfortunately, it is suspected that the route identifier assigned to each trip is unreliable, which makes any comparison between plans & actual drives ineffective.
The challenge is to estimate and fix this possible flaw in the data.

**Goal**: given data sets of planned bus routes and actual bus trips, assign each trip to the most plausible route identifier (wihtout using the reported route identifier).

In the scope of the hackathon, a data set of 6 routes (with ~3 shape-variants per route) was provided. All the routes are quite similar and getting from Tel-Aviv to Raanana (one direction only).

In addition, a data set of ~4000 trips was provided, split to equally train & test groups, where the latter has no reported route identifier.

## Methodology
### Data cleanup

- Remove trips with too few observations, since the high similarity between many routes often requires observations from all along the trip. A threshold of 25 observations per trip was chosen according to the distribution of the number of observations (see distribution in output directory).

- Remove empty observations (with 0 in either latitude or longitude).

- Convert latitude and longitude, respectively, to y and x coordinates within a 2D map, with units of meters.

### Route-ID assignment algorithm

The algorithm essentially picks for every trip the route which is closest to its observed location points:

1. The "error" of a location observation wrt a route interval, is defined as the distance between the location point and the interval (slight old school geometry is required).
The idea is that if the location should be on the interval, the distance should express GPS errors, map inaccuracies and actual deviations from the planned road.

2. The error of a location observation wrt a route, is the minimum error over all the route's intervals.

3. The error of a trip wrt a route, is defined as the mean of the squared observations-errors (MSE).

4. The route corresponding to the smallest error is chosen as the estimated route of the trip.

### Analysis
The algorithm described above allows computation of several useful results and metrics:

- **Best-fit route** - as described above.

- **Plausibility** of the best-fit route: simply provided by the RMSE corresponding to this route (in units of meters). Exceptionally large error indicates that the trip does not well-correspond to any of the routes in the data.

- **Certainty** of the best-fit: provided by the RMSE of the best fit (denoted m1), compared to the 2nd best fit (denoted m2). In particular, we used the metric certainty = (m2-m1)/m2 = 1-m1/m2, which ranges between 0 (two identically pleasible routes) and 1 (one exactly fitted route).

## Results
### Running time
The whole analysis took 15-20 minutes per each dataset (train & test) in a personal laptop (i7 quadcore).
In the partially-supported C++ implementation, it took ~15 seconds.

### Findings
The following findings are demonstrated in the figures available in the output/ directory:

1. In the data that was used in the hackathon, **all the reportd route IDs of the trips seem to be correct**.

2. The current project **reconstructs the route IDs independently and successfully, most of the time with high plausibility and certainty**. In particular, there was **exactly 1 inconsistency** between the reconstructed and the reported route ID (out of more than 2K labeled trips).

3. **Low plausibility** typically corresponds to trips with **radical outlier observations**, which probably express errors in the GPS or in the stored data. Interestingly, **the algorithm seems insensitive to these outliers**, and picks the right route ID nonetheless.

4. **Low certainty** typically corresponds to **very similar routes**, in particular in trips where no observations are available in the areas that distinct between the similar routes.

## Possible Scale-up Extensions
Several possible extensions to the project may be beneficial, in particular for larger scale of data:

1. Running time optimization: quickly reject clearly-unfit routes - without computing the whole MSE.

2. Distinguishing between opposite-direction routes by taking trip direction into account, e.g. through the start & end points.

3. Exploiting times of trip observations, e.g. by forcing the order of the observed trip points to match the order of their corresponding intervals in the route. This would complicate the calculation of the distance between a trip and a route, but should probably be solvable by Dynamic Programming.

4. Distinguishing between routes which are subsets of each other, e.g. by measuring the cover of each route by the observed trip (i.e. if one route is similar to another with an additional interval, and there are no observed points in the additional interval, then the shorter route is better covered by the trip, hence likelier).

5. Probabilistic modeling: the RMSEs of the trips wrt rodfutes may be replaced by probabilistic terms, e.g. by assuming the observation error to follow the distribution P(e)~exp(-alpha\*e^2) (making the SSE equal the log-likelihood).
While this may seem more elegant and allow corresponding decision-making, the probabilities - even if can be approximated by such a model - may be too sensitive to the scale of the model (represented by alpha).

## Relevant Links
Project presentation:
https://docs.google.com/presentation/d/1Bj7gmMqxZy01rXaEYRNMPV5WiuhOmw9ZtTcVtFbSWaQ/edit?usp=sharing

Hackathon homepage:
https://civichack2019.hasadna.org.il/hackathon

Schedule:
https://civichack2019.hasadna.org.il/schedule

Updates:
https://forum.hasadna.org.il/t/topic/2255


Challenges:
https://hackdash.org/dashboards/civichack

Github:
https://github.com/hasadna/open-bus/commit/92e9dd8d0135d8cfe2ebb9c0e2d6b78384336437


Transportation challenge:
https://hackdash.org/projects/5c86bc72256b2a1313910628

Github:
https://github.com/hasadna/open-bus/issues/156

Data:
https://drive.google.com/drive/folders/1uGbutPLIm1cnLUy3-q8QJEaDyoQ4tCHK
