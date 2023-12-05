
class TrainingRule:
    def __init__(self, trainer):
        self.trainer = trainer

    def do_feeding(self):
        self.trainer.feeder.feed()

    def evaluate_scene(self):
        pass



class CatTrainingRule0(TrainingRule):
    pass



