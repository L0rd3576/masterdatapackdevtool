---
name: left-click-detection
description: Use when a datapack must react to a player left-clicking (swinging) with a custom item, hitting an entity, or punching an interaction hitbox in Minecraft Java 26.3. Covers the piercing_weapon + attack_range + post_piercing_attack enchantment trick (works in air), player_hurt_entity, and interaction-entity attack data.
---

# Left-click detection (Minecraft Java 26.3, data format 121)

There is no "left click" trigger. Pick the technique by what the player clicks. [V] = loaded or ran on the real 26.3 server
(`knowledge/_research/probes/tmg-lc-pack*.txt`, probe pack `tmg-lc-pack`); [R] = needs a real player to confirm (add to the
project's `TODO-real-player-tests.md`); [U] = taken from the user's older pack `secondatapack` (older Minecraft version).

## A. Left click with a custom item, even in the air: spear-style attack + enchantment effect
Source: user's `cruz_equip.mcfunction` (redstone torch "explosion wand") and `enchantment/explosion_wand.json` [U], rebuilt for 26.3.
The trick: make the item a zero-reach piercing weapon so a left click performs a "stab" that hits nothing, and attach a
custom enchantment whose `minecraft:post_piercing_attack` effect runs your function (vanilla uses the same effect for the
spear enchantment `lunge`: `reference/vanilla-data/minecraft/enchantment/lunge.json`).

1. Enchantment `data/<ns>/enchantment/left_click.json` [V loads; the effect firing is R]:
```
{"description":{"text":"Left Click"},"max_level":1,"slots":["hand"],"supported_items":"minecraft:redstone_torch","weight":1,"anvil_cost":0,
 "min_cost":{"base":0,"per_level_above_first":0},"max_cost":{"base":0,"per_level_above_first":0},
 "effects":{"minecraft:post_piercing_attack":[{"effect":{"type":"minecraft:run_function","function":"<ns>:on_left"}}]}}
```
   `supported_items` only gates the enchanting table/anvil; the item component below works on any item. The effect is a list of
   `{effect, requirements?}`; vanilla `lunge` shows how to add `requirements` (for example not riding, not in water).
2. Item [V accepted and stored]:
```
give @s minecraft:redstone_torch[custom_data={mypack_item:{key:"wand"}},piercing_weapon={},attack_range={min_reach:0.0,max_reach:0.0,hitbox_margin:0.0},enchantments={"<ns>:left_click":1},attribute_modifiers=[{id:"attack_speed",type:"attack_speed",amount:-1.4,operation:"add_value",slot:"hand",display:{type:"hidden"}}]]
```
   - **26.3 change:** the old form `piercing_weapon={min_reach:0.0,max_reach:0.0,hitbox_margin:0.0}` is accepted but the reach
     fields are SILENTLY DROPPED (stored as `piercing_weapon:{}`; `piercing_weapon={bogus:1}` is accepted too). Reach now lives in the
     `attack_range` component. If you copy the old form the stab keeps normal reach and can hurt what it points at. Always read
     the item back with `data get entity <stand> equipment.mainhand` and compare.
   - `attack_range` is stored as `{max_reach:0.0f,hitbox_margin:0.0f}` (min_reach 0 is the default and omitted).
   - A nonexistent enchantment id is rejected: `Failed to get element <id> from registry minecraft:enchantment`.
   - Negative `attack_speed` modifier (-1.4 in the old pack) slows how fast the swing recharges: a built-in cooldown. [U]
3. Function `<ns>:on_left` runs **as the attacking player** (the old pack used `@s` and `Rotation` there) [U, R].
   Keep your own per-player cooldown score too (the old pack decremented `explosion_wand_cd` every tick and returned early while > 0).
4. The same item can also be a right-click item: add the `consumable`/`use_effects` components of the `right-click-detection`
   skill (the old pack did this on the same torch). [U; combination untested in 26.3, R]
5. Reuse: a Team Minigames style `custom_data` marker lets protection/strip code treat the item like any other (see right-click skill).

## B. Left click that hits a player or mob: `player_hurt_entity` advancement
```
{"criteria":{"hit":{"trigger":"minecraft:player_hurt_entity","conditions":{
   "player":{"type":"minecraft:entity_properties","entity":"this","predicate":{"slots":{"weapon.mainhand":{"predicates":{"minecraft:custom_data":{"mypack_item":{}}}}}}}}}},
 "rewards":{"function":"<ns>:on_hit"}}
```
- [V] Loads on 26.3. **`conditions.player` is ONE object in 26.3, not a list** (a list fails server start: `Not a JSON object: [...]`).
- Optional filter on the damage: `"damage":{"type":{"is_direct":true,"direct_entity":{"type":"minecraft:arrow"}}}` [U, used for arrows];
  for melee use `"direct_entity":{"type":"minecraft:player"}` (R).
- The reward function runs as the attacker; start it with `advancement revoke @s only <ns>:hit` so the next hit fires again [U pattern].
- Fires only when damage was dealt, so it is not a swing detector. Other related triggers present in the registry: `player_killed_entity`, `entity_hurt_player`.

## C. Left click on an `interaction` entity (invisible clickable hitbox)
Source: user's blackjack table (`check_hit.mcfunction`) [U]. Spawn `summon minecraft:interaction ~ ~ ~ {width:0.9f,height:0.5f,response:1b,Tags:["btn"]}`.
- [V] `response:1b` is stored and readable. Before the first click `data get entity @s attack` reports `Found no elements matching attack`.
- After a left click the entity holds `attack` data with the clicker's UUID and a `timestamp` [U; fields not re-verified]. Poll each tick:
```
execute unless data entity @s attack run return 0
execute store result score #t tmp run data get entity @s attack.timestamp
execute if score #t tmp = @s last_hit run return 0
scoreboard players operation @s last_hit = #t tmp
function <ns>:on_hit with entity @s attack
```
  The macro receives `$(player)` (UUID) and `$(timestamp)`; identify the clicker with `@a[nbt={UUID:$(player)}]` or by comparing the stored UUID. Give each interaction its own `last_hit` score.
- Right click on the same entity is the advancement trigger `minecraft:player_interacted_with_entity` with `entity: {"minecraft:entity_type":"minecraft:interaction","minecraft:nbt":"{Tags:[\"btn\"]}"}` [U]; its `interaction` data works similarly.
- Keep the hitbox attached to a model by teleporting it each tick (`tp @s <entity>`) and killing it when the owner is gone [U sync_hitboxes].

## Related command
`swing @s mainhand stab 10t` plays an arm animation (animations: whack, stab, none; duration in ticks; `bonk` is invalid) [V].

## Test without a real player
- Check items by reading them back from an armor stand; check the enchantment by `data get ... equipment.mainhand.components`.
- Call the `on_left`/`on_hit` function directly as the stand-in or player to test the action; assert scores/storage after a `{"ticks":N}` step.
- List in `TODO-real-player-tests.md`: does the stab fire `post_piercing_attack` in the air with zero reach, repeat rate when clicking fast, effect of the attack-speed modifier, that nothing is damaged, creative-mode and spectator behaviour, offhand use.

## Pitfalls
- Unknown component fields are ignored silently by the item parser; the wrong field name does not error.
- Master linter limits seen here: it flags `function` inside an enchantment `run_function` effect as a loot-table rename (false positive, the server loads it) and warns on slot names used as map keys (`weapon.mainhand`). Treat these as known false positives until fixed (queued).
- No swing/left-click event exists: none of the 58 advancement triggers or the custom statistics in `generated/reports/registries.json` is a swing (checked 2026-10-11). Do not promise air-swing detection for ordinary items; use technique A.
