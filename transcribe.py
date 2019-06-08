# !/usr/bin/env python
# coding: utf-8
import argparse
import io
import sys
import codecs
import datetime
import locale

def transcribe_gcs(gcs_uri):
    from google.cloud import speech_v1p1beta1 as speech
    from google.cloud.speech_v1p1beta1 import enums
    from google.cloud.speech_v1p1beta1 import types
    client = speech.SpeechClient()

    audio = types.RecognitionAudio(uri=gcs_uri)
    config = types.RecognitionConfig(
        # sample_rate_hertz=16000,
        sample_rate_hertz=32000,
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        enable_speaker_diarization=True,
        diarization_speaker_count=2,
        language_code='ja-JP')

    operation = client.long_running_recognize(config, audio)

    print('Waiting for operation to complete...')
    operationResult = operation.result()

    d = datetime.datetime.today()
    today = d.strftime("%Y%m%d-%H%M%S")
    fout = codecs.open('output{}.txt'.format(today), 'a', 'shift_jis')

    print(operationResult)

    speaker_1_words = ""
    speaker_1_s = float(0)
    speaker_2_words = ""
    speaker_2_s = float(0)

    for word in operationResult.results[-1].alternatives[0].words:
        tmp_word = u'{}'.format(word.word.split("|")[0])

        start_time = float(word.start_time.seconds) + float(word.start_time.nanos) / 1000 / 1000 / 1000
        end_time = float(word.end_time.seconds) + float(word.end_time.nanos) / 1000 / 1000 / 1000

        print(start_time)
        print(end_time)
        s = end_time - start_time
        print(s)

        if word.speaker_tag == 1:
            speaker_1_s += s
            speaker_1_words += tmp_word
        else:
            speaker_2_s += s
            speaker_2_words += tmp_word

    fout.write("speaker_1: \n")
    fout.write(speaker_1_words)

    fout.write("\n")

    fout.write("s: ")
    fout.write(speaker_1_s)

    fout.write("\n")

    fout.write("speaker_2: \n")
    fout.write(speaker_2_words)

    fout.write("\n")

    fout.write("s: ")
    fout.write(speaker_2_s)
    #fout.write(u'{}\n'.format(operationResult.results[-1].alternatives.words))

    #for result in operationResult.results:
    #  for alternative in result.alternatives:
    #      fout.write(u'{}\n'.format(alternative.transcript))
    fout.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        'path', help='GCS path for audio file to be recognized')
    args = parser.parse_args()
    transcribe_gcs(args.path)
