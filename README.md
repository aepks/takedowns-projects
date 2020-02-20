# takedowns-projects

Tool, built with Flask front-end, to automatically generate fair schedules for takedowns.

Note: After every meal at the Fraternity house, three members are assigned to clean up after the meal, based on their class schedule. In the past, this was done by hand, and this tool successfully and fairly automated this process.

## The Algorithm

#### Constraints

The following constraints exist:

1. Only one new member may be scheduled at each takedown.
2. A member may only have one takedown in a 14 meal period.

The algorithm is based on a two-level greedy choice algorithm.

We first get all available users - those who are available for the takedown.

Then, we select the subset of this list that's done the smallest number of takedowns.

We then order this list by the number of days since the previous takedown, in most to least, and take the first three (depending on new member constraints).

If we run out of users before the takedown is full, run the algorithm again, with all chosen users removed from the pool of all users.

#### Other Notes

The code is still in development, so I haven't had the chance to beautify it, make it run in an efficient amount of time, or really add comments yet. My apologies to the reader.
