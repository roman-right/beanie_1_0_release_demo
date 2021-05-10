import asyncio

import motor
from beanie import init_beanie
from beanie.operators import Set, Text, Inc

from beanie_1_0_release_demo.models import Product, Category, ProductShortView, \
    TotalCountView
from beanie_1_0_release_demo.settings import Settings


async def init():
    settings = Settings()
    cli = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_dsn)
    db = cli[settings.mongodb_db_name]
    await init_beanie(database=db, document_models=[Product])


async def create():
    chocolate = Category(name="Chocolate")

    # One
    caramel_and_nougat = Product(name="Caramel and Nougat ",
                                 num=20,
                                 price=3.05,
                                 category=chocolate)
    await caramel_and_nougat.create()

    # Many
    peanut_bar = Product(name="Peanut Bar",
                         num=4,
                         price=4.44,
                         category=chocolate)
    truffle = Product(name="Chocolate Truffle",
                      num=40,
                      price=2.50,
                      category=chocolate)
    await Product.insert_many([peanut_bar, truffle])


async def find():
    # All

    products = await Product.all().to_list()

    # Category

    products = await Product.find(
        Product.category.name == "Chocolate"
    ).to_list()

    # Operator

    products = await Product.find(Text("Chocolate")).to_list()

    # Complex search with projection

    products = await Product.find(
        Product.category.name == "Chocolate",
        Product.price < 3.5
    ).sort(-Product.price).limit(10).project(ProductShortView)

    # Native
    products = await Product.find({"price": {"gte": 2}}).to_list()

    # One
    product = await Product.find_one(Product.name == "Peanut Bar")


async def update():
    # Many
    await Product.find(
        Product.name == "Peanut Bar"
    ).update(Set({Product.price: 5}))

    # One
    await Product.find_one(Product.name == "Chocolate Truffle").update(
        Set({Product.price: 3}))

    # or

    product = await Product.find_one(Product.name == "Peanut Bar")
    await product.update(Inc({Product.price: -1}))

    # Native
    await Product.find(
        Product.num <= 5
    ).update({"$set": {Product.price: 1}})

    # Preset method
    await Product.find(
        Product.category.name == "Chocolate"
    ).inc({Product.price: 2})


async def delete():
    # Many
    await Product.find(
        Product.category.name == "Chocolate").delete()

    # One
    product = await Product.find_one(Product.name == "Peanut Bar")
    await product.delete()

    # Without fetching

    await Product.find_one(Product.name == "Chocolate Truffle").delete()


async def aggregate():
    # Over collection

    total_count = await Product.aggregate(
        [{"$group": {"_id": "$category", "total": {"$sum": "$num"}}}],
        projection_model=TotalCountView
    ).to_list()

    # Subset

    total_count = await Product.find(Product.price < 10).aggregate(
        [{"$group": {"_id": "$category", "total": {"$sum": "$num"}}}],
        projection_model=TotalCountView
    ).to_list()

    # Preset method

    avg_choco_price = await Product.find(
        Product.category.name == "Chocolate"
    ).avg(Product.price)


async def main():
    await init()
    await create()
    await find()
    await aggregate()
    await delete()


asyncio.run(main())
