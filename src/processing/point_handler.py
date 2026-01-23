import time
import asyncio
import logging
logger = logging.getLogger(__name__)

from dataclasses import dataclass
from farm_ng.canbus.canbus_pb2 import RawCanbusMessage
from custom_pdo.can_message_structure import SetupPdo
from setup.setup import Setup

@dataclass
class Crop:
    location: int
    width: int
    distance: float
    setup_amount: int


class PointHandler:
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
        self.can_bus = self.setup.can_bus

    def handle_point(self, x, y, camera_number):

        logger.debug(f"Camera {camera_number} has x {x}")

        # --- width berekenen ---
        if camera_number > 0:
            width = x + (self.screen_width * camera_number -
                         self.overlap_px * camera_number)
            logger.debug(f"added {width - x} to x {x} coming to width {width}")
        else:
            width = x

        step = self.total_amount_of_pixels // self.amount_of_strips
        #logger.info(f"{step} {width}")

        # --- bepaal strip & setups ---
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

                break  # width kan maar in 1 strip zitten

        # --- niets gevonden ---
        if not setups_for_strip:
            logger.warning(f"out of scope: width={width}")
            return

        # --- afstand bepalen ---
        distance = self.get_distance(y, len(setups_for_strip))

        # --- toevoegen aan setups ---
        for setup in setups_for_strip:
            crop = Crop(
                width=width,
                distance=distance,
                setup_amount=len(setups_for_strip),
                location=0
            )

            if not self._check_crop(crop, self.setups[setup]):
                #logger.debug(f"thirtd of the screen: {self.third_of_screen}")
                #logger.debug(f"nineth of the screen: {self.nineth_of_screen}")
                point = width - self.third_of_screen * (setup - 1)
                #logger.debug(f"point: {point}")
                point_with_offset = point + self.nineth_of_screen * (setup - 1)
                #logger.debug(f"point with offset: {point_with_offset}")
                crop.location = max(
                    0, 110 - (point_with_offset / self.third_of_screen * 110)
                )

                self.setups[setup].append(crop)

                logger.info(
                    f"camera {camera_number} added crop {crop} to setup {setup}"
                )
            else:
                logger.info(f"skipped crop {crop}")

    #def loop die constand de lijst checkt op waar welk punt is
    async def check_distances(self):
        self.old_time = time.monotonic()
        self.old_speed = await self.can_bus.get_speed()
        while True:

            if any(crops for crops in self.setups.values()):
                #check_distance
                #logger.debug(f"found crops")
                distance_traveled = await self.calculate_distance_traveled()
                #loops trough every point in the list and substracts traveld distance from there own distance
                for setup, crops in self.setups.items():
                    new_crops = []

                    for crop in crops:
                        crop.distance -= distance_traveled
                        logger.debug(f"{crop.distance}")
                        # if distance < 2 (staat niet vast is idee) sent give water message (amount depends on how many setups)
                        if crop.distance <= 20:
                            #send give water message
                            #logger.debug(f"{crop.x}")
                            await self.can_bus.send_to_microcontroller(message = RawCanbusMessage(
                                data = SetupPdo(
                                    command=1,
                                    amount=int(crop.location)).to_can_data(),
                                id = 0x300 + setup))
                            logger.debug("done sending")

                            await self.can_bus.send_to_microcontroller(message = RawCanbusMessage(
                                data = SetupPdo(
                                    command = 0,
                                    amount = int(500 / crop.setup_amount)).to_can_data(),
                                id = 0x300 + setup))
                            continue
                        else:
                            new_crops.append(crop)

                    self.setups[setup] = new_crops


            # else wait and set old_time to new time
            else:
                self.old_time = time.monotonic()
                self.old_speed = await self.can_bus.get_speed()
            # wait...
            await asyncio.sleep(0.1)

    #def hulp methode die met gegeven snelheid en huidige punt nieuwe x coordinaat berekend
    async def calculate_distance_traveled(self):
        #gets the current time
        #calculates past distance in given stime stack
        current_time = time.monotonic()
        forgone_time = current_time - self.old_time
        self.old_time = current_time
        
        current_speed = await self.can_bus.get_speed()
        #logger.debug(f"current speed: {current_speed}")
        #logger.debug(f"forgone time: {forgone_time}")

        distance_traveled = current_speed * forgone_time * 1000
        #logger.debug(f"distance_traveled: {distance_traveled}")

        return distance_traveled

    # initial method to set distance for point to where water needs to be given
    def get_distance(self, y, amount_of_setups):
        #gets the y coordinate and calculates the distance to the end point
        distance = (1080 - y) * 0.40 #pixel naar milimeter conversion
        #+ afstand van onderkant camera tot daadwerkelijke punt van watergeven
        distance += 700
        #changes end point to amount_of _setups because turning changes the distance
        if amount_of_setups == 1:
            return distance
        else:
            return distance - 30 #extra afstand bij turnen

    def _check_crop(self, new_crop: Crop, setup, tolerance=50):
        for crop in setup:
            if (
                    abs(crop.distance - new_crop.distance) <= tolerance
                    and abs(crop.width - new_crop.width) <= tolerance
            ):
                return True
        return False