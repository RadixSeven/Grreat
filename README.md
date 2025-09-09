# Grreat

GRREAT (Gerrymandering Resistance Research, Education, And Training)

# First Pass Minimal Demo

Proposed first-pass minimal demo:

- The world is a rectangle connected like a torus (so the neighbor of an edge precinct is the edge precinct on the opposite edge.) This avoids many edge cases.
- Precincts are equal-sized sub-rectangles. (essentially pixels). There are $P_h$ * $P_v$ precincts. Both $P_h$ and $P_v$ are $2^n + 1$ for some power of 2. E.g., 3, 5, 9, 17, 33, 65, ...
- Each precinct has the same number of people. $P\_{pop}$
- There are two parties (red and blue because it's traditional in the US 😊).
- People always vote for the same party.
- When there is more than one seat available in a district, a person always puts all of their party's candidates above all of the candidates of another party. Candidates from the same party are always ranked in the same order. So candidate 1 from R is always above candidate 2 from R. And the top of a blue voter ballot is always candidate 1 from B and candidate 2 from B, etc.
- Every party always fields exactly as many candidates in a district as there are seats in that district. (This might also be the optimal strategy in this scenario, but I'm not sure.)
- Everyone votes. (This is a major problem with real world elections, and my favorite alternative system addresses both this and the factor that voters have very little information capacity.)
- We start with the fraction of the whole world that is red: $f_r$ which yields $n_r$ the number of red voters and $n_b$ the number of blue voters.
- Distribute the population via the following variant of the Diamond-square algorithm (that encourages geographic clustering by party). $g_p$ is an integer geographic clustering variability factor. The higher $g_p$, the more random the distribution. There is another roughness value $g_w$ which determines how much of the value of a point is determined by the average of its neighbors and how much is determined by a random value. The basic diamond-square algorithm has $g_p$=4. This is its minimum value. The first $g_p$ steps essentially work with $g_w$ set to 0. This algorithm gives population clustering while preserving equal-sized precincts, the population of the world and the fraction of the population favoring each party.
  - Set $n\_{r0}=n_r$ and $n\_{b0}=n_b$
  - When there's more than one point to set, choose it at random. To make the math easy, the first 4 points should be the corners of the square done in a random order. You could start with any 4 neighboring points in a square.
  - For $g_p$ points, chose the number of red and blue voters in that point by choosing $p\_{ri}$=\\textrm{binomial}(n\_{r(i-1)}, n\_{b(i-1)})$ and $p\_{bi}=$P\_{pop}-p\_{ri}$ then subtract the resulting number of red and blue voters from the total population for the next point. $n\_{ri}=n\_{r(i-1)}-p\_{ri}$ and $n\_{bi}=n\_{b(i-1)}-p\_{bi}$ After the first 4 points, choose the next point to set uniformly at random.
  - For the $g_p+1$ point and afterward, follow the diamond-square algorithm, choosing the order to set the points that have 4 set neighbors randomly. When a point is already set, skip it. To set a point, calculate the average of its 4 neighbors number of red $a_i$. Then calculate the random $r_i$ the way you'd calculate $p\_{ri}$ above using the Bernoulli above. Finally $p\_{ri}=\\min(\\textrm{round}(a_i g_w + r_i (1-g_w)), $n\_{ri}$) where the $\\min$ is to ensure we don't allocate more people than are available in the population - this is a clipped linear combination of the average and the random. Take care of running out of red or blue people by allocating more of the one that remains. Then update the number of remaining red and blue people.
- To create a starting district map with $n_d$ districts, I'll also start searches with a Voronoi tessellation of the closest points to a random selection of points.
- For optimization, I suspect I'll do a lot better with more sophisticated algorithms than Monte-Carlo Annealing - it requires a lot of hyperparameter tuning and is very inefficient. The other algorithms are easily available in pre-packaged form from places like scikit-learn. However, maintaining connectivity constraints and number of district constraints could be challenging.
- I may use Alpha Phoenix's map quality metrics.
  - For sure his weighted least-squares fit of fraction of voters voting blue in a district to a desired CDF with extra weight for the district closest to 50%.
  - Modified standard deviation of population using 4th power rather than square to equalize district population.
  - For compactness, I don't know what I'll go with. Average distance from the centroid (like he did) is possible. But there are quite a few of these metrics and he was working with a very small neighborhood.
- Since I expect to take many fewer but larger steps, which metrics are appropriate will probably be different from his video.
- I'll probably work with a relaxation of the problem and have increasing penalties for the true constraints.
  - For example, the number of districts does not need to be constant, as long as it is correct at the end.
  - This is similar to how he relaxed the shape penalty and then increased it again.
- I'll probably implement all the visualizations from his video. For each step, output
  - Map plot
  - Graph of district population for all districts (for the equal-district-population metric) - This will be simple to compute since the population is equal in each precinct.
  - CDF gerrymandering graph (for the goodness of fit metric)
  - Map compactness plot (if I use his metric, I can do a pixel-wise contribution plot - otherwise the whole)
  - A visualization for each metric I add (if any).
  - The visualizations will help in debugging and will help show any results to others.
- Because of the fixed voting behavior, we can map voter percentages to number-of-red and number-of-blue from a multi-member district. For example, in a 3-member district, with 550 red and 450 blue voters. The threshold for 1 seat is 25%+1 that is 251. So, candidate R1 gets 550 1st choice votes from red voters. 251 are used to choose candidate R1. The remaining 299 second place votes go to candidate R2. Now we have 450 votes for candidate B1. That beats 299 for candidate R2. So, 251 of those go to B1. 199 go to candidate B2. Now we have 299 R2 vs 199 B2. That selects the final vote as R2. So, 550R vs 450B yields 2R and 1B.

## One-liner for simple bench test

This runs all checks and then runs the main program with a minimal world.

```bash
(set -e; for goal in check lint test package; do pants "$goal" ::; done; pants run src:main -- --world_width 3 --world_height 3)
```
