class CanBusFactory:

    @staticmethod
    def create_online():
        """creates a Canbus on the Robot"""
        from can_bus.can_handler import CanHandler
        return CanHandler()

    @staticmethod
    def create_offline():
        """creates a fake Canbus that only returns messages"""
        from can_bus.mock_can_handler import MockCanHandler
        return MockCanHandler()
