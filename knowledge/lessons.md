# Lessons learned (append newest at the bottom)

Format: `YYYY-MM-DD | what went wrong | verified correct form | how to avoid`


2026-10-09 | Edited Python code via heredoc'd `python -c` string replacement; `\n`, `\` and `\s` got mangled into real newlines/broken regexes (3 times) | Use the Edit tool for code edits | Never script code edits that contain escapes.
2026-10-09 | Assumed `summon ... 0 -60 0` puts the entity at x=0.0 | Integer x coordinates are block-centred: x=0.5 (runtime test tools/selftest/good) | Assert with ranges/boxes or check the real value first.
2026-10-09 | Assumed predicate/item_modifier files may be top-level JSON lists (true before 26.3) | 26.3 rejects them ("Not a JSON object"); use all_of/terms or sequence/functions | Copy shapes from reference/vanilla-data.
2026-10-09 | Assumed the 26.3 `functions`->`modifier` rename applies everywhere | `minecraft:sequence` still requires `functions` ("No key functions") | Treat rename tables as per-field; verify with tools/diff_corpus.py.
2026-10-09 | Wrote `compute default integer 5` | Commands need a provider object or ID: `{type:"minecraft:constant",value:5}`; `add` uses `inputs:[..]` | Check knowledge/loot-predicates.md.
2026-10-09 | Test servers: flat world failed with "No key layers in MapLike[{}]"; RCON dropped on an unknown packet type | Set generator-settings layers; read multi-packet RCON replies by length/timeout | Both handled in tools/run_tests.py + test-server/template.
2026-10-09 | Advancement with `display` but no `parent` | Needs `display.background` ("Visible advancement roots must have background") | Linter now flags it.
2026-10-09 | Wrote `execute if data storage s fe[-1]{c:1b}` (index + compound filter); linter passed, server refused the whole function | Store a flag field and test `fe[-1].c` | Linter rule + corpus lines added; see function-macros.md.
2026-10-09 | Used `random value $(min)..$(max)` in a macro; min = max errors at runtime | Compute with `random value 0..2147483646` + `%=` (mcdp_lib:random/int) | Test edge ranges (min = max) for every random helper.
2026-10-09 | Asserted a whole compound with assert_data; server key order differed (head/mainhand swapped) | assert_data compares text: assert sub-paths, or keep compounds to one key | Prefer per-field assert_data for compounds with several keys.
2026-10-09 | A nested macro call with a missing key fails silently (no log, caller continues) | Lint checks inline-compound calls; test library functions top-level with expect_error | Never rely on runtime logs for macro argument errors.
