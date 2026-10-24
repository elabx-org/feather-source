# elabx Feather source

Sideload elabx iOS apps with [Feather](https://github.com/khcrysalis/Feather):
add this source, then sign and install with your own certificate.

```
https://raw.githubusercontent.com/elabx-org/feather-source/main/source.json
```

| App | From |
|---|---|
| Agent-OS | [elabx-org/agent-os](https://github.com/elabx-org/agent-os) `ios/`, releases `ios-build-*` |

`source.json` is rebuilt every 15 minutes (and on demand from the Actions tab)
from each app's newest releases. To add an app, add it to `apps.json`.
