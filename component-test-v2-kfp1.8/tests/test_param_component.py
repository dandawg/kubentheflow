
import os
import sys
import logging
import json
import pytest
import docker
import tempfile

sys.path.insert(1, '..')
import utils

#Inputs
@pytest.fixture
def executor_input():
    ex_input = {
        "inputs": {
            "parameters": {
                "a": {"intValue": 1},
                "b": {"doubleValue": 2.0},
                "c": {"stringValue": "Testing my string!"}
            }
        },
        "outputs": {
            "parameters": {},
            "outputFile": "/tmp/out/output.json"
        }
    }
    return ex_input

@pytest.fixture
def component_path():
    p = "../components/param_component.yaml"
    return p

def test_param_component(executor_input: dict, component_path: str):
    # run component
    dclient = docker.client.from_env()
    container_id = utils.docker_run(component_path, executor_input, dclient)

    # verify outputs
    try:
        tmpdir = tempfile.gettempdir()
        tarpath = os.path.join(tmpdir, f"output-{container_id}.tar.gz")
        logging.info(f"Extracting to tarpath: {tarpath}")
        stats = utils.extract_output(
            dclient,
            container_id,
            executor_input["outputs"]["outputFile"],
            local_tar_path=tarpath
        )
        output_json = utils.extract_file(stats["name"], tarpath).read().decode('utf-8')
        logging.info(f"Output json: {output_json}")
        recieved = json.loads(output_json)
        expected = {"parameters":
                        {
                            "a": {"intValue": 1},
                            "b": {"doubleValue": 2.0},
                            "res": {"doubleValue": 3.0}
                        }
                }
        logging.info(f"Expected json: {expected}")
        assert recieved == expected, f"Recieved json != expected: received = {recieved}"
    finally:
        # cleanup
        c = dclient.containers.get(container_id)
        c.remove()
        logging.info(f"Pruned container {container_id}")
        logging.info(f"Done.")