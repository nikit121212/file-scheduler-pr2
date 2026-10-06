
# File Scheduler — Практическая работа №2

Файловый шедулер на Python для автоматизации операций с файлами по расписанию.

## Возможности
- Копирование файлов (`copy`)
- Перемещение файлов (`move`)
- Удаление файлов (`delete`)
- Архивирование в ZIP (`archive`)
- Расписание: `daily:HH:MM`, `weekly:HH:MM`
- Логирование всех операций в `scheduler.log`
- Консольный интерфейс (CLI)

## Установка
```bash
pip install schedule

# Добавить задачу на копирование каждый день в 10:00
python file_scheduler.py add --operation copy --src test.txt --dst backup/test.txt --schedule daily:10:00

# Добавить задачу на архивацию
python file_scheduler.py add --operation archive --src test.txt --dst backup.zip --schedule weekly:14:30

# Посмотреть задачи
python file_scheduler.py view

# Удалить задачу
python file_scheduler.py delete --task-id 1

# Запустить шедулер
python file_scheduler.py start

# file-scheduler-pr2
437c4a331642949db64b9ea5ee3503205b389e2f
