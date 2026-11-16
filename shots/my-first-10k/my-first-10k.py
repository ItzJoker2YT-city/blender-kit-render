"""MY FIRST 10K — a 5-second 3D title.

The words swing up one by one over a glossy dark floor, the key word "10K" lands in gold metal,
a light bar sweeps across the metal once, dust drifts in the light, and the camera pushes in slowly.

  python .claude/skills/blender-shots/scripts/render_blender.py shots/my-first-10k/my-first-10k.py \
      --out shots/my-first-10k/my-first-10k.mp4 --frames 150 --stills 1,44,72,150 \
      --arg title="MY FIRST 10K" --arg gold=10K

title: the words (long titles shrink to fit the frame). gold: the word(s) in accent metal (repeatable).
accent: the accent colour #RRGGBB. start: second the first word lands. gap: seconds between words.
size: letter size. Structure follows the kit's title_reveal example; jitter-free shadows added for 1 sample.
"""
import bpy
import blender_kit as kit

a = kit.args()
title = a.get("title", "MY FIRST 10K")
gold_words = {g.upper().strip("!?.,:;'\"") for g in a.all("gold")}
accent = a.get("accent", "#E2B65C")
start = a.get("start", 0.4, float)
gap = a.get("gap", 0.35, float)
size = a.get("size", 1.5, float)
end = a.frames
FLOOR, FOOT = -1.9, -0.55            # floor height; where the words' feet hang above it

kit.setup(world="#04060A")
kit.backdrop("#05070C", center="#141A26", distance=16)
kit.floor("#06080C", z=FLOOR, roughness=0.28)        # glossy: the lit words reflect in it

# Two metals: light chrome for most words, the accent metal for the key word. Metal needs lights to read.
chrome = kit.metal("#E8EBF0", roughness=0.24, name="Chrome")
gold = kit.metal(accent, roughness=0.22, name="Gold")

words = title.split() or ["TITLE"]
objs = [kit.text(w, font="Montserrat-Bold", size=size, extrude=0.16, bevel=0.025,
                 material=(gold if w.upper().strip("!?.,:;'\"") in gold_words else chrome),
                 align="LEFT", name=f"Word{i}")
        for i, w in enumerate(words)]
gapx = 0.32 * size
total = sum(kit.measure(o)[0] for o in objs) + gapx * (len(objs) - 1)
fit = 7.8 * (a.width / a.height) / (16 / 9)          # line width that still fits at the end of the push-in
if total > fit:                                       # long title: shrink the letters so the line fits
    k = fit / total
    for o in objs:
        o.data.size *= k
    gapx *= k
    total = sum(kit.measure(o)[0] for o in objs) + gapx * (len(objs) - 1)

# Each word hangs from a pivot at its foot, lies flat pointing away, and swings up on its beat with overshoot.
x = -total / 2
last = 1
for i, o in enumerate(objs):
    wd, ht = kit.measure(o)
    piv = kit.empty((x, 0, FOOT), f"Pivot{i}")
    kit.parent(o, piv)
    o.location = (0, 0, ht / 2)                       # lift the word onto its pivot
    t0 = kit.f(start + i * gap)
    kit.key(piv, "rotation_euler", [(max(1, t0 - 1), kit.rot(-92, 0, 0)), (t0 + 10, kit.rot(7, 0, 0)),
                                    (t0 + 15, kit.rot(-2, 0, 0)), (t0 + 19, kit.rot(0, 0, 0))], ease="out")
    x += wd + gapx
    last = t0

# A narrow white light bar sweeps left to right across the metal once the words are up.
sweep = kit.light("AREA", (-10, -3.5, 2.6), (0, 0, FOOT + 0.5), power=2200, color="#FFFFFF", size=0.5, name="Sweep")
kit.key(sweep, "location", [(1, (-10, -3.5, 2.6)), (last + 4, (-10, -3.5, 2.6), "hold"),
                            (last + 40, (10, -3.5, 2.6))], ease="in_out")

# Light: warm key and cool rim, plus a soft top light so the metal faces read instead of turning brown.
mid = objs[len(objs) // 2]
kit.three_point(target=(0, 0, FOOT + 0.5), power=1.0, distance=9)
kit.light("AREA", (0, -4, 6.5), (0, 0, FOOT + 0.4), power=1500, color="#FFE7C4", size=7, name="Top")

# 1 sample: area-light shadows jitter without this (hard-won lesson in the skill's BLENDER.md).
for lt in bpy.data.lights:
    if hasattr(lt, "use_shadow_jitter"):
        lt.use_shadow_jitter = False

# Depth: bokeh specks drifting slowly; shallow focus on the middle word.
dust = kit.motes(count=60, center=(0, -1.0, 0.2), spread=(16, 14, 7), size=0.028, strength=2, seed=3)
kit.key(dust, "location", [(1, (0, -1.0, 0.0)), (end, (0.5, -1.0, 0.4))], ease="linear")

# Camera: a slow push in with a slight arc, looking a touch below the words so the reflection stays in frame.
cam = kit.camera((-0.9, -14.0, 1.6), look_at=(0, 0, FOOT + 0.1), lens=45)
kit.key(cam, "location", [(1, (-0.9, -14.0, 1.6)), (end, (0.3, -12.0, 1.0))], ease="in_out")
kit.shake(cam, strength=0.012, speed=35)
kit.depth_of_field(cam, focus=mid, fstop=2.0)

kit.post(bloom=0.3, vignette=0.4, grain=0.03)
