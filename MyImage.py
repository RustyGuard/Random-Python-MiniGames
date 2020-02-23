from PIL import Image, ImageDraw, ImageFont


class MyImage:
    def __init__(self, width, height, color=(255, 255, 255)):
        self.image = Image.new("RGBA", (width, height), color)
        self.draw = ImageDraw.Draw(self.image)

    def Save(self, path):
        self.image.save(path)

    def Rect(self, x, y, width, height, fill="#75BBFD"):
        self.draw.rectangle((x, y, x + width, y + height), fill)

    def Ellipce(self, x, y, width, height, fill="#75BBFD"):
        self.draw.ellipse((x, y, x + width, y + height), fill)

    def Text(self, x, y, text, fill=(0, 0, 0)):
        self.draw.text((x, y), text, fill)


if __name__ == '__main__':
    image = MyImage(1000, 800)
    image.Rect(0, 100, 200, 200)
    image.Text(0, 0, "Hello", (125, 50, 125))
    image.Save("2.png")
