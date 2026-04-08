# Beads issue: ЛР-04 — задача о назначениях

Текущая рабочая задача создана в Beads:

```bash
PATH="$HOME/.local/bin:$PATH" ~/.local/bin/bd show eor-egm
```

Если нужно создать аналогичную задачу вручную:

```bash
PATH="$HOME/.local/bin:$PATH" ~/.local/bin/bd create "ЛР-04: задача о назначениях" \
  --type task \
  --priority 2 \
  --description "Создать материалы ЛР-04 по assignment problem: теория, student notebooks, worked examples, TOC и solver-based verification через scipy.optimize.linear_sum_assignment и scipy.optimize.linprog."
```
