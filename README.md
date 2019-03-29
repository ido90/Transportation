# Public Transportation Data Challenge

Written by Ido Greenberg and Oded Shimon in 2019, as part of a Civil Hackathon of the Israeli Workshop of Public Knowledge.

## Abstract

## Challenge Definition
### Data and Background

#### TODO remove

1. Bus-lines are available as a list of line-numbers along with the corresponding paths.
Each path is available as a list of 2D points (representing the locations of the stations).

2. Drives observations are available as a list of separated drives,
each containing a list of 2D locations along with the corresponding times.

### Goal

## Methodology

## Results
### Running time
The whole analysis took around 15-20 minutes per each dataset (train & test) in a personal laptop (i7 quadcore).

### Results

### Conclusions

## Possible Scale-up Extensions
Several possible extensions to the project may be beneficial, in particular for larger scale of data:

1. Running time optimization: quickly reject clearly-unfit routes - without computing the whole MSE.

2. Distinguishing between opposite-direction routes by taking trip direction into account, e.g. through the start & end points.

3. Exploiting times of trip observations, e.g. by forcing the order of the observed trip points to match the order of their corresponding intervals in the route. This would complicate the calculation of the distance between a trip and a route, but should probably be solvable by Dynamic Programming.

4. Probabilistic modeling: the RMSEs of the trips wrt rodfutes may be replaced by probabilistic terms, e.g. by assuming the observation error to follow the distribution P(e)~exp(-alpha\*e^2) (making the SSE equal the log-likelihood). Such a model can expresses GPS errors, map inaccuracies and actual deviations from the planned road.
While this may seem more elegant and allow corresponding decision-making, the probabilities - even if can be approximated by such a model - may be too sensitive to the scale of the model (represented by alpha).

## Relevant Links

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
