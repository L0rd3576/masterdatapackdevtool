---
name: right-click-detection
description: Use when a datapack must react to a player right-clicking with a custom item (menu items, wands, abilities, game-master buttons) in Minecraft Java 26.3. Gives the verified consumable item + using_item advancement recipe, debounce, protection against dropping, and pitfalls.
---

# Right-click detection (Minecraft Java 26.3, data format 121)

Verified on the real 26.3 server unless marked [R] (needs a real player; listed in the project's `TODO-real-player-tests.md`).
Evidence: `knowledge/item-components.md` ("Right-click items"), `knowledge/advancements.md` (`using_item`),
`knowledge/_research/probes/probe-tmg-gm-1..3.txt`, probe pack `tmg-gm-pack`. Working project code: Team Minigames
`src/pack/data/tmg/gm/` (game master Start/Cancel item). First seen in the user's older pack `secondatapack` (`give_dash_wand`).

## The recipe
1. **An item that is "being used" while right-click is held, and never finishes**, with a marker in `custom_data`:
```
give @s minecraft:emerald[custom_data={mypack_item:{key:"start"}},item_name={text:"Start Game",color:"green",italic:false},consumable={consume_seconds:1000000.0f,animation:"none",sound:"minecraft:intentionally_empty",has_consume_particles:false},use_effects={can_sprint:true,speed_multiplier:1.0f,interact_vibrations:false},max_stack_size=1,enchantments={"minecraft:vanishing_curse":1},enchantment_glint_override=false,tooltip_display={hidden_components:["minecraft:enchantments"]}]
```
   - `consumable` makes the game start the "use" state on right click; a huge `consume_seconds` means it is never eaten.
   - `animation:"none"` (a typo gives `Unknown element name`), silent sound, no particles.
   - `use_effects` stops the use slowdown: `speed_multiplier` 0.0-1.0 (1.5 is rejected), `can_sprint:true`.
   - Old pack forms (`consume_seconds:9999999`, `speed_multiplier:1` as ints) are coerced and still work.
   - `vanishing_curse` on any item stops it dropping on death. Any item works (emerald, stick, breeze_rod, ...).
2. **An advancement** that fires while the item is used and matches the marker (file `data/<ns>/advancement/use.json`):
```
{"criteria":{"use":{"trigger":"minecraft:using_item","conditions":{"item":{"predicates":{"minecraft:custom_data":{"mypack_item":{}}}}}}},
 "rewards":{"function":"<ns>:on_use"}}
```
   - `custom_data~{mypack_item:{}}` matches any item with that compound; add `key:"start"` to match exactly one.
   - Item-id matching also works: `"items":"minecraft:carrot_on_a_stick"`.
3. **The reward function runs as the player** and must revoke the advancement first so it can fire again:
```
# <ns>:on_use
advancement revoke @s only <ns>:use
function <ns>:press
```
   Reward functions run with the normal function permission level, so a non-op player can trigger it. [R]
4. **Dispatch by key** (several items, one advancement): loop the item list from config/storage and test each with
   `execute if items entity @s weapon.* *[custom_data~{mypack_item:{key:"start"}}]` (macro the key). The action is a
   function id stored with the item definition, so adding an item = adding a config entry, not code.

## Debounce (required)
`using_item` keeps firing while the button is held. Treat it as one click:
- Store the last accepted press tick in a per-player score (`time query gametime`); ignore a press within N ticks
  (project default 5 for repeats, 10 between actions; both configurable). Real repeat rate is [R], tune on a real client.
- If an action changes the item (Start -> Cancel), swap it with `item replace entity @s hotbar.8 with ...` in the same call.

## Keep the item from being lost (the "protected item" pattern)
No component prevents dropping or moving (verified). Layer these every tick (cost about 0.06 ms per pass):
- Slot source files `data/<ns>/slot_source/<id>.json` (type `minecraft:filtered`, `item_filter` on the marker, `slot_range`
  groups such as `weapon.*`, `hotbar.*`, `inventory.*`) reference slots as `<ns>:<id>`.
- Check the owner has exactly one correct item in the fixed slot; if not, `item fill entity @s <ns>:<filtered> with minecraft:air`
  then `item replace` one fresh copy. **`item replace` on a multi-slot source changes ONE slot only; use `item fill` to clear all.**
- Clear marked items from everyone who should not hold one.
- Kill dropped copies: `execute as @e[type=minecraft:item] if items entity @s contents *[custom_data~{mypack_item:{}}] run kill @s`.
- Items in chests/item frames are inert; clear frames with `item fill ... contents` through a filtered source if needed.
- If another system saves/clears/restores inventories (rounds, kits), strip the marked items before the snapshot and re-give after.

## Testing (no real players on the test server)
- Stand-ins: armor stands hold the item via `item replace entity @n[tag=s] weapon.mainhand with ...`; call the press
  function directly; assert scores/storage. Add `{"ticks":N}` steps before asserting anything scheduled (world is frozen).
- Add real-player checks to `TODO-real-player-tests.md`: repeat rate while held, no slowdown, no eating, drop with Q,
  inventory-screen moves, cursor/crafting-grid slots, death.

## Pitfalls
- Without the revoke the advancement fires once only. With revoke but no debounce, one hold = many actions.
- Unknown component fields are silently ignored by the item parser in 26.3 (see left-click skill): re-read with
  `data get entity <stand> equipment.mainhand` after any item change and compare to what you wrote.
- The linter may warn on advancement `rewards.function` or marker keys in older tool versions; master `tools/lint_datapack.py` fixes this (G0).
- Reuse: search `library/INDEX.md` first (cooldown/timer/message helpers). Library `msg/countdown` shows titles only.
