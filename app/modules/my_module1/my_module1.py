from modules.manager_modules import module_manager


class my_module1:
    def __init__(self, manager):
        self.manager = manager

    def get_module_data(self):
        return {"name": "my_module1", "status": module_manager.modules["my_module1"]}
