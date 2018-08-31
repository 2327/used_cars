** Учебный проект "Оценка автомобиля" **

Проект может быть запущен в docker и вне докера. 
Для запуска в докере выполните команду:

```
docker-compose up
```

Для запуска в фоне добавьте ключ -d:

```
docker-compose up
```


Для запуска без докера рекомендуется воспользоваться virtualenv:
```
virtualenv <путь_к_директории_проекта>
cd <путь_к_директории_проекта>
source bin/activate
pip install --upgrade pip
pip install -r requirements.txt
./run.py
```
