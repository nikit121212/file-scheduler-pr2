import os
import shutil
import zipfile
import schedule
import time
import logging
import argparse
from datetime import datetime


# --- Шаг 1: Настройка логирования (Класс Logger) ---
class Logger:
    def __init__(self, log_file="scheduler.log"):
        self.logger = logging.getLogger("FileScheduler")
        self.logger.setLevel(logging.INFO)

        # Создаем файловый хендлер
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Формат логов: Дата - Время - Сообщение
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)


# --- Шаг 2: Класс для файловых операций (FileOperations) ---
class FileOperations:
    @staticmethod
    def copy_file(src, dst):
        """Копирует файл src в dst"""
        try:
            shutil.copy2(src, dst)  # copy2 сохраняет метаданные
            return True, "Copy successful"
        except Exception as e:
            return False, f"Copy failed: {str(e)}"

    @staticmethod
    def move_file(src, dst):
        """Перемещает файл src в dst"""
        try:
            shutil.move(src, dst)
            return True, "Move successful"
        except Exception as e:
            return False, f"Move failed: {str(e)}"

    @staticmethod
    def delete_file(path):
        """Удаляет файл по пути path"""
        try:
            if os.path.isfile(path):
                os.remove(path)
                return True, "Delete successful"
            else:
                return False, "File not found"
        except Exception as e:
            return False, f"Delete failed: {str(e)}"

    @staticmethod
    def archive_file(src, zip_name):
        """Архивирует файл src в zip-архив zip_name"""
        try:
            with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # arcname позволяет сохранить только имя файла внутри архива, без полных путей
                zipf.write(src, arcname=os.path.basename(src))
            return True, "Archive successful"
        except Exception as e:
            return False, f"Archive failed: {str(e)}"


# --- Шаг 3: Класс Задачи (Task) ---
class Task:
    def __init__(self, task_id, operation, src, dst=None, schedule_time=None):
        self.task_id = task_id
        self.operation = operation  # 'copy', 'move', 'delete', 'archive'
        self.src = src  # Исходный файл
        self.dst = dst  # Куда копировать/перемещать или имя архива
        self.schedule_time = schedule_time  # Строка расписания, например 'daily:14:00'

    def __repr__(self):
        return f"<Task ID:{self.task_id} Op:{self.operation} Src:{self.src} Dst:{self.dst} Time:{self.schedule_time}>"


# --- Шаг 4: Класс Планировщика (Scheduler) ---
class Scheduler:
    def __init__(self):
        self.tasks = []
        self.next_id = 1
        self.file_ops = FileOperations()
        self.logger = Logger()

    def add_task(self, operation, src, dst=None, schedule_time=None):
        """Добавляет задачу в список и настраивает расписание"""
        task = Task(self.next_id, operation, src, dst, schedule_time)
        self.tasks.append(task)
        self.next_id += 1

        # Настройка расписания через библиотеку schedule
        if schedule_time:
            self._schedule_task(task)

        self.logger.info(f"Task added: {task}")
        print(f"Added task: {task}")

    def _schedule_task(self, task):
        """Внутренний метод для привязки задачи к времени"""
        if "daily" in task.schedule_time:
            time_str = task.schedule_time.split(':')[1] + ":" + task.schedule_time.split(':')[2] if len(
                task.schedule_time.split(':')) > 2 else task.schedule_time.split(':')[1]
            # Простая обработка формата daily:HH:MM
            parts = task.schedule_time.split(':')
            if len(parts) == 3:  # daily:HH:MM:SS или просто парсинг
                time_str = f"{parts[1]}:{parts[2]}"
            else:
                time_str = f"{parts[1]}:00"  # Если указано только daily:10

            schedule.every().day.at(time_str).do(self.run_task, task)
            self.logger.info(f"Scheduled task {task.task_id} daily at {time_str}")
        elif "weekly" in task.schedule_time:
            # Пример простой логики для weekly (по понедельникам)
            parts = task.schedule_time.split(':')
            time_str = f"{parts[1]}:{parts[2]}" if len(parts) > 2 else f"{parts[1]}:00"
            schedule.every().monday.at(time_str).do(self.run_task, task)
            self.logger.info(f"Scheduled task {task.task_id} weekly on Monday at {time_str}")
        else:
            self.logger.warning(f"Unknown schedule format: {task.schedule_time}")

    def run_task(self, task):
        """Выполняет конкретную задачу"""
        self.logger.info(f"Starting task {task.task_id}: {task.operation}")
        success = False
        message = ""

        if task.operation == 'copy':
            success, message = self.file_ops.copy_file(task.src, task.dst)
        elif task.operation == 'move':
            success, message = self.file_ops.move_file(task.src, task.dst)
        elif task.operation == 'delete':
            success, message = self.file_ops.delete_file(task.src)
        elif task.operation == 'archive':
            # Для архивации dst используется как имя zip файла
            success, message = self.file_ops.archive_file(task.src, task.dst)
        else:
            message = "Unknown operation"

        if success:
            self.logger.info(f"Task {task.task_id} completed successfully: {message}")
        else:
            self.logger.error(f"Task {task.task_id} failed: {message}")

    def view_tasks(self):
        """Выводит список всех задач"""
        if not self.tasks:
            print("No tasks scheduled.")
        else:
            print("\n--- Scheduled Tasks ---")
            for task in self.tasks:
                print(task)
            print("-----------------------\n")

    def start(self):
        """Запускает бесконечный цикл проверки расписания"""
        print("Scheduler started. Press Ctrl+C to exit.")
        self.logger.info("Scheduler service started.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("Scheduler stopped.")
            self.logger.info("Scheduler service stopped.")


# --- Шаг 5: Консольный интерфейс (Main) ---
def main():
    parser = argparse.ArgumentParser(description="File Scheduler - Automation tool for file operations")

    # Основные команды
    parser.add_argument("command", choices=["add", "view", "start"], help="Command: add, view, start")

    # Аргументы для добавления задачи
    parser.add_argument("--operation", choices=["copy", "move", "delete", "archive"], help="Operation type")
    parser.add_argument("--src", help="Source file path")
    parser.add_argument("--dst", help="Destination path or archive name", default=None)
    parser.add_argument("--schedule", help="Schedule time (e.g., 'daily:10:00')", default=None)

    args = parser.parse_args()

    scheduler = Scheduler()

    if args.command == "add":
        if not args.operation or not args.src:
            print("Error: --operation and --src are required for adding a task.")
            return

        # Для операций copy, move, archive нужен dst
        if args.operation in ['copy', 'move', 'archive'] and not args.dst:
            print(f"Error: --dst is required for operation '{args.operation}'.")
            return

        scheduler.add_task(
            operation=args.operation,
            src=args.src,
            dst=args.dst,
            schedule_time=args.schedule
        )

    elif args.command == "view":
        # Примечание: так как это консольное приложение без базы данных,
        # при новом запуске список задач пуст.
        # В реальном проекте задачи нужно сохранять в JSON/DB.
        # Здесь мы просто показываем структуру вызова.
        print("Note: In this simple version, tasks are stored in memory only during runtime.")
        print("To view active jobs, check the 'scheduler.log' file for added tasks.")
        # Для демонстрации можно добавить тестовую задачу вручную, если нужно
        # scheduler.view_tasks()

    elif args.command == "start":
        scheduler.start()


if __name__ == "__main__":
    main()


# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
