
class TrainingRule:
    def __init__(self, trainer):
        self.trainer = trainer

    def do_feeding(self):
        self.trainer.feeder.feed()

    def evaluate_scene(self):
        raise NotImplementedError



class CatTrainingRule0(TrainingRule):
    def evaluate_scene(self):
        # FIXME
        self.trainer.image.detections
