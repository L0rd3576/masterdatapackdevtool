# Loot tables, predicates, item modifiers, number providers (26.3 - BREAKING renames)

Sources: `reference/vanilla-data/minecraft/loot_table/**` (copy real examples from here),
`generated/reports/registries.json` (`loot_condition_type`, `loot_function_type`, `loot_pool_entry_type`,
`context_int_provider_type`, `context_float_provider_type`), JSON corpus results (`tools/corpus/json/`, run 2026-10-09).

## The 26.3 renames (vanilla data has zero uses of the old keys; verified by tools/verify_knowledge.py)
| Old (<= 26.2) | 26.3 |
|---|---|
| `"conditions": [ {...}, ... ]` | `"condition": {...}` (one object; combine with `minecraft:all_of` + `terms`) |
| `"functions": [ {...} ]` on entries/pools/tables | `"modifier": {...}` or `"modifier": [ {...}, ... ]` |
| `{"condition": "minecraft:random_chance", ...}` | `{"type": "minecraft:random_chance", ...}` |
| `{"function": "minecraft:set_count", ...}` | `{"type": "minecraft:set_count", ...}` |
| condition `block_state_property` | `match_block` |
| condition `value_check` | `int_value_check` / `float_value_check` |
| condition/function `reference` | removed (use the predicate/modifier ID as a plain string where allowed) |
| number provider `sum` / `product` / `minimum` / `maximum` / `average` | `add` / `mul` / `min` / `max` / `avg` |
| loot `tag` entry `name` | `items` |

Exception (verified): `minecraft:sequence` (item modifier) still uses **`functions`**; `"modifier"` there is rejected
(`No key functions in MapLike[...]`).

What the server does with old keys (verified): `functions`/`conditions` in a loot table are **silently ignored**
(the table loads, the modifiers/conditions just vanish). `{"condition": ...}` / `{"function": ...}` objects as a
predicate/item-modifier file are rejected (`Failed to parse`). The linter flags all of these.

## Loot table (vanilla example, trimmed from `loot_table/blocks/oak_leaves.json`)
```json
{
  "type": "minecraft:block",
  "pools": [{
    "rolls": 1,
    "condition": {"type": "minecraft:inverted", "term": {"type": "minecraft:any_of",
                  "terms": ["minecraft:tool/can_shear", "minecraft:tool/can_silk_touch"]}},
    "entries": [{
      "type": "minecraft:item",
      "name": "minecraft:stick",
      "condition": {"type": "minecraft:table_bonus", "enchantment": "minecraft:fortune", "chances": [0.02, 0.022222223]},
      "modifier": [
        {"type": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 1, "max": 2}},
        {"type": "minecraft:explosion_decay"}
      ]
    }]
  }]
}
```
- A string where a condition is expected = reference to a predicate file (`"minecraft:tool/can_shear"`).
- Verified OK (server-loaded): `{"pools":[{"rolls":1,"entries":[{"type":"minecraft:item","name":"minecraft:diamond"}]}]}`;
  `set_components` modifier with `{"minecraft:custom_name":{"text":"Wand","italic":false},"minecraft:custom_data":{"wand":1}}`.
- Unknown item in `name` -> `Unknown registry key ... minecraft:item: minecraft:nope` (server refuses to start).

## Predicate files (`data/<ns>/predicate/*.json`)
- **Must be a single JSON object** (a top-level list is rejected: `Not a JSON object`). Combine with
  `{"type":"minecraft:all_of","terms":[...]}` / `any_of` / `inverted` + `term`.
- Verified OK: `{"type":"minecraft:random_chance","chance":0.5}`,
  `{"type":"minecraft:entity_properties","entity":"this","predicate":{}}`,
  `{"type":"minecraft:entity_properties","entity":"this","predicate":{"flags":{"is_sneaking":true}}}`,
  `{"type":"minecraft:all_of","terms":[{"type":"minecraft:random_chance","chance":0.5},{"type":"minecraft:weather_check","raining":true}]}`.
- Misspelled field (`chanse`) -> rejected (missing required `chance`).
- Condition types: all_of any_of damage_source_properties enchantment_active_check entity_properties entity_scores
  environment_attribute_check float_value_check int_value_check inverted killed_by_player location_check match_block
  match_tool random_chance random_chance_with_enchanted_bonus survives_explosion table_bonus time_check weather_check.
- Entity predicates (26.2+): keys are component-style, e.g. `"minecraft:entity_type"`,
  `"minecraft:type_specific/player"`, `"minecraft:type_specific/sheep"`, `"minecraft:type_specific/cube_mob"`
  (vanilla advancements use these). Unknown sub-predicates are rejected (wiki).

## Item modifiers (`data/<ns>/item_modifier/*.json`)
- **Single object** (top-level list rejected: `Not a JSON object`). Chain several with
  `{"type":"minecraft:sequence","functions":[{...},{...}]}` (verified).
- Verified OK: `{"type":"minecraft:set_count","count":2}`.
- Function types: apply_bonus copy_components copy_custom_data copy_name copy_state discard enchant_randomly
  enchant_with_levels enchanted_count_increase exploration_map explosion_decay fill_player_head filtered
  furnace_smelt limit_count modify_contents sequence set_attributes set_banner_pattern set_book_cover set_components
  set_contents set_count set_custom_data set_custom_model_data set_damage set_enchantments set_firework_explosion
  set_fireworks set_instrument set_item set_loot_table set_lore set_name set_ominous_bottle_amplifier set_potion
  set_random_dyes set_random_potion set_stew_effect set_writable_book_pages set_written_book_pages toggle_tooltips.

## Number providers (`context_int_provider` / `context_float_provider`, 26.3)
- Inline: a number, or `{"type": "minecraft:uniform", "min": 1, "max": 3}` etc. Or an ID of a file in
  `data/<ns>/context_int_provider/` / `context_float_provider/`.
- Float provider types: abs add avg ceil conditional constant cos div enchantment_level environment_attribute floor
  from_int length max min mod mul negate number_dispatcher pow round sin sqrt storage sub truncate uniform weighted_list.
  Int types: `python -c "import json;print(json.load(open('generated/reports/registries.json'))['minecraft:context_int_provider_type'])"`.
- In commands a bare number is NOT accepted as a provider (it is read as an ID). Verified OK with `/compute`:
  `{type:"minecraft:constant",value:5}`, `{type:"minecraft:constant",value:2.5}`,
  `{type:"minecraft:add",inputs:[1,2]}` (numbers allowed inside), `{type:"minecraft:uniform",min:1,max:6}`,
  `{type:"minecraft:storage",storage:"c:s",path:"v"}`. BAD: `{type:"minecraft:add",left:1,right:2}` (`No key inputs`).
