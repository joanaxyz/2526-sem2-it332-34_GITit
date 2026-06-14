import {
  AdventureSectionPiece,
  ChallengeSectionPiece,
  DoorPiece,
  LandingPiece,
  SpirePiece,
  TomePiece,
} from '@/features/tower-map/components/TowerPieces'
import type { TowerPieceAssetDescriptor } from '@/shared/assets/types'

/**
 * Renders the SVG art for a tower piece by type. Shared by the editor canvas
 * and the focused section editor so both draw a piece the same way.
 */
export function PieceArt({
  pieceType,
  descriptor,
  isFirst = false,
}: {
  pieceType: string
  descriptor: TowerPieceAssetDescriptor | null
  isFirst?: boolean
}) {
  switch (pieceType) {
    case 'spire':
      return (
        <>
          <SpirePiece descriptor={descriptor} />
          {isFirst ? (
            <div className="tower-window-roof">
              <span className="tower-window-roof-spire" />
              <span className="tower-window-roof-peak" />
            </div>
          ) : null}
        </>
      )
    case 'landing':
      return <LandingPiece descriptor={descriptor} />
    case 'adventure_section':
      return <AdventureSectionPiece descriptor={descriptor} />
    case 'challenge_section':
      return <ChallengeSectionPiece descriptor={descriptor} />
    case 'tome':
      return <TomePiece descriptor={descriptor} />
    case 'door':
      return <DoorPiece descriptor={descriptor} />
    default:
      return null
  }
}
