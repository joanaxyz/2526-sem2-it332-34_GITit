import arcaneSpireMasterImage from '@/assets/images/achievements/arcane-spire-master.lossless.webp'
import coinHoarderImage from '@/assets/images/achievements/coin-hoarder.lossless.webp'
import comebackKidImage from '@/assets/images/achievements/comeback-kid.lossless.webp'
import commandCadetImage from '@/assets/images/achievements/command-cadet.lossless.webp'
import commandCaptainImage from '@/assets/images/achievements/command-captain.lossless.webp'
import firstClearImage from '@/assets/images/achievements/first-clear.lossless.webp'
import gateBreakerImage from '@/assets/images/achievements/gate-breaker.lossless.webp'
import gateWardenImage from '@/assets/images/achievements/gate-warden.lossless.webp'
import hardTierBreakerImage from '@/assets/images/achievements/hard-tier-breaker.lossless.webp'
import hardTierHunterImage from '@/assets/images/achievements/hard-tier-hunter.lossless.webp'
import levelAdeptImage from '@/assets/images/achievements/level-adept.lossless.webp'
import levelChampionImage from '@/assets/images/achievements/level-champion.lossless.webp'
import levelVeteranImage from '@/assets/images/achievements/level-veteran.lossless.webp'
import perfectionistImage from '@/assets/images/achievements/perfectionist.lossless.webp'
import rankBaronImage from '@/assets/images/achievements/rank-baron.lossless.webp'
import rankDukeImage from '@/assets/images/achievements/rank-duke.lossless.webp'
import rankKnightImage from '@/assets/images/achievements/rank-knight.lossless.webp'
import sharpshooterImage from '@/assets/images/achievements/sharpshooter.lossless.webp'
import starCollectorImage from '@/assets/images/achievements/star-collector.lossless.webp'

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
  'rank-baron': rankBaronImage,
  'rank-duke': rankDukeImage,
  'rank-knight': rankKnightImage,
  'sharpshooter': sharpshooterImage,
  'star-collector': starCollectorImage,
} as const

export type AchievementImageId = keyof typeof ACHIEVEMENT_IMAGES
