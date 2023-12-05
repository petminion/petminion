from functools import cached_property

class Feeder:
    
    def feed():
        pass

class Camera:
    def read_image():
        return None

class SimCamera(Camera):
    def read_image():
        return None

class ImageClassification:
    pass

class ImageDetection:
    pass

class ImageRecognizer:
    def do_detection(image) -> tuple[any, list[ImageDetection]]:
        return None
    
    def do_classification(image) -> list[ImageClassification]:
        return None


class Trainer: pass 

class TrainingRule:
    def __init__(self, trainer: Trainer):
        self.trainer = trainer

    def do_feeding(self):
        self.trainer.feeder.feed()

    def evaluate_scene(self):
        pass



class CatTrainingRule0(TrainingRule):
    pass


class ProcessedImage:

    def __init__(self, recognizer: ImageRecognizer, image):
        self.__recognizer = recognizer
        self.image = image
        self.__annotated = None

    @property
    def annotated(self):
        self.detections() # implicity will update __annotated
        return self.__annotated

    @cached_property
    def classifications(self):
        return self.__recognizer.do_classification(self.image)        

    @cached_property
    def detections(self):
        a, d = self.__recognizer.do_detection(self.image)
        self.__annotated = a
        return d
    
class Trainer:
    def __init__(self):
        self.camera = SimCamera()
        self.recognizer = ImageRecognizer()
        self.rule = CatTrainingRule0()
        self.feeder = Feeder()
        self.image = None

    def runOnce(self):
        self.image = self.camera.read_image()
        self.rule.evaluate_scene()


