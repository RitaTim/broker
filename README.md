Проект осуществляет взаимодействие между источниками.


Запуск worker'ов

для тасков-обработчиков:
    bin/celery worker -A app_celery -Q receiver --purge
для логирования поступающих сигналов:
    bin/celery worker -A app_celery -Q logger --purge
для отдельных тасков, которые мониторят выполнение обработчиков
    bin/celery worker -A app_celery -Q control --purge

Запуск task'а

bin/celery call -A app_celery --exchange=main --routing-key=logger.* send_signal

Примечания.
1. При изменении имени класса-источника, происходит полное удаление старого
источника из базы и добавление нового. Не забудте сохранить параметры
init_params старого источника и добавить такие же в новый