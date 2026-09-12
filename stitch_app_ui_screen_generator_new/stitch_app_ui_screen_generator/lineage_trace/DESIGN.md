---
name: Lineage Trace
colors:
  surface: '#0b1321'
  surface-dim: '#0b1321'
  surface-bright: '#313949'
  surface-container-lowest: '#060e1c'
  surface-container-low: '#141c2a'
  surface-container: '#18202e'
  surface-container-high: '#222a39'
  surface-container-highest: '#2d3544'
  on-surface: '#dbe2f6'
  on-surface-variant: '#cac4d4'
  inverse-surface: '#dbe2f6'
  inverse-on-surface: '#293140'
  outline: '#948e9d'
  outline-variant: '#494552'
  surface-tint: '#cebdff'
  primary: '#cebdff'
  on-primary: '#381385'
  primary-container: '#a78bfa'
  on-primary-container: '#3c1989'
  inverse-primary: '#674bb5'
  secondary: '#71d8c7'
  on-secondary: '#003731'
  secondary-container: '#33a192'
  on-secondary-container: '#00302a'
  tertiary: '#ffb0cd'
  on-tertiary: '#640039'
  tertiary-container: '#ff65ac'
  on-tertiary-container: '#6b003e'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e8ddff'
  primary-fixed-dim: '#cebdff'
  on-primary-fixed: '#21005e'
  on-primary-fixed-variant: '#4f319c'
  secondary-fixed: '#8ef5e3'
  secondary-fixed-dim: '#71d8c7'
  on-secondary-fixed: '#00201c'
  on-secondary-fixed-variant: '#005047'
  tertiary-fixed: '#ffd9e4'
  tertiary-fixed-dim: '#ffb0cd'
  on-tertiary-fixed: '#3e0022'
  on-tertiary-fixed-variant: '#8c0053'
  background: '#0b1321'
  on-background: '#dbe2f6'
  surface-variant: '#2d3544'
  ink-navy: '#101826'
  panel: '#161f36'
  paper: '#e7ebf2'
  slate: '#7d8aa0'
  border-line: '#23304d'
  signal-teal: '#2f9e8f'
  amplify-amber: '#f0a020'
  alert-pink: '#ec4899'
  accent-purple: '#a78bfa'
typography:
  headline-xl:
    fontFamily: Newsreader
    fontSize: 40px
    fontWeight: '600'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Newsreader
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 38px
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Newsreader
    fontSize: 32px
    fontWeight: '500'
    lineHeight: 40px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Newsreader
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Newsreader
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
  headline-sm:
    fontFamily: Newsreader
    fontSize: 19px
    fontWeight: '500'
    lineHeight: 26px
  body-lg:
    fontFamily: IBM Plex Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: IBM Plex Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: IBM Plex Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  code-lg:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  code-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-md:
    fontFamily: IBM Plex Sans
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.05em
spacing:
  gutter: 1rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1.25rem
  space-xl: 2rem
---

# Lineage Trace, design tokens

This is the token system for the frontend. It sets the vocabulary, color, type, layout, and the reasoning behind each choice, so later UI decisions can be checked against something instead of made from scratch each time.

## 1. Color

### Base surfaces
- Ink Navy: `#101826` (Page background)
- Panel: `#161f36` (Cards, rows, elevated surfaces on top of Ink Navy)
- Paper: `#e7ebf2` (Primary text on navy)
- Slate: `#7d8aa0` (Secondary text, muted metadata, timestamps)
- Border / Line: `#23304d` (Structural borders, dividers)

### Severity colors (the ones that carry meaning)
- Signal Teal: `#2f9e8f` (Organic spread)
- Amplify Amber: `#f0a020` (Coordinated spread)
- Alert Pink: `#ec4899` (Bot-amplified, highest danger)

### Brand and UI accent
- Accent Purple: `#a78bfa` (Logo mark, active nav state, links, header rule, brand identity)

## 2. Typography
- Display and headers: `Fraunces`, serif (Editorial, credible standards register)
- Body: `IBM Plex Sans`, sans-serif (Technical, structured, engineered)
- Data and metrics: `IBM Plex Mono`, monospace (Tabular figures, R_claim, timestamps, danger scores)

## 3. Layout & Aesthetic
- Asymmetric split, dense investigative war-room aesthetic.
- Panels are flat, rectangular, solid-filled (`#161f36`), sharp corners with subtle border.
- Evidence over assertion: no bare severity numbers, structured diffs visible, tabular data alignment.
