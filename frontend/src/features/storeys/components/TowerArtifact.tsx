// Purely decorative ornate crown for the top of the tower, directly above the
// Command Adventure (aria-hidden, no interactions). It is full tower-width at
// its base so it flows straight into the Command Adventure drum as ONE tower:
// an ogee spire + finial and corner pinnacles, an octagonal lantern of three
// arched windows, a balcony, corbels and a crenellated parapet. The lit windows
// warm up with the living sky via the inherited --window-glow var.
export function TowerArtifact() {
  return (
    <svg className="tower-artifact" viewBox="0 0 240 248" aria-hidden="true">
      {/* crenellated parapet — full width, hands off into the drum below */}
      <path className="ta-stroke" d="M8 246 L232 246 L232 230 L8 230 Z" />
      {/* corbel band carrying the parapet out over the wall */}
      <path className="ta-stroke" d="M42 209 L198 209 L218 230 L22 230 Z" />
      <g className="ta-line">
        <path d="M58 211 L56 229" /><path d="M84 211 L82 229" /><path d="M110 211 L109 229" />
        <path d="M130 211 L131 229" /><path d="M156 211 L158 229" /><path d="M182 211 L184 229" />
      </g>
      {/* merlons */}
      <g className="ta-stroke">
        <path d="M12 230 L12 222 L28 222 L28 230 Z" /><path d="M40 230 L40 222 L56 222 L56 230 Z" />
        <path d="M68 230 L68 222 L84 222 L84 230 Z" /><path d="M96 230 L96 222 L112 222 L112 230 Z" />
        <path d="M124 230 L124 222 L140 222 L140 230 Z" /><path d="M152 230 L152 222 L168 222 L168 230 Z" />
        <path d="M180 230 L180 222 L196 222 L196 230 Z" /><path d="M208 230 L208 222 L224 222 L224 230 Z" />
      </g>

      {/* balcony / gallery */}
      <path className="ta-stroke" d="M48 198 L192 198 L192 208 L48 208 Z" />
      <line className="ta-line" x1="46" y1="197" x2="194" y2="197" />
      <g className="ta-line">
        <line x1="56" y1="200" x2="56" y2="207" /><line x1="68" y1="200" x2="68" y2="207" />
        <line x1="80" y1="200" x2="80" y2="207" /><line x1="92" y1="200" x2="92" y2="207" />
        <line x1="104" y1="200" x2="104" y2="207" /><line x1="116" y1="200" x2="116" y2="207" />
        <line x1="124" y1="200" x2="124" y2="207" /><line x1="136" y1="200" x2="136" y2="207" />
        <line x1="148" y1="200" x2="148" y2="207" /><line x1="160" y1="200" x2="160" y2="207" />
        <line x1="172" y1="200" x2="172" y2="207" /><line x1="184" y1="200" x2="184" y2="207" />
      </g>

      {/* octagonal lantern with three arched windows */}
      <path className="ta-stroke" d="M74 144 L166 144 L172 152 L172 188 L166 196 L74 196 L68 188 L68 152 Z" />
      <g>
        <path className="ta-window" d="M89 186 L89 163 A7 7 0 0 1 103 163 L103 186 Z" />
        <path className="ta-window-glow" d="M92 184 L92 165 A4 4 0 0 1 100 165 L100 184 Z" />
        <path className="ta-window" d="M113 186 L113 163 A7 7 0 0 1 127 163 L127 186 Z" />
        <path className="ta-window-glow" d="M116 184 L116 165 A4 4 0 0 1 124 165 L124 184 Z" />
        <path className="ta-window" d="M137 186 L137 163 A7 7 0 0 1 151 163 L151 186 Z" />
        <path className="ta-window-glow" d="M140 184 L140 165 A4 4 0 0 1 148 165 L148 184 Z" />
      </g>

      {/* flared eave */}
      <path className="ta-roof" d="M52 130 L188 130 L178 142 Q120 150 62 142 Z" />

      {/* ogee roof */}
      <path className="ta-roof" d="M120 52 C 104 80 80 106 58 130 L 182 130 C 160 106 136 80 120 52 Z" />
      <path className="ta-sheen" d="M120 56 L80 130 L98 130 Z" />
      <path className="ta-line" d="M92 84 Q120 92 148 84" />
      <path className="ta-line" d="M80 106 Q120 116 160 106" />
      <path className="ta-line" d="M68 124 Q120 134 172 124" />

      {/* corner pinnacles */}
      <path className="ta-roof" d="M62 130 L68 102 L74 130 Z" />
      <path className="ta-roof" d="M166 130 L172 102 L178 130 Z" />
      <line className="ta-finial" x1="68" y1="102" x2="68" y2="95" />
      <line className="ta-finial" x1="172" y1="102" x2="172" y2="95" />

      {/* finial */}
      <path className="ta-finial" d="M120 6 L124 13 L120 20 L116 13 Z" />
      <line className="ta-finial" x1="120" y1="20" x2="120" y2="52" />
      <circle className="ta-finial" cx="120" cy="36" r="3.4" />
    </svg>
  )
}
