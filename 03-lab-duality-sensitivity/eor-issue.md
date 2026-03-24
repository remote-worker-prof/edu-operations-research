# Beads issues: ЛР-03 как полноценная опубликованная лабораторная

Текущая связанная работа заведена в Beads так:

```bash
PATH="$HOME/.local/bin:$PATH" ~/.local/bin/bd show eor-dis
PATH="$HOME/.local/bin:$PATH" ~/.local/bin/bd show eor-otf
```

Где:

- `eor-dis` — эпик на оформление ЛР-03 как полноценной опубликованной лабораторной;
- `eor-otf` — активная задача на разведение тем, навигации и публикации.

Если нужно создать аналогичную задачу заново:

```bash
PATH="$HOME/.local/bin:$PATH" ~/.local/bin/bd create "ЛР-03: оформить как полноценную опубликованную лабораторную" \
  --type epic \
  --priority 1 \
  --description "Сделать 03-lab-duality-sensitivity полноценной опубликованной ЛР-03, включить её в Jupyter Book и убрать прежнее roadmap-позиционирование из публичных точек входа." \
  --prefix eor-
```

```bash
PATH="$HOME/.local/bin:$PATH" ~/.local/bin/bd create "ЛР-03: развести темы и навигацию относительно ЛР-01, ЛР-02 и 01.1" \
  --type task \
  --priority 1 \
  --description "Обновить README, index, TOC и материалы ЛР-03 так, чтобы ЛР-03 была sensitivity-first лабораторной про публичный бюджет, а 01.1 оставался supplementary applied case." \
  --prefix eor-
```
