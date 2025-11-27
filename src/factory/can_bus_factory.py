class CanBusFactory:

    @staticmethod
    def create_online():
        from can_bus.can_handler import AsyncCanHandler
        return AsyncCanHandler()

    @staticmethod
    def create_offline():
        from can_bus.mock_can_handler import MockCanHandler
        return MockCanHandler()