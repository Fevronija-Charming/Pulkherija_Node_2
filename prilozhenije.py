import asyncio
from dataclasses import field
from io import BytesIO
import pandas as pd
from colorama import *
from fastapi import FastAPI, UploadFile, File
from fastapi import HTTPException
from fastapi import Depends
from typing import Annotated
import uvicorn
from openpyxl.styles.builtins import title
from openpyxl.worksheet.table import TableColumn
from pydantic import BaseModel, Field, ValidationError
from dotenv import find_dotenv, load_dotenv
import os
from tokenize import String
load_dotenv(find_dotenv())
#заяц включен
from faststream.rabbit.fastapi import RabbitBroker, RabbitRouter
broker = RabbitBroker(url=os.getenv("CLOUDAMQP_URL"))
router=RabbitRouter(url=os.getenv("CLOUDAMQP_URL"))
app = FastAPI()
#перенос тяжелой задачи в фон
from fastapi import BackgroundTasks
async def vstavka_platka(soobshenije,platok_predstav):
    session = session_factory()
    query = select(Platoky).where(Platoky.Название==platok_predstav[1])
    result = await session.execute(query)
    unikalnost_platka = result.scalar_one_or_none()
    if unikalnost_platka is None:
        session = session_factory()
        query2 = select(Platoky).where(Platoky.id==int(platok_predstav[0]))
        result2 = await session.execute(query2)
        unikalnost_id = result2.scalar_one_or_none()
        if unikalnost_id is None:
            try:
                platoch_eksemp = Platoky(id=int(platok_predstav[0]), Название=platok_predstav[1],
                Автор=platok_predstav[2], Колорит_1=platok_predstav[3],Колорит_2=platok_predstav[4],
                Колорит_3=platok_predstav[5],Колорит_4=platok_predstav[6], Колорит_5=platok_predstav[7],
                Узор_темени=platok_predstav[8],Узор_сердцевины=platok_predstav[9], Узор_сторон=platok_predstav[10],
                Узор_углов=platok_predstav[11],Узор_края=platok_predstav[12], Цветы_Орнамент=platok_predstav[13],
                Изображенный_Цветок_1=platok_predstav[14],Изображенный_Цветок_2=platok_predstav[15],
                Изображенный_Цветок_3=platok_predstav[16],Изображенный_Цветок_4=platok_predstav[17],
                Изображенный_Цветок_5=platok_predstav[18],Размер_Платка=platok_predstav[19],
                Материал_Платка=platok_predstav[20],Материал_Бахромы=platok_predstav[21])
                session = session_factory()
                session.add(platoch_eksemp)
                await session.commit()
                await session.close()
                try:
                    await router.broker.publish(message="Добавлен новый платок", queue="PLATOKY")
                    await router.broker.publish(message=f"{soobshenije}", queue="PLATOKY")
                    return soobshenije, components.FireEvent(event=GoToEvent(url="/gamajun/results"))
                except:
                    raise HTTPException(status_code=500, detail="Проблема с брокером")
            except:
                raise HTTPException(status_code=500, detail="Проблема с базой данных")
        else:
            async with broker:
                await broker.publish(message="Ошибка при вставке платка", queue="PLATOKY")
                await broker.publish(message="Артикул платка занят", queue="PLATOKY")
                return None
    else:
        async with broker:
            await broker.publish(message="Ошибка при вставке платка", queue="PLATOKY")
            await broker.publish(message="Такой платок уже есть", queue="PLATOKY")
            return None
from fastapi import Form, UploadFile
#работа с базой данных
from sqlalchemy import  DateTime, String, Float, Column, Integer, func,Text
from sqlalchemy import  select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from psycopg2.errors import *
engine = create_async_engine(os.getenv("DBURL"),echo=True,max_overflow=5,pool_size=5)
session_factory = async_sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False,autoflush=True)
class Base(DeclarativeBase):
    pass
class Platoky(Base):
    __tablename__="ПППЛАТКИ"
    id: Mapped[int]=mapped_column(primary_key=True, autoincrement=True, nullable=False)
    Название: Mapped[str]=mapped_column(String(128), nullable=False)
    Автор: Mapped[str]=mapped_column(String(128), nullable=False)
    Колорит_1: Mapped[str]=mapped_column(String(128), nullable=False)
    Колорит_2: Mapped[str] = mapped_column(String(128), nullable=False)
    Колорит_3: Mapped[str] = mapped_column(String(128), nullable=False)
    Колорит_4: Mapped[str] = mapped_column(String(128), nullable=False)
    Колорит_5: Mapped[str] = mapped_column(String(128), nullable=False)
    Узор_темени: Mapped[str] = mapped_column(String(128), nullable=False)
    Узор_сердцевины: Mapped[str] = mapped_column(String(128), nullable=False)
    Узор_сторон: Mapped[str] = mapped_column(String(128), nullable=False)
    Узор_углов: Mapped[str] = mapped_column(String(128), nullable=False)
    Узор_края: Mapped[str] = mapped_column(String(128), nullable=False)
    Цветы_Орнамент: Mapped[str] = mapped_column(String(128), nullable=False)
    Изображенный_Цветок_1: Mapped[str] = mapped_column(String(128), nullable=False)
    Изображенный_Цветок_2: Mapped[str] = mapped_column(String(128), nullable=False)
    Изображенный_Цветок_3: Mapped[str] = mapped_column(String(128), nullable=False)
    Изображенный_Цветок_4: Mapped[str] = mapped_column(String(128), nullable=False)
    Изображенный_Цветок_5: Mapped[str] = mapped_column(String(128), nullable=False)
    Размер_Платка: Mapped[str]=mapped_column(String(128), nullable=False)
    Материал_Платка: Mapped[str]=mapped_column(String(128), nullable=False)
    Материал_Бахромы: Mapped[str]=mapped_column(String(128), nullable=False)
    # для проверки '''INSERT INTO ПППЛАТКИ (id, Название, Автор, Колорит_1, Колорит_2, Колорит_3,
    # Колорит_4, Колорит_5, Узор_темени, Узор_сердцевины, Узор_сторон, Узор_углов, Узор_края,
    # Цветы_Орнамент, Изображенный_Цветок_1, Изображенный_Цветок_2, Изображенный_Цветок_3,
    # Изображенный_Цветок_4, Изображенный_Цветок_5, Размер_Платка, Материал_Платка, Материал_Бахромы)'
class Symboly(Base):
    __tablename__="Значение_Символов_Орнамента"
    id: Mapped[int]=mapped_column(primary_key=True, autoincrement=True, nullable=False)
    Название_Символа: Mapped[str]=mapped_column(String(32), nullable=False)
    Значение_Символа: Mapped[str]=mapped_column(Text, nullable=False)
    Встречается_На_Платках: Mapped[str]=mapped_column(Text, nullable=False)
    Ассоциативная_Иллюстрация_1: Mapped[str] = mapped_column(String(128), nullable=False)
    Ассоциативная_Иллюстрация_2: Mapped[str] = mapped_column(String(128), nullable=False)
    Символ_На_Платке_1: Mapped[str] = mapped_column(String(128), nullable=False)
    Символ_На_Платке_2: Mapped[str] = mapped_column(String(128), nullable=False)
    Символ_На_Платке_3: Mapped[str] = mapped_column(String(128), nullable=False)
    Символ_На_Платке_4: Mapped[str] = mapped_column(String(128), nullable=False)
    Символ_На_Платке_5: Mapped[str] = mapped_column(String(128), nullable=False)
