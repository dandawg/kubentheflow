
import os
import sys
import logging
import json
import pytest
import docker
import tempfile
import cloudpickle
from sklearn.neighbors import KNeighborsClassifier

sys.path.insert(1, '..')
import utils

#Inputs
@pytest.fixture
def executor_input():
    ex_input = {
        "inputs": {
            "parameters": {}
        },
        "outputs": {
            "parameters": {},
            "artifacts": {
                "output_model": {
                    "artifacts": [{
                        "name": "output_model",
                        "type": {"schemaTitle": "system.Model"},
                        "uri": "gs://some-bucket/model"
                    }]
                },
                "metrics": {
                    "artifacts": [{
                        "name": "metrics",
                        "type": {"schemaTitle": "system.Metrics"},
                        "uri": "gs://some-bucket/metrics"
                    }]
                }
            },
            "outputFile": "/tmp/out/output.json"
        }
    }
    return ex_input

@pytest.fixture
def component_path():
    p = "../components/artifact_component.yaml"
    return p

def test_artifact_component(executor_input: dict, component_path: str):
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
        expected = {
            'artifacts': {
                'output_model': {
                    'artifacts': [{
                        'name': 'output_model',
                        'uri': 'gs://some-bucket/model',
                        'metadata': {}
                    }]
                },
                'metrics': {
                    'artifacts': [{
                        'name': 'metrics',
                        'uri': 'gs://some-bucket/metrics',
                        'metadata': {'score': 1000, 'comment': 'Amazing!'}}
                    ]}
            }
        }
        logging.info(f"Expected json: {expected}")
        assert recieved == expected, f"Recieved json != expected: received = {recieved}"
        
        # verify artifacts
        logging.info("Checking artifacts...")
        container_model_path = executor_input["outputs"]["artifacts"][
            "output_model"]["artifacts"][0]["uri"].replace("gs://", "/gcs/")
        logging.info(f"Container model path: {container_model_path}")
        model_tar = os.path.join(tmpdir, "model.tar.gz")
        logging.info(f"Writing model locally to: {model_tar}")
        mstats = utils.extract_output(
            dclient,
            container_id,
            container_model_path,
            model_tar
        )
        model_file = utils.extract_file(mstats["name"], model_tar)
        model = cloudpickle.load(model_file)
        err = f"type(model): {type(model)} != KNeighborsClassifier"
        assert type(model) == KNeighborsClassifier, err
    finally:
        # cleanup
        c = dclient.containers.get(container_id)
        c.remove()
        logging.info(f"Pruned container {container_id}")
        logging.info(f"Done.")