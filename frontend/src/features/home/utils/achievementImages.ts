import arcaneSpireMasterImage from '@/assets/images/achievements/arcane-spire-master.png'
import bossReaperImage from '@/assets/images/achievements/boss-reaper.png'
import bossSlayerImage from '@/assets/images/achievements/boss-slayer.png'
import coinHoarderImage from '@/assets/images/achievements/coin-hoarder.png'
import comebackKidImage from '@/assets/images/achievements/comeback-kid.png'
import commandCadetImage from '@/assets/images/achievements/command-cadet.png'
import commandCaptainImage from '@/assets/images/achievements/command-captain.png'
import firstClearImage from '@/assets/images/achievements/first-clear.png'
import fortnightBlazeImage from '@/assets/images/achievements/fortnight-blaze.png'
import levelAdeptImage from '@/assets/images/achievements/level-adept.png'
import levelChampionImage from '@/assets/images/achievements/level-champion.png'
import levelVeteranImage from '@/assets/images/achievements/level-veteran.png'
import perfectionistImage from '@/assets/images/achievements/perfectionist.png'
import sharpshooterImage from '@/assets/images/achievements/sharpshooter.png'
import starCollectorImage from '@/assets/images/achievements/star-collector.png'
import storyClimberImage from '@/assets/images/achievements/story-climber.png'
import storySentinelImage from '@/assets/images/achievements/story-sentinel.png'
import streakSparkImage from '@/assets/images/achievements/streak-spark.png'
import weeklongFlameImage from '@/assets/images/achievements/weeklong-flame.png'

export const ACHIEVEMENT_IMAGES = {
  'arcane-spire-master': arcaneSpireMasterImage,
  'boss-reaper': bossReaperImage,
  'boss-slayer': bossSlayerImage,
  'coin-hoarder': coinHoarderImage,
  'comeback-kid': comebackKidImage,
  'command-cadet': commandCadetImage,
  'command-captain': commandCaptainImage,
  'first-clear': firstClearImage,
  'fortnight-blaze': fortnightBlazeImage,
  'level-adept': levelAdeptImage,
  'level-champion': levelChampionImage,
  'level-veteran': levelVeteranImage,
  'perfectionist': perfectionistImage,
  'sharpshooter': sharpshooterImage,
  'star-collector': starCollectorImage,
  'story-climber': storyClimberImage,
  'story-sentinel': storySentinelImage,
  'streak-spark': streakSparkImage,
  'weeklong-flame': weeklongFlameImage,
} as const

export type AchievementImageId = keyof typeof ACHIEVEMENT_IMAGES