class Banda(Base):
    __tablename__="Платочная_Банда"
    id: Mapped[int]=mapped_column(primary_key=True, autoincrement=True, nullable=False)
    Гражданское_Имя: Mapped[str]=mapped_column(String(128), nullable=False)
    Творческий_Псевдоним: Mapped[str]=mapped_column(String(128), nullable=False)
    Описание_Творческой_Деятельности: Mapped[str]=mapped_column(Text, nullable=False)
    Связь_Творчества_С_Павлопосадскими_Платками: Mapped[str] = mapped_column(Text, nullable=False)
    Ссылка_На_Инстаграм: Mapped[str] = mapped_column(String(128), nullable=False)
    Ссылка_На_ВК: Mapped[str] = mapped_column(String(128), nullable=False)
    Ссылка_На_Ютуб: Mapped[str] = mapped_column(String(128), nullable=False)
    Ссылка_На_Фейсбук: Mapped[str] = mapped_column(String(128), nullable=False)
    Ссылка_На_Телеграм: Mapped[str] = mapped_column(String(128), nullable=False)
    Ссылка_На_Одноклассники: Mapped[str] = mapped_column(String(128), nullable=False)
    Ссылка_На_Яндекс_Дзен: Mapped[str] = mapped_column(String(128), nullable=False)
    Ссылка_На_Сайт: Mapped[str] = mapped_column(String(128), nullable=False)
    Адрес_Деятельности: Mapped[str] = mapped_column(String(128), nullable=False)
    # '''CREATE table Платочная_Банда (id BIGINT NOT NULL PRIMARY KEY, Гражданское_Имя VARCHAR(128) NOT NULL,
    # Творческий_Псевдоним VARCHAR(128) NOT NULL, Описание_Творческой_Деятельности TEXT NOT NULL,
    # Связь_Творчества_С_Павлопосадскими_Платками TEXT NOT NULL, Ссылка_На_Инстаграм VARCHAR(128) NOT NULL,
    # Ссылка_На_ВК VARCHAR(128) NOT NULL, Ссылка_На_Ютуб VARCHAR(128) NOT NULL, Ссылка_На_Фейсбук VARCHAR(128) NOT NULL,
    # Ссылка_На_Телеграм VARCHAR(128) NOT NULL, Ссылка_На_Одноклассники VARCHAR(128) NOT NULL,
    # Ссылка_На_Яндекс_Дзен VARCHAR(128) NOT NULL, Ссылка_на_сайт VARCHAR(128) NOT NULL,
    # Адрес_Деятельности VARCHAR(128) NOT NULL)'''
class Platok_Schema(BaseModel):
    id: int
    Название_Платка: str = Field(min_length=5, max_length=50)
    Автор_Платка: str = Field(min_length=5, max_length=50)
    Колорит_1: str= Field(min_length=3, max_length=50)
    Колорит_2: str= Field(min_length=3, max_length=50)
    Колорит_3: str= Field(min_length=3, max_length=50)
    Колорит_4: str= Field(min_length=3, max_length=50)
    Колорит_5: str= Field(min_length=3, max_length=50)
    Узор_Темени: str= Field(min_length=3, max_length=50)
    Узор_Сердцевины: str= Field(min_length=3, max_length=50)
    Узор_Сторон: str= Field(min_length=3, max_length=50)
    Узор_Углов: str= Field(min_length=3, max_length=50)
    Узор_Края: str= Field(min_length=3, max_length=50)
    Цветы_Орнамент: str= Field(min_length=3, max_length=50)
    Изображённый_Цветок_1: str= Field(min_length=3, max_length=50)
    Изображённый_Цветок_2: str= Field(min_length=3, max_length=50)
    Изображённый_Цветок_3: str= Field(min_length=3, max_length=50)
    Изображённый_Цветок_4: str= Field(min_length=3, max_length=50)
    Изображённый_Цветок_5: str= Field(min_length=3, max_length=50)
    Размер_Платка: str= Field(min_length=3, max_length=50)
    Материал_Платка: str= Field(min_length=3, max_length=50)
    Материал_Бахромы: str= Field(min_length=3, max_length=50)
class Symbol_Schema(BaseModel):
    id: int
    Название_Символа: str = Field(min_length=3, max_length=32)
    Значение_Символа: str = Field(min_length=5, max_length=1000)
    Встречается_На_Платках: str = Field(min_length=5, max_length=200)
    Ассоциативная_Иллюстрация_1: str = Field(min_length=83, max_length=85)
    Ассоциативная_Иллюстрация_2: str= Field(min_length=83, max_length=85)
    Символ_На_Платке_1: str= Field(min_length=83, max_length=85)
    Символ_На_Платке_2: str = Field(min_length=83, max_length=85)
    Символ_На_Платке_3: str = Field(min_length=83, max_length=85)
    Символ_На_Платке_4: str = Field(min_length=83, max_length=85)
    Символ_На_Платке_5: str = Field(min_length=83, max_length=85)
class Banda_Schema(BaseModel):
    id: int
    Гражданское_Имя: str = Field(min_length=5, max_length=32)
    Творческий_Псевдоним: str = Field(min_length=5, max_length=32)
    Описание_Творческой_Деятельности: str = Field(min_length=5, max_length=2000)
    Связь_Творчества_С_Павлопосадскими_Платками: str = Field(min_length=5, max_length=2000)
    Ссылка_На_Инстаграм: str= Field(min_length=5, max_length=100)
    Ссылка_На_ВК: str= Field(min_length=5, max_length=75)
    Ссылка_На_Ютуб: str = Field(min_length=5, max_length=75)
    Ссылка_На_Телеграм: str = Field(min_length=5, max_length=75)
    Ссылка_На_Фейсбук: str = Field(min_length=5, max_length=75)
    Ссылка_На_Одноклассники: str = Field(min_length=5, max_length=75)
    Ссылка_На_Яндекс_Дзен: str = Field(min_length=5, max_length=75)
    Ссылка_На_Сайт: str = Field(min_length=5, max_length=75)
    Адрес_Деятельности: str = Field(min_length=5, max_length=75)
#@app.post("/symboly", summary="Platok", tags=["Symboli"])
@router.post("/symboly", summary="Platok",tags=["Symboli"])
async def create_tradicii(symbol: Annotated[Symbol_Schema, Depends()]):
    try:
        symbol_eksemp = Symboly(id=symbol.id,Название_Символа=symbol.Название_Символа,
            Значение_Символа=symbol.Значение_Символа,
            Встречается_На_Платках=symbol.Встречается_На_Платках,
            Ассоциативная_Иллюстрация_1=symbol.Ассоциативная_Иллюстрация_1,
            Ассоциативная_Иллюстрация_2=symbol.Ассоциативная_Иллюстрация_2,
            Символ_На_Платке_1=symbol.Символ_На_Платке_1, Символ_На_Платке_2=symbol.Символ_На_Платке_2,
            Символ_На_Платке_3=symbol.Символ_На_Платке_3, Символ_На_Платке_4=symbol.Символ_На_Платке_4,
            Символ_На_Платке_5=symbol.Символ_На_Платке_5)
        session = session_factory()
        session.add(symbol_eksemp)
        await session.commit()
        await session.close()
        #заяц_включён
        try:
            await router.broker.publish(message=f"{symbol}", queue="PLATOKY")
            return symbol
        except:
            raise HTTPException(status_code=500, detail="Проблема с брокером")
    except:
        raise HTTPException(status_code=500, detail="Проблема с базой данных")

@app.get("/root", summary="root",tags=["DEBUG"])
def root():
    return {"message": "Здарова, начальник!!!"}
