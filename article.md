I'm happy to introduce to you [Beanie 1.0.0](https://github.com/roman-right/beanie) - Python ODM (Object Document
Mapper) for MongoDB!

Two months ago I published the very first Beanie release. You can find the article about it by the [link](https://dev.to/romanright/announcing-beanie-mongodb-odm-56e). I demonstrated there, how simple it is, to make a CRUD service with FastAPI and Beanie.  

Many features were added since that time. Today I want to show the most interesting things, which
came with this major version update.

For this demo, I will use the `Product` document model.

```python
class Category(BaseModel):
    name: str
    description: str


class Product(Document):
    name: str
    description: Optional[str] = None
    price: Indexed(float, pymongo.DESCENDING)
    category: Category
    num: int

    class Collection:
        name = "products"
        indexes = [
            [
                ("name", pymongo.TEXT),
                ("description", pymongo.TEXT),
            ],
        ]
```

Beanie Document is an abstraction over Pydantic BaseModel. It helps to make documents flexible and structured at the same time.

For this demo I set up indexes here in two ways:

- Simple with the `Indexed` field
- More complex with the `Collection` inner class

More information about document setup could be found by [link](https://roman-right.github.io/beanie/tutorial/install/)

## Create documents

Beanie provides and single document creation pattern and batch inserts:

```python
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
```

## Find queries

Now you can use Python native comparison operators with the document class
fields:

```python
Product.find(Product.category.name == "Chocolate")
```

The `find()` method will return the `FindMany` query, which uses an async generator pattern, and data can be available via `async for` loop. 

```python
async for item in Product.find(Product.category.name == "Chocolate"):
    print(item)
```

To retrieve the list, I use `to_list()` method.

```python
products = await Product.find( Product.category.name == "Chocolate").to_list()
```

`FindMany` queries provide also sort, skip, limit, and project methods:

```python
class ProductShortView(BaseModel):
    name: str
    price: float


products = await Product.find(
    Product.category.name == "Chocolate",
    Product.price < 3.5
).sort(-Product.price).limit(10).project(ProductShortView)

```

Python comparison operators don't cover all the cases. Beanie provides a list
of find operators, which could be used instead:

```python
from beanie.operators import Text

products = await Product.find(Text("Chocolate")).to_list()
```

Or, for the fine-tuning, native PyMongo syntax can be used there:

 ```python
products = await Product.find({"price": {"gte": 2}}).to_list()
```

If you need to find a single document, you can use the `find_one` method instead.

```python
product = await Product.find_one(Product.name == "Peanut Bar")
```

The detailed tutorial about finding the documents can be found by [link](https://roman-right.github.io/beanie/tutorial/find/)

## Update

`update()` method allows updating documents using search criteria of the `FindMany` and `FindOne` queries.

You can do it, using update operators:

```python
from beanie.operators import Inc, Set

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
```

Native PyMongo syntax is also supported for this

```python
await Product.find(
    Product.num <= 5
).update({"$set": {Product.price: 1}})

```

There is a list of preset update operations, which could be used as methods

```python
await Product.find(
    Product.category.name == "Chocolate"
).inc({Product.price: 2})
```

To update all the documents without the find query you can skip the `find` step:

```python
await Product.inc({Product.price: 2})
```

## Aggregations

Aggregations, as updates, could be used over the whole collection or, using`FindMany` searching criteria.

```python
class TotalCountView(BaseModel):
    category: str = Field(None, alias="_id")
    total: int


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
```

As for the update operations, there is a list of preset methods for the popular aggregations. For example, average:

```python
avg_choco_price = await Product.find(
    Product.category.name == "Chocolate"
).avg(Product.price)
```

## Delete

Delete operations support the same patterns:

```python
# Many
await Product.find(
    Product.category.name == "Chocolate").delete()

# One
product = await Product.find_one(Product.name == "Peanut Bar")
await product.delete()

# Without fetching

await Product.find_one(Product.name == "Chocolate Truffle").delete()
```

## Conclusion

In my first article, I said, that Beanie is a micro ODM. I'm removing the prefix `micro` now. Beanie is a rich Python ODM for MongoDB with a lot of features, like query builder, projections, and migrations. It helps me to build services and applications a lot. I hope, it will help many other developers too.

## Links

- [Beanie Project](https://github.com/roman-right/beanie)
- [Documentation](https://roman-right.github.io/beanie/)
- [Discord Server](https://discord.gg/ZTTnM7rMaz)