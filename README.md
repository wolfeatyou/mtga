# mtga — MTG Arena Draft Helper (Claude Code skill)

Live drafting assistant for **MTG Arena Limited**. Reads the Arena `Player.log`, ranks the
current pack by **17Lands GIH win-rate**, and calls each pick given pool / colors / curve.
Also does post-game replay analysis and deck building. Full spec: [`SKILL.md`](SKILL.md).

**Sets:** `msh` (Marvel Super Heroes, current) · `sos` (Secrets of Strixhaven) · `mkm` (Murders at Karlov Manor).

## Scripts
| Script | Job |
|---|---|
| `draft_live.py` | Live pick advisor: `wake` detector + pack snapshot sorted by GIH, pool-aware flags, signal banners. |
| `draft_sim.py` | **Latency test-harness** — replays a real draft from the log into a fake log pick-by-pick, so you can measure advice speed across models/effort (see below). |
| `analyze_game.py` | Post-game log analysis: keep/mull, turn-by-turn casts/combat, engine summary. |
| `replay_moments.py` / `replay_report.py` | HTML replay reports with card images + P/T-with-counters. |
| `draft_goldfish.py` | Monte-Carlo goldfish sim of a built deck (mulligan, curve, color reliability). |
| `build_*_cheatsheet.py` | Regenerate the visual draft cheat sheets. |

## Knowledge files (read before each draft)
- `<set>_knowledge.md` — draft meta: open pairs, signals, over/under-rated cards.
- `<set>_insights.md` — in-game insights: winning lines, combat over/under-performers, matchups.
- `<set>_cheat.md` / `draft_cheat.md`, `<set>_tier.md` — mechanics + tier lists.
- `mtg_readme.md` — setup + accumulated piloting lessons.

## Latency harness (`draft_sim.py`)
Replays a **real** draft's log lines verbatim into `sim/sim_player.log`, one pack at a time on
your command, while `draft_live.py` runs against that fake log via `MTGA_LOG`. Because the same
draft replays identically every run, you can A/B advice latency across models and effort levels.

```bash
python3 draft_sim.py list            # drafts found in the logs
python3 draft_sim.py init            # extract newest draft, empty the fake log
python3 draft_sim.py next [N]        # feed the next wake-pick (pick<=11), N times
python3 draft_sim.py step [N]        # feed exactly one pick (granular)
python3 draft_sim.py finish          # flush pack tail + DraftComplete
python3 draft_sim.py status
```
Assistant side (init prints these with the right `MTGA_LOG`):
```bash
export MTGA_LOG=.../sim/sim_player.log
python3 draft_live.py <set> wake fresh   # before the first `next`
python3 draft_live.py <set>              # snapshot the current pack, then advise
python3 draft_live.py <set> wake         # re-arm for the next pick
```

## Requirements
Arena → Settings → Account → **Detailed Logs (Plugin Support)** = ON, then restart Arena.
Python 3, no third-party packages. Set + rating JSONs are committed; color-pair caches are
fetched on demand from 17lands.com.
