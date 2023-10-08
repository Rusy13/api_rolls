from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import aiosqlite
from typing import Dict

app = FastAPI()

# Создаем модель Pydantic для создания рулона
class RollCreate(BaseModel):
    length: float
    weight: float

# Создаем модель Pydantic для рулона
class RollOut(BaseModel):
    id: int
    length: float
    weight: float
    date_added: str
    date_deletion: Optional[str] = None

# Модель для получения периода времени
class DateRange(BaseModel):
    start_date: str
    end_date: str

# Эта функция создает подключение к базе данных SQLite3
async def connect_db():
    try:
        conn = await aiosqlite.connect("db.sqlite3")
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error")




# Эта функция создает новый рулон
async def create_roll(conn, roll_data: RollCreate):
    async with conn.cursor() as cursor:
        await cursor.execute(
            "INSERT INTO rolls_roll (length, weight, date_added) VALUES (?, ?, ?)",
            (roll_data.length, roll_data.weight, datetime.now().strftime("%Y-%m-%d"))
        )
        await conn.commit()

        roll_id = cursor.lastrowid
        return roll_id
    




async def get_coil_stats(date_range):
    start_date = datetime.strptime(date_range.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(date_range.end_date, "%Y-%m-%d")

    conn = await connect_db()
    try:
        async with conn.cursor() as cursor:
            # Рассчитываем статистику по рулонам
            await cursor.execute(
                "SELECT COUNT(*) FROM rolls_roll WHERE date_added >= ? AND date_added <= ?",
                (start_date, end_date)
            )
            added_rolls_count = await cursor.fetchone()
            added_rolls_count = added_rolls_count[0] if added_rolls_count else 0

            await cursor.execute(
                "SELECT COUNT(*) FROM rolls_roll WHERE date_deletion >= ? AND date_deletion <= ?",
                (start_date, end_date)
            )
            deleted_rolls_count = await cursor.fetchone()
            deleted_rolls_count = deleted_rolls_count[0] if deleted_rolls_count else 0

            await cursor.execute(
                "SELECT AVG(length), AVG(weight) FROM rolls_roll WHERE date_added >= ? AND date_added <= ?",
                (start_date, end_date)
            )
            averages = await cursor.fetchone()

            await cursor.execute(
                "SELECT MAX(length), MIN(length), MAX(weight), MIN(weight) FROM rolls_roll WHERE date_added >= ? AND date_added <= ?",
                (start_date, end_date)
            )
            extrema = await cursor.fetchone()

            await cursor.execute(
                "SELECT SUM(weight) FROM rolls_roll WHERE date_added >= ? AND date_added <= ?",
                (start_date, end_date)
            )
            total_weight = await cursor.fetchone()
            total_weight = total_weight[0] if total_weight else 0

            await cursor.execute(
                "SELECT MAX(julianday(date_deletion) - julianday(date_added)) AS max_duration, MIN(julianday(date_deletion) - julianday(date_added)) AS min_duration FROM rolls_roll WHERE date_added >= ? AND date_added <= ? AND date_deletion IS NOT NULL",
                (start_date, end_date)
            )
            durations = await cursor.fetchone()

    finally:
        await conn.close()

    return {
        "added_rolls_count": added_rolls_count,
        "deleted_rolls_count": deleted_rolls_count,
        "average_length": averages[0],
        "average_weight": averages[1],
        "max_length": extrema[0],
        "min_length": extrema[1],
        "max_weight": extrema[2],
        "min_weight": extrema[3],
        "total_weight": total_weight,
        "max_duration": durations[0],
        "min_duration": durations[1]
    }







# Этот маршрут создает новый рулон
@app.post("/coil/", response_model=int)
async def create_roll_endpoint(roll_data: RollCreate):
    conn = await connect_db()
    try:
        roll_id = await create_roll(conn, roll_data)
        return roll_id
    finally:
        await conn.close()

# Этот маршрут удаляет рулон по его ID
@app.delete("/coil/{roll_id}", response_model=RollOut)
async def delete_roll(roll_id: int):
    conn = await connect_db()
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM rolls_roll WHERE id = ?",
                (roll_id,)
            )
            row = await cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Roll not found")
            
            roll_id, length, weight, date_added, date_deletion = row
            if not date_deletion:
                await cursor.execute(
                    "UPDATE rolls_roll SET date_deletion = ? WHERE id = ?",
                    (datetime.now().strftime("%Y-%m-%d"), roll_id)
                )
                await conn.commit()

            return RollOut(
                id=roll_id,
                length=length,
                weight=weight,
                date_added=date_added,
                date_deletion=date_deletion.strftime("%Y-%m-%d") if date_deletion else None
            )
    finally:
        await conn.close()

# Этот маршрут получает список рулонов с различными фильтрами
@app.get("/coil/", response_model=List[RollOut])
async def get_rolls(
    min_id: Optional[int] = Query(None, description="Minimum roll ID."),
    max_id: Optional[int] = Query(None, description="Maximum roll ID."),
    min_length: Optional[float] = Query(None, description="Minimum roll length."),
    max_length: Optional[float] = Query(None, description="Maximum roll length."),
    min_weight: Optional[float] = Query(None, description="Minimum roll weight."),
    max_weight: Optional[float] = Query(None, description="Maximum roll weight."),
    date_added_start: Optional[str] = Query(None, description="Start date for roll added."),
    date_added_end: Optional[str] = Query(None, description="End date for roll added."),
    date_deletion_start: Optional[str] = Query(None, description="Start date for roll deletion."),
    date_deletion_end: Optional[str] = Query(None, description="End date for roll deletion."),
):
    conn = await connect_db()
    try:
        filters = []
        params = []

        if min_id:
            filters.append("id >= ?")
            params.append(min_id)
        if max_id:
            filters.append("id <= ?")
            params.append(max_id)
        if min_length:
            filters.append("length >= ?")
            params.append(min_length)
        if max_length:
            filters.append("length <= ?")
            params.append(max_length)
        if min_weight:
            filters.append("weight >= ?")
            params.append(min_weight)
        if max_weight:
            filters.append("weight <= ?")
            params.append(max_weight)
        if date_added_start:
            filters.append("date_added >= ?")
            params.append(date_added_start)
        if date_added_end:
            filters.append("date_added <= ?")
            params.append(date_added_end)
        if date_deletion_start:
            filters.append("date_deletion >= ?")
            params.append(date_deletion_start)
        if date_deletion_end:
            filters.append("date_deletion <= ?")
            params.append(date_deletion_end)

        query = "SELECT * FROM rolls_roll"
        if filters:
            query += " WHERE " + " AND ".join(filters)

        async with conn.cursor() as cursor:
            await cursor.execute(query, tuple(params))
            rows = await cursor.fetchall()

        roll_list = []
        for row in rows:
            roll_id, length, weight, date_added, date_deletion = row
            # Проверяем тип date_deletion
            if isinstance(date_deletion, str):
                date_deletion_str = date_deletion
            else:
                date_deletion_str = date_deletion.strftime("%Y-%m-%d") if date_deletion else None
            roll_list.append(
                RollOut(
                    id=roll_id,
                    length=length,
                    weight=weight,
                    date_added=date_added,
                    date_deletion=date_deletion_str
                )
            )

        return roll_list
    finally:
        await conn.close()

# GET-запрос для получения статистики
@app.get("/coil/stats", response_model=dict)
async def get_coil_stats_endpoint(
    start_date: str = Query(..., description="Start date for the period."),
    end_date: str = Query(..., description="End date for the period.")
):
    date_range = DateRange(start_date=start_date, end_date=end_date)
    return await get_coil_stats(date_range)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
