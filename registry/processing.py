"""
Process webhook payloads by submitting and monitoring HTCondor jobs.
"""

import contextlib
import os
import pathlib
import re
import shlex
import textwrap
from typing import Optional, Union

import classad  # type: ignore[import-not-found]  # pylint: disable=import-error
import flask
import htcondor  # type: ignore[import-not-found]  # pylint: disable=import-error

from registry.database import AccessKind, State, WebhookPayload

__all__ = [
    "finalize",
    "process",
]


@contextlib.contextmanager
def local_chdir(path: Union[str, os.PathLike]):
    """
    Temporarily change the current working directory.

    As a context manager: 'with local_chdir(path): ...'.
    """
    oldcwd = os.getcwd()
    try:
        flask.current_app.logger.debug("os.chdir: %s", path)
        os.chdir(path)
        yield
    finally:
        flask.current_app.logger.debug("os.chdir: %s", oldcwd)
        os.chdir(oldcwd)


# --------------------------------------------------------------------------


def get_soteria_constraint(
    *,
    job_ad: Optional[classad.ClassAd] = None,
    payload: Optional[WebhookPayload] = None,
) -> str:
    """
    Return the expression for selecting the corresponding HTCondor job.
    """
    soteria_id = None
    if job_ad:
        soteria_id = job_ad["SOTERIA_ID"]
    elif payload:
        soteria_id = payload.id_

    if not soteria_id:
        return "False"
    return f"(SOTERIA_ID == {classad.quote(soteria_id)})"


def get_submit_dir(payload: WebhookPayload) -> pathlib.Path:
    """
    Return the path to the given payload's HTCondor submit directory.
    """
    app = flask.current_app
    return pathlib.Path(app.config["DATA_DIR"]) / "htcondor" / "jobs" / payload.id_


def write_job_executable(
    payload: WebhookPayload,
    target_dir: pathlib.Path,
) -> pathlib.Path:
    """
    Write the executable script for the given payload's HTCondor job.
    """
    resource = shlex.quote(payload.resource)
    exe_file = target_dir / "run.sh"
    with open(exe_file, mode="w", encoding="utf-8") as fp:
        print(
            textwrap.dedent(
                f"""\
                #!/bin/sh
                apptainer build image.sif docker://{resource}
                status=$?
                rm -f image.sif
                exit ${{status}}
                """
            ),
            file=fp,
        )
    exe_file.chmod(0o755)
    return exe_file


# --------------------------------------------------------------------------


def get_htcondor_job(payload: WebhookPayload) -> Optional[classad.ClassAd]:
    """
    Return the HTCondor job in the queue for the given payload.
    """
    schedd = htcondor.Schedd()
    ads = schedd.query(constraint=get_soteria_constraint(payload=payload))
    return ads[0] if ads else None


def submit_htcondor_job(payload: WebhookPayload) -> classad.ClassAd:
    """
    Prepare and submit an HTCondor job for the given payload.
    """
    submit_dir = get_submit_dir(payload)
    submit_dir.mkdir(parents=True, exist_ok=True)
    job_exe = write_job_executable(payload, submit_dir)

    schedd = htcondor.Schedd()
    job = htcondor.Submit(
        {
            "executable": job_exe.name,
            "My.FROM_SOTERIA": True,
            "My.SOTERIA_ID": classad.quote(payload.id_),
            "My.SOTERIA_RESOURCE": classad.quote(payload.resource),
            "My.SOTERIA_PROJECT": classad.quote(payload.project),
            "My.SOTERIA_REPOSITORY": classad.quote(payload.repository),
            #
            "request_cpus": "2",
            "request_memory": "4G",
            "request_disk": "50G",
            #
            "log": f"{job_exe.name}.log",
            "output": f"{job_exe.name}.out",
            "error": f"{job_exe.name}.err",
        }
    )
    with local_chdir(submit_dir):
        result = schedd.submit(job, spool=True)
        schedd.spool(list(job.jobs(clusterid=result.cluster())))
    return result.clusterad()


def update_htcondor_job(job_ad: classad.ClassAd) -> Optional[State]:
    """
    Determine the current state of the given HTCondor job.
    """
    schedd = htcondor.Schedd()
    status = htcondor.JobStatus(job_ad["JobStatus"])

    if status in [htcondor.JobStatus.HELD, htcondor.JobStatus.REMOVED]:
        return State.failed

    if status in [htcondor.JobStatus.COMPLETED]:
        schedd.retrieve(get_soteria_constraint(job_ad=job_ad))
        return State.completed

    return None


# --------------------------------------------------------------------------


def process(payload: WebhookPayload) -> Optional[State]:
    """
    Determine what to do with a payload, and return its new state.
    """
    app = flask.current_app
    new_state = None

    if payload.access_kind != AccessKind.public_and_tagged:
        return State.skipped

    if not re.match(app.config["WEBHOOKS_HARBOR_RESOURCE_REGEX"], payload.resource):
        return State.skipped

    if job := get_htcondor_job(payload):
        new_state = update_htcondor_job(job)
    else:
        cluster_ad = submit_htcondor_job(payload)
        app.logger.info(f"Submitted HTCondor cluster:\n{cluster_ad}")

    return new_state


def finalize(_: WebhookPayload) -> None:
    """
    Perform any final actions for a 'completed' payload.
    """
    # NOTE (baydemir): Nothing to do, yet?