#ВВОД СТАРОГО ОБРАЗЦА С PYDANTIC БЕЗ ЗАВИСИМОСТЕЙ
#@app.post("/platoky_dict2", summary="Platok",tags=["Platok"])
#async def create_platok_dict(id: int,avtor_platka: str,nazvanije_platka: str,kolorit_1: str,kolorit_2: str,kolorit_3: str,
#kolorit_4: str, kolorit_5: str, uzor_temeni: str, uzor_serdceviny: str, uzor_storon: str,uzor_uglov: str,
#uzor_kraja: str, cvety_ornament: str, izobrazheniy_cvetok_1: str, izobrazheniy_cvetok_2: str, izobrazheniy_cvetok_3: str,
#izobrazheniy_cvetok_4: str, izobrazheniy_cvetok_5: str, razmer_platka: str, material_platka: str, material_bahromi: str):
#peremycka="; ;"
#soobshenije0=[]
#platok_s_api_data = {}
#platok_s_api_data["id"] = id
#soobshenije1 =  soobshenije0 + id
#platok_s_api_data["avtor_platka"] = avtor_platka
#soobshenije2 = soobshenije1 + peremycka + avtor_platka
#platok_s_api_data["nazvanije_platka"] = nazvanije_platka
#soobshenije3 = soobshenije2 + peremycka + nazvanije_platka
#platok_s_api_data["kolorit_1"] = kolorit_1
#soobshenije4 = soobshenije3 + peremycka + kolorit_1
#platok_s_api_data["kolorit_2"] = kolorit_2
#soobshenije5 = soobshenije4 + peremycka + kolorit_2
#platok_s_api_data["kolorit_3"] = kolorit_3
#soobshenije6= soobshenije5 + peremycka + kolorit_3
#platok_s_api_data["kolorit_4"] = kolorit_4
#soobshenije7 = soobshenije6 + peremycka + kolorit_4
#platok_s_api_data["kolorit_5"] = kolorit_5
#soobshenije8 = soobshenije7 + peremycka + kolorit_5
#platok_s_api_data["uzor_temeni"] = uzor_temeni
#soobhsenije9 = soobshenije8 + peremycka + uzor_temeni
#platok_s_api_data["uzor_serdceviny"] = uzor_serdceviny
#soobhsenije10=soobhsenije9 + peremycka + uzor_serdceviny
#platok_s_api_data["uzor_storon"] = uzor_storon
#soobhsenije11=soobhsenije10 + peremycka + uzor_storon
#platok_s_api_data["uzor_uglov"] = uzor_uglov
#soobshenije12=soobhsenije11 + peremycka + uzor_uglov
#platok_s_api_data["uzor_kraja"] = uzor_kraja
#soobshenije13=soobshenije12 + peremycka + uzor_kraja
#platok_s_api_data["cvety_ornament"] = cvety_ornament
#soobshenije14=soobshenije13+peremycka + cvety_ornament
#platok_s_api_data["izobrazheniy_cvetok_1"] = izobrazheniy_cvetok_1
#soobshenije15=soobshenije14 + peremycka + izobrazheniy_cvetok_1
#platok_s_api_data["izobrazheniy_cvetok_2"] = izobrazheniy_cvetok_2
#soobshenije16 = soobshenije15 + peremycka + izobrazheniy_cvetok_2
#platok_s_api_data["izobrazheniy_cvetok_3"] = izobrazheniy_cvetok_3
#soobshenije17 = soobshenije16 + peremycka + izobrazheniy_cvetok_3
#platok_s_api_data["izobrazheniy_cvetok_4"] = izobrazheniy_cvetok_4
#soobshenije18 = soobshenije17 + peremycka + izobrazheniy_cvetok_4
#platok_s_api_data["izobrazheniy_cvetok_5"] = izobrazheniy_cvetok_5
#soobshenije19 = soobshenije18 + peremycka + izobrazheniy_cvetok_5
#platok_s_api_data["razmer_platka"] = razmer_platka
#soobshenije20= soobshenije19 + peremycka + razmer_platka
#platok_s_api_data["material_platka"] = material_platka
#soobshenije21=soobshenije20 + peremycka + material_platka
#platok_s_api_data["material_bahromi"] = material_bahromi
#soobshenije22=soobshenije21 + peremycka + material_bahromi
#try:
#platok_kontroll = Platok_Schema(**platok_s_api_data)
#except:
#raise HTTPException(status_code=422, detail="Данные не прошли валидацию")
#try:
#platoch_eksemp = Platoky(id=platok_kontroll.id,Название=platok_kontroll.nazvanije_platka,
#Автор=platok_kontroll.avtor_platka, Колорит_1=platok_kontroll.kolorit_1, Колорит_2=platok_kontroll.kolorit_2,
#Колорит_3=platok_kontroll.kolorit_3, Колорит_4=platok_kontroll.kolorit_4, Колорит_5=platok_kontroll.kolorit_5,
#Узор_темени=platok_kontroll.uzor_temeni,
#Узор_сердцевины=platok_kontroll.uzor_serdceviny,
#Узор_сторон=platok_kontroll.uzor_storon, Узор_углов=platok_kontroll.uzor_uglov,
#Узор_края=platok_kontroll.uzor_kraja,
#Цветы_Орнамент=platok_kontroll.cvety_ornament,
#Изображенный_Цветок_1=platok_kontroll.izobrazheniy_cvetok_1,
#Изображенный_Цветок_2=platok_kontroll.izobrazheniy_cvetok_2,
#Изображенный_Цветок_3=platok_kontroll.izobrazheniy_cvetok_3,
#Изображенный_Цветок_4=platok_kontroll.izobrazheniy_cvetok_4,
#Изображенный_Цветок_5=platok_kontroll.izobrazheniy_cvetok_5,
#Размер_Платка=platok_kontroll.razmer_platka,
#Материал_Платка=platok_kontroll.material_platka,
#session.add(platoch_eksemp)
#await session.commit()
#except:
#raise HTTPException(status_code=500, detail="Проблема с базой данных")
#КРОЛИК ВЫКЛЮЧЕН
#try:
#await router.broker.publish(message=f"{platok_kontroll.nazvanije_platka}{"; ;"}{platok_kontroll.avtor_platka}{"; ;"}{platok_kontroll.kolorit_1}{"; ;"}{platok_kontroll.kolorit_2}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.avtor_platka}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.kolorit_1}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.kolorit_2}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.kolorit_3}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.kolorit_4}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.kolorit_5}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.uzor_temeni}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.uzor_serdceviny}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.uzor_storon}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.uzor_kraja}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.uzor_uglov}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.cvety_ornament}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.izobrazheniy_cvetok_1}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.izobrazheniy_cvetok_2}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.izobrazheniy_cvetok_3}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.izobrazheniy_cvetok_4}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.izobrazheniy_cvetok_5}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.razmer_platka}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.material_platka}", queue="PLATOKY")
#await router.broker.publish(message=f"{platok_kontroll.material_bahromi}", queue="PLATOKY")
#return {"message": "OK"}
#except:
#raise HTTPException(status_code=500, detail="Проблема с брокером")
#ПОЛУЧЕНИЕ ДАННЫХ ПО ПЛАТКУ
@app.get("/platok3", summary="Platok",tags=["Platok"])
async def root(Название_платка: str):
    platok_s_db_data = {}
    query1 = select(Platoky.Автор).where(Platoky.Название == Название_платка)
    session = session_factory()
    result1 = await session.execute(query1)
    avtor = result1.scalars().all()
    platok_s_db_data["Автор"] = avtor
    query2=select(Platoky.Колорит_1).where(Platoky.Название==Название_платка)
    session=session_factory()
    result2 =await session.execute(query2)
    kolorit_1=result2.scalars().all()
    platok_s_db_data["Колорит_1"] = kolorit_1
    query3=select(Platoky.Колорит_2).where(Platoky.Название==Название_платка)
    result3 = await session.execute(query3)
    kolorit_2 = result3.scalars().all()
    platok_s_db_data["Колорит_2"] = kolorit_2
    query4 = select(Platoky.Колорит_3).where(Platoky.Название == Название_платка)
    result4 = await session.execute(query4)
    kolorit_3 = result4.scalars().all()
    platok_s_db_data["Колорит_3"] = kolorit_3
    query5 = select(Platoky.Колорит_4).where(Platoky.Название == Название_платка)
    result5 = await session.execute(query5)
    kolorit_4 = result5.scalars().all()
    platok_s_db_data["Колорит_4"] = kolorit_4
    query6 = select(Platoky.Колорит_5).where(Platoky.Название == Название_платка)
    result6 = await session.execute(query6)
    kolorit_5 = result6.scalars().all()
    platok_s_db_data["Колорит_5"] = kolorit_5
    query7 = select(Platoky.Узор_темени).where(Platoky.Название == Название_платка)
    result7 = await session.execute(query7)
    uzor_temeni = result7.scalars().all()
    platok_s_db_data["Узор_Темени"] = uzor_temeni
    query8 = select(Platoky.Узор_сердцевины).where(Platoky.Название == Название_платка)
    result8 = await session.execute(query8)
    uzor_cerdcevini = result8.scalars().all()
    platok_s_db_data["Узор_Сердцевины"] = uzor_cerdcevini
    query9 = select(Platoky.Узор_края).where(Platoky.Название == Название_платка)
    result9 = await session.execute(query9)
    uzor_krajev = result9.scalars().all()
    platok_s_db_data["Узор_Края"] = uzor_krajev
    query10 = select(Platoky.Узор_сторон).where(Platoky.Название == Название_платка)
    result10 = await session.execute(query10)
    uzor_stroron = result10.scalars().all()
    platok_s_db_data["Узор_Сторон"] = uzor_stroron
    query11 = select(Platoky.Узор_углов).where(Platoky.Название == Название_платка)
    result11 = await session.execute(query11)
    uzor_uglov = result11.scalars().all()
    platok_s_db_data["Узор_Углов"] = uzor_uglov
    query12 = select(Platoky.Цветы_Орнамент).where(Platoky.Название == Название_платка)
    result12 = await session.execute(query12)
    cvety_ornament = result12.scalars().all()
    platok_s_db_data["Соотношение_цветов и орнамента"] =cvety_ornament
    query13 = select(Platoky.Изображенный_Цветок_1).where(Platoky.Название == Название_платка)
    result13 = await session.execute(query13)
    izobr_cvetok_1 = result13.scalars().all()
    platok_s_db_data["Изображенный цветок_1"] = izobr_cvetok_1
    query14 = select(Platoky.Изображенный_Цветок_2).where(Platoky.Название == Название_платка)
    result14 = await session.execute(query14)
    izobr_cvetok_2 = result14.scalars().all()
    platok_s_db_data["Изображенный цветок_2"] = izobr_cvetok_2
    query15 = select(Platoky.Изображенный_Цветок_3).where(Platoky.Название == Название_платка)
    result15 = await session.execute(query15)
    izobr_cvetok_3 = result15.scalars().all()
    platok_s_db_data["Изображенный цветок_3"] = izobr_cvetok_3
    query16 = select(Platoky.Изображенный_Цветок_4).where(Platoky.Название == Название_платка)
    result16 = await session.execute(query16)
    izobr_cvetok_4 = result16.scalars().all()
    platok_s_db_data["Изображенный цветок_4"] = izobr_cvetok_4
    query17 = select(Platoky.Изображенный_Цветок_5).where(Platoky.Название == Название_платка)
    result17 = await session.execute(query17)
    izobr_cvetok_5 = result17.scalars().all()
    platok_s_db_data["Изображенный цветок_5"] = izobr_cvetok_5
    query18 = select(Platoky.Размер_Платка).where(Platoky.Название == Название_платка)
    result18 = await session.execute(query18)
    razmer_platka = result18.scalars().all()
    platok_s_db_data["Размер_Платка"] = razmer_platka
    query19 = select(Platoky.Материал_Платка).where(Platoky.Название == Название_платка)
    result19 = await session.execute(query19 )
    material_platka = result19.scalars().all()
    platok_s_db_data["Материал_Платка"] = material_platka
    query20 = select(Platoky.Материал_Бахромы).where(Platoky.Название == Название_платка)
    result20 = await session.execute(query20)
    material_bahromi = result20.scalars().all()
    platok_s_db_data["Материал_Бахромы"] = material_bahromi
    return platok_s_db_data
