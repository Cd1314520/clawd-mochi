# Claude Code integration

[Claude Code hooks](https://code.claude.com/docs/en/hooks) run a shell command when something happens in a session.
Four hooks that each `curl` Mochi turn it into a status light you can read from across the room:

| Claude Code event | Request | Mochi | Meaning |
| ----------------- | ------- | ----- | ------- |
| `Stop` | `/notify?view=s` | squints `> <` | finished, your turn |
| `PostToolUseFailure` | `/notify?alert=bad` | flashes red 3× | a tool call failed |
| `Notification` | `/notify?breathe=1` | backlight starts breathing | waiting for your approval / input |
| `UserPromptSubmit` | `/notify?breathe=0` | breathing stops | you replied |

Normal eyes mean it's working, or idle.

## Install

You need Mochi on the same network as your PC (STA mode, see README step 6) and its IP. The example uses `192.168.137.50`.

1. Open your user settings file. Windows: `%USERPROFILE%\.claude\settings.json`. macOS/Linux: `~/.claude/settings.json`.
2. Copy the `"hooks"` block from [`tools/claude-code-hooks.example.json`](../tools/claude-code-hooks.example.json) into it.
   - If the file has no `"hooks"` key yet, add the whole block.
   - If it already has hooks, add each event's entry to the existing array for that event. **Don't replace your file**.
3. If Mochi's IP isn't `192.168.137.50`, change it in all four commands.
4. Restart Claude Code (hooks load at startup).

✅ Ask Claude Code anything. When it finishes, Mochi squints.

To test without Claude Code:
```bash
curl.exe "http://192.168.137.50/notify?alert=bad"
```

## Why the commands look like that

```
curl -s -m 5 "http://.../notify?..." >/dev/null 2>&1 || true
```

- `-m 5`: give up after 5 s if Mochi is off.
- `|| true` and `"async": true`: if Mochi is unreachable, Claude Code neither waits nor reports a hook error.
- The `>/dev/null` syntax is bash. On Windows, Claude Code runs hooks through Git Bash, so it works as written.

## Ideas

Any `/notify` parameter works, see [api.md](api.md): `face=5` when tests pass, `msg=...` to type the last commit message, `alert=good` on `Stop`, etc.

## Remove

Delete the four Mochi entries (the ones containing `/notify`) from `settings.json`.
