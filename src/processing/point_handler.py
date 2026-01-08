import time
import asyncio
import logging
logger = logging.getLogger(__name__)

from dataclasses import dataclass
from custom_pdo.can_message_structure import SetupPdo
from setup.setup import Setup

@dataclass
class Crop:
    x: int
    distance: float
    setup_amount: int

class PointHandler:
    def __init__(self):
        self.setups = {1:[], 2:[], 3:[], 4:[]}
        self.old_time = 0
        self.old_speed = 0
        self.setup = Setup()
        self.can_bus = self.setup.can_bus

    def handle_point(self, x, y):

        setup = None
        setup_amount = 0

        #check in witch setup_list point should go
        for i in range(8):
            if ((i-1)*192) < x < (i * 192):
                setup = i // 2 + 1
                setup_amount = i % 2 + 1

        # stamp with set_distance
        distance = self.get_distance(y, setup_amount)

        # stamp with amount of setup_lists
        # add to correct setup
        if setup is not None and setup_amount > 0:
            crop = Crop(x = x, distance = distance, setup_amount = setup_amount)
            for i in range(setup_amount):
                self.setups[setup + (i - 1)].append(crop)
                print(f"added crop {crop} to setup {setup + (i - 1)}")
                loggin.info(f"added crop {crop} to setup {setup + (i - 1)}")
        else:
            print("out of scope")
            print(setup, setup_amount)
        pass

    #def loop die constand de lijst checkt op waar welk punt is
    async def check_distances(self):

        self.old_time = time.monotonic()
        self.old_speed = 0.2
        while True:

            if any(crops for crops in self.setups.values()):
                #check_distance
                logger.debug(f"found crops")
                distance_traveled = self.calculate_distance_traveled()

                #loops trough every point in the list and substracts traveld distance from there own distance
                for setup, crops in self.setups.items():
                    new_crops = []

                    for crop in crops:
                        crop.distance -= distance_traveled
                        # if distance < 2 (staat niet vast is idee) sent give water message (amount depends on how many setups)
                        if crop.distance <= 20:
                            #send give water message
                            await self.can_bus.send_to_microcontroller(message = SetupPdo(command=2, amount=crop.x), destination = 0x300 + setup)
                            await self.can_bus.send_to_microcontroller(message = SetupPdo(command = 1, amount = int(500 / crop.setup_amount)), destination = 0x300 + setup)
                            continue
                        else:
                            new_crops.append(crop)

                    self.setups[setup] = new_crops


            # else wait and set old_time to new time
            else:
                self.old_time = time.monotonic()
                self.old_speed = 0.2
            # wait...
            await asyncio.sleep(0.1)

    #def hulp methode die met gegeven snelheid en huidige punt nieuwe x coordinaat berekend
    def calculate_distance_traveled(self):
        #gets the current time
        #calculates past distance in given stime stack
        current_time = time.monotonic()
        forgone_time = current_time - self.old_time
        self.old_time = current_time
        
        current_speed = self.can_bus.get_speed()
        average_speed = (current_speed + self.old_speed) / 2
        self.old_speed = current_speed

        distance_traveled = average_speed * forgone_time * 1000
        #print(forgone_time)
        #print(distance_traveled)

        return distance_traveled

    # initial method to set distance for point to where water needs to be given
    def get_distance(self, y, amount_of_setups):
        #gets the y coordinate and calculates the distance to the end point
        distance = (1920 - y) * 0.40 #pixel naar milimeter conversion
        #+ afstand van onderkant camera tot daadwerkelijke punt van watergeven
        distance += 800
        #changes end point to amount_of _setups because turning changes the distance
        if amount_of_setups == 1:
            return distance
        else:
            return distance + 30 #extra afstand bij turnen

