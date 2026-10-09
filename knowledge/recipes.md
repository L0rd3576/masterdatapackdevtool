# Recipes (26.3)

Sources: `reference/vanilla-data/minecraft/recipe/**`, `registries.json` (`recipe_serializer`), JSON corpus.

## Server-verified forms
```json
{"type":"minecraft:crafting_shaped","category":"misc","key":{"#":"minecraft:stick","X":"#minecraft:planks"},
 "pattern":["X","#"],"result":{"id":"minecraft:diamond","count":2}}
```
```json
{"type":"minecraft:crafting_shapeless","ingredients":["minecraft:dirt","#minecraft:sand"],"result":{"id":"minecraft:gravel"}}
```
- Ingredients are plain strings: `"minecraft:x"`, `"#minecraft:tag"`, or a list of item IDs (since 1.21.2).
  `{"item": "minecraft:dirt"}` is **rejected** (old_ingredient.json). Exception: the new `minecraft:brewing` recipe
  uses `{"item": ..., "potion_contents": ...}` objects for `input`/`output` (vanilla).
- `result` uses `id` (+ `count`, `components`); `{"item": ...}` rejected. 26.1+ (wiki): `result` may be a bare string.
- Unknown `type` -> rejected. Types: `python -c "import json;print(json.load(open('generated/reports/registries.json'))['minecraft:recipe_serializer'])"`.
- (wiki, 26.3) cooking recipes require `cookingtime`; new `minecraft:brewing` (`input`, `reagent`, `output`) - brewing verified in registry.
- (wiki, 26.1) special recipes renamed: `crafting_special_armordye` -> `crafting_dye`, `crafting_special_tippedarrow`
  -> `crafting_imbue`, map cloning -> `crafting_transmute`.

Copy the closest vanilla recipe from `reference/vanilla-data/minecraft/recipe/` and edit it.