#ВВОД СТАРОГО ОБРАЗЦА БЕЗ КОНТРАКТА С PYDANTIC И БЕЗ ЗАВИСИМОСТЕЙ
#@app.post("/platoky_dict", summary="Platok",tags=["Platok"])
#async def create_platok_dict2(id: int,avtor_platka: str,nazvanije_platka: str,kolorit_1: str,kolorit_2: str,kolorit_3: str,
#kolorit_4: str, kolorit_5: str, uzor_temeni: str, uzor_serdceviny: str, uzor_storon: str,uzor_uglov: str,
#uzor_kraja: str, cvety_ornament: str, izobrazheniy_cvetok_1: str, izobrazheniy_cvetok_2: str, izobrazheniy_cvetok_3: str,
#izobrazheniy_cvetok_4: str, izobrazheniy_cvetok_5: str, razmer_platka: str, material_platka: str, material_bahromi: str):
#peremycka = "; ;"
#platok_s_api_data = {}
#platok_s_api_data["id"] = id
#soobshenije1 = str(id)
#platok_s_api_data["avtor_platka"] = avtor_platka
#soobshenije2 = soobshenije1 + peremycka + avtor_platka
#platok_s_api_data["nazvanije_platka"] = nazvanije_platka
#soobshenije3 = soobshenije2 + peremycka + nazvanije_platka
#platok_s_api_data["kolorit_1"] = kolorit_1
#soobshenije4 = soobshenije3 + peremycka + kolorit_1
#platok_s_api_data["kolorit_2"] = kolorit_2
#soobshenije5 = soobshenije4 + peremycka + kolorit_2
#platok_s_api_data["kolorit_3"] = kolorit_3
#soobshenije6 = soobshenije5 + peremycka + kolorit_3
#platok_s_api_data["kolorit_4"] = kolorit_4
#soobshenije7 = soobshenije6 + peremycka + kolorit_4
#platok_s_api_data["kolorit_5"] = kolorit_5
#soobshenije8 = soobshenije7 + peremycka + kolorit_5
#platok_s_api_data["uzor_temeni"] = uzor_temeni
#soobhsenije9 = soobshenije8 + peremycka + uzor_temeni
#platok_s_api_data["uzor_serdceviny"] = uzor_serdceviny
#soobhsenije10 = soobhsenije9 + peremycka + uzor_serdceviny
#platok_s_api_data["uzor_storon"] = uzor_storon
#soobhsenije11 = soobhsenije10 + peremycka + uzor_storon
#platok_s_api_data["uzor_uglov"] = uzor_uglov
#soobshenije12 = soobhsenije11 + peremycka + uzor_uglov
#platok_s_api_data["uzor_kraja"] = uzor_kraja
#soobshenije13 = soobshenije12 + peremycka + uzor_kraja
#platok_s_api_data["cvety_ornament"] = cvety_ornament
#soobshenije14 = soobshenije13 + peremycka + cvety_ornament
#platok_s_api_data["izobrazheniy_cvetok_1"] = izobrazheniy_cvetok_1
#soobshenije15 = soobshenije14 + peremycka + izobrazheniy_cvetok_1
#platok_s_api_data["izobrazheniy_cvetok_2"] = izobrazheniy_cvetok_2
#soobshenije16 = soobshenije15 + peremycka + izobrazheniy_cvetok_2
#platok_s_api_data["izobrazheniy_cvetok_3"] = izobrazheniy_cvetok_3
#soobshenije17 = soobshenije16 + peremycka + izobrazheniy_cvetok_3
#platok_s_api_data["izobrazheniy_cvetok_4"] = izobrazheniy_cvetok_4
#soobshenije18 = soobshenije17 + peremycka + izobrazheniy_cvetok_4
#platok_s_api_data["izobrazheniy_cvetok_5"] = izobrazheniy_cvetok_5
#soobshenije19 = soobshenije18 + peremycka + izobrazheniy_cvetok_5
#platok_s_api_data["razmer_platka"] = razmer_platka
#soobshenije20 = soobshenije19 + peremycka + razmer_platka
#platok_s_api_data["material_platka"] = material_platka
#soobshenije21 = soobshenije20 + peremycka + material_platka
#platok_s_api_data["material_bahromi"] = material_bahromi
#soobshenije22 = soobshenije21 + peremycka + material_bahromi
#try:
#platok_kontroll = Platok_Schema(**platok_s_api_data)
#except:
#raise HTTPException(status_code=422, detail="Данные не прошли валидацию")
#ЗАЯЦ ВЫКЛЮЧЕН
#try:
#await router.broker.publish(message=f"{soobshenije22}", queue="PLATOKY")
#return {"платок в публикацию": platok_kontroll}
#except:
#raise HTTPException(status_code=500, detail="Проблема с брокером")
#ВВОД ДАННЫХ ПЛАТКА
#@app.post("/platoky_vvod", summary="Platok",tags=["Platok"]
#кролмк включен
@router.post("/platoky_vvod", summary="Platok",tags=["Platok"])
async def insert_platky(platok: Annotated[Platok_Schema,Depends()]):
    session=session_factory()
    query=select(Platoky).where(Platoky.Название==platok.Название_Платка)
    result=await session.execute(query)
    unikalnost_platka=result.scalar_one_or_none()
    if unikalnost_platka is None:
        session = session_factory()
        query2 = select(Platoky).where(Platoky.id == platok.id)
        result2 = await session.execute(query2)
        unikalnost_id = result2.scalar_one_or_none()
        if unikalnost_id is None:
            try:
                platoch_eksemp = Platoky(id=platok.id, Название=platok.Название_Платка,
                                         Автор=platok.Автор_Платка, Колорит_1=platok.Колорит_1,
                                         Колорит_2=platok.Колорит_2, Колорит_3=platok.Колорит_3,
                                         Колорит_4=platok.Колорит_4, Колорит_5=platok.Колорит_5,
                                         Узор_темени=platok.Узор_Темени,
                                         Узор_сердцевины=platok.Узор_Сердцевины, Узор_сторон=platok.Узор_Сторон,
                                         Узор_углов=platok.Узор_Углов,
                                         Узор_края=platok.Узор_Края, Цветы_Орнамент=platok.Цветы_Орнамент,
                                         Изображенный_Цветок_1=platok.Изображённый_Цветок_1,
                                         Изображенный_Цветок_2=platok.Изображённый_Цветок_2,
                                         Изображенный_Цветок_3=platok.Изображённый_Цветок_3,
                                         Изображенный_Цветок_4=platok.Изображённый_Цветок_4,
                                         Изображенный_Цветок_5=platok.Изображённый_Цветок_5,
                                         Размер_Платка=platok.Размер_Платка, Материал_Платка=platok.Материал_Платка,
                                         Материал_Бахромы=platok.Материал_Бахромы)
                session = session_factory()
                session.add(platoch_eksemp)
                await session.commit()
                await session.close()
                try:
                    await router.broker.publish(message="Добавлен новый платок", queue="PLATOKY")
                    await router.broker.publish(message=f"{platok}", queue="PLATOKY")
                    return platok
                except: raise HTTPException(status_code=500, detail="Проблема с брокером")
            except: raise HTTPException(status_code=500, detail="Проблема с базой данных")
        else: raise HTTPException(status_code=428, detail="ID занят")
    else: raise HTTPException(status_code=428, detail="Такой платок уже есть")
