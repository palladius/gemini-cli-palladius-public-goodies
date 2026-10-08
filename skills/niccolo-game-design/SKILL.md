---
name: niccolo-game-design
description: (💛) Game-architecture skill based on Managers + Event Bus, distilled from Niccolò's code-review feedback and Robert Nystrom's "Game Programming Patterns". Use when designing, reviewing, or refactoring game code (TypeScript/Three.js, Godot, Unity…) that has a god-object game loop, too many singletons, scattered win/lose logic, or ad-hoc loot. Covers EnemyManager, PlayerManager, MapManager (owns Game Over / Victory), DropManager (pity-timer luck meter), GameFlow state machine, object pools, and a strangler-fig refactor recipe.
compatibility: Gemini CLI, Antigravity, Claude Code
metadata:
  version: 0.1.0
---

# 💛 Niccolò Game Design — Managers, Events, and Rules That Own Themselves

> *"Not many managers in this PR — lots of code all in one place. Usually people use the game's `main`
> to handle menus, death screens… The smart way is a **MapManager** that triggers Game Over because it
> finds **no living characters on the map**. You can do that with everything, even Drops: a
> **DropManager** whose drops get better as you kill, and reset when you find something important."*
> — Niccolò, code review

This skill turns that advice into a repeatable architecture, cross-checked against
[Game Programming Patterns](https://gameprogrammingpatterns.com/contents.html) (free online) and
common Unity/Godot practice.

## When to use this skill

Activate when ANY of these is true:
- A single `update()` / `animate()` / `_process()` function is longer than ~100 lines or mixes physics,
  AI, pickups, UI, audio, and win/lose checks.
- Gameplay code calls `SomeService.getInstance()` (or autoload globals) dozens of times.
- "Game Over", "Victory", or screen switching is decided in `main`/UI code instead of by game rules.
- Loot / drops are pure `Math.random()` with no memory.
- You are about to add multiplayer / client-server: managers make the simulation portable to a server.

## The 7 Rules

1. **One manager = one responsibility.** Name it after the *thing it owns*: `EnemyManager` owns
   enemies, `MapManager` owns the map and its rules. Target ≤ ~300 lines. If it grows, split it.
2. **No God Manager.** A `GameManager` that does everything is the same god-object with a new name.
   The top-level object (`Engine`/`Game`) only *orders* managers; it contains no gameplay rules.
3. **Rules live with the data they inspect.** Game Over is a *map rule* ("no living heroes on the map"),
   so `MapManager` emits it. Unsealing a reward is a *map rule* too. `main`/UI only *react*.
4. **Talk via events, query via context.** Managers announce facts (`ENEMY_DEFEATED`, `ALL_HEROES_DOWN`)
   on a typed **Event Bus**. Read-only queries (`enemies.aliveCount()`) go through an injected
   **GameContext**. A manager never calls another manager's mutating methods directly.
5. **Listeners, not callers.** Audio, score, HUD, telemetry, achievements **subscribe** to events.
   Gameplay code never calls `Sound.play()` or `Profile.addScore()` directly.
6. **Logic is headless.** Gameplay managers import no DOM and no renderer. Visuals go through thin
   `*View` adapters. Result: unit-testable in Node, and runnable on a game server.
7. **Data-driven over if/else.** Pickup effects, loot tables, enemy stats live in registries/tables, not
   in `if (type === 'x') … else if …` chains.

## Canonical manager set

| Manager | Owns | Emits (examples) | Typical queries |
|---|---|---|---|
| `GameFlowManager` | State machine: `Lobby → Loading → Playing ⇄ Downed → Victory / GameOver` | `FLOW_STATE_CHANGED` | `state()` |
| `MapManager` | Level load/unload, rooms/zones, objectives, **win/lose rules** | `MAP_LOADED`, `MAP_VICTORY`, `ALL_HEROES_DOWN`, `ZONE_ENTERED` | `roomAt(pos)`, `isObjectiveSealed()` |
| `PlayerManager` (a.k.a. MainCharacterManager) | Local + remote heroes, companions, respawn, shields | `PLAYER_DOWN`, `PLAYER_RESPAWNED` | `livingHeroes()` |
| `EnemyManager` | Spawning, AI tick, pooling, guardians/bosses | `ENEMY_SPAWNED`, `GUARDIANS_CLEARED` | `aliveCount()`, `nearest(pos)` |
| `CombatManager` | The **single** damage path: hits, shields, kills | `DAMAGE_DEALT`, `ENEMY_DEFEATED`, `PLAYER_DOWN` | — |
| `ProjectileManager` | Projectiles with an **object pool** | `PROJECTILE_HIT` | `active()` |
| `PickupManager` | Collectibles on the map + effect registry | `PICKUP_COLLECTED` | `nearby(pos)` |
| `DropManager` | Loot rolls with **pity/luck meter** | `DROP_SPAWNED`, `LUCK_CHANGED`, `LUCK_RESET` | `luck()` |
| Listeners | `AudioListener`, `ScoreListener`, `HudListener`, `TelemetryListener` | — (consume only) | — |

Not every game needs all of them. Start with the ones your god-loop already contains.

## Lifecycle contract (every manager)

```
init(ctx)        // receive GameContext (bus + other managers + services). Subscribe to events here.
onMapLoaded(map) // build per-level state (spawn enemies, place pickups)
update(dt)       // fixed-timestep simulation tick. NO rendering here.
lateUpdate(dt)   // optional: things that must run after everyone moved (camera, minimap feed)
onMapUnloaded()  // free per-level state, return objects to pools
dispose()        // unsubscribe, release everything
```

The top-level loop becomes boring, which is the point:

```
accumulator += frameDt
while accumulator >= STEP:          // fixed step, e.g. 1/30 s (same code runs on a server)
    for m in managers: m.update(STEP)
    bus.flush()                     // deliver queued events once per tick, in order
    accumulator -= STEP
for m in managers: m.lateUpdate(frameDt)
renderer.render()
```

**Update order matters and must be declared once** (typical): Input → Players → Enemies → Projectiles →
Combat → Pickups → Drops → Map (rules) → GameFlow.

## Event Bus rules

- **Typed catalog**: one discriminated union `GameEvent = { type: 'ENEMY_DEFEATED', enemyId, weight, pos } | …`.
- **Past tense, facts not commands**: `ENEMY_DEFEATED` ✅, `PLAY_DEATH_SOUND` ❌.
- **Deferred delivery** (Nystrom's Event Queue): `emit()` enqueues; `flush()` once per tick. Prevents
  re-entrancy bugs (a handler that emits while being dispatched) and makes ordering deterministic.
- **Listeners never mutate the emitter**. If a reaction changes gameplay, it goes through the owning
  manager (e.g. `DropManager` reacts to `ENEMY_DEFEATED` by asking `PickupManager` to place a drop).
- Always unsubscribe in `dispose()` (memory leaks are the #1 event-bus bug).

## Two signature recipes

- **MapManager owns Game Over / Victory** → see [references/map-manager-win-lose.md](references/map-manager-win-lose.md).
  Kid-friendly variant: solo never shows "Game Over" (instant protective respawn); co-op only restarts
  when *all* heroes are down at once.
- **DropManager luck meter (pity timer)** → see [references/drop-manager-pity.md](references/drop-manager-pity.md).
  `luck += enemy.weight` per kill, odds shift towards rarer tiers (soft pity), a guaranteed rare at the
  cap (hard pity), **reset to 0 on an important find**. Seeded RNG + Monte-Carlo tests.

## Refactor recipe (strangler fig — never big-bang)

1. **Baseline**: record automated metrics (bot/sim run: FPS, kills, HP curve, time-to-clear) BEFORE touching code.
2. **Foundations first**: add `GameEventBus`, `IGameManager`, `GameContext`; wire the loop to iterate an
   empty manager list. Ship it. Zero behavior change.
3. **Extract one manager at a time**, tests first: copy the logic out of the god-loop into the manager,
   cover it with unit tests, delete it from the loop, re-run the baseline. Order that usually works:
   `EnemyManager` → `MapManager` → `PlayerManager` → `GameFlowManager` → `CombatManager` →
   `ProjectileManager` → `PickupManager` → `DropManager`.
4. **Convert direct calls to listeners** last (`Sound.play()` → `AudioListener` on `ENEMY_DEFEATED`).
5. **Gate**: metrics within ±10% of baseline, top loop ≤ ~300 lines, `getInstance()` in the loop ≈ 0.

## Review checklist (paste into every MR touching gameplay)

- [ ] Does each new/changed manager have exactly one responsibility (name = what it owns)?
- [ ] Is any rule (win, lose, unlock, reward) decided outside the manager that owns its data?
- [ ] Any new direct call from gameplay to Audio/Score/HUD/Telemetry? → should be an event + listener.
- [ ] Any manager calling another manager's *mutating* method? → should be an event.
- [ ] Any DOM/renderer import inside a logic manager? → move to a `*View` adapter.
- [ ] Any new `if/else` chain on a string "type"? → registry/table.
- [ ] Objects created per frame/shot (projectiles, particles)? → pool them.
- [ ] Are subscriptions released in `dispose()`?
- [ ] Is randomness seeded (deterministic tests, replays, server parity)?
- [ ] Is update order still declared in exactly one place?
- [ ] Top loop still boring? (no gameplay `if`s)

## Anti-patterns to call out in review

| Smell | Fix |
|---|---|
| 400-line `animate()` | Extract managers (recipe above) |
| `X.getInstance()` everywhere | Inject via `GameContext` (Service Locator / DI) |
| Victory check inline in render loop | `MapManager` rule + `MAP_VICTORY` event |
| `main.ts` toggling death/menu screens | `GameFlowManager` state machine reacting to events |
| `applyPowerup(type)` if/else ladder | `PICKUP_EFFECTS[type](ctx)` registry |
| `new Projectile()` per shot | `ProjectileManager` pool |
| `Math.random() < 0.1` loot | `DropManager` with luck meter + seeded RNG |
| `EverythingManager` | Split by owned data |

## References

- [references/patterns.md](references/patterns.md) — pattern catalog (Game Loop, Update Method, Event Queue, Observer, State, Service Locator, Object Pool, Component, Data-driven) with "use when / avoid when".
- [references/map-manager-win-lose.md](references/map-manager-win-lose.md) — win/lose rules per mode.
- [references/drop-manager-pity.md](references/drop-manager-pity.md) — luck meter math + tests.
- [references/typescript-skeletons.md](references/typescript-skeletons.md) — heavily commented TS skeletons (Bus, Manager, Context, DropManager).
- [references/godot-mapping.md](references/godot-mapping.md) — same architecture in Godot 4 (autoloads, signals, scene tree).

## Sources

- Robert Nystrom, *Game Programming Patterns* — https://gameprogrammingpatterns.com/contents.html
  (chapters: Game Loop, Update Method, Event Queue, Observer, State, Service Locator, Object Pool, Component, Singleton).
- Unity, *Level up your code with game programming patterns* (e-book) — manager/SRP/observer guidance.
- Loot design literature on Pseudo-Random Distribution, soft/hard pity timers.
- Niccolò's review feedback (origin of the MapManager/DropManager ideas).
