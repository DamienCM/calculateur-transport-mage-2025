from PyQt5.QtCore import QThread, pyqtSignal
from typing import Dict, List, Any


class CalculatorThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    warning = pyqtSignal(str, name='warning')
   
    def __init__(self, calculator, panier: List[Dict], options: Dict[str, Any]):
        super().__init__()
        self.calculator = calculator
        self.panier = panier
        self.options = options
        self.should_continue = True
       
        def warning_handler(message):
            print("Warning handler called with message:", message)
            self.warning.emit(message)
            while not hasattr(self, 'warning_response'):
                self.msleep(100)
            print("Got warning response:", self.warning_response)
            response = self.warning_response
            delattr(self, 'warning_response')
            return response
       
        transporteurs = list(self.calculator.transporteurs.values())
        for transporteur in transporteurs:
            transporteur.set_warning_callback(warning_handler)
   
    def run(self):
        try:
            print("Starting calculation...")
            results = self.calculator.calculer(self.panier, self.options)
            print("Calculation finished, results:", results)
            if results:  
                print("Emitting finished signal")
                self.finished.emit(results)
                print("Finished signal emitted")
        except Exception as e:
            print("Error in calculation:", str(e))
            self.error.emit(str(e))
