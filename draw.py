#!/usr/bin/env python3
import json
from PIL import Image, ImageDraw, ImageFont
cfg = json.load(open("rack.json"))
U, PX, W, LW = cfg["rack_u"], cfg["unit_px"], cfg["rack_width"], cfg["label_width"]
H, IMG_W, IMG_H = U * PX, W + LW + 20, U * PX + 20
def hex_brightness(h):
   h = h.lstrip("#")
   r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
   return (r * 0.299 + g * 0.587 + b * 0.114)
# ── prepare canvas with transparency ────────────────────────────────────────
img = Image.new("RGBA", (IMG_W, IMG_H), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)
try:
   font = ImageFont.truetype("DejaVuSans.ttf", 12)
except:
   font = ImageFont.load_default()
rack_l, rack_t = 10, 10
rack_r, rack_b = rack_l + W, rack_t + H
# ── rack outline ────────────────────────────────────────────────────────────
draw.rectangle([(rack_l, rack_t), (rack_r, rack_b)], outline="black", width=2)
# ── fill all slots with black (empty panels) ─────────────────────────────────
for n in range(1, U + 1):
   yb = rack_b - (n - 1) * PX
   yt = yb - PX
   x0, x1 = rack_l + 1, rack_r - 1
   draw.rectangle([(x0, yt + 1), (x1, yb - 1)], fill="#00181e")
# ── draw each multi-U device as one rectangle ────────────────────────────────
for dev in cfg["devices"]:
   name, bu, hu, col = dev["name"], dev["bottom_u"], dev["height_u"], dev["color"]
   yb = rack_b - (bu - 1) * PX
   yt = yb - hu * PX
   x0, x1 = rack_l + 1, rack_r - 1
   draw.rectangle([(x0, yt + 1), (x1, yb - 1)], fill=col)
   # center label within multi-U block
   bb = font.getbbox(name)
   tw, th = bb[2] - bb[0], bb[3] - bb[1]
   tx = (x0 + x1) / 2 - tw / 2
   ty = yt + (hu * PX - th) / 2
   txt_col = "white" if hex_brightness(col) < 128 else "black"
   draw.text((tx, ty), name, font=font, fill=txt_col)
# ── grid lines for U boundaries (skip lines that cut through multi-U devices) ─
occupied = set()
for dev in cfg["devices"]:
   bu, hu = dev["bottom_u"], dev["height_u"]
   for u in range(bu, bu + hu):
       occupied.add(u)
for i in range(U + 1):
   y = rack_t + i * PX
   u_below = U - i + 1
   if u_below in occupied and (u_below - 1) in occupied:
       continue
   draw.line([(rack_l, y), (rack_r, y)], fill="#444", width=1)
# ── draw slot labels "U<n>" in the white margin ───────────────────────────────
label_x = rack_r + 10
for n in range(1, U + 1):
   yb = rack_b - (n - 1) * PX
   y_mid = yb - PX / 2
   txt = f"U{n}"
   bb = font.getbbox(txt)
   tw, th = bb[2] - bb[0], bb[3] - bb[1]
   draw.text((label_x, y_mid - th / 2), txt, font=font, fill="black")
img.save("rack.png")
