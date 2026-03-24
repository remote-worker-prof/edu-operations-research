# edu-operations-research

Публичный учебный репозиторий по исследованию операций с упором на понятные лабораторные работы, воспроизводимые ноутбуки и аккуратную публикацию материалов через GitHub Pages.

## Что здесь есть

- лабораторные работы в numbered-папках, которые остаются основным источником правды;
- подробные теоретические заметки на русском языке;
- Jupyter ноутбуки с пошаговыми объяснениями и проверкой решений через Python;
- отдельный публикуемый сайт, который повторяет структуру репозитория и не скрывает исходные материалы.

## Быстрый старт локально

```bash
uv sync --group authoring --group docs
uv run python scripts/validate_notebooks.py
uv run jupyter nbconvert --to notebook --execute --inplace 02-lab-transport-problem/lab_02_transport_problem.ipynb
uv run jupyter nbconvert --to notebook --execute --inplace 03-lab-duality-sensitivity/lab_03_duality_sensitivity.ipynb
uv run jupyter-book build . --warningiserror
```

После сборки сайт лежит в `_build/html/index.html`.

## Навигация

- Репозиторий: `https://github.com/remote-worker-prof/edu-operations-research`
- Сайт: `https://remote-worker-prof.github.io/edu-operations-research/`

### Опубликованные лабораторные

| Статус | Раздел | Исходники | Страница |
| --- | --- | --- | --- |
| published | ЛР-01. Теория линейного программирования | [source](01-lab-essentials/theory_linear_programming_for_beginners.md) | [page](https://remote-worker-prof.github.io/edu-operations-research/01-lab-essentials/theory_linear_programming_for_beginners.html) |
| published | ЛР-01. Основной ноутбук | [source](01-lab-essentials/lab_01_linear_programming.ipynb) | [page](https://remote-worker-prof.github.io/edu-operations-research/01-lab-essentials/lab_01_linear_programming.html) |
| published | ЛР-01. Самостоятельная часть | [source](01-lab-essentials/lab_01_part2_independent.ipynb) | [page](https://remote-worker-prof.github.io/edu-operations-research/01-lab-essentials/lab_01_part2_independent.html) |
| published | ЛР-01.1. Дополнительный прикладной кейс (supplementary applied case): fair-price audit | [source](01-lab-essentials/lab_01.1_corruption_detection_primal_dual.ipynb) | [page](https://remote-worker-prof.github.io/edu-operations-research/01-lab-essentials/lab_01.1_corruption_detection_primal_dual.html) |
| published | ЛР-02. Транспортная задача: обзор | [source](02-lab-transport-problem/README.md) | [page](https://remote-worker-prof.github.io/edu-operations-research/02-lab-transport-problem/README.html) |
| published | ЛР-02. Теория | [source](02-lab-transport-problem/theory_transport_problem.md) | [page](https://remote-worker-prof.github.io/edu-operations-research/02-lab-transport-problem/theory_transport_problem.html) |
| published | ЛР-02. Основной ноутбук | [source](02-lab-transport-problem/lab_02_transport_problem.ipynb) | [page](https://remote-worker-prof.github.io/edu-operations-research/02-lab-transport-problem/lab_02_transport_problem.html) |
| published | ЛР-02. Самостоятельные варианты | [source](02-lab-transport-problem/lab_02_part2_variants.ipynb) | [page](https://remote-worker-prof.github.io/edu-operations-research/02-lab-transport-problem/lab_02_part2_variants.html) |
| published | ЛР-03. Двойственность и анализ чувствительности: обзор | [source](03-lab-duality-sensitivity/README.md) | [page](https://remote-worker-prof.github.io/edu-operations-research/03-lab-duality-sensitivity/README.html) |
| published | ЛР-03. Теория | [source](03-lab-duality-sensitivity/theory_03_duality_sensitivity.md) | [page](https://remote-worker-prof.github.io/edu-operations-research/03-lab-duality-sensitivity/theory_03_duality_sensitivity.html) |
| published | ЛР-03. Основной ноутбук | [source](03-lab-duality-sensitivity/lab_03_duality_sensitivity.ipynb) | [page](https://remote-worker-prof.github.io/edu-operations-research/03-lab-duality-sensitivity/lab_03_duality_sensitivity.html) |
| published | ЛР-03. Самостоятельная часть | [source](03-lab-duality-sensitivity/lab_03_part2_independent.ipynb) | [page](https://remote-worker-prof.github.io/edu-operations-research/03-lab-duality-sensitivity/lab_03_part2_independent.html) |

## Как темы разведены

- **ЛР-01**: базовое ЛП, геометрия, канонизация, первый `linprog` и первое знакомство с двойственностью.
- **ЛР-01.1**: дополнительный прикладной кейс (supplementary applied case) по госзакупкам, fair-price audit и primal-dual интерпретации.
- **ЛР-02**: транспортная задача, баланс, фиктивные узлы и матрица перевозок.
- **ЛР-03**: лабораторная с фокусом на анализ чувствительности (sensitivity-first): теневые цены (shadow prices), активные ограничения (binding), запас ресурса (slack) и сценарные изменения параметров.

### Roadmap

- Следующие лабораторные и прикладные кейсы попадают в публикацию только после отдельной проверки структуры, навигации и воспроизводимости ноутбуков.

## Структура проекта

- `01-lab-essentials/` — завершённые материалы ЛР-01 и дополнительного прикладного кейса `01.1`.
- `02-lab-transport-problem/` — новая ЛР-02 по транспортной задаче.
- `03-lab-duality-sensitivity/` — полноценная ЛР-03 по двойственности и анализу чувствительности.
- `.github/workflows/` — CI и публикация GitHub Pages.
- `scripts/` — локальные утилиты проверки ноутбуков.
- `PROJECT_INIT_PROMPT.md` — проектный prompt для инициализации и workflow-ограничений.
- `agents-issue-workflow.cncf.yaml` — формула issue-driven процесса.

## Права на материалы

Репозиторий открыт для просмотра, но не является open-source проектом.

- Любое копирование, адаптация, переработка, распространение, использование в курсах, корпоративных программах, публикациях и коммерческих или некоммерческих продуктах требует личного разрешения владельца.
- Это правило относится ко всем ноутбукам, markdown-материалам, коду, схемам, таблицам, данным и сгенерированному сайту.
- Подробности зафиксированы в [LICENSE.md](LICENSE.md) и [PERMISSIONS.md](PERMISSIONS.md).

Если вам нужно разрешение на использование материалов, связывайтесь с владельцем репозитория через GitHub-профиль `remote-worker-prof`.
