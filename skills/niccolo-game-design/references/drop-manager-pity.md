# Recipe: DropManager with a Luck Meter (Pity Timer)

**Idea (Niccolò):** drops improve the more you kill, and **reset when you find something important**.
This is the well-known *pity timer* / *Pseudo-Random Distribution* technique from loot design.

## Concepts
- **Luck** `L ≥ 0`: grows with every kill by the enemy's `weight` (bigger monsters → more luck).
- **Tiers** ordered by rarity, e.g. `common → uncommon → rare → epic`.
- **Soft pity:** odds of higher tiers rise smoothly as `L` grows.
- **Hard pity:** when `L ≥ L_max`, the next drop is guaranteed to be at least `rare`.
- **Reset:** a drop of tier ≥ `rare` (or finding a level objective) sets `L = 0`.
- **Drop chance vs tier:** first roll *whether* something drops (`p_drop`), then *which tier*.

## Suggested math (simple, tunable, testable)

```
t        = clamp(L / L_max, 0, 1)                  // 0 = unlucky start, 1 = pity reached
p_drop   = p_base + (p_maxDrop - p_base) * t        // e.g. 0.35 → 0.9
weights  = lerp(baseWeights, luckyWeights, t)       // per tier, then normalize
if L >= L_max: force tier >= rare                    // hard pity
tier     = weightedPick(weights, rng)
if tier >= rare: L = 0  (emit LUCK_RESET)            // reset on important find
```

Example table (kid-friendly shooter):

| Tier | Example items | baseWeights | luckyWeights |
|---|---|---|---|
| common | health food | 70 | 30 |
| uncommon | buff spheres | 25 | 35 |
| rare | special ammo / special weapon | 5 | 28 |
| epic | gem / jackpot | 0 | 7 |

`L_max = 20` weight points, enemy weights: small 1, medium 2, guardian/boss 5.

## Anti-gaming & feel
- Add small variance to `L_max` (e.g. ±15%) so it doesn't feel like a clock.
- Never let players "store" luck by avoiding pickups: luck changes on kill/drop, not on pickup.
- For kids, **show** the meter (a small 🍀 bar that fills and flashes on reset): visible progress is
  motivating. Hide it for competitive adult games.
- Per-player luck in multiplayer (key the state by player id) to avoid kill-stealing drama.
- Finding the level objective also resets luck (prevents rare-item flood right before victory).

## Events
- Listens: `ENEMY_DEFEATED { killerId, weight, pos }`, `PICKUP_COLLECTED { kind:'objective' }`.
- Emits: `DROP_SPAWNED { tier, item, pos }`, `LUCK_CHANGED { playerId, luck, t }`, `LUCK_RESET { playerId }`.
- Asks `PickupManager` (via event or context command) to place the item. DropManager owns *odds*,
  PickupManager owns *items on the map*.

## Seeded RNG (mandatory)
Use a small deterministic PRNG (e.g. mulberry32) injected via `GameContext`. Same seed → same drops →
reproducible tests, replays, and client/server parity.

## Tests to write first
1. Luck increases by `weight` per kill; killing without drop still increases luck.
2. `t` = 0 → distribution ≈ baseWeights (Monte-Carlo, tolerance ±2%).
3. Hard pity: with `L ≥ L_max`, 1,000 consecutive rolls are all ≥ rare.
4. Reset: a rare drop sets `L = 0` and emits `LUCK_RESET` exactly once.
5. **Monte-Carlo 10,000 kills:** max kills between two rare+ drops ≤ `L_max / minWeight` (+ variance);
   mean drops per kill within the designed band.
6. Objective collected → luck reset.
7. Determinism: same seed → identical sequence.
