# Transportation

relevant links:

hackathon homepage:
https://civichack2019.hasadna.org.il/hackathon

schedule:
https://civichack2019.hasadna.org.il/schedule

updates:
https://forum.hasadna.org.il/t/topic/2255


challenges:
https://hackdash.org/dashboards/civichack

github:
https://github.com/hasadna/open-bus/commit/92e9dd8d0135d8cfe2ebb9c0e2d6b78384336437


our challenge:
https://hackdash.org/projects/5c86bc72256b2a1313910628

github:
https://github.com/hasadna/open-bus/issues/156

data:
https://drive.google.com/drive/folders/1uGbutPLIm1cnLUy3-q8QJEaDyoQ4tCHK




--------------- Data assumptions ---------------

1. Bus-lines are available as a list of line-numbers along with the corresponding paths.
Each path is available as a list of 2D points (representing the locations of the stations).

2. Drives observations are available as a list of separated drives,
each containing a list of 2D locations along with the corresponding times.


--------------- Model assumptions ---------------

1. The probability of observation of a bus in distance d from the line goes like exp(-d^2),
expressing GPS errors, map inaccuracies, and actual deviations from the planned road.

Note: that's a quite arbitrary-scale assumption, since the basis of the exponent e,
determines the ratio between probabilities. This will be a problem when estimating the
gap between the probabilities. However, it does not affect the identity of the ML line.

Note: the ML line is actually the one that minimizes the MSE.

2. The prior probability for all the lines is identical. Alternatively,
we look for ML line given the observation, rather than max-probability line.

3. The roads between the stations can be approximated as straight lines:
the distance between the actual road and the straight line,
is negligible compared to the distance between roads of two different buses.


--------------- Possible improvements ---------------

1. Temporal direction of the bus line is currently not exploited, and really should be.

Simple exploitation: at each point, note which interval is the closest, and if the intervals
are not monotonous, then reduce probability. Drawback: closest interval may be just a close interval,
where the actual interval of the drive is adjacent. So assigning the other,
slightly more distant interval could be better, hence we don't really maximize the likelihood.
 
Advanced exploitation: choose best assignment of intervals under constraint of monotony, eg using DP. 

2. Running time optimization: remove most of the lines at early stage (eg using beginning and end),
and possibly remove more as the process goes on (eg improve resolution of points
instead of going over points sequentially).


--------------- Time complexity estimation ---------------

total computations:       ~1e11
  computations per drive:   ~4e5
    bus lines:                ~100
    intervals per line:       ~40
    points per drive:         ~100
  total drives:             ~3e5
    drives per day:           ~3e3
    total days:               ~90
