---
description: 현재 프로젝트의 파괴적 작업 gate를 제한 시간 동안 열거나 닫는다
argument-hint: "<on [minutes]|off|status>"
---

Run exactly this gate command and report its output:

```sh
node "$CLAUDE_PLUGIN_ROOT/scripts/gate-control.mjs" danger $ARGUMENTS
```

Do not perform any destructive operation as part of this command.
