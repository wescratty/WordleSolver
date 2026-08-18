
class AWARENESS(EMPTY_SPACE):
    pass








class EMPTY_SPACE(AWARENESS):
    pass


class Soul(AWARENESS):
    def __init__(self):
        self.body = Body()


class Senses:
    def __init__(self):
        self.eyes = Sight()
        self.ears = Hearing()
        self.nose = Smell()
        self.tongue = Taste()
        self.feeling = Feeling()
        self.imagination = Vision()


class Body(Senses):
    def __init__(self):
        super().__init__()


class Sight:
    pass


class Hearing:
    pass


class Feeling:
    pass


class Smell:
    pass


class Taste:
    pass


class Vision:
    pass