#@app.post("/platoky_vvod", summary="Platok",tags=["Platok"]
#кролмк включен
@router.post("/platoky_grupovoy", summary="Platok",tags=["Platok"])
async def insert_boundle_platoky(file:UploadFile = File(...)):
    #проверка расширения файла
    if not (file.filename.endswith(".xls") or file.filename.endswith(".xlsx") or file.filename.endswith(".csv")):
        raise HTTPException(status_code=400, detail="В обработку принмаем только EXCEL, дятел!!! ")
    try:
        contents = await file.read()
        dataframe=pd.read_excel(BytesIO(contents))
        nazvanije_platki_vstavka=dataframe.iloc[:,1].tolist()
        id_platki_vstavka=dataframe.iloc[:,0].tolist()
    except: raise HTTPException(status_code=428, detail="Не удалось обработать входящий файл")
    try:
        session=session_factory()
        query11 = select(Platoky.Название)
        result11 = await session.execute(query11)
        nazvanije_platki_DB=result11.scalars().all()
        query22 = select(Platoky.id)
        result22 = await session.execute(query22)
        id_platki_DB = result22.scalars().all()
        await session.close()
    except: raise HTTPException(status_code=500, detail="Проблема с БД при предварительной проверке данных")
    zanjatyje_id=[]
    zanjatyje_imena=[]
    for i in range(len(nazvanije_platki_vstavka)):
        if nazvanije_platki_vstavka[i] in nazvanije_platki_DB:
            zanjatyje_imena.append(nazvanije_platki_vstavka[i])
        if id_platki_vstavka[i] in id_platki_DB:
            zanjatyje_id.append(str(id_platki_vstavka[i]))
    if len(zanjatyje_imena) > 0 or len(zanjatyje_id)>0:
        soobhenije2 = ("Эти названия платков уже есть в БД")
        soobhenije1 = ("Эти артикулы платков уже заняты в БД")
        return soobhenije2, zanjatyje_imena, soobhenije1, zanjatyje_id
    platok_vstavka = []
    bityje_rjady = []
    platok_predstav = ["id: ", "Название платка: ", "Автор платка: ", "Вариант окраски 1: ",
    "Вариант окраски 2: ", "Вариант окраски 3 ", "Вариант окраски 4: ", "Вариант окраски 5: ",
    "Узор темени: ", "Узор сердцевины: ", "Узор сторон: ", "Узор углов: ", "Узор края: ",
    "Соотношение цветов и узора: ", "Нарисованный цветок 1: ", "Нарисованный цветок 2: ",
    "Нарисованный цветок 3: ", "Нарисованный цветок 4: ", "Нарисованный цветок 5: ",
    "Размер платка: ", "Материал платка: ", "Материал бахромы: "]
    for i in range(len(nazvanije_platki_vstavka)):
        platok_s_excel_data = {}
        platok_s_excel_data["id"] = dataframe.iloc[i,0]
        platok_s_excel_data["Название_Платка"] = dataframe.iloc[i, 1]
        platok_s_excel_data["Автор_Платка"]= dataframe.iloc[i, 2]
        platok_s_excel_data["Колорит_1"] = dataframe.iloc[i, 3]
        platok_s_excel_data["Колорит_2"] = dataframe.iloc[i, 4]
        platok_s_excel_data["Колорит_3"] = dataframe.iloc[i, 5]
        platok_s_excel_data["Колорит_4"] = dataframe.iloc[i, 6]
        platok_s_excel_data["Колорит_5"] = dataframe.iloc[i, 7]
        platok_s_excel_data["Узор_Темени"] = dataframe.iloc[i, 8]
        platok_s_excel_data["Узор_Сердцевины"] = dataframe.iloc[i, 9]
        platok_s_excel_data["Узор_Сторон"] = dataframe.iloc[i, 10]
        platok_s_excel_data["Узор_Углов"] = dataframe.iloc[i, 11]
        platok_s_excel_data["Узор_Края"] = dataframe.iloc[i, 12]
        platok_s_excel_data["Цветы_Орнамент"] = dataframe.iloc[i, 13]
        platok_s_excel_data["Изображённый_Цветок_1"] = dataframe.iloc[i, 14]
        platok_s_excel_data["Изображённый_Цветок_2"] = dataframe.iloc[i, 15]
        platok_s_excel_data["Изображённый_Цветок_3"] = dataframe.iloc[i, 16]
        platok_s_excel_data["Изображённый_Цветок_4"] = dataframe.iloc[i, 17]
        platok_s_excel_data["Изображённый_Цветок_5"] = dataframe.iloc[i, 18]
        platok_s_excel_data["Размер_Платка"] = dataframe.iloc[i, 19]
        platok_s_excel_data["Материал_Платка"] = dataframe.iloc[i, 20]
        platok_s_excel_data["Материал_Бахромы"] = dataframe.iloc[i, 21]
        try:
            platok_kontroll = Platok_Schema(**platok_s_excel_data)
        except:
            soobjenije3=("Платок под данным id не прошёл валидацию->>>")
            peremycka=(" ")
            bityje_rjady.append(soobjenije3+peremycka+str(dataframe.iloc[i,0]))
            continue
        try:
            session = session_factory()
            platoch_eksemp = Platoky(id=platok_kontroll.id,Название=platok_kontroll.Название_Платка,
            Автор=platok_kontroll.Автор_Платка, Колорит_1=platok_kontroll.Колорит_1,
            Колорит_2=platok_kontroll.Колорит_2, Колорит_3=platok_kontroll.Колорит_3,
            Колорит_4=platok_kontroll.Колорит_4, Колорит_5=platok_kontroll.Колорит_5,
            Узор_темени=platok_kontroll.Узор_Темени, Узор_сердцевины=platok_kontroll.Узор_Сердцевины,
            Узор_сторон=platok_kontroll.Узор_Сторон, Узор_углов=platok_kontroll.Узор_Углов,
            Узор_края=platok_kontroll.Узор_Края, Цветы_Орнамент=platok_kontroll.Цветы_Орнамент,
            Изображенный_Цветок_1=platok_kontroll.Изображённый_Цветок_1,
            Изображенный_Цветок_2=platok_kontroll.Изображённый_Цветок_2,
            Изображенный_Цветок_3=platok_kontroll.Изображённый_Цветок_3,
            Изображенный_Цветок_4=platok_kontroll.Изображённый_Цветок_4,
            Изображенный_Цветок_5=platok_kontroll.Изображённый_Цветок_5,
            Размер_Платка=platok_kontroll.Размер_Платка, Материал_Платка=platok_kontroll.Материал_Платка,
            Материал_Бахромы=platok_kontroll.Материал_Бахромы)
            session.add(platoch_eksemp)
            await session.commit()
            await session.close()
        except:
            raise HTTPException(status_code=500, detail="Проблема с БД при вставке данных")
        try:
            platok_dannye = []
            for j in range(len(dataframe.columns)):
                platok_rjad = platok_predstav[j] + " " + str(dataframe.iloc[i,j])
                platok_dannye.append(platok_rjad)
            await router.broker.publish(message="Добавлен новый платок", queue="PLATOKY")
            await router.broker.publish(message=f"{platok_dannye}", queue="PLATOKY")
            platok_vstavka.append(platok_dannye)
        except: raise HTTPException(status_code=500, detail="Проблема с брокером")
    return platok_vstavka, bityje_rjady
