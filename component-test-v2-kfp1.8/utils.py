
import yaml
import json
import os
import utils
import docker
import logging
import tarfile
import datetime as dt
from typing import List
from requests.exceptions import ReadTimeout
from typing import List, AnyStr


def get_cmd(comp_yaml: str) -> List:
    """Extract the command from a v2 component yaml file
    
    args:
        comp_yaml(str): path to v2 component yaml

    Returns:
        The extracted command as a list type. 
    """
    with open(comp_yaml, 'r') as f:
        y = yaml.safe_load(f.read())
    cmd = y["implementation"]["container"]["command"]
    return cmd


def get_args(comp_yaml: str) -> List:
    """Extract the args from a v2 component yaml file
    
    args:
        comp_yaml(str): path to v2 component yaml

    Returns:
        The extracted args as a list type. 
    """
    with open(comp_yaml, 'r') as f:
        y = yaml.safe_load(f.read())
    args = y["implementation"]["container"]["args"]
    # yaml loads the executor input as a dictionary
    # we need it as a json string for downstream
    assert args[0] == "--executor_input"  # check formatting
    assert list(args[1].keys()) == ["executorInput"], f"{print(args)}"
    args[1] = json.dumps(args[1])  
    return args


def get_image(comp_yaml: str) -> AnyStr:
    """Extract the image from a v2 component yaml file
    
    args:
        comp_yaml(str): path to v2 component yaml

    Returns:
        The extracted image as a String type. 
    """
    with open(comp_yaml, 'r') as f:
        y = yaml.safe_load(f.read())
    image = y["implementation"]["container"]["image"]
    return image


def docker_run(
    component_yaml_path: str,
    inputs: dict,
    docker_client: docker.DockerClient,
    loglevel : int = logging.DEBUG,
    timeout: int = 600
):
    """Run kfp v2 component on docker"""
    logger = logging.getLogger()
    logger.setLevel(level=loglevel)

    start = dt.datetime.now()
    # construct component command
    image = utils.get_image(component_yaml_path)
    cmd = utils.get_cmd(component_yaml_path)
    args = utils.get_args(component_yaml_path)
    args[1] = json.dumps(inputs)

    combined_cmd = cmd + args

    logger.debug("Command to run: ")
    logging.info(str(combined_cmd))
    
    # run in docker
    dclient = docker_client
    container = dclient.containers.run(
        image=image,
        command=combined_cmd,
        detach=True,
        stderr=True
    )
    assert container.status == "created"
    logging.info(f"Created container: {container.short_id}")
    for line in container.logs(stream=True, timestamps=True):
        logging.info(line)
        now = dt.datetime.now()
        total_secs = (now - start).total_seconds()
        if total_secs > timeout:
            raise ReadTimeout
    # container.wait(timeout=timeout - total_secs)
    # check status
    cont_after = dclient.containers.get(container.id)
    logging.info(f"Container status: {cont_after.status}")
    assert cont_after.status == "exited"
    # & exit code?
    return container.id


def docker_exec(
    component_yaml_path: str,
    inputs: dict,
    docker_client: docker.DockerClient,
    container_id: str,
    loglevel : int = logging.DEBUG,
    timeout: int = 600
):
    """Run kfp v2 component on docker"""
    logger = logging.getLogger()
    logger.setLevel(level=loglevel)

    start = dt.datetime.now()
    # construct component command
    image = utils.get_image(component_yaml_path)
    cmd = utils.get_cmd(component_yaml_path)
    args = utils.get_args(component_yaml_path)

    args[1] = json.dumps(inputs)

    combined_cmd = cmd + args

    logger.debug(str(combined_cmd))
    
    # run in docker
    dclient = docker_client
    container = dclient.containers.get(container_id)
    (exit_status, output) = container.exec_run(
        cmd=combined_cmd,
        # detach=True,
        stderr=True
    )
    return (exit_status, output)


def extract_output(
    d_client: docker.DockerClient,
    container_id: str,
    output_path: str,
    local_tar_path: str
):
    """Extract output to local tarfile
    
    Returns:
        Archive stats (from docker container get_archive)    
    """
    # extract file from container
    container = d_client.containers.get(container_id)
    output_archive, stats = container.get_archive(output_path)
    # (output_archive is a generator of a binary)
    with open(local_tar_path, 'wb') as trball:
        for line in output_archive:
            trball.write(line)
    assert os.path.exists(local_tar_path), f"Tar write failed for {local_tar_path}"
    return stats


def extract_file(filename: str, tar_path: str):
    """Extract file from tar.gz file
    
    Returns:
        Output binary file handle
    """
    # extract file from tar
    tr = tarfile.open(tar_path)
    output_f = tr.extractfile(filename)
    return output_f
    
    