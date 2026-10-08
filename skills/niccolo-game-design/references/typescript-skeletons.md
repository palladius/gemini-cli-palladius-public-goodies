# TypeScript Skeletons (heavily commented)

Written for readers who are **not** TypeScript experts: every block explains *why*, not just *what*.
This exact code is verified with `tsc --strict --noEmit` and its self-test runs with `npx tsx`.

**Verified Monte-Carlo result (seed 42, 10,000 kills, weight 1, luckMax 20):**
`{"drops":5372,"rares":976,"maxKillsBetweenRares":20}`, so the hard pity holds (never more than 20 kills without a rare+).

Contents: 1) Event catalog · 2) Event Bus · 3) Manager contract + Context + seeded RNG · 4) DropManager · 5) MapManager rule · 6) Fixed-timestep loop · Self-test.

```typescript
// Type-checkable source of the skeletons embedded in references/typescript-skeletons.md.
// Kept in scratch to verify they compile under `tsc --strict`.

// ─────────────────────────────────────────────────────────────────────────────
// 1) EVENT CATALOG
// A "discriminated union": every event has a literal `type` field, so TypeScript
// knows exactly which extra fields exist for each event type.
// Rule: events are FACTS in the past tense (ENEMY_DEFEATED), never commands.
// ─────────────────────────────────────────────────────────────────────────────
export type Vec3 = { x: number; y: number; z: number };

export type GameEvent =
  | { type: 'ENEMY_DEFEATED'; enemyId: string; killerId: string; weight: number; pos: Vec3 }
  | { type: 'PLAYER_DOWN'; playerId: string }
  | { type: 'PLAYER_RESPAWNED'; playerId: string }
  | { type: 'GUARDIANS_CLEARED' }
  | { type: 'PICKUP_COLLECTED'; playerId: string; kind: string }
  | { type: 'DROP_SPAWNED'; tier: LootTier; item: string; pos: Vec3 }
  | { type: 'LUCK_CHANGED'; playerId: string; luck: number; t: number }
  | { type: 'LUCK_RESET'; playerId: string }
  | { type: 'MAP_VICTORY' }
  | { type: 'ALL_HEROES_DOWN' };

/** Helper: given an event name, get the exact shape of that event. */
export type EventOf<T extends GameEvent['type']> = Extract<GameEvent, { type: T }>;

// ─────────────────────────────────────────────────────────────────────────────
// 2) EVENT BUS (Observer + Event Queue)
// emit() only QUEUES the event. flush() delivers everything once per tick.
// Why: deterministic order, and no "handler emits while being dispatched" bugs.
// ─────────────────────────────────────────────────────────────────────────────
type Handler<T extends GameEvent['type']> = (event: EventOf<T>) => void;

export class GameEventBus {
  // Map from event type → set of handler functions.
  private handlers = new Map<GameEvent['type'], Set<(e: GameEvent) => void>>();
  private queue: GameEvent[] = [];

  /** Subscribe. Returns an "unsubscribe" function: call it in dispose(). */
  on<T extends GameEvent['type']>(type: T, handler: Handler<T>): () => void {
    const set = this.handlers.get(type) ?? new Set();
    const wrapped = handler as (e: GameEvent) => void;
    set.add(wrapped);
    this.handlers.set(type, set);
    return () => set.delete(wrapped);
  }

  /** Queue an event; it is delivered at the next flush(). */
  emit(event: GameEvent): void {
    this.queue.push(event);
  }

  /** Deliver queued events. Events emitted DURING flush wait for the next flush. */
  flush(): void {
    const batch = this.queue;
    this.queue = [];
    for (const event of batch) {
      this.handlers.get(event.type)?.forEach((h) => h(event));
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 3) MANAGER CONTRACT + CONTEXT (Service Locator / Dependency Injection)
// Every manager gets the same lifecycle. The context is how managers find
// each other and services, instead of calling SomeThing.getInstance().
// ─────────────────────────────────────────────────────────────────────────────
export interface Rng {
  /** Returns a float in [0, 1). Seeded → deterministic. */
  next(): number;
}

export interface GameContext {
  bus: GameEventBus;
  rng: Rng;
  // Read-only queries other managers may use (keep this list small!).
  players: { livingHeroes(): string[] };
  mode: 'solo' | 'coop' | 'pvp';
}

export interface IGameManager {
  init(ctx: GameContext): void;
  onMapLoaded?(mapId: string): void;
  update(dt: number): void;
  lateUpdate?(dt: number): void;
  onMapUnloaded?(): void;
  dispose(): void;
}

/** Tiny seeded PRNG (mulberry32). Same seed → same sequence. */
export function mulberry32(seed: number): Rng {
  let a = seed >>> 0;
  return {
    next() {
      a = (a + 0x6d2b79f5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    },
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// 4) DROP MANAGER with luck meter (pity timer)
// Listens to ENEMY_DEFEATED, rolls loot, resets luck on rare+ or objective.
// ─────────────────────────────────────────────────────────────────────────────
export type LootTier = 'common' | 'uncommon' | 'rare' | 'epic';
const TIERS: LootTier[] = ['common', 'uncommon', 'rare', 'epic'];
const RARE_INDEX = 2; // index of 'rare' in TIERS: rare and above reset luck

export interface DropConfig {
  luckMax: number; // hard pity threshold (in enemy-weight points)
  pBase: number; // drop chance at zero luck
  pMax: number; // drop chance at full luck
  baseWeights: number[]; // per tier, at zero luck
  luckyWeights: number[]; // per tier, at full luck
  itemsByTier: Record<LootTier, string[]>;
}

export class DropManager implements IGameManager {
  private ctx!: GameContext; // "!" = assigned in init(), not in constructor
  private luck = new Map<string, number>(); // per-player luck
  private unsubscribers: Array<() => void> = [];

  constructor(private readonly cfg: DropConfig) {}

  init(ctx: GameContext): void {
    this.ctx = ctx;
    this.unsubscribers.push(
      ctx.bus.on('ENEMY_DEFEATED', (e) => this.onEnemyDefeated(e)),
      ctx.bus.on('PICKUP_COLLECTED', (e) => {
        if (e.kind === 'objective') this.reset(e.playerId);
      }),
    );
  }

  update(_dt: number): void {
    /* event-driven: nothing per tick */
  }

  dispose(): void {
    this.unsubscribers.forEach((off) => off());
    this.unsubscribers = [];
  }

  getLuck(playerId: string): number {
    return this.luck.get(playerId) ?? 0;
  }

  private onEnemyDefeated(e: EventOf<'ENEMY_DEFEATED'>): void {
    const luck = this.getLuck(e.killerId) + e.weight;
    this.luck.set(e.killerId, luck);
    const t = Math.min(1, luck / this.cfg.luckMax);
    this.ctx.bus.emit({ type: 'LUCK_CHANGED', playerId: e.killerId, luck, t });

    const pDrop = this.cfg.pBase + (this.cfg.pMax - this.cfg.pBase) * t;
    const hardPity = luck >= this.cfg.luckMax;
    if (!hardPity && this.ctx.rng.next() >= pDrop) return; // no drop this time

    const tierIndex = this.pickTier(t, hardPity);
    const tier = TIERS[tierIndex];
    const items = this.cfg.itemsByTier[tier];
    const item = items[Math.floor(this.ctx.rng.next() * items.length)];
    this.ctx.bus.emit({ type: 'DROP_SPAWNED', tier, item, pos: e.pos });

    if (tierIndex >= RARE_INDEX) this.reset(e.killerId); // important find → reset
  }

  private pickTier(t: number, hardPity: boolean): number {
    // Interpolate weights between "unlucky" and "lucky" tables.
    const w = this.cfg.baseWeights.map((b, i) => b + (this.cfg.luckyWeights[i] - b) * t);
    if (hardPity) for (let i = 0; i < RARE_INDEX; i++) w[i] = 0; // force rare+
    const total = w.reduce((s, x) => s + x, 0);
    let roll = this.ctx.rng.next() * total;
    for (let i = 0; i < w.length; i++) {
      roll -= w[i];
      if (roll < 0) return i;
    }
    return w.length - 1;
  }

  private reset(playerId: string): void {
    this.luck.set(playerId, 0);
    this.ctx.bus.emit({ type: 'LUCK_RESET', playerId });
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 5) MAP MANAGER rule: "no living heroes → ALL_HEROES_DOWN" (co-op only)
// ─────────────────────────────────────────────────────────────────────────────
export class MapManager implements IGameManager {
  private ctx!: GameContext;
  private allDownEmitted = false;
  private offs: Array<() => void> = [];

  init(ctx: GameContext): void {
    this.ctx = ctx;
    this.offs.push(
      ctx.bus.on('PICKUP_COLLECTED', (e) => {
        if (e.kind === 'objective') ctx.bus.emit({ type: 'MAP_VICTORY' });
      }),
    );
  }

  update(_dt: number): void {
    if (this.ctx.mode !== 'coop') return; // solo: never Game Over; pvp: no map loss
    const living = this.ctx.players.livingHeroes().length;
    if (living === 0 && !this.allDownEmitted) {
      this.ctx.bus.emit({ type: 'ALL_HEROES_DOWN' }); // once per transition
      this.allDownEmitted = true;
    } else if (living > 0) {
      this.allDownEmitted = false; // re-arm
    }
  }

  dispose(): void {
    this.offs.forEach((off) => off());
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 6) THE BORING TOP LOOP (fixed timestep)
// ─────────────────────────────────────────────────────────────────────────────
export class GameLoop {
  private acc = 0;
  constructor(
    private readonly managers: IGameManager[], // ORDER MATTERS, declared once
    private readonly bus: GameEventBus,
    private readonly step = 1 / 30,
  ) {}

  frame(frameDt: number, render: () => void): void {
    this.acc += Math.min(frameDt, 0.25); // clamp to avoid "spiral of death" after a tab switch
    while (this.acc >= this.step) {
      for (const m of this.managers) m.update(this.step);
      this.bus.flush();
      this.acc -= this.step;
    }
    for (const m of this.managers) m.lateUpdate?.(frameDt);
    render();
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Self-test (run with: npx tsx skeletons.ts) — Monte-Carlo sanity of DropManager
// ─────────────────────────────────────────────────────────────────────────────
const bus = new GameEventBus();
const ctx: GameContext = { bus, rng: mulberry32(42), players: { livingHeroes: () => ['p1'] }, mode: 'solo' };
const drops = new DropManager({
  luckMax: 20, pBase: 0.35, pMax: 0.9,
  baseWeights: [70, 25, 5, 0], luckyWeights: [30, 35, 28, 7],
  itemsByTier: { common: ['nigiri'], uncommon: ['sphere'], rare: ['ammo'], epic: ['gem'] },
});
drops.init(ctx);
let sinceRare = 0, maxGap = 0, rares = 0, total = 0;
bus.on('DROP_SPAWNED', (e) => { total++; if (e.tier === 'rare' || e.tier === 'epic') { rares++; maxGap = Math.max(maxGap, sinceRare); sinceRare = 0; } });
for (let i = 0; i < 10000; i++) {
  sinceRare++;
  bus.emit({ type: 'ENEMY_DEFEATED', enemyId: 'e' + i, killerId: 'p1', weight: 1, pos: { x: 0, y: 0, z: 0 } });
  bus.flush(); bus.flush(); // 2nd flush delivers DROP/LUCK events emitted during the 1st
}
console.log(JSON.stringify({ kills: 10000, drops: total, rares, maxKillsBetweenRares: maxGap }));
if (maxGap > 20) throw new Error('hard pity violated');
```
