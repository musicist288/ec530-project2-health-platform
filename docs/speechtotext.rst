Speech To Text
==============

MedOps includes a speech-to-text where users can submit an audio file
to be analyzed. The speech-to-text service is built using
`Mozilla's DeepSpeech <https://deepspeech.readthedocs.io/en/r0.9/>`_
project. To stand up the service you'll need to download the pretrained
models (or train your own) and make sure that their filepaths are set
in the correct environment variables before the application loads the service.

In addition to using deepmind, the :py:ref:process: function can be used
as a Celery task.


Environment Variables
^^^^^^^^^^^^^^^^^^^^^
The following environment variables must be set in order to use the speech-to-text
module.

* CELERY_NAME - The name to give to the celery app.
* CELERY_BROKER_URL - URL to the broker backend for celery to use.
* CELERY_BACKEND_URL - The URL of the backend to store result tasks. You'll
  need this set so that speech to text results are handled.
* DEEPSPEECH_MODEL - The filepath to the trained model for speech-to-text
  recognition
* DEEPSPEECH_SCORER - The filepath to the trained scoring model for deepsearch.


Setting Up DeepSpeech
^^^^^^^^^^^^^^^^^^^^^
Make sure to follow the steps on
`DeepSpeech’s documentation <https://deepspeech.readthedocs.io/en/r0.9/>`_ to
get deep mind setup. There are publically available training models available,
or you can train your own.


API Usage
^^^^^^^^^
Make sure to check out :ref:`rest-api-documentation`.

.. currentmodule:: medops.speech2text

.. autofunction:: process

|

.. autofunction:: is_task_ready

|

.. autofunction:: get_task_result
