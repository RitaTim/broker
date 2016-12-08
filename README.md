Проект демонстрирует несколько различный обработчиков на одно сообщение

Запуск worker'ов

bin/celery worker -A app_celery.analize -Q analize --purge
bin/celery worker -A app_celery.logger -Q logger --purge

Запуск task'а

bin/celery call -A app_celery --exchange=main --routing-key=task.* hello