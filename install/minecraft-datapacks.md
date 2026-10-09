# Minecraft datapacks (any project containing a pack.mcmeta)

Applies whenever the working project contains a `pack.mcmeta` with a `data/` folder, or the task is about
Minecraft Java datapacks, `.mcfunction` files, or datapack JSON (loot tables, advancements, predicates, recipes...).

Target: Minecraft Java Edition 26.3, data pack format 121.0 (unless the project says otherwise).
Tools and verified knowledge live in `C:\Users\lrafy\mc-datapack-tools` (read its `CLAUDE.md` first).

Mandatory workflow:
1. Do not write datapack syntax from memory; it changed heavily (26.3 renamed loot keys, 1.21.11 renamed gamerules,
   1.21.5 made text components SNBT). Look things up first:
   - `python C:\Users\lrafy\mc-datapack-tools\tools\cmd_syntax.py <command> [sub...]` for command grammar
   - `C:\Users\lrafy\mc-datapack-tools\knowledge\*.md` (start with `pitfalls.md`)
   - `C:\Users\lrafy\mc-datapack-tools\reference\vanilla-data\minecraft\` for real JSON examples
   - `C:\Users\lrafy\mc-datapack-tools\generated\reports\` for registries, blocks, components
2. After every edit: `python C:\Users\lrafy\mc-datapack-tools\tools\lint_datapack.py <pack-dir>`
3. Before saying work is done: `python C:\Users\lrafy\mc-datapack-tools\tools\run_tests.py <pack-dir>`
   (boots a throwaway 26.3 server; tests go in `<pack-dir>/tests/*.test.json`, format in `knowledge\testing.md`).
4. Never claim success without real tool output. Never touch `%APPDATA%\.minecraft\saves` unless asked.
5. Record mistakes in `C:\Users\lrafy\mc-datapack-tools\knowledge\lessons.md`.

New pack: copy `C:\Users\lrafy\mc-datapack-tools\template-datapack\`.
