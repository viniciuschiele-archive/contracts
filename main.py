from contracts import Contract, fields
from contracts.io  import DictReader, DictWriter


contract = Contract()
contract.fields['name'] = fields.String('name')
contract.fields['name'].bind('name')

data = {'name': 'vini'}
writer = DictWriter()

contract.write(data, writer)

reader = DictReader(writer.data)
data = contract.read(reader)

print(data)
