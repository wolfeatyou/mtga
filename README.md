# mtga — MTG Arena Draft Helper (Claude Code skill)

Live drafting assistant for **MTG Arena Limited**. Reads the Arena `Player.log`, ranks the
current pack by **17Lands GIH win-rate**, and calls each pick given pool / colors / curve.
Also does post-game replay analysis and deck building. Full spec: [`SKILL.md`](SKILL.md).

**Sets:** `msh` (Marvel Super Heroes, current) · `sos` (Secrets of Strixhaven) · `mkm` (Murders at Karlov Manor).

## Scripts
| Script | Job |
|---|---|
| `draft_live.py` | Live pick advisor: blocking `watch` (single inference pass, default) or `wake`+snapshot (older 2-pass fallback), pack ranked by GIH, pool-aware flags, signal banners. |
| `draft_sim.py` | **Latency test-harness** — replays a real draft from the log into a fake log pick-by-pick, so you can measure advice speed across models/effort (see below). |
| `analyze_game.py` | Post-game log analysis: keep/mull, turn-by-turn casts/combat, engine summary. |
| `replay_moments.py` / `replay_report.py` | HTML replay reports with card images + P/T-with-counters. |
| `draft_goldfish.py` | Monte-Carlo goldfish sim of a built deck (mulligan, curve, color reliability). |
| `build_*_cheatsheet.py` | Regenerate the visual draft cheat sheets. |

## Live draft — recommended setup
**Model: Sonnet 5, effort medium.** Validated (2026-07-02) via the latency harness below — Opus /
high / xhigh effort ran 20–55s per pick even in the fastest mode, consistently slower than the
user's pick pace; Sonnet 5 medium kept up with no observed drop in decision quality.

Live loop = one **foreground blocking call**, re-issued after each pick:
```bash
MTGA_SETTLE=1 python3 draft_live.py <set> watch fresh   # first call of a draft
MTGA_SETTLE=1 python3 draft_live.py <set> watch         # every call after
```
It blocks until a new pack lands and returns the fully analyzed pack as the result — one inference
pass straight to advice, no separate snapshot call needed. `MTGA_SETTLE` (default 1s) debounces
picks made faster than advice can be given: it always returns the latest pack, silently skipping
stale ones. Raise it if running on a slower model/effort than Sonnet medium.

## Knowledge files (read before each draft)
- `<set>_knowledge.md` — draft meta: open pairs, signals, over/under-rated cards.
- `<set>_insights.md` — in-game insights: winning lines, combat over/under-performers, matchups.
- `<set>_cheat.md` / `draft_cheat.md`, `<set>_tier.md` — mechanics + tier lists.
- `mtg_readme.md` — setup + accumulated piloting lessons.

## Latency harness (`draft_sim.py`)
Replays a **real** draft's log lines verbatim into `sim/sim_player.log`, one pack at a time on
your command, while `draft_live.py` runs against that fake log via `MTGA_LOG`. Because the same
draft replays identically every run, you can A/B advice latency across models and effort levels.
Note: the pool always reflects the *real historical picks* from that draft, not the assistant's
advice — you're timing/practicing advice, not steering the outcome.

```bash
python3 draft_sim.py list            # drafts found in the logs
python3 draft_sim.py init [id8]      # extract one (default: newest), empty the fake log
python3 draft_sim.py next [N]        # feed the next wake-pick (pick<=11), N times
python3 draft_sim.py step [N]        # feed exactly one pick (granular)
python3 draft_sim.py status
python3 draft_sim.py reset           # rewind the same draft to pick 1
python3 draft_sim.py finish          # flush pack tail + DraftComplete
```
Assistant side — same blocking `watch` loop as live draft, pointed at the fake log:
```bash
MTGA_SETTLE=1 MTGA_OFFLINE=1 MTGA_LOG=.../sim/sim_player.log \
  python3 draft_live.py <set> watch fresh   # first call; drop `fresh` after
```
`MTGA_OFFLINE=1` skips 17Lands network fetches entirely — recommended for pure latency
measurement so a first-time cache-miss fetch never pollutes the timing.

## Requirements
Arena → Settings → Account → **Detailed Logs (Plugin Support)** = ON, then restart Arena.
Python 3, no third-party packages. Set + rating JSONs are committed; color-pair caches are
fetched on demand from 17lands.com.
