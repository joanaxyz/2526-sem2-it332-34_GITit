import arcaneSpireMasterImage from '@/assets/images/achievements/arcane-spire-master.png'
import coinHoarderImage from '@/assets/images/achievements/coin-hoarder.png'
import comebackKidImage from '@/assets/images/achievements/comeback-kid.png'
import commandCadetImage from '@/assets/images/achievements/command-cadet.png'
import commandCaptainImage from '@/assets/images/achievements/command-captain.png'
import firstClearImage from '@/assets/images/achievements/first-clear.png'
import gateBreakerImage from '@/assets/images/achievements/gate-breaker.png'
import gateWardenImage from '@/assets/images/achievements/gate-warden.png'
import hardTierBreakerImage from '@/assets/images/achievements/hard-tier-breaker.png'
import hardTierHunterImage from '@/assets/images/achievements/hard-tier-hunter.png'
import levelAdeptImage from '@/assets/images/achievements/level-adept.png'
import levelChampionImage from '@/assets/images/achievements/level-champion.png'
import levelVeteranImage from '@/assets/images/achievements/level-veteran.png'
import perfectionistImage from '@/assets/images/achievements/perfectionist.png'
import rankArcaneAdeptImage from '@/assets/images/achievements/rank-arcane-adept.png'
import rankArchonImage from '@/assets/images/achievements/rank-archon.png'
import rankGlyphWeaverImage from '@/assets/images/achievements/rank-glyph-weaver.png'
import sharpshooterImage from '@/assets/images/achievements/sharpshooter.png'
import starCollectorImage from '@/assets/images/achievements/star-collector.png'

export const ACHIEVEMENT_IMAGES = {
  'arcane-spire-master': arcaneSpireMasterImage,
  'coin-hoarder': coinHoarderImage,
  'comeback-kid': comebackKidImage,
  'command-cadet': commandCadetImage,
  'command-captain': commandCaptainImage,
  'first-clear': firstClearImage,
  'gate-breaker': gateBreakerImage,
  'gate-warden': gateWardenImage,
  'hard-tier-breaker': hardTierBreakerImage,
  'hard-tier-hunter': hardTierHunterImage,
  'level-adept': levelAdeptImage,
  'level-champion': levelChampionImage,
  'level-veteran': levelVeteranImage,
  'perfectionist': perfectionistImage,
  'rank-arcane-adept': rankArcaneAdeptImage,
  'rank-archon': rankArchonImage,
  'rank-glyph-weaver': rankGlyphWeaverImage,
  'sharpshooter': sharpshooterImage,
  'star-collector': starCollectorImage,
} as const

export type AchievementImageId = keyof typeof ACHIEVEMENT_IMAGES
