from fastapi import Depends, FastAPI
#importing FastAPI class from fastapi module
from models import Product
#import Product class from models module
from database import session, engine
import database_model
from sqlalchemy.orm import Session #it is not the same session that we created in database. it is a class of orm for dependency injection 
from fastapi.middleware.cors import CORSMiddleware

#creating an instance/object of FastAPI class
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_methods = ["*"],
    allow_headers = ["*"]
)

#create a table in the database using the metadata of the Product class defined in database_model.py
database_model.Base.metadata.create_all(bind=engine)



#creating a list of Product objects to store the products
products = [
    Product(id=1, name="Product 1", description="Description of Product 1", price=10.99, quantity=5),
    Product(id=2, name="Product 2", description="Description of Product 2", price=19.99, quantity=3),
    Product(id=3, name="Product 3", description="Description of Product 3", price=5.99, quantity=10),
    Product(id=4, name="Product 4", description="Description of Product 4", price=15.99, quantity=7)
]

#creating the session just once: using dependency injection
#Dependency Injection means FastAPI automatically provides an object or resource that your function needs, instead of you creating it yourself. now get_db() will be automatically called whenever we call depend()
def get_db():
    db = session()
    try:
        yield db
    finally: 
        db.close()

#initialising the table 
#method: if no data in the table then populate with the dummy data from the previous products list, else do nothing
def init_db():
    db = session()
    count = db.query(database_model.Product).count()

    if count ==0:
        for product in products:
            # db.add(product) --> this will not work as db will accept the mapped object and not the normal class object that we created 
            #we have to pass the object of database_models.Product
            db.add(database_model.Product(**product.model_dump()))
            #product.model_dump will chnage into dictionary and ** will unpack it and using database_model.Product() it will change into 
        db.commit()

init_db()


#using the decorator to define a method (here get method) and a route for the root URL ("/") and associate it with the greet function
@app.get("/")
def greet():
    return "Welcome to the server"




@app.get("/products")
def get_products(db: Session =Depends(get_db)):
    db_products = db.query(database_model.Product).all()
    return db_products

#get a single product by its ID
@app.get("/products/{id}")
def get_product_by_id(id:int,db:Session = Depends(get_db)):
    db_product = db.query(database_model.Product).filter(database_model.Product.id ==id).first()
    if db_product:
        return db_product
    return "product not found"

@app.post("/products")
def add_product(product: Product, db: Session = Depends(get_db)):
    db_product = database_model.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

#update a product by its ID
@app.put("/products/{id}")
def update_product(id:int, product:Product, db: Session = Depends(get_db)):
    db_product = db.query(database_model.Product).filter(database_model.Product.id==id).first()
    if db_product:
        db_product.name= product.name
        db_product.description = product.description
        db_product.price = product.price
        db_product.quantity = product.quantity
        db.commit()
        return product
    else:
        return "No product found"
    

@app.delete("/products/{id}")
def delete_product(id: int, db:Session = Depends(get_db)):
    db_product = db.query(database_model.Product).filter(database_model.Product.id == id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return "Product deleted Successfully"
    else:
        return "Product Not Found"
    





# db: Session =Depends(get_db) it means 
'''
db is the variable name, it can be anything
Session is the type hint, it means db should be of the type Session
& db must be equal to Depends(that is call get_db and assign its return value to db)
now get_db is just returning db which is db = session(), which is nothing but the sessionmaker that binds the engine(i.e db_url)
'''
