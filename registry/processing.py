"""
Process webhook payloads.
"""

import contextlib
import os
import pathlib
from typing import Optional, Union

import classad  # type: ignore[import-not-found]  # pylint: disable=import-error
import flask
import htcondor  # type: ignore[import-not-found]  # pylint: disable=import-error

from registry.database import AccessKind, Source, State, WebhookPayload


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
        soteria_id = job_ad.get["SOTERIA_ID"]
    elif payload:
        soteria_id = payload.id_

    if not soteria_id:
        return "False"
    return f"SOTERIA_ID == {classad.quote(soteria_id)}"


def get_submit_dir(
    payload: WebhookPayload,
    app: Optional[flask.Flask] = None,
) -> pathlib.Path:
    """
    Return the path to the payload's HTCondor submit directory.
    """
    if not app:
        app = flask.current_app
    return pathlib.Path(app.config["DATA_DIR"]) / "htcondor" / "jobs" / payload.id_


def get_htcondor_job(payload: WebhookPayload) -> Optional[classad.ClassAd]:
    """
    Return the HTCondor job in the queue for the given payload, if any.
    """
    schedd = htcondor.Schedd()
    ads = schedd.query(constraint=get_soteria_constraint(payload=payload))
    return ads[0] if ads else None


def write_job_executable(payload: WebhookPayload, target_dir: pathlib.Path) -> pathlib.Path:
    exe_file = target_dir / "run.sh"
    with open(exe_file, mode="w", encoding="utf-8") as fp:
        print("#!/bin/sh", file=fp)
        print(f"echo {payload.resource}", file=fp)
        print("sleep 10s", file=fp)
    exe_file.chmod(0o755)
    return exe_file


def submit_htcondor_job(payload: WebhookPayload) -> classad.ClassAd:
    app = flask.current_app

    submit_dir = get_submit_dir(payload, app)
    submit_dir.mkdir(parents=True, exist_ok=True)
    job_exe = write_job_executable(payload, submit_dir)

    schedd = htcondor.Schedd()
    job = htcondor.Submit(
        {
            "executable": job_exe.name,
            "My.FROM_SOTERIA": true,
            "My.SOTERIA_ID": classad.quote(payload.id_),
            "My.SOTERIA_RESOURCE": classad.quote(payload.resource),
            #
            "request_cpus": "2",
            "request_memory": "4G",
            "request_disk": "1G",
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
    app = flask.current_app
    schedd = htcondor.Schedd()

    if job_ad["JobStatus"] == 4:  # Completed
        soteria_id = classad.quote(job_ad["SOTERIA_ID"])
        schedd.retrieve(f"SOTERIA_ID == {soteria_id}")
        return State.completed


def process(payload: WebhookPayload) -> Optional[State]:
    """
    Determine what to do with a webhook payload, and return its new state.
    """
    app = flask.current_app
    new_state = None

    if payload.source != Source.harbor:
        app.logger.error(f"Unexpected payload source: {payload}")  # type: ignore[unreachable]
        return State.failed

    if payload.access_kind != AccessKind.public_and_tagged:
        return State.skipped

    if job := get_htcondor_job(payload):
        new_state = update_htcondor_job(job)
    else:
        clusterad = submit_htcondor_job(payload)
        app.logger.info(f"Submitted HTCondor cluster:\n{clusterad}")

    return new_state


def finalize_payload(payload: WebhookPayload) -> None:
    schedd = htcondor.Schedd()
    soteria_id = classad.quote(payload.id_)
    schedd.act(htcondor.JobAction.Remove, f"SOTERIA_ID == {soteria_id}")
