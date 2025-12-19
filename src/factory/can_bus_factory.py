class CanBusFactory:

    @staticmethod
    def create_online():
        from can_bus.can_handler import CanHandler
        print("create online canbus")
        return CanHandler()

    @staticmethod
    def create_offline():
        from can_bus.mock_can_handler import MockCanHandler
        return MockCanHandler()