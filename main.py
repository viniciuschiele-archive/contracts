import random
import string

from uuid import uuid4
from contracts.utils import missing
from contracts import Contract, Context, fields
from datetime import datetime
from marshmallow import fields as mmfields, Schema, post_load, post_dump
from pytz import timezone


def generate_random_string(size):
    return ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(size))


class NestedContract(Contract):
    property1 = fields.String()
    property2 = fields.String()


class MyContract(Contract):
    property1 = fields.Boolean()
    # property2 = fields.Date()
    property3 = fields.Integer()
    property4 = fields.String()
    property5 = fields.List(fields.Integer())
    # property6 = fields.UUID()
    # property7 = fields.DateTime()
    property8 = fields.Float()
    property9 = fields.Nested(NestedContract)

    # def _post_load(self, data, context):
    #     return data
    #
    # def _post_dump(self, data, context):
    #     return data


class NestedSchema(Schema):
    property1 = mmfields.String()
    property2 = mmfields.String()


class MySchema(Schema):
    property1 = mmfields.Boolean()
    # property2 = mmfields.Date()
    property3 = mmfields.Integer()
    property4 = mmfields.String()
    property5 = mmfields.List(mmfields.Integer())
    # property6 = mmfields.UUID()
    # property7 = mmfields.DateTime()
    property8 = mmfields.Float()
    property9 = mmfields.Nested(NestedSchema)

    # @post_load
    # def _post_load(self, data):
    #     return MyData(**data)
    #
    # @post_dump
    # def _post_dump(self, data):
    #     return data

# class MyData:
#     property1 = None
#     property2 = True
#     property3 = generate_random_string(30)
#     property4 = generate_random_string(40)
#     property5 = generate_random_string(50)
#     property6 = generate_random_string(60)
#     property7 = generate_random_string(70)
#     property8 = generate_random_string(80)
#     property9 = generate_random_string(90)
#     property10 = generate_random_string(100)
#     property11 = generate_random_string(110)
#     property12 = generate_random_string(120)
#     property13 = generate_random_string(130)
#     property14 = generate_random_string(140)
#     property15 = 123456789
#
#     def __init__(self, **kwargs):
#         self.__dict__ = kwargs


data = dict(
    property1=True,
    property2=datetime.now().date(),
    property3=1234,
    property4=generate_random_string(40),
    property5=['1', '2', '3', '4'],
    property6=uuid4(),
    property7=datetime.now(),
    property8=1.2,
    property9=dict(property1='123', property2='456')
)


def perf(func1, func2, count):
    start = datetime.now()
    for _ in range(count):
        func1()
    elapsed1 = datetime.now() - start
    print(elapsed1)

    start = datetime.now()
    for _ in range(count):
        func2()
    elapsed2 = datetime.now() - start
    print(elapsed2)

    print(elapsed2.total_seconds() / elapsed1.total_seconds())


print('init and dump')
def contract_init_and_dump():
    contract = MyContract()
    contract.dump(data)


def schema_init_and_dump():
    schema = MySchema()
    schema.dump(data)

perf(contract_init_and_dump, schema_init_and_dump, 1000)

print('init')
perf(lambda: MyContract(), lambda: MySchema(), 1000)

print()

print('dump')
contract = MyContract()
schema = MySchema()
perf(lambda: contract.dump(data), lambda: schema.dump(data), 1000)

print()

print('load')
contract = MyContract()
schema = MySchema()
perf(lambda: contract.load(data), lambda: schema.dump(data), 1000)
print()


print('dump many')
lst = [data for _ in range(0, 1000)]
contract = MyContract(many=True)
schema = MySchema(many=True)
perf(lambda: contract.dump(lst), lambda: schema.dump(lst), 1)

print()

print('load many')
lst = [data for _ in range(0, 1000)]
contract = MyContract(many=True)
schema = MySchema(many=True)
perf(lambda: contract.load(lst), lambda: schema.load(lst), 1)
