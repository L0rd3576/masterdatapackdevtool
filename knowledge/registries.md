# Registries, IDs and data-driven content (26.3)

Never guess an ID. Look it up:
```
python -c "import json;r=json.load(open('generated/reports/registries.json'));print(sorted(r['minecraft:mob_effect']['entries']))"
```
- `generated/reports/registries.json`: static registries (95): block, item, entity_type, mob_effect, attribute,
  particle_type, sound_event, data_component_type, trigger_type, loot_*_type, recipe_serializer, game_rule,
  stat_type, custom_stat, slot_source_type, context_*_provider_type, ...
- Data-driven (dynamic) registries are NOT in registries.json; their vanilla IDs are the files under
  `reference/vanilla-data/minecraft/<registry>/` (enchantment, damage_type, painting_variant, jukebox_song,
  trim_material, dialog, timeline, world_clock, worldgen/*, ...). Pack files add more.
- `generated/reports/blocks.json`: every block with its properties and allowed values.
- `generated/reports/minecraft/components/item/<item>.json`: default components per item.
- Vanilla tags: `reference/vanilla-data/minecraft/tags/<registry>/`.
- `generated/reports/datapack.json`: which registries accept files (`elements`) and tags (`tags`).

## Verified renames worth remembering
- Attributes have no `generic.`/`player.` prefix (1.21.2): `minecraft:max_health`, `minecraft:movement_speed`,
  `minecraft:scale`, `minecraft:attack_damage`.
- Block/item `chain` -> `iron_chain` (1.21.9).
- trim_material uses `palette_id` (26.3; `asset_name` gone).
- Every vanilla `timeline` has a `clock` (26.1 made it required); clocks live in `world_clock/`.
- dimension_type (26.3 vanilla overworld keys): ambient_light, attributes, coordinate_scale, default_clock,
  has_ceiling, has_ender_dragon_fight, has_skylight, height, infiniburn, logical_height, min_y,
  monster_spawn_block_light_limit, monster_spawn_light_level, timelines. (`effects`, `ultrawarm`, `piglin_safe`,
  `bed_works`, `fixed_time`, ... are gone - moved to environment attributes in 1.21.11.)
- Game rules are a registry (`game_rule`) with snake_case IDs (see commands.md).

## Enchantment (vanilla `enchantment/sharpness.json` keys)
anvil_cost, description, effects, exclusive_set, max_cost, max_level, min_cost, primary_items, slots,
supported_items, weight. Copy a vanilla file and edit; effect components are keyed like `"minecraft:damage"`.

## New 26.x data-driven registries (folders exist per datapack.json)
villager_trade + trade_set (26.1), world_clock (26.1), cat/pig/cow/chicken_sound_variant (26.1),
sulfur_cube_archetype (26.2), context_int_provider / context_float_provider (26.3), block_transformer (26.3),
worldgen/material_condition, worldgen/material_rule (26.3). Field details: wiki notes in
`knowledge/changes-since-1.21.md`; always copy the vanilla file shape from `reference/vanilla-data/`.
