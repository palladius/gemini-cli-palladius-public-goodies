# Pattern Catalog for Manager-Based Game Architecture

Distilled from Robert Nystrom's *Game Programming Patterns* (https://gameprogrammingpatterns.com) and
common engine practice. Each entry: **what**, **use when**, **avoid when**, **in our architecture**.

---

## 1. Game Loop (fixed timestep)
- **What:** decouple simulation speed from frame rate. Accumulate real time, step the simulation in
  fixed slices (e.g. 1/30 s), render as often as possible.
- **Use when:** physics, AI, or networking must be deterministic or identical on client and server.
- **Avoid when:** never avoid it for gameplay; only purely cosmetic animation can use variable `dt`.
- **Here:** `Engine` owns the accumulator and calls `manager.update(STEP)`. A server runs the same loop.

## 2. Update Method
- **What:** every active object/system exposes `update(dt)`; the loop calls them in a known order.
- **Use when:** many independent things simulate each tick.
- **Avoid when:** objects are inactive most of the time; keep them out of the list (or in a pool).
- **Here:** `IGameManager.update(dt)`. Managers in turn update their own entities (enemies, projectiles).

## 3. Observer
- **What:** a subject notifies subscribers about something that happened, without knowing who they are.
- **Use when:** one fact has many unrelated consequences (enemy dies → sound, score, drop, HUD, telemetry).
- **Avoid when:** the reaction is the *core* behavior of the emitter (then just call it), or the chain
  of observers becomes hard to trace (document events in one catalog).
- **Here:** `GameEventBus.on(type, handler)`.

## 4. Event Queue
- **What:** Observer + time decoupling. Events are enqueued and processed later (once per tick).
- **Use when:** you want deterministic ordering, to avoid re-entrancy, or to batch work (audio, network).
- **Avoid when:** a response is needed synchronously within the same call (use a query instead).
- **Here:** `emit()` enqueues; `flush()` after the manager update pass. Events emitted during a flush go
  to the *next* flush (prevents infinite loops).

## 5. State (finite state machine)
- **What:** behavior depends on a current state; transitions are explicit.
- **Use when:** screens/flow (lobby, playing, downed, victory), enemy AI (idle, chase, attack, flee).
- **Avoid when:** states multiply combinatorially → use hierarchical states or behavior trees.
- **Here:** `GameFlowManager` (game screens) and per-enemy AI states inside `EnemyManager`.

## 6. Service Locator / Dependency Injection
- **What:** obtain services (audio, storage, telemetry, RNG) through one registry or constructor
  arguments, instead of global singletons.
- **Use when:** you want testable managers (swap in fakes) and visible dependencies.
- **Avoid when:** trivial scripts. Never let the locator become a junk drawer: register *interfaces*.
- **Here:** `GameContext` is passed to `init(ctx)`. Legacy singletons are wrapped as services first, then
  phased out.

## 7. Singleton (and why to minimize it)
- Nystrom: a singleton is "a global variable in disguise": hidden coupling, hard to test, lifecycle
  issues. Acceptable for truly process-wide, stateless-ish things (logger). Gameplay state must **not**
  be a singleton (multiplayer and tests need several instances).

## 8. Object Pool
- **What:** pre-allocate and reuse objects instead of `new`/GC churn.
- **Use when:** projectiles, particles, damage numbers, enemies that respawn. Critical on mobile/web where
  GC pauses cause frame drops.
- **Avoid when:** objects are few and long-lived.
- **Here:** `ProjectileManager`, explosion/particle managers, optionally `EnemyManager`.

## 9. Component
- **What:** an entity is a bag of components (physics, render, AI) instead of a deep class hierarchy.
- **Use when:** entities share behaviors in mixed combinations; classes like `Player` exceed ~800 lines.
- **Avoid when:** small games: managers + plain entities are enough. ECS is the scaled-up version
  (data-oriented, high entity counts).
- **Here:** a later step to split `Player` into movement/weapon/buff components owned by `PlayerManager`.

## 10. Data-driven registries (Strategy / Type Object)
- **What:** behavior selected by looking up a table (`EFFECTS[type]`), and entity "types" described by
  data (`ENEMY_TYPES.walker = { hp, speed, weight }`).
- **Use when:** you have `if/else` or `switch` ladders on a string type, or designers tweak numbers.
- **Here:** `PICKUP_EFFECTS`, `LOOT_TABLE`, `ENEMY_TYPES` (includes `weight` for the luck meter).

## 11. Dirty Flag / Spatial Partition (performance helpers)
- Recompute derived data (minimap feed, room lookup) only when inputs change; use a grid/room index for
  "nearest enemy"/"in which room am I" instead of scanning everything every frame.

---

### Quick decision table

| Problem | Pattern |
|---|---|
| "Who should decide Game Over?" | State (GameFlow) + rule in MapManager + Observer |
| "Sound/score code everywhere" | Observer/Event Queue + listeners |
| "Can't unit test, everything is global" | Service Locator / DI via GameContext |
| "GC stutter when shooting" | Object Pool |
| "FPS-dependent physics, server mismatch" | Fixed-timestep Game Loop |
| "Giant if/else on item type" | Data-driven registry |
| "Player.ts is 1400 lines" | Component |