@app.post("/banda", summary="Platok",tags=["Платочная_Банда"])
async def insert_persona(platoch_persona: Annotated[Banda_Schema,Depends()]):
    try:
        banda_eksemp = Banda(id=platoch_persona.id, Гражданское_Имя=platoch_persona.Гражданское_Имя,
        Творческий_Псевдоним=platoch_persona.Творческий_Псевдоним,
        Описание_Творческой_Деятельности=platoch_persona.Описание_Творческой_Деятельности,
        Связь_Творчества_С_Павлопосадскими_Платками=platoch_persona.Связь_Творчества_С_Павлопосадскими_Платками,
        Ссылка_На_Инстаграм=platoch_persona.Ссылка_На_Инстаграм, Ссылка_На_ВК=platoch_persona.Ссылка_На_ВК,
        Ссылка_На_Ютуб=platoch_persona.Ссылка_На_Ютуб, Ссылка_На_Фейсбук=platoch_persona.Ссылка_На_Фейсбук,
        Ссылка_На_Телеграм=platoch_persona.Ссылка_На_Телеграм,
        Ссылка_На_Одноклассники=platoch_persona.Ссылка_На_Одноклассники,
        Ссылка_На_Яндекс_Дзен=platoch_persona.Ссылка_На_Яндекс_Дзен, Ссылка_На_Сайт=platoch_persona.Ссылка_На_Сайт,
        Адрес_Деятельности=platoch_persona.Адрес_Деятельности)
        session = session_factory()
        session.add(banda_eksemp)
        await session.commit()
        await session.close()
        #заяц включен
        try:
            await router.broker.publish(message="Добавлен новый персонаж", queue="PLATOKY")
            await router.broker.publish(message=f"{platoch_persona}", queue="PLATOKY")
            return platoch_persona
        except:
            raise HTTPException(status_code=500, detail="Проблема с брокером")
    except:
        raise HTTPException(status_code=500, detail="Проблема с базой данных")
#frontend часть
from fastui.forms import fastui_form
from fastapi.responses import HTMLResponse
from fastui import FastUI, AnyComponent, prebuilt_html, components as components
from fastui.components.display import DisplayMode,DisplayLookup
from fastui.events import GoToEvent, BackEvent
import fastui.forms as forms
import python_multipart
#пристройка для отрисовки фронта
app = FastAPI()
gamajun=FastAPI()
app.mount("/gamajun",gamajun)
#фронт на fastUI ВИДЖЕТЫ СТРАНИЦЫ ФРОНТА
#from templates import field_labels_project
#@app.post("/add/project")
#async def insert_DB_project_s_GrIntr(background_task: BackgroundTasks, id: int= Form(), Название_проекта: str = Form(),
    #Критерий_завершенности: str =  Form(), Этап_1: str = Form(), Этап_2: str = Form(), Этап_3: str = Form(),
    #Этап_4: str = Form(), Этап_5: str = Form(), Этап_6: str = Form(), Этап_7: str = Form(), Этап_8: str = Form(),
    #Этап_9: str = Form(), Этап_10: str = Form()):
    #svedenija_project = [Название_проекта,Критерий_завершенности,Этап_1,Этап_2,Этап_3,Этап_4,Этап_5,Этап_6,Этап_7,
    #Этап_8,Этап_9,Этап_10]
    #peremycka1 = " -> "
    #peremycka2 = "; "
    #soobshenije=""
    #for i in range(len(svedenija_project)):
        #soobshenije=soobshenije + field_labels_project[i] + peremycka1 + svedenija_project[i] + peremycka2
    #print(soobshenije)
    #try:
        #tochnoje_vremja = str(datetime.datetime.now())
        #vremja_format = tochnoje_vremja[:-10]
        #sekundi = int(time.time())
        #Project_s_GrIntr = Проект(#id=id,
        #Название_проекта=Название_проекта,Критерий_завершенности=Критерий_завершенности,
        #Завершённость_проекта=0, Этап_1 = Этап_1, Завершенность_Этап_1=0, Этап_2 = Этап_2, Завершенность_Этап_2=0,
        #Этап_3 = Этап_3, Завершенность_Этап_3=0, Этап_4 = Этап_4, Завершенность_Этап_4=0, Этап_5 = Этап_5,
        #Завершенность_Этап_5=0, Этап_6 = Этап_6, Завершенность_Этап_6=0, Этап_7 = Этап_7, Завершенность_Этап_7=0,
        #Этап_8 = Этап_8, Завершенность_Этап_8=0, Этап_9 = Этап_9, Завершенность_Этап_9=0, Этап_10 = Этап_10,
        #Завершенность_Этап_10=0, Дата_регистрации=vremja_format, Дата_изменения=vremja_format,Синхронизация=sekundi)
        #session = session_factory()
        #session.add(Project_s_GrIntr)
        #await session.commit()
        #await session.close()
        #try:
            # заяц включен
            #await router.broker.publish(message="Добавлен новый проект", queue="UROKI")
            #await router.broker.publish(message=f"{soobshenije}", queue="UROKI")
            #try:
                #recipient = os.getenv("RECIPIENT1")
                #background_task.add_task(send_email_async, "Добавлен новый проект", recipient, soobshenije)
                #return soobshenije`
#except:
                #raise HTTPException(status_code=500, detail="Проблема с почтой")
#except:
            #raise HTTPException(status_code=500, detail="Проблема с брокером")
#except:
        #raise HTTPException(status_code=500, detail="Проблема с базой данных")
########################################################################################################################
#Отрисовка уроков по платкам
########################################################################################################################
class TablaSymboly(BaseModel):
    Название_Символа: str = Field(min_length=3, max_length=32)
    Значение_Символа: str = Field(min_length=5, max_length=1000)
    Символ_На_Платке: str = Field(min_length=5, max_length=85)
class TablaColority(BaseModel):
    Cтолбец_Колорита_1: str = Field(min_length=3, max_length=128)
    Cтолбец_Колорита_2: str = Field(min_length=3, max_length=128)
    Cтолбец_Колорита_3: str = Field(min_length=3, max_length=128)
    Cтолбец_Колорита_4: str = Field(min_length=3, max_length=128)
