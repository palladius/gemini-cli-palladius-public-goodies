# Recipe: MapManager Owns Game Over & Victory

**Idea (Niccolò):** don't let `main`/UI decide "Game Over". The **map** knows who is alive on it and what
its objectives are, so the map emits the verdict, the flow state machine switches screens, and the UI
just reacts.

## Responsibilities
- Load/unload the level (geometry, colliders, rooms/zones, spawn points).
- Track **objectives** (e.g. "defeat all guardians to unseal the reward", "collect the booster").
- Evaluate **win/lose rules** every tick (cheap checks only) and emit **once** per transition.
- Answer spatial queries: `roomAt(pos)`, `isInWater(pos)`, `spawnPointFor(playerId, mode)`.

## Inputs (events it listens to)
| Event | Reaction |
|---|---|
| `GUARDIANS_CLEARED` (from EnemyManager) | unseal objective → emit `OBJECTIVE_UNSEALED` |
| `PICKUP_COLLECTED { kind: 'objective' }` | emit `MAP_VICTORY` |
| `PLAYER_DOWN` / `PLAYER_RESPAWNED` | re-evaluate "living heroes" rule |

## Rules per mode (kid-friendly defaults)

| Mode | Lose condition | Result |
|---|---|---|
| **Solo** | hero down | **never Game Over** → `PLAYER_DOWN` → short protective respawn (e.g. 3 s shield) |
| **Co-op** | `PlayerManager.livingHeroes().length === 0` (all down at the same time) | `ALL_HEROES_DOWN` → GameFlow does a soft map restart, **keeping** collected rewards |
| **PvP** | n/a (no map-level loss) | individual respawns with mode-specific delays |

Victory (all modes with objectives): objective unsealed **and** collected → `MAP_VICTORY`.

## Pseudocode

```
class MapManager implements IGameManager
  update(dt):
    if flow.state != Playing: return            // rules only evaluated while playing
    living = ctx.players.livingHeroes().length
    if mode == 'coop' and living == 0 and not allDownEmitted:
        bus.emit(ALL_HEROES_DOWN)                // emit ONCE per transition
        allDownEmitted = true
    if living > 0: allDownEmitted = false

  on GUARDIANS_CLEARED: objectiveSealed = false; bus.emit(OBJECTIVE_UNSEALED)
  on PICKUP_COLLECTED(kind='objective'): bus.emit(MAP_VICTORY)
```

```
class GameFlowManager   // state machine; the ONLY place that switches screens
  on MAP_VICTORY      -> transition(Victory)
  on ALL_HEROES_DOWN  -> transition(Restarting) -> map.reload(keepRewards=true) -> Playing
  on PLAYER_DOWN (solo) -> transition(Downed) -> after respawnDelay -> Playing
```

## Tests to write first
- Solo: hero down → no `ALL_HEROES_DOWN`, `PLAYER_DOWN` handled with respawn.
- Co-op 2 heroes: one down → nothing; both down → exactly one `ALL_HEROES_DOWN`; one respawns, both
  down again → a second emission (transition re-armed).
- Guardians cleared → `OBJECTIVE_UNSEALED`; collecting the sealed objective before that → no victory.
- Rules not evaluated in `Lobby`/`Loading` states.

## Common mistakes
- Emitting every tick instead of once per transition (UI flickers, sounds spam).
- Checking victory in the renderer/UI loop.
- MapManager directly showing a modal (it must emit; UI listens).
