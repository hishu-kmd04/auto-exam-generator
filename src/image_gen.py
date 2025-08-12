# image_gen.py
"""
Programmatic image generator for math diagrams using Pillow.
Usage:
  python image_gen.py --input output/questions.json --out output/images
"""
import argparse
import os
from PIL import Image, ImageDraw, ImageFont
from utils import load_json, ensure_dir

def make_uniform_table_image(shirts, pants, outpath, cellw=140, cellh=60):
    cols = max(len(shirts), len(pants))
    width = cellw * 2 + 40
    height = (cols+1) * cellh + 40
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 16)
    except:
        font = ImageFont.load_default()

    x0, y0 = 20, 20
    draw.rectangle([x0, y0, x0 + cellw - 1, y0 + cellh - 1], outline="black")
    draw.rectangle([x0 + cellw, y0, x0 + cellw*2 - 1, y0 + cellh - 1], outline="black")
    draw.text((x0 + 10, y0 + 15), "Shirt Color", font=font, fill="black")
    draw.text((x0 + cellw + 10, y0 + 15), "Pants Color", font=font, fill="black")

    y = y0 + cellh
    for i in range(cols):
        draw.rectangle([x0, y, x0 + cellw - 1, y + cellh - 1], outline="black")
        draw.rectangle([x0 + cellw, y, x0 + cellw*2 - 1, y + cellh - 1], outline="black")
        s = shirts[i] if i < len(shirts) else ""
        p = pants[i] if i < len(pants) else ""
        draw.text((x0 + 10, y + 15), s, font=font, fill="black")
        draw.text((x0 + cellw + 10, y + 15), p, font=font, fill="black")
        y += cellh
    img.save(outpath)
    print("Saved table image:", outpath)
    return outpath

def make_packed_balls_image(rows, cols, radius, outpath, spacing=None):
    spacing = spacing if spacing is not None else radius*2 + 4
    width = cols * spacing + 40
    height = rows * spacing + 40
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 14)
    except:
        font = ImageFont.load_default()
    x0, y0 = 20, 20
    for r in range(rows):
        for c in range(cols):
            cx = x0 + c*spacing + spacing//2
            cy = y0 + r*spacing + spacing//2
            draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline="black", fill=None)
    draw.text((10, height - 20), f"Each circle radius={radius} units", font=font, fill="black")
    img.save(outpath)
    print("Saved balls image:", outpath)
    return outpath

def make_text_banner_image(text, outpath, width=800, height=200):
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
    except:
        font = ImageFont.load_default()

    # Wrap text manually for better fit
    lines = []
    words = text.split()
    line = ""
    for word in words:
        if len(line + " " + word) < 30:
            line += " " + word
        else:
            lines.append(line.strip())
            line = word
    lines.append(line.strip())

    y_text = height // 2 - (len(lines) * 15)
    for line in lines:
        w, h = draw.textsize(line, font=font)
        draw.text(((width - w) / 2, y_text), line, font=font, fill="black")
        y_text += h + 5

    img.save(outpath)
    print("Saved banner image:", outpath)
    return outpath

def auto_generate_images(questions_json, out_dir):
    ensure_dir(out_dir)
    data = load_json(questions_json)
    results = {}
    for q in data.get("questions", []):
        title = q.get("title", "q").replace(" ", "_")[:40]
        qt = q.get("question", "").lower()

        if "shirt" in qt or "pants" in qt or "uniform" in qt:
            shirts = ["Blue","Green","Gray","White"]
            pants = ["Black","Khaki","Navy"]
            path = os.path.join(out_dir, f"{title}_table.png")
            make_uniform_table_image(shirts, pants, path)
        elif "ball" in qt or "radius" in qt or "packed" in qt:
            path = os.path.join(out_dir, f"{title}_balls.png")
            make_packed_balls_image(2, 3, radius=20, outpath=path)
        else:
            path = os.path.join(out_dir, f"{title}_banner.png")
            make_text_banner_image(q.get("title", "Question"), path)

        results[q.get("order")] = path
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="questions.json")
    parser.add_argument("--out", required=True, help="out images dir")
    args = parser.parse_args()
    paths = auto_generate_images(args.input, args.out)
    print("Generated images map:", paths)

if __name__ == "__main__":
    main()
