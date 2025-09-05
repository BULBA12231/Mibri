"""
Заготовка для голосовых вызовов по зашифрованному UDP.

Идея:
- Сигнализация через существующий TCP-сервер (обмен SDP-данными/парами сокетов).
- RTP-пакеты шифровать NaCl SecretBox (или SRTP) поверх UDP.
- Захват/воспроизведение аудио: sounddevice/pyaudio.
- Кодек: opus (через pyAV/opuslib).

Это файл-заготовка. Полная реализация требует зависимостей и тестов сети/NAT.
"""

class VoiceCallStub:
    def __init__(self, local_user: str, remote_user: str):
        self.local_user = local_user
        self.remote_user = remote_user

    def start_call(self) -> None:
        print("[voice] Not implemented. This is a stub for future work.")

    def accept_call(self) -> None:
        print("[voice] Not implemented. This is a stub for future work.")

    def hangup(self) -> None:
        print("[voice] Not implemented. This is a stub for future work.")
