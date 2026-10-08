# Same Architecture in Godot 4

Godot already *is* a manager/observer engine. The ideas map almost 1:1, so a manager refactor in a
TS/Three.js codebase is also the best preparation for a possible Godot port.

| Concept (this skill) | Godot 4 equivalent | Notes |
|---|---|---|
| `GameEventBus` | An **autoload** `Events.gd` declaring `signal enemy_defeated(enemy_id, killer_id, weight, pos)` etc. | "Signal bus" pattern; emit with `Events.enemy_defeated.emit(...)` |
| Deferred delivery (`flush`) | `signal.emit.call_deferred(...)` or `connect(..., CONNECT_DEFERRED)` | Delivers at idle time, avoiding re-entrancy |
| `GameContext` / Service Locator | Autoload singletons **for services only** (`Audio`, `Save`, `Rng`) + `@export` node references / dependency injection for managers | Don't make gameplay managers autoloads if they are per-level |
| `IGameManager.update(dt)` | `_physics_process(delta)` (fixed tick, default 60 Hz; set `physics/common/physics_ticks_per_second`) | Gameplay in `_physics_process`, visuals in `_process` |
| Update order | Scene-tree order + `process_priority` / `process_physics_priority` | Declare priorities in one place (e.g. a `Managers` node) |
| `MapManager` | Script on the level root (`Level.gd`) owning spawn points, zones (`Area3D`), objectives | Emits `Events.map_victory` / `Events.all_heroes_down` |
| `EnemyManager` | Node owning enemies as children; group `"enemies"`; `get_tree().get_nodes_in_group("enemies")` | Pool by hiding/reparenting instead of `queue_free()` for frequent spawns |
| `GameFlowManager` | Autoload `GameFlow.gd` with an enum state + `change_scene_to_packed()` | The only place switching scenes |
| `*View` adapters | Child `MeshInstance3D` / `AnimationPlayer` nodes; logic node stays mesh-agnostic | Keeps logic testable with GUT/gdUnit4 |
| Data-driven registries | `Resource` subclasses (`EnemyType.tres`, `LootTable.tres`) | Designers edit them in the inspector |
| Seeded RNG | `RandomNumberGenerator` with `.seed = …` injected via a service | Deterministic tests/replays |
| Listeners (Audio/Score/HUD) | Nodes that `Events.enemy_defeated.connect(_on_enemy_defeated)` in `_ready()` and disconnect in `_exit_tree()` | Same rule: gameplay never calls Audio directly |

## Minimal signal bus

```gdscript
# res://autoload/events.gd  (Project Settings → Autoload → "Events")
extends Node
signal enemy_defeated(enemy_id: String, killer_id: String, weight: int, pos: Vector3)
signal player_down(player_id: String)
signal guardians_cleared
signal pickup_collected(player_id: String, kind: String)
signal map_victory
signal all_heroes_down
```

```gdscript
# Level.gd: the MapManager rule
extends Node3D
@export var mode := "solo"
var _all_down_emitted := false

func _physics_process(_delta: float) -> void:
    if mode != "coop":
        return
    var living := get_tree().get_nodes_in_group("heroes").filter(func(h): return h.is_alive()).size()
    if living == 0 and not _all_down_emitted:
        Events.all_heroes_down.emit()
        _all_down_emitted = true
    elif living > 0:
        _all_down_emitted = false
```
