import os
from pathlib import Path
from typing import Optional
import logging

import librosa
import numpy as np

from celery import Celery
from celery.result import AsyncResult
from deepspeech import Model

CELERY_NAME = os.getenv("CELERY_NAME", "celery_tasks")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/10")
CELERY_BACKEND_URL = os.getenv("CELERY_BACKEND_URL", None)
DEEPSPEECH_MODEL = os.getenv("DEEPSPEECH_MODEL", None)
DEEPSPEECH_SCORER = os.getenv("DEEPSPEECH_SCORER", None)

CELERYAPP = Celery(CELERY_NAME, broker=CELERY_BROKER_URL, backend=CELERY_BACKEND_URL)

@CELERYAPP.task
def process(filename: str):
    """Extract text from the given audio file. The audio file passed in should
    can be in any format that librosa understand. Librosa will read and
    resample the file as necessary before passing it to DeepSpeech for text
    extraction.

    While this function is a celery task, it can also be used a pure model

    Arguments
    ---------
    filename : str
        Filepath to the audio file to process.

    Returns
    -------
    A string of text extracted from the audio file, or None if the process
    failed.
    """
    if not Path(filename).exists():
        logging.error("File does not exist: %s", filename)
        return None

    if not DEEPSPEECH_MODEL or not Path(DEEPSPEECH_MODEL).exists():
        logging.error("Not processing audio file. Deepspeech model file cannot be found: %s", DEEPSPEECH_MODEL)
        return None

    if not DEEPSPEECH_SCORER or not Path(DEEPSPEECH_SCORER).exists():
        logging.error("Not processing audio file. Deepspeech scorer file cannot be found: %s", DEEPSPEECH_SCORER)
        return None

    try:
        ds = Model(DEEPSPEECH_MODEL)
        ds.enableExternalScorer(DEEPSPEECH_SCORER)
    except RuntimeError as err:
        logging.error("Failed to create model: %s", err)
        return None

    try:
        audio, fs = librosa.load(filename, sr=ds.sampleRate())
        audio = np.int16(audio * (2**16 / 2))
    except Exception as err:
        logging.error("Error loading file %s: %s", filename, err)
        return None

    logging.info("Processing file: ", filename)
    text = ds.stt(audio)
    return text


def is_task_ready(task_id: str) -> bool:
    """If using the speech-to-text processing as a celery task, you can check
    the status of the task using this function.

    Arguments
    ---------
    task_id : str
        The task id from the AsyncResult returned when using `process` as a
        celery task.

    Returns
    -------
    A boolean value explaining whether
    """
    if not CELERY_BACKEND_URL:
        raise RuntimeError("No backend is configured. Results will not be stored.")

    result = AsyncResult(task_id)
    return result.ready()


def get_task_result(task_id: str) -> Optional[str]:
    """Get the result of a task.

    Arguments
    ---------
    task_id : str
        The task id from the AsyncResult returned when using `process` as a
        celery task.

    Returns
    -------
    The text extrated from the audio file if available, otherwise None
    """

    if not is_task_ready(task_id):
        return None

    result = AsyncResult(task_id)
    return result.get(propagate=False, timeout=1)
