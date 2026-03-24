# edu-operations-research

Публичный учебный репозиторий по исследованию операций с упором на понятные лабораторные работы, разделение student notebooks и worked examples и аккуратную публикацию материалов через GitHub Pages.

## Как теперь устроен курс

- В корне каждой лаборатории лежат только `student notebooks`.
- В `examples-civil/` и `examples-military/` лежат полностью разобранные `worked examples`.
- Сначала студент проходит теорию и свой student notebook, и только потом смотрит solved examples.
- Бывшая линия `01.1` больше не живёт как отдельный раздел: её полезное содержимое встроено в гражданские примеры ЛР-01.

## Быстрый старт локально

```bash
uv sync --group authoring --group docs
uv run python scripts/validate_notebooks.py
uv run python scripts/check_notebook_contracts.py
uv run python scripts/execute_worked_examples.py
uv run jupyter-book build . --warningiserror
```

После сборки сайт лежит в `_build/html/index.html`.

## Как читать материалы

### ЛР-01. Основы линейного программирования

- Теория: `01-lab-essentials/theory_linear_programming_for_beginners.md`
- Student notebooks:
  - `lab_01_student_civil_01.ipynb` — муниципальная пекарня
  - `lab_01_student_civil_02.ipynb` — городской ремонтный участок
  - `lab_01_student_military_01.ipynb` — комплектование полевых рационов
  - `lab_01_student_military_02.ipynb` — ремонтно-обслуживающий склад
- Worked examples:
  - `examples-civil/` — 3 разобранных гражданских примера
  - `examples-military/` — 3 разобранных военных примера

### ЛР-02. Транспортная задача

- Теория: `02-lab-transport-problem/theory_transport_problem.md`
- Student notebooks:
  - `lab_02_student_civil_01.ipynb` — лекарства в районные больницы
  - `lab_02_student_civil_02.ipynb` — школьное питание
  - `lab_02_student_military_01.ipynb` — топливо для частей
  - `lab_02_student_military_02.ipynb` — запчасти на ремонтные базы
- Worked examples:
  - `examples-civil/` — 3 разобранных гражданских транспортных примера
  - `examples-military/` — 3 разобранных военных транспортных примера

### ЛР-03. Двойственность и анализ чувствительности

- Теория: `03-lab-duality-sensitivity/theory_03_duality_sensitivity.md`
- Student notebooks:
  - `lab_03_student_civil_01.ipynb` — муниципальное здравоохранение
  - `lab_03_student_civil_02.ipynb` — социальная защита в зимний период
  - `lab_03_student_military_01.ipynb` — бюджет логистической готовности
  - `lab_03_student_military_02.ipynb` — модернизация ремонтной базы
- Worked examples:
  - `examples-civil/` — 3 разобранных гражданских sensitivity-примера
  - `examples-military/` — 3 разобранных военных sensitivity-примера

## Правила публикации

- `student notebooks` публикуются раньше solved examples и остаются главным маршрутом для обучения.
- `worked examples` тоже видны в основном TOC, но идут после student notebooks.
- Контракт по ролям файлов простой:
  - `_student_` в имени = notebook для заполнения студентом
  - `_example_` в имени = полностью разобранный notebook

## Права на материалы

Репозиторий открыт для просмотра, но не является open-source проектом.

- Любое копирование, адаптация, переработка, распространение, использование в курсах, корпоративных программах, публикациях и коммерческих или некоммерческих продуктах требует личного разрешения владельца.
- Это правило относится ко всем ноутбукам, markdown-материалам, коду, схемам, таблицам, данным и сгенерированному сайту.
- Подробности зафиксированы в [LICENSE.md](LICENSE.md) и [PERMISSIONS.md](PERMISSIONS.md).