from fastapi.staticfiles import StaticFiles
gamajun.mount("/static",StaticFiles(directory="static"))
from templates import nazv_symbolov,opis_symboli
data_symboli=[
    TablaSymboly(Название_Символа=nazv_symbolov[0],Значение_Символа=opis_symboli[0], Символ_На_Платке="![Прямой_крест](static/prjamoykrest13.jpg)"),
    TablaSymboly(Название_Символа=nazv_symbolov[1],Значение_Символа=opis_symboli[1], Символ_На_Платке="![Косой_крест](static/prjamoykrest12.jpg)"),
    TablaSymboly(Название_Символа=nazv_symbolov[2],Значение_Символа=opis_symboli[2], Символ_На_Платке="![Квадрат](static/prjamoykrest16.jpg)"),
    TablaSymboly(Название_Символа=nazv_symbolov[3],Значение_Символа=opis_symboli[3], Символ_На_Платке="![Ромб](static/prjamoykrest17.jpg)"),
    TablaSymboly(Название_Символа=nazv_symbolov[4],Значение_Символа=opis_symboli[4], Символ_На_Платке="![Восьмиугольник](static/prjamoykrest18.jpg)"),
    TablaSymboly(Название_Символа=nazv_symbolov[5],Значение_Символа=opis_symboli[5], Символ_На_Платке="![Круг](static/prjamoykrest19.jpg)"),
    TablaSymboly(Название_Символа=nazv_symbolov[6],Значение_Символа=opis_symboli[6], Символ_На_Платке="![Алатырь](static/prjamoykrest20.jpg)")
]
data_koloryty=[
TablaColority(Cтолбец_Колорита_1="Лунный!""[Прямой_крест](static/luna.jpg)",
                Cтолбец_Колорита_2="Зелёный!""[Прямой_крест](static/zeleny.jpg)",
                Cтолбец_Колорита_3="Жёлтый+Оранжевый!""[Прямой_крест](static/zholt.jpg)",
                Cтолбец_Колорита_4="Лимонный!""[Прямой_крест](static/kremy.jpg"),
TablaColority(Cтолбец_Колорита_1="Черный!""[Прямой_крест](static/prjamoykrest20.jpg)",
                Cтолбец_Колорита_2="Синий!""[Прямой_крест](static/tayna.jpg)",
                Cтолбец_Колорита_3="Красный!""[Прямой_крест](static/kraski.jpg)",
                Cтолбец_Колорита_4="Белый!""[Прямой_крест](static/bely.jpg)"),
TablaColority(Cтолбец_Колорита_1="Серый!""[Прямой_крест](static/serost.jpg)",
                Cтолбец_Колорита_2="Фиолетоый""![Прямой_крест](static/krem.jpg)",
                Cтолбец_Колорита_3="Бордовый""![Прямой_крест](static/kremy.jpg)",
                Cтолбец_Колорита_4="Розовый!""[Прямой_крест](static/korich.jpg)"),
]
@gamajun.get("/api/symboli",response_model=FastUI,response_model_exclude_none=True)
async def otris_symboli():
    return components.Page(components=
                            [components.Heading(text="Значение символов на платке",level=3),
                             components.Table(data=data_symboli,columns=[DisplayLookup(field="Название_Символа",title="Название_Символа"),
                                                                         DisplayLookup(field="Значение_Символа",title="Значение_Символа"),
                                                                        DisplayLookup(field="Символ_На_Платке",title="Символ_На_Платке",mode=DisplayMode.markdown)
                                                                         ]),])
@gamajun.get("/api/kolority",response_model=FastUI,response_model_exclude_none=True)
async def otris_kolority():
    return components.Page(components=
                            [components.Heading(text="Таблица колоритов платков",level=3),
                             components.Table(data=data_koloryty,columns=[DisplayLookup(field="Cтолбец_Колорита_1",title="",mode=DisplayMode.markdown),
                                                                        DisplayLookup(field="Cтолбец_Колорита_2",title="",mode=DisplayMode.markdown),
                                                                        DisplayLookup(field="Cтолбец_Колорита_3",title="",mode=DisplayMode.markdown),
                                                                        DisplayLookup(field="Cтолбец_Колорита_4",title="",mode=DisplayMode.markdown),
                                                                         ]),])
@gamajun.post("/api/add",response_model=FastUI,response_model_exclude_none=True)
async def insert_DB_platok_s_GrIntr(background_task: BackgroundTasks,id: int = Form(),Название_Платка: str = Form(),
    Автор_Платка: str = Form(),Колорит_1: str = Form(), Колорит_2: str = Form(), Колорит_3: str= Form(),
    Колорит_4: str=Form(),Колорит_5: str=Form(),Узор_Темени: str=Form(),Узор_Сердцевины: str=Form(),
    Узор_Сторон: str=Form(),Узор_Углов:str=Form(),Узор_Края:str=Form(),Цветы_Орнамент:str=Form(),
    Изображённый_Цветок_1:str=Form(),Изображённый_Цветок_2:str=Form(),Изображённый_Цветок_3: str=Form(),
    Изображённый_Цветок_4: str=Form(),Изображённый_Цветок_5: str=Form(), Размер_Платка: str=Form(),
    Материал_Платка:str=Form(),Материал_Бахромы:str=Form()):
    platok_predstav = [str(id),Название_Платка,Автор_Платка,Колорит_1,Колорит_2, Колорит_3,Колорит_4,Колорит_5,Узор_Темени,
    Узор_Сердцевины,Узор_Сторон,Узор_Углов,Узор_Края, Цветы_Орнамент,Изображённый_Цветок_1,Изображённый_Цветок_2,
    Изображённый_Цветок_3, Изображённый_Цветок_4,Изображённый_Цветок_5,Размер_Платка,Материал_Платка,Материал_Бахромы]
    platok_label = ["id: ", "Название платка: ", "Автор платка: ", "Вариант окраски 1: ",
    "Вариант окраски 2: ", "Вариант окраски 3 ", "Вариант окраски 4: ", "Вариант окраски 5: ","Узор темени: ",
    "Узор сердцевины: ", "Узор сторон: ", "Узор углов: ", "Узор края: ","Соотношение цветов и узора: ",
    "Нарисованный цветок 1: ", "Нарисованный цветок 2: ","Нарисованный цветок 3: ", "Нарисованный цветок 4: ",
    "Нарисованный цветок 5: ","Размер платка: ", "Материал платка: ", "Материал бахромы: "]
    soobshenije = ""
    for i in range(len(platok_predstav)):
        soobshenije = soobshenije + platok_label[i] + " -> " + platok_predstav[i] + "; "
    #вывод тяжёлой задачи в фон
    #background_task.add_task(vstavka_platka,soobshenije,platok_predstav)
    try:
        session = session_factory()
        platoch_eksemp = Platoky(id=id,Название=Название_Платка,Автор=Автор_Платка, Колорит_1=Колорит_1,
        Колорит_2=Колорит_2, Колорит_3=Колорит_3,Колорит_4=Колорит_4, Колорит_5=Колорит_5,Узор_темени=Узор_Темени,
        Узор_сердцевины=Узор_Сердцевины,Узор_сторон=Узор_Сторон, Узор_углов=Узор_Углов,Узор_края=Узор_Края,
        Цветы_Орнамент=Цветы_Орнамент,Изображенный_Цветок_1=Изображённый_Цветок_1,
        Изображенный_Цветок_2=Изображённый_Цветок_2,Изображенный_Цветок_3=Изображённый_Цветок_3,
        Изображенный_Цветок_4=Изображённый_Цветок_4,Изображенный_Цветок_5=Изображённый_Цветок_5,
        Размер_Платка=Размер_Платка, Материал_Платка=Материал_Платка,
        Материал_Бахромы=Материал_Бахромы)
        session.add(platoch_eksemp)
        await session.commit()
        await session.close()
        try:
            async with broker:
                await broker.publish(message=f"{soobshenije}", queue="PLATOKY")
                return components.FireEvent(event=GoToEvent(url="/gamajun/results"))
        except:
            raise HTTPException(status_code=500, detail="Проблема с брокером")
    except:
        raise HTTPException(status_code=500, detail="Проблема с БД при вставке данных")
        #try:
            #platok_dannye = []
            #for j in range(len(dataframe.columns)):
                #platok_rjad = platok_predstav[j] + " " + str(dataframe.iloc[i,j])
                #platok_dannye.append(platok_rjad)
            #await router.broker.publish(message="Добавлен новый платок", queue="PLATOKY")
            #await router.broker.publish(message=f"{platok_dannye}", queue="PLATOKY")
            #platok_vstavka.append(platok_dannye)
            #except: raise HTTPException(status_code=500, detail="Проблема с брокером")
    #return platok_vstavka, bityje_rjady
    #peremycka1 = " -> "
    #peremycka2 = "; "
    #soobshenije1 = "Имя_Преподавателя"
    #soobshenije2 = soobshenije1 + peremycka1 + Имя_Преподавателя + peremycka2
    #soobshenije3 = "Фамилия_Преподавателя"
    #soobshenije4 = soobshenije2 + soobshenije3 +  peremycka1 + Фамилия_Преподавателя + peremycka2
    #soobshenije5="Предмет_Обучения"
    #soobshenije6 = soobshenije4 + soobshenije5 + peremycka1 + Предмет_Обучения + peremycka2
    #soobshenije7 = "Имя_Ученика"
    #soobshenije8=soobshenije6 + soobshenije7 + peremycka1 + Имя_Ученика + peremycka2
    #soobshenije9="Фамилия_Ученика"
    #soobshenije10 = soobshenije8 + soobshenije9 + peremycka1 + Фамилия_Ученика + peremycka2
    #soobshenije11= "Ступень_Обучения"
    #soobshenije12 = soobshenije10 + soobshenije11 + peremycka1 + Ступень_Обучения + peremycka2
    #soobshenije13 = "Дата_Проведения"
    #soobshenije14 = soobshenije12 + soobshenije13 + peremycka1 + Дата_Проведения + peremycka2
    #soobshenije15= "Время_Начала"
    #soobshenije16= soobshenije14 + soobshenije15 + peremycka1 + Время_Начала + peremycka2
    #soobshenije17 = "Длительность_Занятия_Мин"
    #soobshenije18 = soobshenije16 + soobshenije17 + peremycka1 + str(Длительность_Занятия_Мин) + peremycka2
    #soobshenije19 = "Стоимость_Занятия_Центов"
    #soobshenije20 = soobshenije18 + soobshenije19 + peremycka1 + str(Стоимость_Занятия_Центов) + peremycka2
    #soobshenije21="Что_Делали_На_Уроке"
    #soobshenije22 = soobshenije20 + soobshenije21 + peremycka1 + Что_Делали_На_Уроке + peremycka2
    #soobshenije23="Задание_На_Дом"
    #soobshenije24= soobshenije22 + soobshenije23 + peremycka1 + Задание_На_Дом + peremycka2
    #soobshenije25="Примечание"
    #soobshenije26 = soobshenije24 + soobshenije25 + peremycka1 + Примечание
    #try:
        #Urok_s_GrIntr = Уроки(Имя_Преподавателя=Имя_Преподавателя,Фамилия_Преподавателя=Фамилия_Преподавателя,
        #Предмет_Обучения = Предмет_Обучения, Имя_Ученика = Имя_Ученика,Фамилия_Ученика = Фамилия_Ученика,
        #Ступень_Обучения = Ступень_Обучения,Дата_Проведения = Дата_Проведения, Время_Начала = Время_Начала,
        #Длительность_Занятия_Мин = Длительность_Занятия_Мин, Стоимость_Занятия_Центов = Стоимость_Занятия_Центов,
        #Что_Делали_На_Уроке = Что_Делали_На_Уроке, Задание_На_Дом = Задание_На_Дом, Примечание = Примечание)
        #session = session_factory()
        #session.add(Urok_s_GrIntr)
        #await session.commit()
        #await session.close()
        #try:
            # заяц включен
            #await router.broker.publish(message="Добавлен новый урок", queue="UROKI")
            #await router.broker.publish(message=f"{soobshenije26}", queue="UROKI")
            #try:
                #recipient = os.getenv("RECIPIENT1")
                #background_task.add_task(send_email_async, "Добавлен новый урок", recipient,soobshenije26)
                #return soobshenije26
                #except:
                #raise HTTPException(status_code=500, detail="Проблема с почтой")
                #except:
            #raise HTTPException(status_code=500, detail="Проблема с брокером")
            #except:
        #raise HTTPException(status_code=500, detail="Проблема с базой данных")
