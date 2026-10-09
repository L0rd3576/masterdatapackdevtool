# Unverified / open questions (26.3)

Items here were read on the wiki or assumed but NOT confirmed against the 26.3 jar or server. Before relying on
one, verify it (copy a vanilla file, add a corpus line to `tools/corpus/commands.txt` or a JSON case to
`tools/corpus/json/`, run `python tools/diff_corpus.py`) and then move it into the matching knowledge file.

## Formats
- Overlay entry structure in pack.mcmeta (`directory` + `min_format`/`max_format`) - wiki only, no server test.
- Data pack formats for versions before 26.3 (table in changes-since-1.21.md) - wiki only.
- `filter` block in pack.mcmeta - wiki says still supported; untested.

## Commands
- Exact accepted syntax of slot sources beyond the tested names (container.*, weapon.*, weapon.mainhand, armor.*,
  armor.head/chest/body, hotbar.0, mob.inventory.0, contents) - and how to reference a `slot_source/` file.
- `/publish` lost `gamemode` (26.3), `/give` over-limit errors, `/tick step` errors (wiki).
- Whether integer y coordinates are centred like x/z for entity positions (only x was runtime-verified).

## Data formats (wiki, not server-tested)
- Trigger field pluralisation other than `recipe_unlocked.recipes`: `recipe_crafted.recipes`,
  `player_generates_container_loot.loot_tables`, `enter_block.blocks`.
- `set_loot_table`: `name` -> `loot_table_id`; `limit_count.limit` no single number; `exploration_map` fields.
- `filtered` loot function `on_pass`/`on_fail`.
- `custom_model_data` 1.21.4 structure; `equippable.asset_id`; `fire_resistant` -> `damage_resistant`.
- 1.21.5 entity NBT renames other than `equipment` (`drop_chances`, `fall_distance`, `respawn`, `block_pos`, ...).
- 26.3 block state SNBT `Name`/`Properties` -> `id`/`properties`; `pot_decorations` object form;
  furnace/brewing stand int fields; sign `allow_op_features`.
- 26.1 recipe changes (`crafting_dye`, `crafting_imbue`, string `result`, `show_notification`).
- 26.3 worldgen renames (block state providers, density functions, noise settings, carvers) beyond the folder renames.
- 26.2 tag renames (`#concrete_powders`, ...) and team colour restrictions.
- Enchantment `explode` effect field name (`block_particles` vs `block_effects`).

## Behaviour
- `@s` context of tick/load functions and `execute as` without `at` (standard behaviour, not re-tested).
- Load order across multiple packs and `/reload` re-running `#minecraft:load` (not tested this session).
