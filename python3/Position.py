class Position:
    def __init__(self, y, x):
        self.y = y
        self.x = x

    def reprJSON(self):
        return dict(y=self.y,
                    x=self.x)
