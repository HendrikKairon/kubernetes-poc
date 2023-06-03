import logging
import uuid
import os
from dotenv import load_dotenv
from kubernetes import client, config

# Load .env file
load_dotenv()

NAMESPACE = os.getenv("NAMESPACE")
IMAGE = os.getenv("IMAGE")
JOB_LABELS = {"app": os.getenv("JOB_LABEL_APP")}

logging.basicConfig(level=logging.INFO)


config.load_kube_config()


def create_job_object(job_name: str, symbol: str) -> client.V1Job:
    """Create a Kubernetes job object.

    This function constructs a Kubernetes Job object with a specified job_name and
    symbol. The Job runs a 'bot' container that executes a 'bot.py' script using
    the provided symbol as an argument.

    Args:
        job_name (str): The name to assign to the job.
        symbol (str): The symbol to pass as an argument to the 'bot.py' script.

    Returns:
        client.V1Job: A Kubernetes Job object.
    """

    # Define the 'bot' container to run within the Job's Pod.
    # The 'bot.py' script in the container is run with the provided symbol as an argument.
    container = client.V1Container(
        name="bot",
        image=IMAGE,
        image_pull_policy="Always",
        args=["python3", "bot.py", symbol],
    )

    # Define the Pod's template spec. This includes metadata about the Pod (like labels)
    # and the spec of the Pod itself (such as what containers it should run).
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels=JOB_LABELS),
        spec=client.V1PodSpec(
            restart_policy="Never",
            containers=[container],
            image_pull_secrets=[client.V1LocalObjectReference(name="dockerhubcred")],
        ),
    )

    # Define the spec for the Job. This includes the template for the Pod it should run
    # and a 'backoff_limit', which is the number of times to retry the job before considering it failed.
    spec = client.V1JobSpec(template=template, backoff_limit=4)

    # Define the Job object. This includes the API version, the kind of the object (Job),
    # metadata (like the name of the Job), and the spec of the Job itself.
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=job_name),
        spec=spec,
    )

    # Return the created Job object.
    return job


def create_job(kube_batch_api: client.BatchV1Api, job: client.V1Job) -> str:
    """Create a new Kubernetes job."""
    try:
        api_response = kube_batch_api.create_namespaced_job(
            body=job, namespace=NAMESPACE
        )
        return str(api_response.status)
    except client.exceptions.ApiException as e:
        logging.error("Failed to create job: %s", e)
        return None


def delete_job(job_name: str) -> None:
    """Delete a Kubernetes job."""
    try:
        kube_batch_api = client.BatchV1Api()
        kube_batch_api.delete_namespaced_job(
            name=job_name,
            namespace=NAMESPACE,
            # grace_period_seconds' sets the time for processes to shutdown before forced termination.
            # I set it to 0 here to just kill it off for the POC
            # This sends a signal to the pod but might still take a few seconds before its being shut down
            body=client.V1DeleteOptions(
                propagation_policy="Foreground", grace_period_seconds=0
            ),
        )
    except client.exceptions.ApiException as e:
        logging.error("Failed to delete job %s: %s", job_name, e)
