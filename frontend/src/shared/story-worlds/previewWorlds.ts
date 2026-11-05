import { frostboundCitadelWorld } from './frostbound-citadel'
import { neonBackstreetsWorld } from './neon-backstreets'

/** Asset-library worlds loaded only by local development previews. */
export const previewStoryWorlds = {
  [frostboundCitadelWorld.slug]: frostboundCitadelWorld,
  [neonBackstreetsWorld.slug]: neonBackstreetsWorld,
}
