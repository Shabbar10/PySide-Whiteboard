import time
from collections import deque
import threading

circular_buffer = deque(maxlen=5)


def append_data():
    while True:
        print(f"Reader Thread : {threading.current_thread().name} ")
        circular_buffer.appendleft("hello")
        print("\nAppended : hello")
        time.sleep(1)


def pop_data():
    while True:
        print(f"Writer Thread : {threading.current_thread().name} ")
        try:
            print(circular_buffer.pop())
        except IndexError:
            print("OVERFLOW\n")
        time.sleep(1)


def main() -> None:
    try:
        # Create reader threads
        for i in range(5):
            reader = threading.Thread(target=append_data)
            reader.start()

        # Create writer threads
        for i in range(7):
            writer = threading.Thread(target=pop_data)
            writer.start()

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Exiting...")


main()
