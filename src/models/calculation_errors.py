class CalculationError(Exception):
    def __init__(self, messsage = "[ERROR] Unknown error happened during calculation"):
        self.message = messsage
        super().__init__(self.message)        
