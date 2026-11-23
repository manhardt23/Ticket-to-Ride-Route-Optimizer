# Route choice on high-point ticket sets

Within one ticket the router now keeps the simple path with the most
new route points, then the fewest new trains, that still fits in
45 minus trains already placed. The old rule kept the
fewest new edges, then the fewest trains, then the most points.
Ticket sets are the ones the combinatorial search already considers:
size 10, sum of ticket points >= 150.
Trips inside a set are routed in trip-list order, the same order
`evaluate_set` uses. Hands from `evaluate_hand` are still sorted
by ticket points, highest first.

Scored **113884** of **113884** pruned sets.
Best score under the new key: **176**.
Kept **26** sets with score >= 176 (the best score).
Among those, the best score under the old key was **219** (1 of 26 stayed within 45 trains).
The old key still uses the hard fail in `evaluate_set`: the set scores 0
once placed trains pass 45. Path changed compares the route each key
chose for a ticket, including tickets routed before that fail.
The set that stayed under the cap scored 219 with the old key (10 tickets reached) and 176 with the new key (6 tickets reached).
The new key changed at least one ticket path in **26** of 26 kept sets.

Route points below are the track's own value. A kept set adds that
value once when the edge is placed, even if later tickets reuse it.
Extra tickets counts, across the kept sets, later tickets that use
the edge and have no budget-feasible path if that edge is no longer
free. Path changed is yes when any kept set uses the edge on a
ticket whose path differs from the old key.

Top score counts:

- 176: 26 sets
- 175: 9 sets
- 174: 3 sets
- 168: 229 sets
- 167: 338 sets
- 166: 250 sets
- 165: 85 sets
- 164: 6 sets

## Ties after points and trains

8 tickets still tie on an empty board: same route points and same trains, so the first path is kept.

- **Calgary — Phoenix**: 98 route points, 45 trains, 2 paths
  - Calgary -> Winnipeg -> Sault-St-Marie -> Duluth -> Helena -> Seattle -> Portland -> Salt-Lake-City -> San-Francisco -> Los-Angeles -> Phoenix
  - Calgary -> Winnipeg -> Sault-St-Marie -> Duluth -> Helena -> Seattle -> Portland -> San-Francisco -> Los-Angeles -> El-Paso -> Phoenix
- **Denver — El-Paso**: 96 route points, 45 trains, 2 paths
  - Denver -> Helena -> Duluth -> Winnipeg -> Calgary -> Seattle -> Portland -> Salt-Lake-City -> San-Francisco -> Los-Angeles -> El-Paso
  - Denver -> Omaha -> Chicago -> Toronto -> Duluth -> Helena -> Seattle -> Portland -> San-Francisco -> Los-Angeles -> El-Paso
- **Duluth — El-Paso**: 99 route points, 45 trains, 3 paths
  - Duluth -> Toronto -> Sault-St-Marie -> Winnipeg -> Helena -> Seattle -> Portland -> Salt-Lake-City -> San-Francisco -> Los-Angeles -> El-Paso
  - Duluth -> Toronto -> Sault-St-Marie -> Winnipeg -> Calgary -> Seattle -> Portland -> Salt-Lake-City -> San-Francisco -> Los-Angeles -> El-Paso
  - Duluth -> Toronto -> Sault-St-Marie -> Winnipeg -> Calgary -> Helena -> Seattle -> Portland -> San-Francisco -> Los-Angeles -> El-Paso
- **Duluth — Houston**: 99 route points, 45 trains, 2 paths
  - Duluth -> Toronto -> Sault-St-Marie -> Winnipeg -> Helena -> Seattle -> Portland -> San-Francisco -> Los-Angeles -> El-Paso -> Houston
  - Duluth -> Toronto -> Sault-St-Marie -> Winnipeg -> Calgary -> Seattle -> Portland -> San-Francisco -> Los-Angeles -> El-Paso -> Houston
- **Los-Angeles — Chicago**: 96 route points, 45 trains, 2 paths
  - Los-Angeles -> San-Francisco -> Salt-Lake-City -> Portland -> Seattle -> Calgary -> Winnipeg -> Helena -> Duluth -> Toronto -> Chicago
  - Los-Angeles -> San-Francisco -> Salt-Lake-City -> Portland -> Seattle -> Helena -> Calgary -> Winnipeg -> Duluth -> Toronto -> Chicago
- **Los-Angeles — New-York**: 96 route points, 45 trains, 2 paths
  - Los-Angeles -> San-Francisco -> Salt-Lake-City -> Portland -> Seattle -> Helena -> Calgary -> Winnipeg -> Sault-St-Marie -> Montreal -> New-York
  - Los-Angeles -> San-Francisco -> Salt-Lake-City -> Portland -> Seattle -> Helena -> Duluth -> Winnipeg -> Sault-St-Marie -> Montreal -> New-York
- **Sault-St-Marie — Oklahoma-City**: 99 route points, 45 trains, 2 paths (never first in a size-10 set)
  - Sault-St-Marie -> Winnipeg -> Calgary -> Seattle -> Helena -> Duluth -> Toronto -> Chicago -> Omaha -> Kansas-City -> Oklahoma-City
  - Sault-St-Marie -> Toronto -> Duluth -> Helena -> Seattle -> Portland -> Salt-Lake-City -> San-Francisco -> Los-Angeles -> El-Paso -> Oklahoma-City
- **Seattle — Los-Angeles**: 96 route points, 45 trains, 6 paths (never first in a size-10 set)
  - Seattle -> Helena -> Calgary -> Winnipeg -> Sault-St-Marie -> Toronto -> Duluth -> Omaha -> Kansas-City -> Oklahoma-City -> El-Paso -> Los-Angeles
  - Seattle -> Helena -> Duluth -> Toronto -> Chicago -> Omaha -> Kansas-City -> Denver -> Phoenix -> El-Paso -> Los-Angeles
  - Seattle -> Helena -> Duluth -> Toronto -> Chicago -> Omaha -> Kansas-City -> Denver -> Oklahoma-City -> El-Paso -> Los-Angeles
  - Seattle -> Helena -> Duluth -> Toronto -> Chicago -> Saint-Louis -> Nashville -> Atlanta -> New-Orleans -> Houston -> El-Paso -> Los-Angeles
  - Seattle -> Helena -> Duluth -> Toronto -> Pittsburgh -> Saint-Louis -> Nashville -> Little-Rock -> Dallas -> Houston -> El-Paso -> Los-Angeles
  - Seattle -> Helena -> Duluth -> Chicago -> Saint-Louis -> Nashville -> Atlanta -> Miami -> New-Orleans -> Houston -> El-Paso -> Los-Angeles

No size-10 set tied again after some track was already claimed.

## Edges in the kept sets

| Edge | Times used | Route points | Extra tickets | Path changed |
| --- | ---: | ---: | ---: | --- |
| Helena — Seattle | 26 | 15 | 104 | yes |
| Duluth — Helena | 26 | 15 | 91 | yes |
| Duluth — Toronto | 26 | 15 | 52 | yes |
| El-Paso — Los-Angeles | 26 | 15 | 39 | yes |
| El-Paso — Houston | 26 | 15 | 13 | yes |
| Portland — San-Francisco | 26 | 10 | 104 | yes |
| Los-Angeles — San-Francisco | 26 | 4 | 104 | yes |
| New-York — Pittsburgh | 26 | 2 | 52 | yes |
| Pittsburgh — Toronto | 26 | 2 | 52 | yes |
| Dallas — Houston | 26 | 1 | 0 | yes |
| Portland — Seattle | 26 | 1 | 0 | yes |
