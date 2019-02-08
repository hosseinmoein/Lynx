![Alt text](dep_graph.png "Dependency Graph")

# Dependency Grpah
This is a dependency graph. The very end product is SystemItem and an example of that could be seen in app/tests/system_item.py.
The goal of this is to manage systems that have a large number of calculations that should happen in special order when an external event happens. Basically this mimics an ecosystem, if you will. There are a lot of components in an ecosystem and when an external stimulus enters the system, it triggers a lot of reactions until the system comes to an equilibrium again. Trading alpha and risk models are also similar to an ecosystem with a lot of factors that can change as a result of external market events (e.g. a new bid, a new trade, etc.).
The code is arranged as follows

DataItemBase: This is an abstract class that defines an interface. Most of the interface throw `Not Implemented`. It also contains hooks so the later derived classes can implement dependencies relationships. Please see `data_item_base.py` for more explanations.
    DataItem: This is a concrete data item with actual value. The type of values it can be are limited to a set of fundamental types + `datetime`. Also once a data item is declared, it cannot change type (like other Python variables) with a couple exceptions. Please see `data_item.py` for more explanation.
    ContainerItem: This is a tubular container of data items accessible by column name or index and row index. Because of this recursive definition, a container item column can be another container item. So, container item is really not tabular. It could take any arbitrary shape. Please see `container_item.py` for more explanation.
        SystemItem: This is where dependency mechanism is implemented. You can define a dependency which signifies an independent column -> dependent column relationships between columns. Circular dependencies are allowed and handled properly by going around the circle once.  You can also define action on columns. Please see `system_item.py` and `test_system_item.py` for more explanation and example.


# Documentation
Docs to come ...

# Test/Example
[Dependency Test](app/tests/test_system_item.py)
[DataItem Test](app/tests/test_data_item.py)
