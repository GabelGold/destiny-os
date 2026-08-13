#!/usr/bin/env python3
"""
Destiny Voice Commander – sehr einfache Sprachsteuerung (Stub).
"""

import time

try:
    import speech_recognition as sr
except ImportError:
    sr = None
    print("⚠ SpeechRecognition nicht installiert – Voice Commander läuft nur im Dummy-Modus.")


def loop():
    if sr is None:
        while True:
            print("🎙 Voice Commander Stub aktiv – keine echte Erkennung.")
            time.sleep(10)
    else:
        r = sr.Recognizer()
        mic = sr.Microphone()
        print("🎙 Voice Commander bereit – 'Strg+C' zum Beenden (im manuellen Start).")
        while True:
            with mic as source:
                print("… höre zu …")
                audio = r.listen(source)
            try:
                text = r.recognize_google(audio, language="de-DE")
                print(f"🗣 Gehört: {text}")
            except Exception as e:
                print(f"⚠ Erkennungsfehler: {e}")


if __name__ == "__main__":
    loop()
