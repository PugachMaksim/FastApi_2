"""Объедините студентов в команды по 2-5 человек в сессионных залах.

Необходимо создать базу данных для интернет-магазина. База данных должна состоять из трёх таблиц: товары, заказы и пользователи.
— Таблица «Товары» должна содержать информацию о доступных товарах, их описаниях и ценах.
— Таблица «Заказы» должна содержать информацию о заказах, сделанных пользователями.
— Таблица «Пользователи» должна содержать информацию о зарегистрированных пользователях магазина.
• Таблица пользователей должна содержать следующие поля: id (PRIMARY KEY), имя, фамилия, адрес электронной почты и пароль.
• Таблица заказов должна содержать следующие поля: id (PRIMARY KEY), id пользователя (FOREIGN KEY), id товара (FOREIGN KEY), дата заказа и статус заказа.
• Таблица товаров должна содержать следующие поля: id (PRIMARY KEY), название, описание и цена."""

from random import randint
import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, ForeignKey

DATABASE_URL = "sqlite:///mydatabase.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

products = sqlalchemy.Table(
    'products', metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('prod_name', sqlalchemy.String(50), nullable=False),  # , unique=True
    sqlalchemy.Column('quantity', sqlalchemy.Integer, default=0, nullable=False),
    sqlalchemy.Column('price', sqlalchemy.Float, nullable=False)
)

users = sqlalchemy.Table(
    'users', metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String(30), nullable=False),
    sqlalchemy.Column('surname', sqlalchemy.String(50), nullable=False),
    sqlalchemy.Column('email', sqlalchemy.String(50), nullable=False),
    sqlalchemy.Column('password', sqlalchemy.String(50), nullable=False)
)

orders = sqlalchemy.Table(
    'orders', metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, ForeignKey(users.c.id), nullable=False),
    sqlalchemy.Column('prod_id', sqlalchemy.Integer, ForeignKey(products.c.id), nullable=False),
    sqlalchemy.Column('quantity', sqlalchemy.Integer, nullable=False)

)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

app = FastAPI()


class Products(BaseModel):
    prod_name: str = Field(max_length=50)
    price: float
    quantity: int


class ProductsId(Products):
    id: int


class User(BaseModel):
    name: str = Field(max_length=30)
    surname: str = Field(max_length=50)
    email: str = Field(max_length=50)
    password: str = Field(max_length=50)


class UserId(User):
    id: int


class Order(BaseModel):
    user_id: int
    prod_id: int
    quantity: int


class OrderId(Order):
    id: int


# users.drop(engine)
# products.drop(engine)
# orders.drop(engine)


@app.get("/f_users/{count}")
async def create_note(count: int):
    for i in range(count):
        query = users.insert().values(name=f'user{i}', surname=f'surname{i}', email=f'mail{i}@mail.ru',
                                      password=f'password{i}')
        await database.execute(query)
    return {'message': f'{count} fake users create'}


@app.get("/f_products/{count}")
async def create_note(count: int):
    for i in range(count):
        query = products.insert().values(prod_name=f'product {i}', price=randint(1, 1000), quantity=randint(1, 50))
        await database.execute(query)
    return {'message': f'{count} fake products create'}


@app.get("/f_orders/{count}")
async def create_note(count: int):
    for i in range(count):
        query = orders.insert().values(user_id=randint(1, 20), prod_id=randint(1, 20), quantity=randint(1, 100))
        await database.execute(query)
    return {'message': f'{count} fake orders create'}


@app.post('/add_user/', response_model=UserId)
async def add_user(user: User):
    query = users.insert().values(name=user.name, surname=user.surname, email=user.email,
                                  password=user.password)
    last_record_id = await database.execute(query)
    return {**user.dict(), 'id': last_record_id}


@app.post('/add_product/', response_model=ProductsId)
async def add_product(product: Products):
    query = products.insert().values(prod_name=product.prod_name, quantity=product.quantity, price=product.price)
    last_record_id = await database.execute(query)
    return {**product.dict(), "id": last_record_id}


@app.post('/add_order/{user_id}/{prod_id}/{quantity}', response_model=Order)
async def add_order(order: OrderId, user_id: int, prod_id: int, quantity: int):
    query = orders.insert().values(user_id=user_id, prod_id=prod_id, quantity=quantity)
    last_record_id = await database.execute(query)
    return {**order.dict(), "id": last_record_id}


@app.delete('/del_prod/{prod_id}')
async def del_prod(prod_id: int):
    query = products.delete().where(products.c.id == prod_id)
    await database.execute(query)
    return {'message': 'Product deleted'}


@app.delete('/del_user/{user_id}')
async def del_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {'message': 'User deleted'}


@app.delete('/del_order/{order_id}')
async def del_order(order_id: int):
    query = orders.delete().where(orders.c.id == order_id)
    await database.execute(query)
    return {'message': 'Order deleted'}


@app.get('/users/')
async def get_user():
    query = users.select()
    return await database.fetch_all(query)


@app.get('/get_order/{user_id}')
async def det_order_id(user_id: int):
    query = orders.select().where(orders.c.user_id == user_id)
    return await database.fetch_all(query)


@app.get('/get_products/')
async def get_products():
    query = products.select()
    return await database.fetch_all(query)


@app.get('/get_order/')
async def get_order():
    query = orders.select()
    return await database.fetch_all(query)


@app.put('/update_user/{user_id}', response_model=UserId)
async def update_user(user_id: int, new_user: User):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    return await database.execute(query)


@app.put('/update_products/{products_id}', response_model=Products)
async def update_product(product_id: int, new_product: ProductsId):
    query = products.update().where(products.c.id == product_id).values(**new_product.dict)
    return await database.execute(query)
