# Fire At Will Shakespeare

**Fire At Will Shakespeare** is a strategy game about communication under surveillance.

The player can see the entire battlefield. Their ally cannot. The enemy can hear everything.

Every turn, the player issues a natural-language instruction over an open channel. That instruction is heard by both an allied artillery unit and an adversary. The ally must decide whether and where to fire based solely on the instruction. The enemy, hearing the same words, may reposition assets in an attempt to bait a catastrophic mistake.

The core challenge is not secrecy, but **asymmetric interpretation**.

---

## Core Premise

The game explores a specific problem:

> How do you convey precise, actionable information to an ally when an intelligent adversary is listening and allowed to interfere?

There is no pre-established encryption protocol, no private channel, and no trusted sender identity. Language is the only tool available, and it is shared by all parties.

Victory depends on making your ally understand faster and more accurately than the enemy.

---

## High-Level Gameplay Loop

1. **Perfect Information (Player Only)**  
   The player sees the full board: enemy ships, hostages, and empty squares.

2. **Open-Channel Instruction**  
   The player issues a single instruction in plain English.  
   - No coordinates
   - No direct geometry
   - No explicit “fire at X” commands
   The player isn't outright *forbidden* from offering such instructions, but they would be extremely foolish to do so, because that would enable the enemy to simply reposition whatever token was at that location.

3. **Adversarial Injection**  
   The enemy may also issue instructions on the same channel.  
   The ally does not know which messages are genuine.

4. **Enemy Counterplay**  
   After hearing the instruction, the enemy may reposition a single asset:
   - Move a ship to avoid a suspected strike
   - Move a hostage to a suspected strike to force friendly fire

5. **Ally Decision**  
   The ally may:
   - Fire at a chosen square
   - Hold fire and wait for more information

6. **Resolution**  
   - Hitting a ship destroys it  
   - Hitting a hostage is catastrophic  
   - Ties and endgame conditions favor restraint and careful timing

---

## Asymmetry by Interpretation, Not Access

All participants hear the same words.

The asymmetry arises from **interpretive context**, not hidden data:
- The player chooses a conceptual frame (a “lore” or narrative context) to encode commands.
- The AI ally only *applies* that frame; it does not choose or change it.
- The enemy does not know which frame is being used and must guess it before they can meaningfully interfere.

A good instruction is:
- Clear enough that the ally converges on the intended action
- Ambiguous enough that the enemy commits to the wrong interpretation

---

## Why Language Matters

This is not a coding game and not a cipher puzzle.

Any stable encoding can be learned, mimicked, or sabotaged by an adversary.  
Instead, the game rewards:
- Plausible deniability
- Frame misclassification
- Timing and restraint
- Multi-turn pressure rather than single-turn certainty

Language is treated as **strategy**, not as a transport layer.

## Lore Context: Your Shared Narrative Key

Before a match starts, the player picks a “lore context” the AI ally will use to decode later instructions. Think of it as a cognitive shared key: a movie series, author, band, era, etc. The ally has no agency here—it simply assumes whatever frame you declare.

Your goal is to express target coordinates in language that only resolves with that frame in mind, while staying ambiguous to an eavesdropper who lacks it.

Example (lore: Shakespeare): you want to hit C4. Do **not** say “Fire at C4” (gives it away). Avoid clues that expose the frame (“Capulet and Iago”). Prefer oblique phrasing that is obvious only if Shakespeare is the frame: “The first letter of the Italian girl’s last name, and the number of letters in the first name of the Black man’s friend.” To outsiders it is noise; to an ally primed on Shakespeare it is C4.

Practical loop:
- Pick a lore context up front (player-only choice).
- Issue one natural-language instruction per turn, encoded in that lore.
- The enemy hears the same words and tries to guess/reframe them; the ally fires or holds based on the shared frame.

---

## Design Goals

- Open-channel communication only
- Intelligent adversaries, not scripted puzzles
- No “perfect security” solutions
- Meaningful risk in every instruction
- Emergent play from natural language interpretation

The game is intended to be:
- Small in rules
- Deep in interaction
- Hostile to degenerate strategies
- Resistant to trivial optimization

---

## Status

This repository contains an early prototype focused on:
- Core mechanics
- Turn structure
- Language-driven interaction
- Adversarial dynamics

Implementation details, UI, and platform targets will evolve later.
