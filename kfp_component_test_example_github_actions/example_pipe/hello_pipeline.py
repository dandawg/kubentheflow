
from kfp.dsl import pipeline
from kfp.components import create_component_from_func

from .components import hello_comp

# package component as pipe
image = "python:3.8-slim-buster"
comp = create_component_from_func(hello_comp.hello, base_image=image)

@pipeline(name='hello-pipe')
def hello_pipe(name: str):
    op1 = comp(name)
    return


