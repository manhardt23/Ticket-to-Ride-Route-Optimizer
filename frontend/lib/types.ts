export type City = {
  name: string;
  x: number | null;
  y: number | null;
};

export type Track = {
  city_a: string;
  city_b: string;
  route_points: number;
  train_cost: number;
};

export type Trip = {
  id: number;
  start: string;
  end: string;
  points: number;
};

export type BoardData = {
  cities: City[];
  tracks: Track[];
};

export type EdgeOwner = "self" | "opponent";

/** Canonical edge key (sorted city names) → owner. Absent = unclaimed. */
export type EdgeClaims = Record<string, EdgeOwner>;
