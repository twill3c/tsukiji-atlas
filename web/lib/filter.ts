// F-06: 絞り込みは AND-of-OR(時代内は OR、時代×分野は AND)。純関数(T-041)
import type { FilterState, SiteFeature, SiteProps } from "./types";

export function matchesFilter(props: SiteProps, state: FilterState): boolean {
  const eraOk = state.eras.length === 0 || state.eras.includes(props.era);
  const catOk = state.cats.length === 0 || state.cats.includes(props.category);
  return eraOk && catOk;
}

export function filterFeatures(features: SiteFeature[], state: FilterState): SiteFeature[] {
  return features.filter((f) => matchesFilter(f.properties, state));
}
