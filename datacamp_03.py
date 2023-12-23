import singer
import json

columns = ("id", "name", "age", "city", "has_children")
users = {(1, "John", 29, "New York", False),
         (2, "Jane", 30, "New York", True),
         (3, "Joe", 27, "Chicago", False),}

singer.write_schema(stream_name="users", record=dict(zip(columns, users.pop())))

fixed_dict = {"type": "RECORD", "stream": "users"}
# ** its used to unpack a dictionary in another dictionary
record_msg = {**fixed_dict, "record": dict(zip(columns, users.pop()))}
print(json.dumps(record_msg))