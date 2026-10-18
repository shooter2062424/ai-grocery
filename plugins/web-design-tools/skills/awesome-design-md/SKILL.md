---
name: awesome-design-md
description: Use a ready-made DESIGN.md (a plain-text design system document with color tokens, typography, spacing, components and rules) extracted from a well-known site, so generated UI matches that site's visual language. Use when the user says "make it look like Stripe / Linear / Apple / Notion / Vercel…", "build a page in the style of X", "give me a DESIGN.md for X", wants brand-consistent UI, or needs design tokens (colors, type scale, radii) to start from. Covers 84 sites; see the index in this file. （繁中觸發詞：做成像 Stripe / Linear / Apple 那種風格、照某某網站的設計語言做頁面、給我一份 DESIGN.md、找設計 token、配色與字級參考、品牌風格一致的 UI。）
---

# Awesome DESIGN.md

84 份從知名網站萃取出來的 `DESIGN.md`:純文字設計系統文件,含色彩 token、字級、間距、元件與使用規則。
把其中一份當成設計語言來源,agent 產出的 UI 就能跟那個網站的視覺保持一致。

來源:[VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md)(MIT)。
`DESIGN.md` 是 Google Stitch 提出的格式,本身就是一份 markdown,不需要 Figma 匯出或特殊工具。

## 怎麼用

1. 從下面的索引挑出最接近使用者想要的品牌 slug。使用者點名品牌就直接用;只說「簡潔、深色、科技感」這類形容時,從摘要欄挑 1–3 個候選,先講給使用者聽再選。
2. 讀對應檔案:`${CLAUDE_PLUGIN_ROOT}/skills/awesome-design-md/design-md/<slug>/DESIGN.md`。
3. 把 frontmatter 的 token(`colors`、`typography`、`rounded`、`spacing`、`components`)當作單一事實來源,正文的 `Do's and Don'ts`、`Iteration Guide`、`Known Gaps` 當作規則與已知缺口。
4. 產出 UI 時:
   - 色彩、字級、圓角、間距**只用文件裡的 token**,不要自己發明相近的值。
   - 文件指定的字型若是專有字型(例如 SF Pro、品牌自家字體),用文件列出的 fallback stack,不要假裝有授權字型。
   - 不要把品牌的 logo、商標或文案直接搬進使用者的產品。這份文件只借**設計語言**(版面節奏、色彩關係、元件形狀),不借品牌本身。
5. 使用者要的是「混合」(例如 A 的版面配 B 的配色)時,明講取捨,別默默混出一個沒有一致性的東西。

## 跟其他 skill 的分工

- 想**自己創造**有品味、不像 AI 做的設計 → `taste-skill`。
- 想**照某個既有網站**的設計語言做 → 這個 skill。
- 想**產生**一份新的 `DESIGN.md`(給自己的品牌)→ `taste-skill` 裡的 `stitch-design-taste`。
- 做完想審查無障礙與 UX 規範 → `web-design-guidelines`。

## 索引

下表的摘要是上游原文。

