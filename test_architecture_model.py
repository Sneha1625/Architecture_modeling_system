from architecture_model.model import (
    Component,
    Relationship,
    ArchitectureSnapshot
)


component = Component(
    id="component_payment",
    name="Payment",
    responsibility="Payment processing",
    layer="service",
    files=[
        "payment/controller.py",
        "payment/service.py",
        "payment/repository.py"
    ],
    dependencies=[
        "component_database"
    ]
)


relationship = Relationship(
    source="component_payment",
    target="component_database",
    type="depends_on"
)


snapshot = ArchitectureSnapshot(
    version="1.0",
    commit_hash="test123",
    components=[component],
    relationships=[relationship],
    metrics={
        "total_components": 1
    },
    violations=[]
)


snapshot.save_json(
    "test_architecture_snapshot.json"
)


print("Architecture snapshot created successfully!")
print(snapshot.to_dict())