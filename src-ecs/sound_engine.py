import pygame
import random
from pathlib import Path
from typing import Dict, List


class SoundEngine:
    _instance = None

    @classmethod
    def get(cls) -> "SoundEngine":
        if cls._instance is None:
            raise RuntimeError(
                "SoundEngine не инициализирован")
        return cls._instance

    @classmethod
    def init(cls, base_dir: Path, channels: int = 16, master_volume: float = 1.0, music_volume: float = 0.5) -> "SoundEngine":
        if cls._instance is None:
            cls._instance = cls(base_dir, channels,
                                master_volume, music_volume)
        return cls._instance

    def __init__(self, base_dir: Path, channels: int, master_volume: float, music_volume: float):
        if SoundEngine._instance is not None:
            raise RuntimeError()

        self.base_dir = base_dir
        self.master_volume = master_volume
        self.music_volume = music_volume
        self.registry: Dict[str, List[pygame.mixer.Sound]] = {}
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.set_num_channels(channels)
        pygame.mixer.music.set_volume(self.music_volume)

    def register(self, name: str, *relative_paths: str) -> None:
        sounds: List[pygame.mixer.Sound] = []
        for rel in relative_paths:
            full_path = self.base_dir / rel
            if not full_path.exists():
                print(f"[SoundEngine] Файл не найден: {full_path}")
                continue
            try:
                sfx = pygame.mixer.Sound(str(full_path))
                sounds.append(sfx)
            except pygame.error as exc:
                print(f"[SoundEngine] Не удалось загрузить {full_path}: {exc}")
        if sounds:
            self.registry[name] = sounds
        else:
            print(f"[SoundEngine] Для {name} не загружено ни одного звука.")

    def play(self, name: str, volume: float = 1.0) -> None:
        sounds = self.registry.get(name)
        if not sounds:
            auto_path = self.base_dir / f"{name}.wav"
            if auto_path.exists():
                self.register(name, f"{name}.wav")
                sounds = self.registry.get(name)
            if not sounds:
                print(f"[SoundEngine] Звук '{name}' не зарегистрирован.")
                return
        snd = random.choice(sounds)
        snd.set_volume(max(0.0, min(1.0, volume)) * self.master_volume)
        snd.play()

    def play_music(self, file_path: str, loop: bool = True) -> None:
        music_path = self.base_dir / file_path

        if not music_path.exists():
            print(f"[SoundEngine] Музыкальный файл не найден: {music_path}")
            return

        try:
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.play(-1 if loop else 0)
            print(f"[SoundEngine] Начато воспроизведение: {music_path.name}")
        except pygame.error as exc:
            print(f"[SoundEngine] Ошибка воспроизведения музыки: {exc}")

    def stop_music(self) -> None:
        """Останавливает фоновую музыку."""
        pygame.mixer.music.stop()

    def pause_music(self) -> None:
        """Приостанавливает фоновую музыку."""
        pygame.mixer.music.pause()

    def resume_music(self) -> None:
        """Возобновляет фоновую музыку."""
        pygame.mixer.music.unpause()

    def set_music_volume(self, volume: float) -> None:
        """Устанавливает громкость фоновой музыки"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def is_music_playing(self) -> bool:
        """Проверяет, играет ли музыка в данный момент."""
        return pygame.mixer.music.get_busy()

    # ------------------------------------------------------------------
    # Дополнительные возможности
    # ------------------------------------------------------------------

    def set_master_volume(self, volume: float):
        """Устанавливает глобальную громкость звуковых эффектов"""
        self.master_volume = max(0.0, min(1.0, volume))

    def stop_all(self):
        """Останавливает все звучащие эффекты (но не музыку)."""
        pygame.mixer.stop()

    def stop_everything(self):
        """Останавливает все звуки включая музыку."""
        pygame.mixer.stop()
        self.stop_music()


def init_sound_engine(channels: int = 16, master_volume: float = 1.0, music_volume: float = 0.5) -> SoundEngine:
    from settings import GameSettings
    base_dir = GameSettings.BASE_DIR / 'data' / 'sounds'
    return SoundEngine.init(base_dir, channels=channels, master_volume=master_volume, music_volume=music_volume)
