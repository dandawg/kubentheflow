
import kfp
from kfp.v2 import dsl
from typing import NamedTuple
from collections import namedtuple
from kfp.v2.dsl import (Input, InputPath, Output,
    OutputPath, Model, Dataset, Metrics)

base_image = "python:3.8-slim-buster"
#simple component
@dsl.component(
    base_image=base_image,
    packages_to_install=None,
    output_component_file="simple_component.yaml",
)
def simple_component():
    a, b = 1, 2
    print("a+b: ", a + b)

# parameter component
@dsl.component(
    base_image=base_image,
    packages_to_install=["numpy"],
    output_component_file="param_component.yaml"
)
def param_component(
    a: int, b: float, c: str = "param_comonent"
) -> NamedTuple("Outputs", [("a", int), ("b", float), ("res", float)]):
    from collections import namedtuple
    print(c)
    print("a+b result: ", a + b)
    result = namedtuple("Outputs", ("a", "b", "res"))
    return result(a, b, a+b)

# artifact component
@dsl.component(
    base_image=base_image,
    packages_to_install=["pandas", "scikit-learn", "cloudpickle"],
    output_component_file="artifact_component.yaml"
)
def artifact_component(
    input_data: Input[Dataset],
    input_file: InputPath(),
    output_file: OutputPath(),
    output_model: Output[Model],
    metrics: Output[Metrics]
):
    import pandas as pd
    import cloudpickle
    from sklearn.neighbors import KNeighborsClassifier

    # read input data artifact
    with open(input_data.path) as d:
        inp_d = pd.read_csv(d)
    # read input file
    with open(input_file) as f:
        inp_f = f.read()
    
    # output model artifact
    model = KNeighborsClassifier()
    with open(output_model.path, 'wb') as m:
        cloudpickle.dump(model)
    
    # metrics artifact
    metrics.name = "Test"
    metrics.log_metric("score", 1000)
    metrics.metadata["comment"] = "Amazing!"


