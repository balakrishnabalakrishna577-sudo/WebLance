"""
Simple image CAPTCHA generator using Pillow.
Generates a distorted alphanumeric code as a PNG image.
"""
import io
import random
import string
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def generate_captcha_text(length=6):
    """Generate a random alphanumeric code (numbers + uppercase letters)."""
    chars = string.digits + string.ascii_uppercase
    # Remove confusing chars: 0, O, 1, I, l
    chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('I', '').replace('l', '')
    return ''.join(random.choices(chars, k=length))


def generate_captcha_image(text):
    """Generate a distorted CAPTCHA image and return as bytes."""
    width, height = 160, 50
    bg_color = (18, 18, 28)       # dark background
    text_color = (0, 255, 136)    # green text

    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Draw noise lines
    for _ in range(6):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(40, 80, 60), width=1)

    # Draw noise dots
    for _ in range(80):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill=(30, 100, 60))

    # Draw each character with slight rotation and offset
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except Exception:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        except Exception:
            font = ImageFont.load_default()

    char_width = width // len(text)
    for i, char in enumerate(text):
        x = i * char_width + random.randint(2, 8)
        y = random.randint(5, 15)
        # Slight color variation
        r = random.randint(0, 50)
        g = random.randint(200, 255)
        b = random.randint(80, 150)
        draw.text((x, y), char, font=font, fill=(r, g, b))

    # Apply slight blur for distortion
    img = img.filter(ImageFilter.GaussianBlur(radius=0.8))

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue()
