import json
import logging
logger = logging.getLogger(__name__)

class JsonHandler:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.info("creating instance: jsonHandler")
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            logger.info("already has JsonHandler")
            return

        """
        open json once to get alle the info from last session
        """
        with open("filter_values.json") as json_file:
            data = json.load(json_file)

        self._initialized = True
        self.upper_hue = data.get("upper_hue")
        self.lower_hue = data.get("lower_hue")
        self.upper_sat = data.get("upper_sat")
        self.lower_sat = data.get("lower_sat")
        self.upper_val = data.get("upper_val")
        self.lower_val = data.get("lower_val")
        self.detection_radius = data.get("detection_radius")
        self.water_amount = data.get("water_amount")


    def update_json(self):
        """
        takes al the current value's and replaces the old ones in the json file
        """
        data = {
            "lower_hue": self.lower_hue,
            "upper_hue": self.upper_hue,
            "lower_sat": self.lower_sat,
            "upper_sat": self.upper_sat,
            "lower_val": self.lower_val,
            "upper_val": self.upper_val,
            "detection_radius": self.detection_radius,
            "water_amount": self.water_amount,
        }

        with open("filter_values.json", "w") as json_file:
            json.dump(
                data,
                json_file,
                indent = 4
            )

    def get_filter_values(self):
        """
        returns in this order:
        upperHue, lowerHue, upperSat, lowerSat, upperVal, lowerVal
        """
        return self.upper_hue, self.lower_hue, self.upper_sat, self.lower_sat, self.upper_val, self.lower_val

    def get_detection_radius(self):
        return self.detection_radius

    def get_water_amount(self):
        return self.water_amount

    def update_property(self, property, value):
        """
        update any given property
        - property: property to update
        - value: value to update property with
        """
        setattr(self, property, value)

    def update_filter(self, filter):
        """
        updates all the filter values
        - filter: ImageFilter witch values will update the values of this class
        """
        self.upper_hue = filter.upper_hue
        self.lower_hue = filter.lower_hue
        self.upper_sat = filter.upper_sat
        self.lower_sat = filter.lower_sat
        self.upper_val = filter.upper_val
        self.lower_val = filter.lower_val

