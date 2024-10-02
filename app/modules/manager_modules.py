import importlib
import time
from pathlib import Path


class ModuleManager:
    def __init__(self, config_path):
        self.modules_states = {}
        self.modules = {}
        self.config_path = config_path
        self.read_config()

    def read_config(self):
        absolute_path = Path(self.config_path).resolve()
        with Path(absolute_path).open("r") as file:
            for line in file.readlines():
                module_name, status = line.strip().split("=")
                self.modules_states[module_name] = status

    def load_module(self, module_name):
        """Динамическое импортирование модуля."""
        module_path = f"modules.{module_name}.{module_name}"
        module = importlib.import_module(module_path)
        module_class = getattr(module, module_name)
        self.modules[module_name] = module_class(self)

    def unload_module(self, module_name):
        """Удаление модуля из системы."""
        if module_name in self.modules:
            del self.modules[module_name]

    def reload_module(self, module_name):
        """Перезагрузка модуля."""
        if module_name in self.modules:
            self.unload_module(module_name)
        self.load_module(module_name)

    def manage_modules(self):
        """Обновление состояния модулей на основе конфигурации."""
        self.read_config()
        for module_name, status in self.modules_states.items():
            if status == "enable" and module_name not in self.modules:
                self.load_module(module_name)
            elif status == "disable" and module_name in self.modules:
                self.unload_module(module_name)
            elif status == "reload":
                self.reload_module(module_name)


def monitor_modules(manager):
    while True:
        manager.manage_modules()
        time.sleep(10)


module_manager = ModuleManager(config_path="modules/modules.conf")
