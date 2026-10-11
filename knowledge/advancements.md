# Advancements (26.3)

Sources: `reference/vanilla-data/minecraft/advancement/**`, `generated/reports/registries.json` (`trigger_type`),
JSON corpus (`tools/corpus/json/advancement/`).

## Minimal working forms (server-verified)
```json
{"criteria": {"t": {"trigger": "minecraft:tick"}}, "rewards": {"function": "c:helper"}}
```
```json
{
  "parent": "minecraft:story/root",
  "criteria": {"get_stone": {"trigger": "minecraft:inventory_changed",
               "conditions": {"items": [{"items": "#minecraft:stone_tool_materials"}]}}},
  "display": {"icon": {"id": "minecraft:wooden_pickaxe"}, "title": {"translate": "..."},
              "description": {"translate": "..."}},
  "requirements": [["get_stone"]]
}
```
- Criteria still use **`conditions`** (plural) - unlike loot tables. `trigger` must be in `trigger_type`
  (unknown trigger -> load failure).
- `display.icon` is an item stack with **`id`** (`{"item": ...}` rejected).
- An advancement with `display` and **no `parent`** is a tab root and **must have `display.background`**
  (server: `Visible advancement roots must have background`). Vanilla root example:
  `"background": "minecraft:gui/advancements/backgrounds/adventure"` (no `textures/` prefix or `.png`, since 1.21.5).
- `rewards.function` pointing to a missing function is **not** checked at load (silent). Linter checks it.
- Hidden "logic only" advancements: omit `display` (no toast, not shown) - vanilla recipe advancements do this.

## Trigger field renames (26.3; verified in vanilla where marked)
- `recipe_unlocked`: `recipe` -> `recipes` (verified: vanilla uses `recipes`, never `recipe`).
- (wiki) `recipe_crafted`/`crafter_recipe_crafted`: `recipe_id` -> `recipes`; `player_generates_container_loot`:
  `loot_table` -> `loot_tables`; `enter_block`/`slide_down_block`/`bee_nest_destroyed`: `block` -> `blocks`.
- Entity predicates inside conditions use 26.2+ keys (`minecraft:entity_type`, `minecraft:type_specific/*`).

## Useful triggers
`minecraft:tick` (every tick per player), `inventory_changed`, `consume_item`, `player_killed_entity`,
`entity_killed_player`, `placed_block`, `item_used_on_block`, `location`, `player_interacted_with_entity`,
`using_item`, `impossible` (grant only via command). Full list: `registries.json` -> `minecraft:trigger_type`.

## Common pattern: detect + revoke
```mcfunction
# advancement c:used_carrot_stick: {"criteria":{"u":{"trigger":"minecraft:using_item","conditions":{"item":{"items":"minecraft:carrot_on_a_stick"}}}},"rewards":{"function":"c:on_use"}}
# c:on_use
advancement revoke @s only c:used_carrot_stick
```
(The advancement JSON above loaded on the 26.3 server: `tools/corpus/json/advancement/ok_using_item.json`.)

## using_item with custom_data (probe 2026-10-11, `_research/probes/tmg-gm-pack/data/p/advancement`)
- [V loads] `"item":{"predicates":{"minecraft:custom_data":{"tmg_gm":{"key":"start"}}}}` (JSON object) and the SNBT string form
  `"minecraft:custom_data":"{tmg_gm:{key:\"start\"}}"` both load; `inventory_changed` with `"items":[{"predicates":{...}}]` loads.
- [P] How often `using_item` fires while the button is held needs a real player (vanilla code fires it each use tick). Debounce on
  game time: ignore a fire if the previous fire was <= N ticks ago; treat an unset last-fire score as a new press
  (a fresh test world has game time < 5, so "now - 0" looked like a hold in the probe).
- [V] `"rewards":{"function":"c:helper","experience":0}` loads (diff_corpus, `tools/corpus/json/advancement/ok_reward_custom_data__nowarn.json`).
  Linter fixed 2026-10-11 (GM G0): `rewards` keys function/loot/recipes/experience accepted; `custom_data` /
  `minecraft:custom_data` values are never key-checked (any depth).
