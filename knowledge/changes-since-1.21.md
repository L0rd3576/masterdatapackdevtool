# Breaking changes for datapacks: 1.21 -> 26.3

Legend: [V] verified this session against the 26.3 jar (reports, vanilla data, or the live server);
[W] from Minecraft Wiki version pages only (raw notes with URLs: `knowledge/_research/1.21.x.md`, `_research/26.x.md`).
When writing something marked [W], check the vanilla file or run the corpus first.

## Pack format by version
1.21-1.21.1: 48 | 1.21.2-3: 57 | 1.21.4: 61 | 1.21.5: 71 | 1.21.6: 80 | 1.21.7-8: 81 | 1.21.9-10: 88.0 |
1.21.11: 94.1 | 26.1-26.1.2: 101.1 | 26.2: 107.1 | **26.3: 121.0 [V]** (others [W]).

## 1.21 (48)
- Folders singular: function, advancement, loot_table, predicate, item_modifier, recipe, structure,
  tags/function, tags/block, tags/item, tags/entity_type, tags/fluid, tags/game_event [V: datapack.json + silent ignore].
- Data-driven enchantment, painting_variant, jukebox_song, enchantment_provider [V: folders exist].
- Attribute modifiers use namespaced `id` instead of `uuid`+`name` [V: corpus give with attribute_modifiers id].
- `@n` selector [V]. `!component` removal in item args [V].
- Loot: `random_chance_with_looting` -> `random_chance_with_enchanted_bonus`; `looting_enchant` -> `enchanted_count_increase` [V: registry].

## 1.21.2 (57)
- Attribute IDs lose `generic.`/`player.` prefixes [V].
- Recipe ingredients are strings / `#tag` (no `{"item":..}`) [V: server rejects old form].
- `food` split: `consumable` holds consume_seconds/animation/effects [V: both components exist; corpus OK].
- `fire_resistant` -> `damage_resistant` [W]. New components equippable, item_model, use_cooldown, ... [V: registry].
- `/rotate` added [V].

## 1.21.4 (61)
- `custom_model_data` is `{floats, flags, strings, colors}` [W]. `equippable.model` -> `asset_id` [W].

## 1.21.5 (71) - big one
- Text components are SNBT in commands; `clickEvent`/`hoverEvent` -> `click_event`/`hover_event` with renamed
  fields (`command`, `url`, `value`, ...) [V: new form accepted; old keys silently ignored].
- Components flattened: `enchantments={levels:{..}}` -> `enchantments={..}` [V: old rejected];
  `attribute_modifiers={modifiers:[..]}` -> `[..]` [W]; `show_in_tooltip`/`hide_tooltip` -> `tooltip_display` [W; component exists V].
- Entity NBT: `ArmorItems`/`HandItems` -> `equipment` map [V runtime]; `ArmorDropChances`/`HandDropChances` ->
  `drop_chances` [W]; `FallDistance` -> `fall_distance` [W]; player spawn fields -> `respawn` [W].
- Variant entity sub-predicates removed in favour of components [W].
- `/test` command, `test_environment`/`test_instance` registries [V: exist].
- fill/clone/setblock `strict` mode [W].

## 1.21.6 (80)
- `/dialog`, `/waypoint`, `/version` [V: exist]; `dialog` registry [V]. Strict JSON parsing [V: trailing comma rejected].

## 1.21.9 (88.0)
- pack.mcmeta `min_format`/`max_format` replace `supported_formats` [V: server warnings]. Pack formats have minors.
- `chain` -> `iron_chain` [V]. `/fetchprofile` [V]. Spawn chunks removed [V: `Loading 0 persistent chunks`].

## 1.21.11 (94.1)
- Game rules are a registry with snake_case IDs (`doMobSpawning` -> `spawn_mobs`, ...) [V].
- dimension_type `effects` etc. moved to environment `attributes`; `timelines` [V: vanilla keys].
- Biome visuals/audio -> environment attributes [W]. `timeline` registry [V]. `/stopwatch` [V].
- Loot `filtered` uses `on_pass`/`on_fail` [W]; `slots` pool entry + slot sources [V: registry].

## 26.1 (101.1)
- New version numbering; Java 25 [V]. `world_clock` registry, `/time of <clock> ...` [V: commands.json].
  `timeline` requires `clock` [V: all vanilla timelines have it].
- `villager_trade` + `trade_set` registries [V: folders]. Inventory slots `villager.*` -> `mob.inventory.*` [V: server].
- Sound variant registries (cat/pig/cow/chicken) [V]. `/swing` [V].
- Recipes: special recipes reworked (`crafting_dye`, `crafting_imbue`, ...) [W]; `result` may be a string [W].
- World save layout moved (`dimensions/minecraft/overworld`, `players/`, `data/minecraft/scoreboard.dat`) [W].

## 26.2 (107.1)
- Entity predicate keys: `minecraft:entity_type`, `minecraft:type_specific/<x>`; slime -> `type_specific/cube_mob`
  [V: vanilla advancements]. Unknown sub-predicates rejected [W].
- `sulfur_cube_archetype` registry [V]. Block tag `#concrete_powder` -> `#concrete_powders` [W].
- `HurtByTimestamp` removed [W]. Team colours lowercase snake only [W].

## 26.3 (121.0)
- Loot/predicate/modifier keys: `condition`/`modifier`/`type` (see loot-predicates.md) [V].
  `sequence` keeps `functions` [V]. Predicate/modifier files must be single objects [V].
- `number_provider` -> `context_int_provider`/`context_float_provider`; `sum`->`add` etc. [V].
- Conditions `block_state_property` -> `match_block`, `value_check` -> `int_/float_value_check`, `reference` removed [V].
- Loot `tag` entry `name` -> `items` [V]. `set_loot_table`: `name` -> `loot_table_id` [W].
- Trigger fields pluralised (`recipes`, `loot_tables`, `blocks`) [V for recipes; rest W].
- `/compute`, `/posteffect`, `/item fill|override`, `execute if slots`, `data ... compute` [V]. Slot arguments are
  slot sources [V]. `/swing` animation + duration [V]. `/publish` lost `gamemode` [W].
- Components: `attack_animation`/`interact_animation` replace `swing_animation`; `block_transformer`, `cooking_fuel`,
  `brewing_fuel` added; `map_color` removed [V]. `pot_decorations` list -> object [W].
- Block state SNBT `Name`/`Properties` -> `id`/`properties` [W]. Sign `allow_op_features` [W].
- Worldgen: `configured_feature` -> `feature` (inline config), `configured_carver` -> `carver` [V folders];
  block state provider and density function renames [W]. trim_material `asset_name` -> `palette_id` [V].
- Recipe type `minecraft:brewing` [V]; cooking `cookingtime` mandatory [W].
