---
description: 현재 프로젝트의 NAS·원격 접속 gate를 제한 시간 동안 열거나 닫는다
argument-hint: "<on [minutes]|off|status>"
---

Run exactly this gate command and report its output:

```sh
node "$CLAUDE_PLUGIN_ROOT/scripts/gate-control.mjs" nas $ARGUMENTS
```

Do not perform any NAS or remote operation as part of this command.
