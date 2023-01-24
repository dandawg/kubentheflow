
import sys
import pytest
import kfp
import json
import base64
import tarfile
from io import BytesIO

sys.path.insert(1, "../")
from example_pipe.hello_pipeline import hello_pipe

# fixtures
@pytest.fixture
def name_doug():
    return "Doug"

@pytest.fixture
def name_alice3000():
    return "Alice3000"

def hello_pipeline(
    name,
    component_name="hello",
    output_param="greeting"
):
    expected_output = f"Hello {name}!"
    # setup kfp client
    endpoint = "http://127.0.0.1:30001"
    client = kfp.Client(host=endpoint)
    # run component pipe on kfp
    print("running pipe...")
    run = client.create_run_from_pipeline_func(
        pipeline_func=hello_pipe,
        arguments={"name": name}
    )
    run.wait_for_run_completion(timeout=600)

    # Check output
    # ============
    r_out = client.get_run(run.run_id)
    wfm = json.loads(r_out.pipeline_runtime.workflow_manifest)
    # status completed?
    status = wfm["status"]["phase"]
    assert status == "Succeeded", f"Expected run status \"Succeeded\". Got run status {status}"
    # we need node id, to get output for the component
    node_id = [v["id"] for k,v in wfm["status"]["nodes"].items()
        if v["templateName"] == component_name and v["type"] == "Pod"]
    assert len(node_id) == 1, f"Component name {component_name} is expected to exist and be unique."
    # read and parse the associated artifact
    output_b64 = client.runs.read_artifact(
        run.run_id, node_id[0], f"{component_name}-{output_param}"
    )
    output_gz = base64.b64decode(output_b64.data)
    tar_out = tarfile.open(fileobj=BytesIO(output_gz))
    fnames = tar_out.getnames()
    assert len(fnames) == 1
    fname = fnames[0]  # fname = 'data'
    output = tar_out.extractfile(fname).read().decode("utf-8")
    # output is as expected?
    assert output == expected_output, f"output = {output} | expected_output = {expected_output}"

# Tests
# test Doug
def test_hello_pipeline_doug(name_doug):
    hello_pipeline(name_doug)

# test Alice3000
def test_hello_pipeline_alice3000(name_alice3000):
    hello_pipeline(name_alice3000)
