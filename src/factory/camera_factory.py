class CameraFactory:

    def add_camera_online(self, name: str, stream_name: str = "rgb"):
        """
        creates a new camera from the robot
        """
        from camera.camera_handler import CameraHandler
        return CameraHandler(name, stream_name)

    def add_camera_offline(self, source: str = None):
        """
        creates a new offline camera with prerecorded feed
        """
        from camera.offline_camera_handler import OfflineCameraHandler
        return OfflineCameraHandler(source)
