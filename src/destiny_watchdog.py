import time, os

SERVICES = ["destiny_gui", "destiny_core", "destiny_monitor"]


def main():
    while True:
        for svc in SERVICES:
            os.system(f"systemctl restart {svc}.service --no-block")
        time.sleep(900)


if __name__ == "__main__":
    main()
