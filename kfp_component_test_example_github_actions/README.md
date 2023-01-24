
# kfp-component-test-example-github-actions

## Introduction
This example explores a solution to testing Kubeflow Pipelines (KFP) components on a local Kubernetes cluster running as part of GitHub Actions jobs. The example assumes no access to a KFP or Kubernetes cluster. All resources are provisioned as needed on GitHub Actions VM, and cleaned up after the jobs complete.

## Example Code Files

```bash
├── .github
│   └── workflows
│       └── k3s-hello-component-test.yml
├── README.md
└── kfp_component_test_example_github_actions
    ├── README.md
    ├── example_pipe
    │   ├── components
    │   │   ├── __init__.py
    │   │   └── hello_comp.py
    │   └── hello_pipeline.py
    └── tests
        ├── __init__.py
        ├── test_hello.py
        └── test_hello_kfp.py
```

The repo is structured as follows:
1. Component and Pipeline
    - There is an example KFP component (python function) in `example_pipe/components/hello_comp.py`. The fuction takes a name string, checks if it is alphabetic, and then returns "Hello <name>!" for alphabetic strings, and "Hello!" otherwise.
    - There is an example one-component KFP pipeline in `hello_pipeline.py` that wraps the example hello component (so the component is tested in the context of a pipeline).

2. Tests
    - `tests/test_hello.py` contains two `pytest` tests that serve as reference tests. One tests the component code (python function only) against the name "Doug", and the other tests against the name "Alice3000". The first test is meant to pass, while the second is meant to fail. The tests can be run locally (on your computer) with `pytest tests/test_hello.py`, which is dependent on `pytest` being installed.
    - `tests/test_hello_kfp.py` contains counterpart tests (Doug and Alice3000) to `test_hello.py`, however, now the tests are run on a Kubernetes cluster containing KFP. The component is run on the intended base image as part of a pipeline, and the output is validated. Note that the test assumes the cluster environment is up, which is what the GitHub Actions job does.

3. GitHub Actions Jobs
    - `.github/workflows/k3s-hello-component-test.yml` is a GitHub action that runs two jobs (one for the Doug test, and one for the Alice3000 test). The jobs both spin up local Kubernetes k3s clusters, install KFP, run the one-component pipeline with the respective input, and validate the output. The jobs could easily be combined for better efficiency, but for example purposes, this approach demonstrates both success and failure, as well as parallel running jobs. The action is triggered by a 'push' event, as indicated by the `on: push` designation in the second line of the `yml` file.

## Run the Example
To test out this example, fork the code, and make a push to your fork. Then go to the Actions section in the repo to see your jobs spin up. You can click around in the jobs to see more details. You should see the "Doug" job succeed, and the "Alice3000" job fail. Prior to this, there are steps that show the spinning up of the Kubernetes cluser and installation of KFP.

## Background Motivation
There is a lot to think about when testing pipelines that run on distributed clusters. End-to-end test can be time consuming, costly, and complex to set up and run; while local testing often overlooks important computing environment factors. 

There is a need for middle-ground local component tests, that allow for the validation of pipeline component code run in the intended image/container environment. One challenge is handling the inputs and outputs the container is expected to consume and produce.

This repo was originally built as a concept exploring local Kubeflow Pipelines (KFP) components CI using GitHub Actions--it is a basic prototype, no more, no less. This is a sandbox idea, turned sharable. As such, it is not intended to be robustly developed, much less production ready at this point. Hopefully it is useful as a conceptual starting point for some.

