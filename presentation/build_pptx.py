"""Build demetro_slides.pptx as NATIVE PowerPoint shapes/text.

All text is editable, rectangles/chevrons are native AutoShapes, colours match
the team design guide. Only the generated matplotlib bullseye stays as an image
(it's a scientific chart, not a layout element).
"""
import shutil
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

HERE = Path(__file__).parent
OUT_PPTX = HERE / "demetro_slides.pptx"
DOWNLOADS = Path.home() / "Downloads" / "demetro_slides.pptx"

# ── Team design guide colours ──────────────────────────────────────────────
BLUE_TITLE   = RGBColor(0x00, 0x70, 0xC0)  # primary title blue
BLUE_MID     = RGBColor(0x21, 0x96, 0xF3)  # secondary
BLUE_LIGHT   = RGBColor(0x42, 0xA5, 0xF5)  # tertiary
GREEN_MID    = RGBColor(0x66, 0xBB, 0x6A)
GREEN_DARK   = RGBColor(0x43, 0xA0, 0x47)
GREEN_ACCENT = RGBColor(0x27, 0xAE, 0x60)
ORANGE       = RGBColor(0xE9, 0x71, 0x32)
WHITE        = RGBColor(0xFF, 0xFF, 0xFF)
BLACK        = RGBColor(0x22, 0x22, 0x22)
GREY_TEXT    = RGBColor(0x55, 0x55, 0x55)
GREY_LIGHT   = RGBColor(0x88, 0x88, 0x88)
GREY_BORDER  = RGBColor(0xE0, 0xE0, 0xE0)
BG_LIGHT     = RGBColor(0xF8, 0xF9, 0xFA)
RED_BORDER   = RGBColor(0xE7, 0x4C, 0x3C)
RED_BG       = RGBColor(0xFE, 0xF2, 0xF2)
GREEN_BG     = RGBColor(0xF0, 0xFD, 0xF4)
GREEN_BORDER = RGBColor(0x86, 0xEF, 0xAC)
STAR_YELLOW  = RGBColor(0xF1, 0xC4, 0x0F)

FONT = "Calibri"


# ── Helpers ────────────────────────────────────────────────────────────────
def set_font(run, size_pt, bold=False, color=BLACK, name=FONT):
    run.font.name = name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.color.rgb = color


