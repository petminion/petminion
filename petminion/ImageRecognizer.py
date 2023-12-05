

class ImageClassification:
    pass

class ImageDetection:
    pass

class ImageRecognizer:
    def do_detection(image) -> tuple[any, list[ImageDetection]]:
        return None
    
    def do_classification(image) -> list[ImageClassification]:
        return None
