import pyttsx3, time

def main():
    engine = pyttsx3.init()
    while True:
        try:
            engine.say("System online. Destiny läuft stabil.")
            engine.runAndWait()
            time.sleep(600)
        except Exception:
            time.sleep(10)


if __name__ == "__main__":
    main()
