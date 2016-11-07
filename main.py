import random
import string

from contracts.utils import missing
from contracts.fields import Contract, IntegerField, StringField
from datetime import datetime
from marshmallow import fields, Schema, post_load


def generate_random_string(size):
    return ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(size))


class MyContract(Contract):
    property1 = StringField(allow_none=True)
    property2 = StringField()
    property3 = StringField()
    property4 = StringField()
    property5 = StringField()
    property6 = StringField()
    property7 = StringField()
    property8 = StringField()
    property9 = StringField()
    property10 = StringField()
    property11 = StringField()
    property12 = StringField()
    property13 = StringField()
    property14 = StringField()
    property15 = IntegerField()

    # def post_load(self, data, original_data):
    #     return MyData(**data)


class MySchema(Schema):
    property1 = fields.String(allow_none=True)
    property2 = fields.String()
    property3 = fields.String()
    property4 = fields.String()
    property5 = fields.String()
    property6 = fields.String()
    property7 = fields.String()
    property8 = fields.String()
    property9 = fields.String()
    property10 = fields.String()
    property11 = fields.String()
    property12 = fields.String()
    property13 = fields.String()
    property14 = fields.String()
    property15 = fields.Integer()

    @post_load
    def post_load(self, data):
        return MyData(**data)


class MyData:
    property1 = None
    property2 = generate_random_string(20)
    property3 = generate_random_string(30)
    property4 = generate_random_string(40)
    property5 = generate_random_string(50)
    property6 = generate_random_string(60)
    property7 = generate_random_string(70)
    property8 = generate_random_string(80)
    property9 = generate_random_string(90)
    property10 = generate_random_string(100)
    property11 = generate_random_string(110)
    property12 = generate_random_string(120)
    property13 = generate_random_string(130)
    property14 = generate_random_string(140)
    property15 = 123456789

    def __init__(self, **kwargs):
        self.__dict__ = kwargs


contract = MyContract()
schema = MySchema()
# data = MyData()
data = dict(
    property1=None,
    property2=generate_random_string(20),
    property3=generate_random_string(30),
    property4=generate_random_string(40),
    property5=generate_random_string(50),
    property6=generate_random_string(60),
    property7=generate_random_string(70),
    property8=generate_random_string(80),
    property9=generate_random_string(90),
    property10=generate_random_string(100),
    property11=generate_random_string(110),
    property12=generate_random_string(120),
    property13=generate_random_string(130),
    property14=generate_random_string(140),
    property15=123456789,
)

# start = datetime.now()
# for _ in range(0, 1000):
#     contract.load(data)
# stop = datetime.now()
# print(stop-start)
#
# start = datetime.now()
# for _ in range(0, 1000):
#     schema.load(data)
# stop = datetime.now()
# print(stop-start)

start = datetime.now()
for _ in range(0, 1000):
    contract.dump(data)
stop = datetime.now()
print(stop-start)

start = datetime.now()
for _ in range(0, 1000):
    schema.dump(data)
stop = datetime.now()
print(stop-start)
