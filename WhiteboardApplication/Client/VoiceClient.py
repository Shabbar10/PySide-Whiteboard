import socket
import pyaudio
import threading
import time

class VoiceClient:
    def __init__(self):
        # Audio settings
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.audio = pyaudio.PyAudio()

        # Voice stream
        self.stream = self.audio.open(
            format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE,
            input=True, output=True, frames_per_buffer=self.CHUNK
        )

        # Socket
        self.client_socket = None
        self.is_connected = False
        self.mic_on = False

    def connect(self, server_ip, port=5000):
        """Connect to the voice server."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((server_ip, port))

            self.is_connected = True

            print("[DEBUG] Connected to voice server, starting audio threads...")
            print(f"[DEBUG] connect() running on instance: {self}")  # ✅ Debug print

            # Start threads for sending and receiving voice
            threading.Thread(target=self.receive_audio, daemon=True).start()
            threading.Thread(target=self.send_audio, daemon=True).start()
            return True
        except Exception as e:
            print(f"Voice connection failed: {e}")
            return False

    def receive_audio(self):
        """Receive and play audio from the server."""
        while self.is_connected:
            try:
                data = self.client_socket.recv(self.CHUNK)
                if not data:
                    break
                print("[CLIENT] Received voice from server")
                self.stream.write(data)
            except Exception as e:
                print(f"[CLIENT] Voice receive error: {e}")
                break

    def send_audio(self):
        """Send microphone input when mic is ON."""
        try:
            while self.is_connected:
                if self.mic_on:
                    data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                    # print(f"[DEBUG] Captured Audio Data: {data[:10]}")
                    print("Audio Received......\n")
                    self.client_socket.sendall(data)
                    time.sleep(0.02)  # Prevent flooding
                else:
                    time.sleep(0.02)  # Avoid high CPU usage
            else:
                print("no while")
        except Exception as e:
            print(f"[CLIENT] Voice send error: {e}")

    def toggle_mic(self):
        """Toggle microphone ON/OFF."""
        self.mic_on = not self.mic_on
        print(f"[DEBUG] Mic toggled: {'ON' if self.mic_on else 'OFF'}")


    def disconnect(self):
        """Disconnect from the server."""
        self.is_connected = False
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
