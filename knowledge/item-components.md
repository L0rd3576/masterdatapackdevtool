# Item stacks and data components (26.3)

Sources: `generated/reports/registries.json` (`minecraft:data_component_type`, `data_component_predicate_type`),
`generated/reports/minecraft/components/item/<item>.json` (default components of every item),
corpus results (`generated/corpus-results.txt`), `tools/selftest/runtime_facts` (runtime-verified).

## Command syntax: `id[component=value,...]` (NBT `{...}` after the id is gone since 1.20.5)
Verified OK in 26.3:
```mcfunction
give @s minecraft:diamond_sword[minecraft:damage=5]
give @s minecraft:diamond_sword[damage=5,unbreakable={}]
give @s minecraft:stick[custom_name={text:"Wand",italic:false},lore=[{text:"line"}]]
give @s minecraft:stick[custom_data={c:{wand:1b}}]
give @s minecraft:stick[enchantment_glint_override=true,max_stack_size=1]
give @s minecraft:diamond_sword[enchantments={"minecraft:sharpness":5}]
give @s minecraft:potion[potion_contents={potion:"minecraft:swiftness"}]
give @s minecraft:stick[!food]
give @s minecraft:player_head[profile={name:"Notch"}]
give @s minecraft:leather_helmet[dyed_color=16711680]
give @s minecraft:stick[item_model="minecraft:blaze_rod"]
give @s minecraft:stick[tooltip_display={hidden_components:["minecraft:enchantments"]}]
give @s minecraft:stick[attribute_modifiers=[{type:"minecraft:attack_damage",amount:5,id:"c:dmg",operation:"add_value",slot:"mainhand"}]]
give @s minecraft:stick[minecraft:food={nutrition:4,saturation:0.5f}]
give @s minecraft:stick[consumable={consume_seconds:1.6f}]
```
- Component names may omit `minecraft:`. `!name` removes a default component.
- Values are SNBT. Text components inside (custom_name, lore, item_name) are SNBT objects, not JSON strings.

BAD (server message):
- `give @s minecraft:diamond_sword{Damage:5}` -> `Expected whitespace to end one argument, but found trailing data`
- `give @s minecraft:stick[not_a_component=1]` -> `Unknown item component 'minecraft:not_a_component'`
- `enchantments={levels:{"minecraft:sharpness":5}}` -> `Malformed 'minecraft:enchantments' component` (flattened in 1.21.5)
- `attribute_modifiers={modifiers:[...]}` and `show_in_tooltip` fields: pre-1.21.5 forms (wiki; linter flags them).

## Item predicates (execute if items, clear, selectors' item checks)
- `minecraft:stick`, `#minecraft:swords`, `*` (any item), plus `[...]`:
  - `component=value` exact match; `component~{...}` sub-predicate (partial match); `|` alternatives; `!` negation.
- Verified OK: `execute if items entity @s weapon.mainhand *[minecraft:custom_data~{c:{id:1}}] run ...`,
  `clear @s *[custom_data~{c:{wand:1b}}]`.
- Runtime-verified: `execute if items entity <item entity> contents minecraft:stick[minecraft:custom_data~{rf:1b}]`
  matches a dropped stick with that custom_data; `~{rf:2b}` does not.

## Item stacks inside NBT / JSON (runtime-verified)
- Shape: `{id:"minecraft:stick",count:3,components:{"minecraft:custom_data":{rf:1b}}}` (lowercase `id`, `count`,
  `components`; old `Count`/`tag` are gone).
- Item entity: `Item:{...}`; mob equipment: `equipment:{head:{...},chest:{...},legs,feet,mainhand,offhand,body,saddle}`
  (1.21.5 replaced `ArmorItems`/`HandItems`; verified `equipment.head.id` after summon).
- After `item replace ... armor.chest with minecraft:iron_chestplate[minecraft:unbreakable={}]`,
  `equipment.chest.components` = `{"minecraft:unbreakable":{}}`.
- In JSON files (loot `set_components`, recipe results, advancement icons) use `"id"`, never `"item"`
  (`old_icon_item.json` and `old_result.json` were rejected).

## Component list
- All component IDs: `python -c "import json;print(sorted(json.load(open('generated/reports/registries.json'))['minecraft:data_component_type']['entries']))"`
- Default components of an item: `generated/reports/minecraft/components/item/<item>.json`.
- 26.3 additions (registry-verified): attack_animation, interact_animation, block_transformer, cooking_fuel,
  brewing_fuel. Removed: swing_animation, map_color.
- Common: custom_data, custom_name, item_name, lore, rarity, unbreakable, damage, max_damage, max_stack_size,
  enchantments, stored_enchantments, enchantment_glint_override, attribute_modifiers, tooltip_display, item_model,
  consumable, food, equippable, use_cooldown, potion_contents, dyed_color, profile, tool, weapon.