@gamajun.get("/api/results", response_model=FastUI,response_model_exclude_none=True)
async def show_platoky():
    import psycopg2 as ps
    connection = ps.connect(host=os.getenv("DBHOST"), database=os.getenv("DBNAME"), user=os.getenv("DBUSERNAME"),
    password=os.getenv("DBPASSWORD"), port=os.getenv("DBPORT"))
    # создание интерфейса для sql запроса
    cursor = connection.cursor()
    zapros = "SELECT * FROM ПППЛАТКИ ORDER BY id ASC ;"
    cursor.execute(zapros)
    vedomost=[]
    while True:
        next_row = cursor.fetchone()
        if next_row:
            platok_disp=Platok_Schema(id=next_row[0], Название_Платка = next_row[1], Автор_Платка= next_row[2],
            Колорит_1= next_row[3], Колорит_2= next_row[4], Колорит_3 = next_row[5], Колорит_4= next_row[6],
            Колорит_5= next_row[7], Узор_Темени= next_row[8], Узор_Сердцевины= next_row[9], Узор_Сторон= next_row[10],
            Узор_Углов= next_row[11], Узор_Края= next_row[12], Цветы_Орнамент=next_row[13],
            Изображённый_Цветок_1=next_row[14], Изображённый_Цветок_2=next_row[15], Изображённый_Цветок_3=next_row[16],
            Изображённый_Цветок_4=next_row[17], Изображённый_Цветок_5=next_row[18], Размер_Платка=next_row[19],
            Материал_Платка=next_row[20], Материал_Бахромы=next_row[21])
            vedomost.append(platok_disp)
        else:
            cursor.close()
            connection.close()
            return components.Page(components=
                            [components.Heading(text="Вот здесь платоки",level=3),
                             components.Table(data=vedomost),])
@gamajun.get("/api/create/", response_model=FastUI,response_model_exclude_none=True)
async def create_platk_graph_interf():
    return components.Page(components=
    [components.Heading(text="Добавить платок",level=2),
    components.ModelForm(model=Platok_Schema,submit_url="/gamajun/api/add")])
#@gamajun.get("/api/project", response_model=FastUI,response_model_exclude_none=True)
#def create_urok_graph_inter():
#return components.Page(components=
#[components.Heading(text="Добавить проект",level=2),
#components.ModelForm(model=Project_Schema,submit_url="/add/project")])
#переадрессация для включения фронта
@gamajun.get('/{path:path}')
def gamajun_root() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title='FastUI Demo',api_root_url='/gamajun/api',api_path_strip='/gamajun'))
@gamajun.post('/{path:path}')
def gamajun_root2() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title='FastUI Demo',api_root_url='/gamajun/api',api_path_strip='/gamajun'))
from fastapi.middleware.cors import CORSMiddleware
gamajun.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
def kostily_BD():
    # создать ДБ
    import psycopg2 as ps
    from psycopg2.errors import DuplicateDatabase as Oshibka
    from psycopg2 import sql
    connection = None
    try:
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print(Back.GREEN + Fore.BLACK + Style.BRIGHT + 'Создать базу Данных')
        databasename = os.getenv('DATABASENAME')
        connection = ps.connect(host="localhost", database="postgres", user="postgres", password=os.getenv("DBPASSWORD"),
                                port="5432")
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(databasename)))
        cursor.close()
        print(Back.LIGHTGREEN_EX + Fore.BLACK + Style.BRIGHT + 'БД успешно создана, моя Госпожа')
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    except Oshibka:
        print('Такая БД уже есть, моя Госпожа!!!')
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    finally:
        if connection:
            connection.close()
        if cursor:
            cursor.close()
async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
async def main():
    init(autoreset=True)
    await create_tables()
    uvicorn.run("prilozhenije:app", reload=True, port=8000)
#ЗАЯЦ ВКЛЮЧЕН
app.include_router(router)
if __name__ == "__main__":
    asyncio.run(main())
#except:
#peremycka=(" ")
#soobhenije=("Данные не прошли валидацию, ошибка в строке")
#return soobhenije + peremycka + str(i+1)
