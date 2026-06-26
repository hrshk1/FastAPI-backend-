from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int



# After using pydantic models, we don't need to create a constructor for the Product class as Pydantic automatically generates one for us based on the defined attributes.
# #creating a constructor to initialize the attributes of the Product class
#     def __init__(self, id: int, name: str, description: str, price: float, quantity: int):
#         self.id = id
#         self.name = name
#         self.description = description
#         self.price = price
#         self.quantity = quantity