| slug | 品牌 | 風格摘要(上游原文) |
|---|---|---|
| `1win` | 1win | Crypto casino and sportsbook. Near-black canvas, vivid green action color, dense game-tile rails |
| `airbnb` | Airbnb | Travel marketplace. Warm coral accent, photography-driven, rounded UI |
| `airtable` | Airtable | Spreadsheet-database hybrid. Colorful, friendly, structured data aesthetic |
| `aljazeera` | Al Jazeera | Global news network. Flat white paper, dense Roboto headlines, orange signature and live red |
| `apple` | Apple | Consumer electronics. Premium white space, SF Pro, cinematic imagery |
| `binance` | Binance | Crypto exchange. Bold Binance Yellow on monochrome, trading-floor urgency |
| `bmw` | BMW | Luxury automotive. Dark premium surfaces, precise German engineering aesthetic |
| `bmw-m` | BMW M | Performance automotive. Motorsport-inspired contrast, M color accents, precision-driven layout |
| `bugatti` | Bugatti | Luxury hypercar. Cinema-black canvas, monochrome austerity, monumental display type |
| `cal` | Cal.com | Open-source scheduling. Clean neutral UI, developer-oriented simplicity |
| `claude` | Claude | Anthropic's AI assistant. Warm terracotta accent, clean editorial layout |
| `clay` | Clay | Creative agency. Organic shapes, soft gradients, art-directed layout |
| `clickhouse` | ClickHouse | Fast analytics database. Yellow-accented, technical documentation style |
| `cohere` | Cohere | Enterprise AI platform. Vibrant gradients, data-rich dashboard aesthetic |
| `coinbase` | Coinbase | Crypto exchange. Clean blue identity, trust-focused, institutional feel |
| `composio` | Composio | Tool integration platform. Modern dark with colorful integration icons |
| `cursor` | Cursor | AI-first code editor. Sleek dark interface, gradient accents |
| `dell-1996` | Dell (1996) | Catalog-era enterprise web. Literal black page frame, flat color-block "ribbon cards", chunky Helvetica-Black titles over Times Roman body, and hand-cut GIF stickers (NEW! bursts, award seals, beveled product photos). |
| `dji` | DJI | Drone and camera maker. Studio product tiles, engineering-blue pills, tight Open Sans |
| `elevenlabs` | ElevenLabs | AI voice platform. Dark cinematic UI, audio-waveform aesthetics |
| `expo` | Expo | React Native platform. Dark theme, tight letter-spacing, code-centric |
| `ferrari` | Ferrari | Luxury automotive. Chiaroscuro black-white editorial, Ferrari Red with extreme sparseness |
| `figma` | Figma | Collaborative design tool. Vibrant multi-color, playful yet professional |
| `framer` | Framer | Website builder. Bold black and blue, motion-first, design-forward |
| `hashicorp` | HashiCorp | Infrastructure automation. Enterprise-clean, black and white |
| `hp` | HP | PC and printer maker. Pure white canvas, HP Electric Blue signal CTA, geometric Forma DJR Micro, blue chevron decorations |
| `ibm` | IBM | Enterprise technology. Carbon design system, structured blue palette |
| `intercom` | Intercom | Customer messaging. Friendly blue palette, conversational UI patterns |
| `jobright` | Jobright | AI job-hunting platform. Spring-mint green, black pill buttons, condensed Titillium headlines |
| `kraken` | Kraken | Crypto trading platform. Purple-accented dark UI, data-dense dashboards |
| `lamborghini` | Lamborghini | Luxury automotive. True black cathedral, gold accent, LamboType custom Neo-Grotesk |
| `linear.app` | Linear | Project management for engineers. Ultra-minimal, precise, purple accent |
| `lovable` | Lovable | AI full-stack builder. Playful gradients, friendly dev aesthetic |
| `mastercard` | Mastercard | Global payments network. Warm cream canvas, orbital pill shapes, editorial warmth |
| `mercury` | Mercury | Startup banking platform. Ink-violet night world, indigo action pill, light custom sans |
| `meta` | Meta | Tech retail store. Photography-first, binary light/dark surfaces, Meta Blue CTAs |
| `minimax` | Minimax | AI model provider. Bold dark interface with neon accents |
| `mintlify` | Mintlify | Documentation platform. Clean, green-accented, reading-optimized |
| `miro` | Miro | Visual collaboration. Bright yellow accent, infinite canvas aesthetic |
| `mistral.ai` | Mistral AI | Open-weight LLM provider. French-engineered minimalism, purple-toned |
| `mongodb` | MongoDB | Document database. Green leaf branding, developer documentation focus |
| `mydealz` | mydealz | German deals community. Dense white-card feed, hot and cold voting pill, brand green |
| `nerdwallet` | NerdWallet | Personal finance comparison platform. Deep spruce green, mint washes, near-square corners |
| `nike` | Nike | Athletic retail. Monochrome UI, massive uppercase Futura, full-bleed photography |
| `nintendo-2001` | Nintendo.com (2001) | Y2K "console chrome" web. Brushed-periwinkle beveled metal panels, a halftone-dotted carbon nav glowing amber, outlined Arial-Black box-art wordmarks over circuit-board hero fields, and a pixel Mario welcome bubble. |
| `notion` | Notion | All-in-one workspace. Warm minimalism, serif headings, soft surfaces |
| `nvidia` | NVIDIA | GPU computing. Green-black energy, technical power aesthetic |
| `ollama` | Ollama | Run LLMs locally. Terminal-first, monochrome simplicity |
| `opencode.ai` | OpenCode AI | AI coding platform. Developer-centric dark theme |
| `oracle` | Oracle | Enterprise cloud and database software. Warm neutral ladder, charcoal-only actions, red saved for the wordmark |
| `oura` | Oura | Smart ring wellness brand. Warm paper cream, editorial serif, earth-tone accents |
| `pinterest` | Pinterest | Visual discovery platform. Red accent, masonry grid, image-first |
| `playstation` | PlayStation | Gaming console retail. Three-surface channel layout, cyan hover-scale interaction |
| `posthog` | PostHog | Product analytics. Playful hedgehog branding, developer-friendly dark UI |
| `raycast` | Raycast | Productivity launcher. Sleek dark chrome, vibrant gradient accents |
| `renault` | Renault | French automotive. Vivid aurora gradients, NouvelR proprietary typeface, zero-radius buttons |
| `replicate` | Replicate | Run ML models via API. Clean white canvas, code-forward |
| `resend` | Resend | Email API for developers. Minimal dark theme, monospace accents |
| `revolut` | Revolut | Digital banking. Sleek dark interface, gradient cards, fintech precision |
| `runwayml` | Runway | AI creative-tools platform with an editorial film-festival aesthetic — cinematic dark heroes, paper-white reading bands, single proprietary sans, and pure black pill CTAs. |
| `sanity` | Sanity | Headless content platform with a dark-first editorial marketing surface — 112px display type, IBM Plex Mono technical eyebrows, and a single coral-red accent reserved for the highest-priority CTA. |
| `sap` | SAP | Enterprise business software. White canvas, flat blue bands, application-frame chrome |
| `sentry` | Sentry | Error monitoring. Dark dashboard, data-dense, pink-purple accent |
| `shopify` | Shopify | E-commerce platform. Dark-first cinematic, neon green accent, ultra-light display type |
| `slack` | Slack | Workplace messaging. Deep aubergine primary, cream-lavender hero gradients, blue inline links, pill CTAs |
| `spacex` | SpaceX | Space technology. Stark black and white, full-bleed imagery, futuristic |
| `spotify` | Spotify | Music streaming. Vibrant green on dark, bold type, album-art-driven |
| `starbucks` | Starbucks | Coffee retail flagship. Four-tier earth-green system, warm cream canvas, proprietary SoDoSans typography |
| `stripe` | Stripe | Payment infrastructure. Signature purple gradients, weight-300 elegance |
| `supabase` | Supabase | Open-source Firebase alternative. Dark emerald theme, code-first |
| `superhuman` | Superhuman | Fast email client. Premium dark UI, keyboard-first, purple glow |
| `tesla` | Tesla | Electric vehicles. Radical subtraction, cinematic full-viewport photography, Universal Sans |
| `theverge` | The Verge | Tech editorial media. Acid-mint and ultraviolet accents, Manuka display type |
| `together.ai` | Together AI | Open-source AI infrastructure. Technical, blueprint-style design |
| `uber` | Uber | Mobility platform. Bold black and white, tight type, urban energy |
| `vercel` | Vercel | Frontend deployment platform. Black and white precision, Geist font |
| `vodafone` | Vodafone | Global telecom brand. Monumental uppercase display, Vodafone Red chapter bands |
| `voltagent` | VoltAgent | AI agent framework. Void-black canvas, emerald accent, terminal-native |
| `warp` | Warp | Modern terminal. Dark IDE-like interface, block-based command UI |
| `webflow` | Webflow | Visual web builder. Blue-accented, polished marketing site aesthetic |
| `wired` | WIRED | Tech magazine. Paper-white broadsheet density, custom serif, ink-blue links |
| `wise` | Wise | International money transfer. Bright green accent, friendly and clear |
| `x.ai` | xAI | Elon Musk's AI lab. Stark monochrome, futuristic minimalism |
| `zapier` | Zapier | Automation platform. Warm orange, friendly illustration-driven |
