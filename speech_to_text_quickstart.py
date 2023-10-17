# Quickstart taken from: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-speech-to-text?tabs=windows%2Cterminal&pivots=programming-language-python

import azure.cognitiveservices.speech as speechsdk

# Set your own subscription key and service region for the Speech Service
speech_key = "<your_speech_key>"
service_region = "<your_service_region>"

# Configure speech translation
speech_translation_config = speechsdk.translation.SpeechTranslationConfig(subscription=speech_key, region=service_region)
speech_translation_config.speech_recognition_language="en-GB"

# Set target language
target_language = "fr"
speech_translation_config.add_target_language(target_language)

# Configure audio input
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
translation_recognizer = speechsdk.translation.TranslationRecognizer(translation_config=speech_translation_config, audio_config=audio_config)

# Start recognition
print("Speak into your microphone.")
while True:
    translation_recognition_result = translation_recognizer.recognize_once_async().get()

    if translation_recognition_result.reason == speechsdk.ResultReason.TranslatedSpeech:
        print("Recognized: {}".format(translation_recognition_result.text))
        print("""Translated into '{}': {}""".format(
            target_language, 
            translation_recognition_result.translations[target_language]))
    elif translation_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(translation_recognition_result.no_match_details))
    elif translation_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = translation_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