def add_textbox(slide, x, y, w, h, text, size=12, bold=False, color=BLACK,
                align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    set_font(r, size, bold=bold, color=color)
    return box


def add_multiline(slide, x, y, w, h, lines, size=10, color=GREY_TEXT, line_spacing=1.15):
    """Add a textbox with multiple lines. Each line can be a string or (text, bold, color_override)."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    for i, line in enumerate(lines):
        if isinstance(line, str):
            text, bold, col = line, False, color
        else:
            text = line[0]
            bold = line[1] if len(line) > 1 else False
            col = line[2] if len(line) > 2 else color
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = text
        set_font(r, size, bold=bold, color=col)
    return box


def add_rect(slide, x, y, w, h, fill=WHITE, line=GREY_BORDER, line_w=0.75, radius=False):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    s.line.color.rgb = line
    s.line.width = Pt(line_w)
    s.text_frame.text = ""
    # Clear default text frame margins
    s.text_frame.margin_left = Inches(0)
    s.text_frame.margin_right = Inches(0)
    s.text_frame.margin_top = Inches(0)
    s.text_frame.margin_bottom = Inches(0)
    return s


def add_chevron(slide, x, y, w, h, fill, title, detail, sub=""):
    """Pipeline chevron with 3 lines of text inside."""
    s = slide.shapes.add_shape(MSO_SHAPE.CHEVRON, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    s.line.fill.background()
    tf = s.text_frame
    tf.margin_left = Inches(0.25)
    tf.margin_right = Inches(0.15)
    tf.margin_top = Inches(0.12)
    tf.margin_bottom = Inches(0.08)
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE

    p1 = tf.paragraphs[0]
    p1.alignment = PP_ALIGN.LEFT
    r1 = p1.add_run()
    r1.text = title
    set_font(r1, 13, bold=True, color=WHITE)

    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.LEFT
    r2 = p2.add_run()
    r2.text = detail
    set_font(r2, 9, color=WHITE)

    if sub:
        p3 = tf.add_paragraph()
        p3.alignment = PP_ALIGN.LEFT
        r3 = p3.add_run()
        r3.text = sub
        set_font(r3, 8, color=RGBColor(0xDD, 0xE6, 0xF0))
    return s


# ── Build presentation ─────────────────────────────────────────────────────
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]


# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 1: CV to Target Estimate Pipeline
# ═══════════════════════════════════════════════════════════════════════════
s1 = prs.slides.add_slide(blank)

# --- Title ---
add_textbox(s1, 0.4, 0.25, 10, 0.65,
            "CV to Target Estimate Pipeline",
            size=32, bold=True, color=BLUE_TITLE)

# --- Pipeline ribbon (5 chevrons) ---
pipe_y = 1.0
pipe_h = 1.1
pipe_w = 1.95
pipe_x0 = 0.4
pipe_overlap = 0.18  # chevrons overlap slightly

pipeline = [
    ("Camera Capture",     "1456 x 1088 px",           "IMX296 global shutter",  BLUE_TITLE),
    ("YOLOv8n Inference",  "NCNN backend - 73 ms",     "640x640 input tensor",   BLUE_MID),
    ("Pixel -> GPS",       "FOV projection + altitude","Calibrated focal length",BLUE_LIGHT),
    ("Attitude Correction","Pitch + roll ray-trace",   "From flight controller", GREEN_MID),
    ("Target GPS",         "~9 FPS effective",         "CEP50 = 2.2 m",          GREEN_DARK),
]
for i, (title, detail, sub, colour) in enumerate(pipeline):
    x = pipe_x0 + i * (pipe_w - pipe_overlap)
    add_chevron(s1, x, pipe_y, pipe_w, pipe_h, colour, title, detail, sub)

# --- Bottom row: bullseye + bar chart + triangle + right column ---
bottom_y = 2.4
bottom_h = 4.8

# Bullseye chart (image)
bulls_x, bulls_y = 0.4, bottom_y
bulls_w, bulls_h = 3.3, bottom_h
add_rect(s1, bulls_x, bulls_y, bulls_w, bulls_h, fill=BG_LIGHT, line=GREY_BORDER)
bulls_img = HERE.parent / "report" / "figs" / "estimation_heatmap_all.png"
if bulls_img.exists():
    s1.shapes.add_picture(str(bulls_img),
                          Inches(bulls_x + 0.05), Inches(bulls_y + 0.05),
                          width=Inches(bulls_w - 0.10), height=Inches(bulls_h - 0.10))

# Bar chart (native shapes)
bar_x, bar_y = 3.85, bottom_y
bar_w, bar_h = 2.3, bottom_h
add_rect(s1, bar_x, bar_y, bar_w, bar_h, fill=BG_LIGHT, line=GREY_BORDER)
add_textbox(s1, bar_x + 0.2, bar_y + 0.15, bar_w - 0.4, 0.3,
            "Backend (Pi 5)", size=12, bold=True, color=BLUE_TITLE, align=PP_ALIGN.CENTER)
add_textbox(s1, bar_x + 0.2, bar_y + 0.5, 0.7, 0.25,
            "Eff. FPS", size=9, color=GREY_LIGHT)

# Y axis guide lines + labels
for val, y_rel in [(12, 0.85), (9, 1.35), (6, 1.85), (3, 2.35), (0, 2.85)]:
    add_textbox(s1, bar_x + 0.2, bar_y + y_rel, 0.4, 0.22,
                str(val), size=8, color=GREY_LIGHT, align=PP_ALIGN.RIGHT)

# TFLite bar (red) - 4.8 FPS
tflite_h = (4.8 / 12) * 2.1  # 0.84"
tflite_y = bar_y + 0.9 + (2.1 - tflite_h)
tflite_bar = add_rect(s1, bar_x + 0.75, tflite_y, 0.5, tflite_h,
                      fill=ORANGE, line=ORANGE)
add_textbox(s1, bar_x + 0.7, tflite_y - 0.35, 0.6, 0.3,
            "4.8", size=14, bold=True, color=ORANGE, align=PP_ALIGN.CENTER)
add_textbox(s1, bar_x + 0.7, bar_y + 3.05, 0.6, 0.25,
            "TFLite", size=10, color=GREY_TEXT, align=PP_ALIGN.CENTER)

# NCNN bar (blue) - 10.9 FPS
ncnn_h = (10.9 / 12) * 2.1  # 1.91"
ncnn_y = bar_y + 0.9 + (2.1 - ncnn_h)
add_rect(s1, bar_x + 1.45, ncnn_y, 0.5, ncnn_h, fill=BLUE_TITLE, line=BLUE_TITLE)
add_textbox(s1, bar_x + 1.4, ncnn_y - 0.35, 0.6, 0.3,
            "10.9", size=14, bold=True, color=BLUE_TITLE, align=PP_ALIGN.CENTER)
add_textbox(s1, bar_x + 1.4, bar_y + 3.05, 0.6, 0.25,
            "NCNN", size=10, color=GREY_TEXT, align=PP_ALIGN.CENTER)

# Faster label
add_textbox(s1, bar_x + 0.2, bar_y + 3.5, bar_w - 0.4, 0.3,
            "2.3x faster", size=12, bold=True, color=GREEN_ACCENT, align=PP_ALIGN.CENTER)

# Pixel -> Distance diagram (native shapes)
tri_x, tri_y = 6.3, bottom_y
tri_w, tri_h = 2.5, bottom_h
add_rect(s1, tri_x, tri_y, tri_w, tri_h, fill=BG_LIGHT, line=GREY_BORDER)
add_textbox(s1, tri_x + 0.1, tri_y + 0.15, tri_w - 0.2, 0.3,
            "Pixel -> Distance", size=12, bold=True, color=BLUE_TITLE, align=PP_ALIGN.CENTER)

# Drone body
drone_cx = tri_x + tri_w / 2
drone_y = tri_y + 0.55
add_rect(s1, drone_cx - 0.2, drone_y, 0.4, 0.15, fill=GREY_LIGHT, line=GREY_LIGHT)
# Propeller arms
from pptx.oxml.ns import qn
arm_left = s1.shapes.add_connector(1, Inches(drone_cx - 0.4), Inches(drone_y + 0.07),
                                    Inches(drone_cx - 0.2), Inches(drone_y + 0.07))
arm_left.line.color.rgb = GREY_LIGHT
arm_left.line.width = Pt(1.5)
arm_right = s1.shapes.add_connector(1, Inches(drone_cx + 0.2), Inches(drone_y + 0.07),
                                     Inches(drone_cx + 0.4), Inches(drone_y + 0.07))
arm_right.line.color.rgb = GREY_LIGHT
arm_right.line.width = Pt(1.5)
# Propeller blades
add_rect(s1, drone_cx - 0.5, drone_y + 0.02, 0.2, 0.08, fill=GREY_LIGHT, line=GREY_LIGHT, radius=True)
add_rect(s1, drone_cx + 0.3, drone_y + 0.02, 0.2, 0.08, fill=GREY_LIGHT, line=GREY_LIGHT, radius=True)

# Altitude dashed line
alt_top = drone_y + 0.17
alt_bot = tri_y + 4.0
alt_line = s1.shapes.add_connector(1, Inches(drone_cx), Inches(alt_top),
                                    Inches(drone_cx), Inches(alt_bot))
alt_line.line.color.rgb = BLUE_TITLE
alt_line.line.width = Pt(1)
alt_line.line.dash_style = 6  # DASH
add_textbox(s1, drone_cx + 0.05, (alt_top + alt_bot) / 2 - 0.1, 0.8, 0.3,
            "h = 35m", size=9, bold=True, color=BLUE_TITLE)

# FOV cone
cone_left = tri_x + 0.3
cone_right = tri_x + tri_w - 0.3
fov_left = s1.shapes.add_connector(1, Inches(drone_cx), Inches(alt_top),
                                    Inches(cone_left), Inches(alt_bot))
fov_left.line.color.rgb = GREY_LIGHT
fov_left.line.width = Pt(1)
fov_right = s1.shapes.add_connector(1, Inches(drone_cx), Inches(alt_top),
                                     Inches(cone_right), Inches(alt_bot))
fov_right.line.color.rgb = GREY_LIGHT
fov_right.line.width = Pt(1)

# 54 deg label
add_textbox(s1, drone_cx - 0.3, drone_y + 0.65, 0.6, 0.3,
            "54°", size=10, bold=True, color=ORANGE, align=PP_ALIGN.CENTER)

# Ground line
ground_y = alt_bot
ground_line = s1.shapes.add_connector(1, Inches(tri_x + 0.2), Inches(ground_y),
                                       Inches(tri_x + tri_w - 0.2), Inches(ground_y))
ground_line.line.color.rgb = BLACK
ground_line.line.width = Pt(2)

# Target dot
tgt_x = drone_cx + 0.5
tgt_dot = s1.shapes.add_shape(MSO_SHAPE.OVAL,
                                Inches(tgt_x - 0.07), Inches(ground_y - 0.07),
                                Inches(0.14), Inches(0.14))
tgt_dot.fill.solid()
tgt_dot.fill.fore_color.rgb = ORANGE
tgt_dot.line.fill.background()
add_textbox(s1, tgt_x - 0.25, ground_y - 0.35, 0.5, 0.2,
            "target", size=8, color=ORANGE, align=PP_ALIGN.CENTER)

# Distance bracket
bracket_y = ground_y - 0.2
d_line = s1.shapes.add_connector(1, Inches(drone_cx), Inches(bracket_y),
                                  Inches(tgt_x), Inches(bracket_y))
d_line.line.color.rgb = GREEN_ACCENT
d_line.line.width = Pt(2)
add_textbox(s1, drone_cx - 0.1, bracket_y - 0.3, 0.8, 0.25,
            "d = px × GSD", size=9, bold=True, color=GREEN_ACCENT)

# Ground width label
add_textbox(s1, tri_x + 0.2, ground_y + 0.1, tri_w - 0.4, 0.25,
            "32m ground width", size=9, color=GREY_LIGHT, align=PP_ALIGN.CENTER)

# GSD formula
add_textbox(s1, tri_x + 0.1, tri_y + tri_h - 0.5, tri_w - 0.2, 0.3,
            "GSD = 0.022 m/px at 35m", size=9, color=GREY_TEXT, align=PP_ALIGN.CENTER)

# --- Right column: Camera & Calibration ---
cam_x = 8.95
cam_w = 4.15

add_textbox(s1, cam_x, bottom_y, cam_w, 0.35,
            "Camera & Calibration", size=14, bold=True, color=BLUE_TITLE)

# IMX296 box
box1_y = bottom_y + 0.4
box1_h = 1.35
add_rect(s1, cam_x, box1_y, cam_w, box1_h, fill=BG_LIGHT, line=GREY_BORDER)
add_textbox(s1, cam_x + 0.15, box1_y + 0.08, cam_w - 0.3, 0.3,
            "IMX296 Global Shutter", size=12, bold=True, color=BLUE_TITLE)
add_multiline(s1, cam_x + 0.15, box1_y + 0.4, cam_w - 0.3, box1_h - 0.5, [
    ("1456 x 1088 px native resolution, 30 fps capture", False, BLACK),
    ("Global shutter - no rolling-shutter distortion at any speed", False, GREY_TEXT),
    ("Sub-pixel motion blur (<0.5 px at 8 m/s) - no gimbal needed", False, GREY_TEXT),
], size=11)

# Pixel → Real-World Distance box
box2_y = box1_y + box1_h + 0.15
box2_h = 1.6
add_rect(s1, cam_x, box2_y, cam_w, box2_h, fill=BG_LIGHT, line=GREY_BORDER)
add_textbox(s1, cam_x + 0.15, box2_y + 0.08, cam_w - 0.3, 0.3,
            "Pixel -> Real-World Distance", size=12, bold=True, color=BLUE_TITLE)
add_multiline(s1, cam_x + 0.15, box2_y + 0.4, cam_w - 0.3, box2_h - 0.5, [
    "FOV calibrated - focal length 5.46mm (22% off datasheet!)",
    "GSD = 0.022 m/px at 35m altitude",
    "Ground footprint = 32 x 24 m at 35m alt",
    "Pixel offset × GSD -> metre offset -> add to drone GPS",
], size=11)

# Lens Distortion Correction box
box3_y = box2_y + box2_h + 0.15
box3_h = 1.3
add_rect(s1, cam_x, box3_y, cam_w, box3_h, fill=BG_LIGHT, line=GREY_BORDER)
add_textbox(s1, cam_x + 0.15, box3_y + 0.08, cam_w - 0.3, 0.3,
            "Lens Distortion Correction", size=12, bold=True, color=BLUE_TITLE)
add_multiline(s1, cam_x + 0.15, box3_y + 0.4, cam_w - 0.3, box3_h - 0.5, [
    "Checkerboard calibration - 14x9 board, RMS = 0.4 px",
    "Precomputed undistortion maps applied every frame",
    "Cost: +1.5ms per frame (negligible on 206ms inference)",
], size=11)


# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 2: Simulation and Sim2Real Ladder
# ═══════════════════════════════════════════════════════════════════════════
s2 = prs.slides.add_slide(blank)

# --- Title ---
add_textbox(s2, 0.4, 0.25, 10, 0.65,
            "Simulation and Sim2Real Ladder",
            size=28, bold=True, color=BLUE_TITLE)

# --- Left: video placeholder ---
vid_x, vid_y = 0.4, 1.1
vid_w, vid_h = 5.8, 6.2
add_rect(s2, vid_x, vid_y, vid_w, vid_h, fill=BG_LIGHT, line=GREY_BORDER)
# Play triangle
play = s2.shapes.add_shape(MSO_SHAPE.RIGHT_TRIANGLE,
                            Inches(vid_x + vid_w/2 - 0.5), Inches(vid_y + vid_h/2 - 0.5),
                            Inches(1.0), Inches(1.0))
play.rotation = 30
play.fill.solid()
play.fill.fore_color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
play.line.fill.background()
add_textbox(s2, vid_x, vid_y + vid_h/2 + 0.6, vid_w, 0.3,
            "Simulation Recording", size=13, color=GREY_LIGHT, align=PP_ALIGN.CENTER)
add_textbox(s2, vid_x, vid_y + vid_h/2 + 0.95, vid_w, 0.25,
            "takeoff -> search -> detect -> centre -> verify -> land",
            size=10, color=GREY_LIGHT, align=PP_ALIGN.CENTER)

# --- Right: Sim2Real Ladder ---
right_x = 6.5
right_w = 6.5

# Ladder title
add_textbox(s2, right_x, 1.1, right_w, 0.35,
            "Sim2Real Ladder", size=16, bold=True, color=BLUE_TITLE)
add_textbox(s2, right_x, 1.45, right_w, 0.25,
            "(never fly something you haven't proven at every level below it)",
            size=9, color=GREY_LIGHT)

# Real Mission goal box
goal_y = 1.75
goal_h = 0.55
add_rect(s2, right_x, goal_y, right_w, goal_h, fill=RED_BG, line=RED_BORDER, line_w=2)
# Star icon (as text - Calibri renders unicode star)
add_textbox(s2, right_x + 0.1, goal_y + 0.05, 0.5, 0.45,
            "★", size=24, color=STAR_YELLOW)
add_textbox(s2, right_x + 0.55, goal_y + 0.05, 3, 0.25,
            "Real Mission", size=14, bold=True, color=RED_BORDER)
add_textbox(s2, right_x + 0.55, goal_y + 0.28, 3, 0.22,
            "Full autonomous SAR - demo day", size=10, color=GREY_LIGHT)
add_textbox(s2, right_x + right_w - 0.7, goal_y + 0.18, 0.6, 0.25,
            "GOAL", size=11, bold=True, color=RED_BORDER, align=PP_ALIGN.RIGHT)

# Arrow up
add_textbox(s2, right_x + right_w/2 - 0.2, goal_y + goal_h + 0.02, 0.4, 0.2,
            "▲", size=14, color=GREY_LIGHT, align=PP_ALIGN.CENTER)

# Flight Missions box
fm_y = goal_y + goal_h + 0.3
fm_h = 1.5
add_rect(s2, right_x + 0.5, fm_y, right_w - 1, fm_h, fill=BG_LIGHT, line=GREY_BORDER)
add_textbox(s2, right_x + 0.65, fm_y + 0.08, right_w - 1.3, 0.25,
            "FLIGHT MISSIONS", size=10, bold=True, color=BLUE_TITLE)

# Flight mission rows
def add_mission_row(yoff, code, label, checked):
    y_row = fm_y + yoff
    # Checkbox
    cb = add_rect(s2, right_x + 0.7, y_row + 0.03, 0.22, 0.22,
                  fill=BLUE_TITLE if checked else WHITE,
                  line=BLUE_TITLE if checked else RED_BORDER, line_w=1.25)
    if checked:
        add_textbox(s2, right_x + 0.7, y_row - 0.02, 0.22, 0.28,
                    "✓", size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    # Code
    add_textbox(s2, right_x + 1.0, y_row + 0.02, 0.5, 0.25,
                code, size=11, bold=True, color=BLACK)
    # Label
    add_textbox(s2, right_x + 1.45, y_row + 0.02, 3, 0.25,
                label, size=11, color=BLACK)

add_mission_row(0.36, "M4", "Auto detect + hover", False)
add_mission_row(0.62, "M3", "Waypoint flight", False)
add_mission_row(0.88, "M2", "Passive flight", True)
add_mission_row(1.14, "M1", "Bench integration", True)

# Arrow up
add_textbox(s2, right_x + right_w/2 - 0.2, fm_y + fm_h + 0.02, 0.4, 0.2,
            "▲", size=13, color=GREY_LIGHT, align=PP_ALIGN.CENTER)

# Ground Verification box
gv_y = fm_y + fm_h + 0.3
gv_h = 0.95
add_rect(s2, right_x + 0.5, gv_y, right_w - 1, gv_h, fill=BG_LIGHT, line=GREY_BORDER)
add_textbox(s2, right_x + 0.65, gv_y + 0.08, right_w - 1.3, 0.25,
            "GROUND VERIFICATION", size=10, bold=True, color=BLUE_TITLE)

def add_ground_row(yoff, code, label):
    y_row = gv_y + yoff
    cb = add_rect(s2, right_x + 0.7, y_row + 0.03, 0.22, 0.22,
                  fill=BLUE_TITLE, line=BLUE_TITLE, line_w=1.25)
    add_textbox(s2, right_x + 0.7, y_row - 0.02, 0.22, 0.28,
                "✓", size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_textbox(s2, right_x + 1.0, y_row + 0.02, 0.5, 0.25,
                code, size=11, bold=True, color=BLACK)
    add_textbox(s2, right_x + 1.45, y_row + 0.02, 3, 0.25,
                label, size=11, color=BLACK)

add_ground_row(0.36, "G2", "Outdoor calibration")
add_ground_row(0.62, "G1", "Unit tests + dry-run")

# Arrow up
add_textbox(s2, right_x + right_w/2 - 0.2, gv_y + gv_h + 0.02, 0.4, 0.2,
            "▲", size=12, color=GREY_LIGHT, align=PP_ALIGN.CENTER)

# Simulation Foundation box
sf_y = gv_y + gv_h + 0.3
sf_h = 1.85
add_rect(s2, right_x, sf_y, right_w, sf_h, fill=GREEN_BG, line=GREEN_ACCENT, line_w=2)
add_textbox(s2, right_x + 0.15, sf_y + 0.08, right_w - 0.3, 0.3,
            "SIMULATION FOUNDATION", size=12, bold=True, color=GREEN_ACCENT)
add_textbox(s2, right_x + 0.15, sf_y + 0.38, right_w - 0.3, 0.25,
            "All 12 mission requirements verified end-to-end in SITL",
            size=10, color=GREEN_ACCENT)

# 3 columns of requirements
col_w = 1.9
col_y = sf_y + 0.68

# Col 1
add_multiline(s2, right_x + 0.15, col_y, col_w, 1.0, [
    "Spiral search pattern",
    "AI detection + centering",
    "Geofence + SSSI no-fly zone",
    "PLB beacon redirect",
], size=9, color=GREY_TEXT)

# Col 2
add_multiline(s2, right_x + 0.15 + col_w + 0.1, col_y, col_w, 1.0, [
    "Attitude-compensated GPS",
    "Payload deploy sequence",
    "RTL failsafes",
    "Offset landing",
], size=9, color=GREY_TEXT)

# Col 3 - Simulated realism
col3_x = right_x + 0.15 + 2 * (col_w + 0.1)
add_textbox(s2, col3_x, col_y, col_w, 0.22,
            "Simulated Realism", size=10, bold=True, color=GREEN_ACCENT)
add_multiline(s2, col3_x, col_y + 0.25, col_w + 0.3, 1.0, [
    "Same 1456×1088 as real camera",
    "Camera tilt (pitch/roll)",
    "Motion blur at flight speed",
    "GPS drift noise (±3m)",
    "Altitude-correct target scaling",
], size=8, color=GREY_TEXT)


# ── Save ───────────────────────────────────────────────────────────────────
prs.save(OUT_PPTX)
print(f"Saved: {OUT_PPTX}")
try:
    shutil.copy(OUT_PPTX, DOWNLOADS)
    print(f"Copied to: {DOWNLOADS}")
except PermissionError:
    print(f"Skipped Downloads copy (file locked - close PowerPoint and re-run).")
print("All text and shapes are native PowerPoint - fully editable.")
