# Files that could not be installed automatically

The unattended setup run was not allowed to write to `~/.claude/rules/` or `.claude/skills/` (permission-gated
paths). Copy them yourself (PowerShell):

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\rules" | Out-Null
Copy-Item "C:\Users\lrafy\mc-datapack-tools\install\minecraft-datapacks.md" "$env:USERPROFILE\.claude\rules\"
New-Item -ItemType Directory -Force "C:\Users\lrafy\mc-datapack-tools\.claude\skills\datapack-workflow" | Out-Null
Copy-Item "C:\Users\lrafy\mc-datapack-tools\install\skills\datapack-workflow\SKILL.md" "C:\Users\lrafy\mc-datapack-tools\.claude\skills\datapack-workflow\"
```
