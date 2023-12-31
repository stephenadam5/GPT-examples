# This repository contains a Python script for audio transcription and AI-driven chat. It combines the Microsoft 
# Speech Service for transcription and OpenAI's GPT-3.5-turbo for interactive conversations. The user-friendly Tkinter-based 
# interface makes it easy to use. Great for transcription services and chatbot development.

# Import modules
import openai
import logging
import sys
import requests
import time
import swagger_client
import tiktoken
import os
import tkinter as tk
import openai

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
        format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p %Z")

# Your subscription key and region for the speech service
SUBSCRIPTION_KEY = "<your_speech_key>"
SERVICE_REGION = "<your_speech_region>"

NAME = "Simple transcription"
DESCRIPTION = "Simple transcription description"

LOCALE = "en-US"

RECORDINGS_BLOB_URI = "<Your SAS Uri to a audio file>"
# Or
RECORDINGS_CONTAINER_URI = "<Your SAS Uri to a container of audio files>"

# Set model information when doing transcription with custom models
MODEL_REFERENCE = None  # guid of a custom model

def transcribe_from_single_blob(uri, properties):
    """
    Transcribe a single audio file located at `uri` using the settings specified in `properties`
    using the base model for the specified locale.
    """
    transcription_definition = swagger_client.Transcription(
        display_name=NAME,
        description=DESCRIPTION,
        locale=LOCALE,
        content_urls=[uri],
        properties=properties
    )

    return transcription_definition


def transcribe_with_custom_model(client, uri, properties):
    """
    Transcribe a single audio file located at `uri` using the settings specified in `properties`
    using the base model for the specified locale.
    """
    # Model information (ADAPTED_ACOUSTIC_ID and ADAPTED_LANGUAGE_ID) must be set above.
    if MODEL_REFERENCE is None:
        logging.error("Custom model ids must be set when using custom models")
        sys.exit()

    model = {'self': f'{client.configuration.host}/models/{MODEL_REFERENCE}'}

    transcription_definition = swagger_client.Transcription(
        display_name=NAME,
        description=DESCRIPTION,
        locale=LOCALE,
        content_urls=[uri],
        model=model,
        properties=properties
    )

    return transcription_definition


def transcribe_from_container(uri, properties):
    """
    Transcribe all files in the container located at `uri` using the settings specified in `properties`
    using the base model for the specified locale.
    """
    transcription_definition = swagger_client.Transcription(
        display_name=NAME,
        description=DESCRIPTION,
        locale=LOCALE,
        content_container_url=uri,
        properties=properties
    )

    return transcription_definition


def _paginate(api, paginated_object):
    """
    The autogenerated client does not support pagination. This function returns a generator over
    all items of the array that the paginated object `paginated_object` is part of.
    """
    yield from paginated_object.values
    typename = type(paginated_object).__name__
    auth_settings = ["api_key"]
    while paginated_object.next_link:
        link = paginated_object.next_link[len(api.api_client.configuration.host):]
        paginated_object, status, headers = api.api_client.call_api(link, "GET",
            response_type=typename, auth_settings=auth_settings)

        if status == 200:
            yield from paginated_object.values
        else:
            raise Exception(f"could not receive paginated data: status {status}")


def delete_all_transcriptions(api):
    """
    Delete all transcriptions associated with your speech resource.
    """
    logging.info("Deleting all existing completed transcriptions.")

    # get all transcriptions for the subscription
    transcriptions = list(_paginate(api, api.get_transcriptions()))

    # Delete all pre-existing completed transcriptions.
    # If transcriptions are still running or not started, they will not be deleted.
    for transcription in transcriptions:
        transcription_id = transcription._self.split('/')[-1]
        logging.debug(f"Deleting transcription with id {transcription_id}")
        try:
            api.delete_transcription(transcription_id)
        except swagger_client.rest.ApiException as exc:
            logging.error(f"Could not delete transcription {transcription_id}: {exc}")


