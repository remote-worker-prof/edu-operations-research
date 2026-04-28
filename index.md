# edu-operations-research

Добро пожаловать в учебный проект по исследованию операций.

Теперь курс устроен в логике **student first, examples second**:

- в корне каждой лаборатории лежат только `student notebooks`;
- в подпапках `examples-civil/` и `examples-military/` лежат полностью разобранные `worked examples`;
- сначала студент решает свой notebook, а потом при необходимости сверяется с разобранными примерами.

## Как пользоваться проектом

1. Идите по левой навигации сверху вниз.
2. Сначала читайте теорию.
3. Затем открывайте student notebook своей лабораторной.
4. Worked examples используйте как образец структуры решения и интерпретации.

## Текущая структура курса

- **ЛР-01**: основы линейного программирования, геометрия, вершины, канонизация и первый `linprog`.
- **ЛР-02**: транспортная задача, баланс, фиктивные узлы и векторизация маршрутов.
- **ЛР-03**: двойственность, активные ограничения, запас ресурса, теневая цена и анализ чувствительности.
- **ЛР-04**: задача о назначениях, взаимно-однозначные соответствия и проверка через `linear_sum_assignment` и `linprog`.

## Что публикуется

- 4 student notebooks на каждую лабораторную: `2 civil + 2 military`;
- 6 worked examples на каждую лабораторную: `3 civil + 3 military`;
- solved examples видны в main TOC, но стоят после student notebooks.

## Локальная сборка

```bash
uv sync --group authoring --group docs
uv run python scripts/validate_notebooks.py
uv run python scripts/check_notebook_contracts.py
uv run python scripts/check_lab02_transport_contract.py
uv run python scripts/execute_worked_examples.py
uv run jupyter-book clean . --all
uv run jupyter-book build . --all --warningiserror
```

Для локального smoke-test и Playwright-проверок используйте именно clean build, чтобы `_build/html` не содержал stale-страницы от удалённых notebook-ов.

## Важно о правах

Материалы доступны для чтения, но не для свободного переиспользования.

Подробные ограничения и процедура запроса разрешения описаны в `LICENSE.md` и `PERMISSIONS.md`.
