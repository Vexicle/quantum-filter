from PIL import Image
import secrets
import math

from PIL import Image


def vignette(image: Image) -> Image:
    """ Take image, output image with vignette
    """
    strength=0.5
    start=0.5
    falloff=1.0

    rgb = image.convert("RGB")

    def darkness(value):
        distance = value / 255.0
        if distance <= start:
            return 0
        t = (distance - start) / (1.0 - start)
        return round(255 * strength * t ** falloff)

    mask = Image.radial_gradient("L").point(darkness)
    mask = mask.resize(rgb.size, Image.Resampling.BICUBIC)

    black = Image.new("RGB", rgb.size, (0, 0, 0))
    result = Image.composite(black, rgb, mask)

    return result

def barrel(img: Image) -> Image:
    """ Take image, output a barrel-distorted image
    """
    strength=0.2
    grid=64
    fill=(0, 0, 0)
    
    img = img.convert("RGB")
    w, h = img.size

    def source_point(x, y):

        nx = 2 * x / w - 1
        ny = 2 * y / h - 1
        r2 = nx * nx + ny * ny
        f = (1 + strength * r2) / (1 + 2 * strength)

        return ((nx * f + 1) * w / 2, (ny * f + 1) * h / 2)

    xs = [round(i * w / grid) for i in range(grid + 1)]
    ys = [round(j * h / grid) for j in range(grid + 1)]

    mesh = []
    for j in range(grid):
        for i in range(grid):
            x0, x1 = xs[i], xs[i + 1]
            y0, y1 = ys[j], ys[j + 1]
            quad = (
                *source_point(x0, y0),  # upper-left
                *source_point(x0, y1),  # lower-left
                *source_point(x1, y1),  # lower-right
                *source_point(x1, y0),  # upper-right
            )
            mesh.append(((x0, y0, x1, y1), quad))

    return img.transform(
        (w, h),
        Image.Transform.MESH,
        mesh,
        resample=Image.Resampling.BICUBIC,
        fillcolor=fill,
    )

def noise(image) -> Image:
    """ Creates an image with the same dimensions as the input's image
    """
    pixels = image.load()
    for x in range(image.width):
        for y in range(image.height):
            r,g,b = pixels[x, y]
            
            pixels[x, y] = (
                secrets.randbelow(256), 
                secrets.randbelow(256), 
                secrets.randbelow(256)
            )
            
    return image
    
def analogue(img: Image) -> Image:
    """ Outputs an image with black-white lines based on the image input's size
    """
    base = Image.new("RGB", img.size, 128)
    
    left = 1 + secrets.randbelow(128)
    black_turn = True
    white_turn = False
    pixels = base.load()
    
    for x in range(base.width):
        for y in range(base.height):
            r,g,b = pixels[x, y]
                
            if black_turn == True:
                if left == 0:
                    white_turn = True
                    black_turn = False
                    left = secrets.randbelow(128)
                else:
                    pixels[x, y] = (0,0,0)
                    left += -1
                    
            elif white_turn == True:
                if left == 0:
                    white_turn = False
                    black_turn = True
                    left = secrets.randbelow(128)
                else:
                    pixels[x, y] = (256,256,256)
                    left += -1
            else:
                print("!!!this is not meant to happen!!!")
                    
    return base
    
def camera(input: Image) -> Image:
    """ Acts as a digital camera
        Takes image, outputs with a camera filter
    """
    noisemap = noise(Image.new("RGB",input.size, 128))
    analoguemap = analogue(input)
    black = Image.new("RGBA", input.size, (0, 0, 0, 12))
    black2 = Image.new("RGBA", input.size, (0, 0, 0, 3))
    
    result = Image.composite(analoguemap, input, black)
    result2 = Image.composite(noisemap, result, black2)
    return result2

def main() -> None:
    #display = Image.new("RGB",(647,647), 128)
    #display = noise(display)
    display = black = Image.new("RGB", (657, 657), (0, 0, 0))
    #display = camera(display)
    #display = vignette(display)
    #display = barrel(display)
    
    for i in range(1,128):
        display = camera(display)
        display = vignette(display)
        display = barrel(display)
        
    display.save("output.jpeg", "JPEG")
    ...


if __name__ == '__main__':
    main()