def transcribe():
    logging.info("Starting transcription client...")

    # configure API key authorization: subscription_key
    configuration = swagger_client.Configuration()
    configuration.api_key["Ocp-Apim-Subscription-Key"] = SUBSCRIPTION_KEY
    configuration.host = f"https://{SERVICE_REGION}.api.cognitive.microsoft.com/speechtotext/v3.1"

    # create the client object and authenticate
    client = swagger_client.ApiClient(configuration)

    # create an instance of the transcription api class
    api = swagger_client.CustomSpeechTranscriptionsApi(api_client=client)

    # Specify transcription properties by passing a dict to the properties parameter. See
    # https://learn.microsoft.com/azure/cognitive-services/speech-service/batch-transcription-create?pivots=rest-api#request-configuration-options
    # for supported parameters.
    properties = swagger_client.TranscriptionProperties()
    # properties.word_level_timestamps_enabled = True
    # properties.display_form_word_level_timestamps_enabled = True
    # properties.punctuation_mode = "DictatedAndAutomatic"
    # properties.profanity_filter_mode = "Masked"
    # properties.destination_container_url = "<SAS Uri with at least write (w) permissions for an Azure Storage blob container that results should be written to>"
    # properties.time_to_live = "PT1H"

    # uncomment the following block to enable and configure speaker separation
    # properties.diarization_enabled = True
    # properties.diarization = swagger_client.DiarizationProperties(
    #     swagger_client.DiarizationSpeakersProperties(min_count=1, max_count=5))

    # properties.language_identification = swagger_client.LanguageIdentificationProperties(["en-US", "ja-JP"])

    # Use base models for transcription. Comment this block if you are using a custom model.
    transcription_definition = transcribe_from_single_blob(RECORDINGS_BLOB_URI, properties)

    # Uncomment this block to use custom models for transcription.
    # transcription_definition = transcribe_with_custom_model(client, RECORDINGS_BLOB_URI, properties)

    # uncomment the following block to enable and configure language identification prior to transcription
    # Uncomment this block to transcribe all files from a container.
    # transcription_definition = transcribe_from_container(RECORDINGS_CONTAINER_URI, properties)

    created_transcription, status, headers = api.transcriptions_create_with_http_info(transcription=transcription_definition)

    # get the transcription Id from the location URI
    transcription_id = headers["location"].split("/")[-1]

    # Log information about the created transcription. If you should ask for support, please
    # include this information.
    logging.info(f"Created new transcription with id '{transcription_id}' in region {SERVICE_REGION}")

    logging.info("Checking status.")

    completed = False

    while not completed:
        # wait for 5 seconds before refreshing the transcription status
        time.sleep(5)

        transcription = api.transcriptions_get(transcription_id)
        logging.info(f"Transcriptions status: {transcription.status}")

        if transcription.status in ("Failed", "Succeeded"):
            completed = True

        if transcription.status == "Succeeded":
            pag_files = api.transcriptions_list_files(transcription_id)
            for file_data in _paginate(api, pag_files):
                if file_data.kind != "Transcription":
                    continue

                audiofilename = file_data.name
                results_url = file_data.links.content_url
                results = requests.get(results_url)
                return results
                logging.info(f"Results for {audiofilename}:\n{results.content.decode('utf-8')}")
        elif transcription.status == "Failed":
            logging.info(f"Transcription failed: {transcription.properties.error.message}")

d = transcribe()

json_data = d.json()

# Access the combinedRecognizedPhrases key
text = json_data["combinedRecognizedPhrases"][1]["display"]
# print(text)


openai.api_type = "azure"
openai.api_base = "https://YOUR_DEPLOYMENT_ID.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key ="<YOUR_API_KEY>"

import tkinter as tk

system_message = {"role": "system", "content": "You are a helpful assistant who answers questions based of the following transcript: " + text + ". Summary:"}
max_response_tokens = 250
token_limit = 4096
conversation = []
conversation.append(system_message)


def num_tokens_from_messages(messages):
    encoding= tiktoken.get_encoding("cl100k_base")  #model to encoding mapping https://github.com/openai/tiktoken/blob/main/tiktoken/model.py
    num_tokens = 0
    for message in messages:
        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":  # if there's a name, the role is omitted
                num_tokens += -1  # role is always required and always 1 token
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens

def send_message():
    user_input = input_box.get()
    conversation.append({"role": "user", "content": user_input})
    conv_history_tokens = num_tokens_from_messages(conversation)

    while conv_history_tokens + max_response_tokens >= token_limit:
        del conversation[1] 
        conv_history_tokens = num_tokens_from_messages(conversation)

    response = openai.ChatCompletion.create(
        engine="gpt-35-turbo", # The deployment name you chose when you deployed the GPT-35-Turbo or GPT-4 model.
        messages=conversation,
        temperature=0.7,
        max_tokens=max_response_tokens,
        stop=["\n\n"],
    )

    conversation.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
    output_box.insert(tk.END, "\n" + response['choices'][0]['message']['content'] + "\n")
    input_box.delete(0, tk.END)

# Create the UI
root = tk.Tk()
root.title("AI Assistant")

# Create the input box
input_box = tk.Entry(root, width=50)
input_box.pack(side=tk.LEFT, padx=5, pady=5)

# Create the send button
send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(side=tk.LEFT, padx=5, pady=5)

# Create the output box
output_box = tk.Text(root, width=50, height=20)
output_box.pack(side=tk.LEFT, padx=5, pady=5)

# Start the main loop
root.mainloop()

if not root.winfo_exists():
    root.quit()
