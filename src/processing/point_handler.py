import time
import asyncio
import logging
logger = logging.getLogger(__name__)

from dataclasses import dataclass
from farm_ng.canbus.canbus_pb2 import RawCanbusMessage
from custom_pdo.can_message_structure import SetupPdo
from file_communication.json_handler import JsonHandler
from setup.setup import Setup

@dataclass
class Crop:
    """
    data class to keep track of all the info of a crop
    """
    location: int       # horizontal location calculated for stepper motor
    width: int          # horizontal location under the robot
    distance: float     # distance to place where water needs to be given
    setup_amount: int   # amount of setups the crop is in


class PointHandler:
    """
    needed info for calculations later on
    """
    amount_of_cameras = 2
    amount_of_strips = 9
    amount_of_setups = 4
    screen_width = 1920
    pixels_per_cm = 1920 / 86
    camera_px = 86 * 22.33
    overlap_px = 30 * 22.33
    total_amount_of_pixels = (amount_of_cameras * camera_px) - (
            (amount_of_cameras - 1) * overlap_px)
    third_of_screen = total_amount_of_pixels // 3
    nineth_of_screen = total_amount_of_pixels // amount_of_strips


    def __init__(self):
        self.setups = {1:[], 2:[], 3:[], 4:[]}
        self.old_time = 0
        self.old_speed = 0
        self.setup = Setup()
        self.json_handler = JsonHandler()
        self.can_bus = self.setup.can_bus

    def handle_point(self, x, y, camera_number):
        """
        turns contour into crop, checks if it already exists then puts it in the according setup
        - x: x coordinate of a contour
        - y: y coordinate of a contour
        - camera_number: number of camera witch spotted the contour going from left(0) to right
        """
        logger.debug(f"Camera {camera_number} has x {x}")

        # calculate actual width according to witch camera gives x point
        if camera_number > 0:
            width = x + (self.screen_width * camera_number -
                         self.overlap_px * camera_number)
            logger.debug(f"added {width - x} to x {x} coming to width {width}")
        else:
            width = x

        step = self.total_amount_of_pixels // self.amount_of_strips

        # checks in witch strip/strips crop is found and break after finding one
        setups_for_strip = []

        for strip in range(self.amount_of_strips):
            logger.debug(f"{strip * step} <= {width} < {(strip + 1) * step}")

            if (strip * step) <= width < ((strip + 1) * step):
                logger.debug(f"found strip {strip} for width {width}")

                for setup in range(1, self.amount_of_setups + 1):
                    start_strip = (setup - 1) * 2
                    end_strip = start_strip + 2

                    if start_strip <= strip <= end_strip:
                        setups_for_strip.append(setup)
                        logger.debug(
                            f"strip {strip} belongs to setup {setup}"
                        )

                break

        # return of no correct strip is found
        if not setups_for_strip:
            logger.warning(f"out of scope: width={width}")
            return

        # get distance to place where water needs to be given with given y coordinate
        distance = self.get_distance(y, len(setups_for_strip))

        # create crop with available data check if crop already exists if not adds the crop to setup
        for setup in setups_for_strip:
            crop = Crop(
                width=width,
                distance=distance,
                setup_amount=len(setups_for_strip),
                location=0
            )

            if not self._check_crop(crop, self.setups[setup]):
                point = width - self.third_of_screen * (setup - 1)

                point_with_offset = point + self.nineth_of_screen * (setup - 1)

                crop.location = max(
                    0, 110 - (point_with_offset / self.third_of_screen * 110)
                )

                self.setups[setup].append(crop)

                logger.info(
                    f"camera {camera_number} added crop {crop} to setup {setup}"
                )
            else:
                logger.info(f"skipped crop {crop}")


    async def check_distances(self):
        """
        loop that constantly checks the distance traveled,
        subtracts that from the distanced from each crop and
        checks if crop is on the correct place to give water
        """
        self.old_time = time.monotonic()
        self.old_speed = await self.can_bus.get_speed()
        while True:

            if any(crops for crops in self.setups.values()):

                distance_traveled = await self.calculate_distance_traveled()
                #loops trough every point in the list and subtracts traveled distance from their own distance
                for setup, crops in self.setups.items():
                    new_crops = []

                    for crop in crops:
                        crop.distance -= distance_traveled
                        logger.debug(f"{crop.distance}")
                        # if distance is small enough sent give water message (amount depends on how many setups)
                        if crop.distance <= 20:
                            #send give water message
                            await self.can_bus.send_to_microcontroller(message = RawCanbusMessage(
                                data = SetupPdo(
                                    command=1,
                                    amount=int(crop.location)).to_can_data(),
                                id = 0x300 + setup))

                            await self.can_bus.send_to_microcontroller(message = RawCanbusMessage(
                                data = SetupPdo(
                                    command = 0,
                                    amount = int(200 / crop.setup_amount)).to_can_data(),
                                id = 0x300 + setup))
                            logger.debug("done sending")
                            continue
                        else:
                            new_crops.append(crop)

                    #adds all crops to new list, because of the continue crop that needs to get water will be skipped
                    self.setups[setup] = new_crops


            # if no crops, wait and set old_time to new time
            else:
                self.old_time = time.monotonic()
                self.old_speed = await self.can_bus.get_speed()
            await asyncio.sleep(0.1)

    #def hulp methode die met gegeven snelheid en huidige punt nieuwe x coordinaat berekend
    async def calculate_distance_traveled(self):
        """
        gets the current time and speed and calculates the distance traveled
        """
        current_time = time.monotonic()

        #get the time that has passed by subtracting current time with last measured time
        forgone_time = current_time - self.old_time
        self.old_time = current_time

        #currenet speed is in m/s
        current_speed = await self.can_bus.get_speed()


        distance_traveled = current_speed * forgone_time * 1000
        return distance_traveled


    def get_distance(self, y, amount_of_setups):
        """
        gets the y coordinate and calculates the distance to the end point
        - y: y coordinate of the crop where distance is measured
        - amount_of_setups: amount of setups in witch the crop wil go
        """
        distance = (1080 - y) * 0.40 #pixel to millimeter conversion
        #+ distance of were camera has no view to the place were water needs to be given
        distance += 700
        #changes end point to amount_of _setups because turning changes the distance
        if amount_of_setups == 1:
            return distance
        else:
            return distance - 30

    def _check_crop(self, new_crop: Crop, setup, tolerance=50):
        """
        checks if crop is already in the current list with crops
        - new_crop: crop that wil be added to the list of crops
        - setup: setup where the crop is located
        - tolerance: amount of pixels in witch range the crop measures as already existing
        """
        for crop in setup:
            if (
                    abs(crop.distance - new_crop.distance) <= tolerance
                    and abs(crop.width - new_crop.width) <= tolerance
            ):
                return True
        return False