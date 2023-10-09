# api_rolls

svstl$ uvicorn main:app --reload
для запуска


примеры основных запросов
GET http://127.0.0.1:8000/coil/
POST http://127.0.0.1:8000/coil/
с телом
{
    "length": 222,
    "weight": 222.4,
}
DELETE http://127.0.0.1:8000/coil/2/

GET http://127.0.0.1:8000/coil/stats?start_date=2023-01-01&end_date=2023-12-31

GET http://127.0.0.1:8000/coil/?min_id=1&max_id=5
