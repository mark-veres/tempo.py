from tempo import Node, LeafNode

# nodes = Node.get_all()
# [print(" " * n.level + n.name) for n in nodes]

# nodes = Node.by_property("name", "POPULATIA REZIDENTA", lambda a, b: b in a)
# print(nodes[0].name)

# nodes = Node.by_name("POPULATIA REZIDENTA").children
# [print(n.code, n.name) for n in nodes]

node = LeafNode.by_code('1010', 'POP105A')
[print(d.label) for d in node.dimensions]
q = node.query(
    ('Varste si grupe de varsta', ['Total'])
)