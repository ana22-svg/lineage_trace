# Lineage Trace, design tokens

This is the token system for the frontend. It sets the vocabulary, color, type, layout, and the reasoning behind each choice, so later UI decisions can be checked against something instead of made from scratch each time.

## 1. Color

### Base surfaces

| Token | Hex | Role |
|---|---|---|
| Ink Navy | `#101826` | Page background |
| Panel | `#161f36` | Cards, rows, elevated surfaces on top of Ink Navy |
| Paper | `#e7ebf2` | Primary text on navy |
| Slate | `#7d8aa0` | Secondary text, muted metadata, timestamps |

Ink Navy is anchored to the theme-factory Ocean Depths preset (`#1a2332`), shifted slightly darker and desaturated. That anchor matters: Ocean Depths is theme-factory's own preset for trust-building, professional, calming content, which lines up with your actual buyers (newsroom standards desks, political monitoring teams) rather than being picked on looks alone.

### Severity colors, the ones that carry meaning

| Token | Hex | Meaning |
|---|---|---|
| Signal Teal | `#2f9e8f` | Organic spread |
| Amplify Amber | `#f0a020` | Coordinated spread |
| Alert Pink | `#ec4899` | Bot-amplified, highest danger |

Why amber and not purple for coordinated: a scan across the category, ThreatConnect, Cortex, and the general OSINT dashboard pattern, along with Blackbird.AI and Cyabra's positioning, showed the same severity logic everywhere: red or pink at the top, amber or orange in the middle, blue or green at the bottom. That's not a style trend, it's the traffic-light hierarchy every risk analyst already has memorized, red is the highest-arousal color the eye reacts to, which is exactly why it's reserved for real danger everywhere from road signs to security tooling. Amber sits one step down in that same learned scale, meaning caution, look closer. Purple's actual psychological association is premium or creative, not urgent, which is why no severity-coded dashboard in the category uses it for an active risk signal. Using purple for coordinated would have meant asking every newsroom editor and war-room analyst to unlearn a convention they use daily, right at the moment they need to scan fast.

### Brand and UI accent

| Token | Hex | Role |
|---|---|---|
| Accent Purple | `#a78bfa` | Logo mark, active nav state, links, header rule, anything that is identity rather than a live risk signal |

Purple stays in the palette, it's just demoted out of the severity system and into brand chrome, where its actual psychological register (distinct, premium, analytical) does real work instead of competing with the traffic-light logic.

### Text on colored surfaces

Never place plain black or plain white text on a colored badge or chip. Use a darkened version of that same hue for text on a light chip, or a lightened version of that same hue for text on a dark chip. This keeps contrast readable without introducing a fourth unrelated color into a two-color element, and it's the same rule accessibility-conscious design systems use for WCAG contrast on tinted surfaces.

## 2. Typography

| Role | Typeface | Why |
|---|---|---|
| Display and headers | Fraunces | A serif with real personality, reads as editorial and credible rather than as a generic startup landing page. Matters specifically because the primary buyer is newsroom standards desks, who trust a masthead register more than a SaaS one. |
| Body | IBM Plex Sans | Technical and engineered in character without going full monospace, matches a product built on graph math and structured diffs. |
| Data and metrics | IBM Plex Mono | Used only for numbers that need to line up in a column: R_claim values, timestamps, danger scores. This is a functional choice, tabular figures need fixed-width alignment to compare across rows, not a decorative "looks technical" choice. Monospace used as a label decoration is one of the generic tells frontend-design flags, monospace used because the numbers genuinely need to align is not. |

Type scale follows Elements of Typographic Style defaults: a clear jump between display, header, body, and caption sizes rather than many close sizes that blur together. Body copy stays under 80 characters per line for readability.

## 3. Layout

Concept: an asymmetric split. Narrative text sits in a fixed-width left column. The live mutation river runs right and bleeds to the edge, since the diagram is the actual hero of the product, not a headline plus stock art.

```
+----------------+-------------------------------+
| Narrative      |                               |
| column         |     Mutation river             |
| (fixed width,  |     (bleeds to right edge,     |
| left-aligned)  |     the actual demo moment)    |
|                |                               |
+----------------+-------------------------------+
```

Alignment is left throughout, no centered marketing-page blocks. Panels are flat, rectangular, solid-filled, consistent with the existing preference for solid-color boxes over neon outlines. A single thin flowing line, echoing the river itself, is the one connective visual motif, used once as the signature move rather than repeated everywhere as decoration.

## 4. Principles

1. Evidence over assertion. Anything shown as a claim on screen ties back to a real number underneath, the UI mirrors the system's own rule that no danger score exists without a diff behind it.
2. Investigative, not SaaS. No gradient washes, no soft drop shadows, no rounded-corner card kit.
3. One deliberate motion moment per view, not motion on every hover.
4. No template chrome: no ALL CAPS eyebrow labels, no middot-joined metadata strings, no arrow appended to button text.
5. Severity color is a convention worth keeping, not breaking, because the audience already reads it fluently. Brand color is a place to be distinctive instead.

## 5. Jargon glossary

A few terms used above and worth having on hand going forward.

- **Accent color**: a color used sparingly to draw the eye to something specific (a link, an active state), as opposed to a base or surface color that fills large areas.
- **Type scale**: the set of font sizes used across a design (for example, 14px body, 18px subhead, 32px display), chosen deliberately rather than picked ad hoc per element.
- **Tabular figures**: numeral styles where every digit takes up the same width, so numbers align in columns. This is why monospace fonts are used for data tables.
- **Ramp**: a set of shades of one color, from lightest to darkest, used so the same hue can appear as a light background fill and a dark, readable text color without introducing a second color.
- **Hairline rule**: a very thin (often 0.5px or 1px) divider line, common in editorial and broadsheet-style layouts.
- **Eyebrow label**: a small line of text sitting above a headline, usually a category or context tag. Overused in templated design, listed here so you can recognize it when you see it elsewhere.
- **WCAG contrast**: the Web Content Accessibility Guidelines' standard for how much contrast text needs against its background to remain readable, including for people with low vision.
- **ASCII wireframe**: a rough layout sketch made of plain text characters and boxes, used to communicate structure before any visual design is applied.

## 6. What this ruled out, for the record

- Theme-factory's Midnight Galaxy and Tech Innovation presets, dark enough but built for nightlife or generic tech branding, not investigative tooling.
- Purple as a severity color, breaks the learned convention the target buyers already carry in from other risk tools.
- The five generic AI-design tells (warm cream plus serif plus terracotta, near-black plus single neon accent, broadsheet hairline grid, rounded SaaS card kit, template chrome like ALL CAPS eyebrows and arrow-suffixed buttons) were checked against this plan directly and avoided.
