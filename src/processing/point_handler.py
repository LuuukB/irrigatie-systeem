class PointHandler:
    def __init__(self):
        self.setup1 = []
        self.setup2 = []
        self.setup3 = []
        self.setup4 = []

    def handle_point(self):
        #stamp point with time
        #stamp with set_distance
        #check in witch setup_list point should go
        #stamp with amount of setup_lists
        #add to correct setup
        pass

    #def loop die konstand de lijst checkt op waar welk punt is
    def handle_setup(self, setup: List):
        #gets current speed,
        #loops trough every point in the list and checks_distance
        #if distance < 2 (staat niet vast is idee) sent give water message
        #imediatly after that send new point
        pass

    #def hulp methode die met gegeven snelheid en huidige punt nieuwe x coordinaat berekend
    def check_distance(self, crop_info, speed):
        #gets the current time
        #calculates new distance trough speed and time (difference between last and current time)
        pass

    # initial method to set distance for point to where water needs to be given
    def set_distance(self, point):
        #gets the x coordinate and calculates the distance to the end point
        #return y,distance
        pass