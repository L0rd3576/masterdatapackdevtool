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
