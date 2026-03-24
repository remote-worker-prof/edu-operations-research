# Beads issue: ЛР-02 — транспортная задача

Текущая рабочая задача уже создана в Beads:

```bash
PATH="$HOME/.local/bin:$PATH" ~/.local/bin/bd show eor-prr.2
```

Если нужно заново создать аналогичную задачу вручную:

```bash
PATH="$HOME/.local/bin:$PATH" ~/.local/bin/bd create "ЛР-02: транспортная задача" \
  --type task \
  --priority 1 \
  --description "Создать материалы ЛР-02 по транспортной задаче: теория, основной ноутбук, самостоятельные варианты, требования к отчёту и solver-based verification через scipy.optimize.linprog." \
  --prefix eor-
```
