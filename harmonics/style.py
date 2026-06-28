"""Shared, pre-verified building blocks for the film
"From Rings to Spheres: The Topology of Frequencies".

Every scene does ``from style import *`` then calls ``configure()`` once at module
level. This module centralizes the palette, the 1-D target function, the 2-D axes,
and (crucially) the hard MORPH MATH + spherical harmonics + per-face coloring, all
verified with real Manim renders before use. Scene files should COMPOSE these
building blocks (camera / timing / labels) rather than re-derive the geometry.

Verified environment facts (do not relearn the hard way):
  * Manim CE 0.20.1, Python 3.12, scipy 1.18.0.
  * scipy.special.sph_harm is REMOVED in 1.18 -> real_Y() below uses lpmv
    (stable across versions, no dependency on sph_harm_y existing).
  * Color a Surface by an arbitrary field by iterating its faces and using the
    PARAMETRIC (u,v) recovered from the row-major submobject index
    (i -> (iu, iv) = divmod(i, nv)). set_fill_by_value only maps a coordinate
    axis; face.get_center() back-inference breaks on radially-bulged surfaces.
  * In a ThreeDScene, relation/punchline labels must go through
    add_fixed_in_frame_mobjects (after the camera orientation is set) or they
    tumble with the camera.
  * Run renders from the project root: ``uv run manim -ql <file.py> <Scene>``.
"""
import numpy as np
from manim import *
from scipy.special import lpmv, factorial

TAU = 2 * np.pi

# =========================== PALETTE (named roles) =========================== #
BG         = "#0E1116"   # background: near-black, faint blue
AXIS       = "#5A6472"   # axes, ticks, gridlines, reference interval (slate)
AXIS_LABEL = "#9DA5B4"   # axis number / letter labels
CURVE      = "#4FC3F7"   # THE primary function curve / wrapped ring (signal cyan)
COMP       = "#FFC857"   # Fourier component waves "ingredients you sum" (amber)
COMP_2     = "#2EC4B6"   # secondary component (teal) -- cos vs sin contrast
ACCENT     = "#FF6B6B"   # highlight / endpoint dots / "this matters" (coral)
GLUE       = "#9DE0AD"   # edges being identified (soft green)
POLE       = "#FF4D9D"   # north / south pole markers (magenta-pink)
TEXT       = "#E8EDF2"   # labels, equivalence-class relations

# Neutral surface checkerboard (topology morphs, before any field coloring)
CHECK_A    = "#2E8BA6"
CHECK_B    = "#1E5C70"
CHECKERS   = [CHECK_A, CHECK_B]

# Diverging colormap reserved EXCLUSIVELY for signed field values
# (Fourier mode sign, spherical-harmonic lobes). Learned once, reused everywhere.
DIV_NEG    = "#3457D5"   # negative lobe (blue)
DIV_MID    = "#1C2433"   # zero on FILLED surfaces (near-BG so flat zero reads dark)
DIV_MID_LOOP = "#D7DBE3" # zero on thin CURVES (light, so a heatmap line stays visible)
DIV_POS    = "#FF5A4D"   # positive lobe (red)

# =========================== STROKES / SIZES =========================== #
SW_PRIMARY = 5.0
SW_COMP    = 2.5
SW_AXIS    = 2.0
SW_SURF    = 0.45        # faint wireframe; fill carries the story
SW_GLUE    = 8.0         # highlight of edges being glued
DOT_R      = 0.07
POLE_R     = 0.09
RING_R     = 2.0         # radius of the Scene-1/2 ring; also sets the axes x-scale
FS_TITLE   = 44
FS_MATH    = 34
FS_REL     = 30          # equivalence-class relations
FS_NOTE    = 26          # small annotations / punchlines


# =========================== GLOBAL CONFIG =========================== #
def configure():
    """Apply background + default text colors. Call ONCE at module level per scene."""
    config.background_color = BG
    Text.set_default(color=TEXT, font_size=FS_NOTE)
    MathTex.set_default(color=TEXT)
    Tex.set_default(color=TEXT)


# =========================== THE 1-D TARGET FUNCTION =========================== #
# Pure trig => f(0) == f(2pi) (periodic), which is exactly why the ring closes.
COEFFS = [("sin", 1, 0.55), ("cos", 2, 0.30), ("sin", 3, 0.18)]   # (kind, n, amp)


def target_f(x):
    """f(x) = sum of COEFFS modes on [0, 2pi]. Scalar or ndarray. Periodic."""
    s = 0.0
    for kind, n, a in COEFFS:
        s = s + (a * np.sin(n * x) if kind == "sin" else a * np.cos(n * x))
    return s


def component(kind, n, a):
    """Return a Python f(x) for one component a*sin(nx) or a*cos(nx)."""
    if kind == "sin":
        return lambda x: a * np.sin(n * x)
    return lambda x: a * np.cos(n * x)


def partial_sum(k):
    """Return f(x) using only the first k components (for the build-up reveal)."""
    use = COEFFS[:k]

    def f(x):
        s = 0.0
        for kind, n, a in use:
            s = s + (a * np.sin(n * x) if kind == "sin" else a * np.cos(n * x))
        return s

    return f


# =========================== 2-D AXES + WAVE =========================== #
def make_axes(x_max=TAU):
    """Styled Axes on [0,x_max] x [-1.3,1.3]; no tips. Used by S1 and recalled in S3.

    The x-scale is RING_R screen-units per data-unit and the y-scale is 1.0, so the
    plotted graph coincides EXACTLY with ring_roll_point(x, 0) -- the line->ring
    morph can take over with no jump in width or amplitude.
    """
    return Axes(
        x_range=[0, x_max, np.pi / 2], y_range=[-1.3, 1.3, 0.5],
        x_length=x_max * RING_R, y_length=2.6, tips=False,
        axis_config={"color": AXIS, "stroke_width": SW_AXIS, "include_ticks": True},
    )


def wave(axes, fn, color=CURVE, width=SW_PRIMARY, x_range=(0, TAU)):
    """axes.plot of fn over x_range, styled. Centralizes curve styling."""
    return axes.plot(
        fn, x_range=[x_range[0], x_range[1], 0.02], color=color, stroke_width=width
    )


# =========================== S1: LINE <-> RING MORPH =========================== #
def line_circle_point(x, t, R=2.0, x0=-4.0, x1=4.0, fn=target_f, amp=1.0):
    """Simple linear blend straight-graph (t=0) <-> wrapped ring (t=1).

    Reference kernel (verified to close seamlessly since fn(0)==fn(2pi)). The film
    prefers ``ring_roll_point`` for a more physical "rolling" motion, but this is a
    robust fallback. Returns np.array([X, Y, 0]).
    """
    val = fn(x)
    sx = x0 + (x1 - x0) * (x / TAU)
    line_pt = np.array([sx, val, 0.0])
    rad = R + amp * val
    ang = x - np.pi / 2                       # ring starts at bottom, sweeps CCW
    circ_pt = np.array([rad * np.cos(ang), rad * np.sin(ang), 0.0])
    return (1 - t) * line_pt + t * circ_pt


def bend_point(q, t, length):
    """Roll a 1-D strip into an arc / full circle (the *physical* roll-up).

    q in [0,1] along the strip; t in [0,1] bend amount (0 = straight horizontal
    segment centered at origin with +y "up" normal; 1 = closed circle of radius
    length/(2pi) with OUTWARD normal). Returns (point2d, normal2d).
    """
    if t < 1e-3:
        return np.array([(q - 0.5) * length, 0.0]), np.array([0.0, 1.0])
    phi = t * TAU
    rho = length / phi
    theta = (q - 0.5) * phi
    pt = np.array([rho * np.sin(theta), rho * (np.cos(theta) - 1.0)])
    nrm = np.array([np.sin(theta), np.cos(theta)])
    return pt, nrm


def ring_base_point(x, t, R=RING_R):
    """Bare rolling axis point (no function). x in [0,2pi]. Recentered on origin."""
    pt, _ = bend_point(x / TAU, t, TAU * R)
    return np.array([pt[0], pt[1] + t * R, 0.0])


def ring_roll_point(x, t, R=RING_R, fn=target_f, amp=1.0):
    """Function graph riding the rolling axis: the strip bends into a ring and the
    graph rides as a radial (outward) offset. x in [0,2pi]. Returns np.array([X,Y,0]).
    Verified to produce a clean arch mid-roll and a seamless wavy ring at t=1.
    """
    pt, nrm = bend_point(x / TAU, t, TAU * R)
    p = pt + amp * fn(x) * nrm
    return np.array([p[0], p[1] + t * R, 0.0])


# =========================== S2: POLAR LOOP + HEART =========================== #
def polar_loop_point(theta, harmonics, R=2.0):
    """Closed star-shaped loop r(theta)=R + sum a_k cos(k th)+b_k sin(k th).
    harmonics: list of (k, a_k, b_k). Returns np.array([x,y,0])."""
    r = R
    for k, a, b in harmonics:
        r = r + a * np.cos(k * theta) + b * np.sin(k * theta)
    return np.array([r * np.cos(theta), r * np.sin(theta), 0.0])


def heart_point(theta, scale=0.13, center=np.array([0.0, -0.3, 0.0])):
    """Classic parametric heart (finite trig sum). theta in [0,2pi]."""
    x = 16 * np.sin(theta) ** 3
    y = (13 * np.cos(theta) - 5 * np.cos(2 * theta)
         - 2 * np.cos(3 * theta) - np.cos(4 * theta))
    return center + scale * np.array([x, y, 0.0])


# Named coefficient sets for the S2 morph sequence (base R=2.0).
LOOP_RING   = [(1, 0.0, 0.55), (2, 0.30, 0.0), (3, 0.0, 0.18)]   # ~ the S1 wrap
LOOP_CLOVER = [(4, 0.9, 0.0)]                                    # 4-fold petals
LOOP_BLOB   = [(2, 0.25, 0.0), (3, 0.0, 0.5), (5, 0.0, 0.3)]     # organic wobble


# --------------------------------------------------------------------------- #
# Scene 2 unified deformation: every shape shares ONE direction convention so
# morphs never rotate or flip. The direction matches ring_roll_point(x, 1) (the
# Scene-1 ring), so Scene 2 can pick up exactly where Scene 1 left off.
# --------------------------------------------------------------------------- #
def ring_dir(x):
    """Unit direction of the Scene-1 ring at parameter x in [0,2pi]
    (== ring_base_point(x,1)/R). Sweeps the loop once."""
    return np.array([-np.sin(x), -np.cos(x), 0.0])


def wave_radial(x):
    """Radial offset that reproduces the Scene-1 wavy ring."""
    return target_f(x)


def clover_radial(x):
    """4-fold petals as x sweeps the loop once."""
    return 0.9 * np.cos(4 * x)


def blob_radial(x):
    """Organic multi-frequency wobble."""
    return 0.25 * np.cos(2 * x) + 0.5 * np.sin(3 * x) + 0.3 * np.sin(5 * x)


def deform_point(x, radial, R=RING_R):
    """A closed loop point: (R + radial(x)) along the shared ring direction.
    deform_point(x, wave_radial) == ring_roll_point(x, 1)."""
    return (R + radial(x)) * ring_dir(x)


def heart_aligned(x):
    """Heart parametrized to match ring_dir's start (bottom) and direction, so a
    blob->heart blend morphs cleanly without flipping."""
    return heart_point(x + np.pi)


# =========================== SPHERICAL HARMONICS =========================== #
def real_Y(l, m, theta, phi):
    """Real spherical harmonic Y_l^m.  theta = colatitude [0,pi], phi = azimuth
    [0,2pi]. Built on lpmv (version-independent). Scalars or ndarrays.
    Verified against the Y_2^0 closed form."""
    am = abs(m)
    norm = np.sqrt(
        (2 * l + 1) / (4 * np.pi) * factorial(l - am) / factorial(l + am)
    )
    P = lpmv(am, l, np.cos(theta))
    if m > 0:
        return np.sqrt(2.0) * norm * P * np.cos(m * phi)
    if m < 0:
        return np.sqrt(2.0) * norm * P * np.sin(am * phi)
    return norm * P


# =========================== FIELD COLORING =========================== #
def div_color(value, vmax, mid=DIV_MID):
    """Map a signed scalar in [-vmax, vmax] to the diverging ManimColor
    (blue < 0, `mid` ~ 0, red > 0). `mid` defaults to the near-BG dark used for
    filled surfaces; pass DIV_MID_LOOP for thin curves."""
    t = float(np.clip((value / vmax + 1) / 2, 0.0, 1.0))
    if t < 0.5:
        return interpolate_color(ManimColor(DIV_NEG), ManimColor(mid), t * 2)
    return interpolate_color(ManimColor(mid), ManimColor(DIV_POS), (t - 0.5) * 2)


def loop_vmax(value_fn, n=300):
    """Max |value_fn| around the loop, for normalizing a heatmap."""
    xs = np.linspace(0, TAU, n, endpoint=False)
    return max(float(np.max(np.abs([value_fn(x) for x in xs]))), 1e-6)


def colored_loop(point_fn, value_fn, vmax=None, n=300, stroke_width=SW_PRIMARY):
    """A closed curve drawn as `n` short segments, each colored by value_fn via the
    SAME diverging map used for spherical harmonics (red = positive, blue = negative).
    point_fn(x) -> 3D point, value_fn(x) -> signed scalar; x in [0, TAU]. Returns a
    VGroup of n Lines, so Transform between two colored_loops interpolates both the
    geometry and the colors."""
    if vmax is None:
        vmax = loop_vmax(value_fn, n)
    xs = np.linspace(0, TAU, n + 1)
    segs = VGroup()
    for i in range(n):
        xm = 0.5 * (xs[i] + xs[i + 1])
        segs.add(Line(
            point_fn(xs[i]), point_fn(xs[i + 1]),
            color=div_color(value_fn(xm), vmax, mid=DIV_MID_LOOP),
            stroke_width=stroke_width,
        ))
    return segs


def uniform_loop(point_fn, color=CURVE, n=300, stroke_width=SW_PRIMARY):
    """A closed curve as `n` segments of a single color (heatmap OFF). Same segment
    count as colored_loop, so Transform between the two cleanly turns the heatmap
    on/off while (optionally) deforming the shape."""
    xs = np.linspace(0, TAU, n + 1)
    return VGroup(*[
        Line(point_fn(xs[i]), point_fn(xs[i + 1]), color=color,
             stroke_width=stroke_width)
        for i in range(n)
    ])


def radial_offset(point_fn, R=RING_R):
    """value_fn giving the signed radial deviation |point_fn(x)| - R (how far the
    loop bulges out/in from the base circle). Drives the Scene-2 heatmaps."""
    return lambda x: float(np.linalg.norm(point_fn(x))) - R


def color_surface_by_field(surface, field_uv, nu, nv,
                           u_range=(0, TAU), v_range=(0, TAU),
                           vmax=None, opacity=1.0):
    """Color each face of `surface` by field_uv(u, v) at the face's PARAMETRIC
    center. Uses verified row-major index i -> (iu, iv) = divmod(i, nv) (u outer,
    v inner). Exact regardless of radial displacement. Mutates & returns surface.
    """
    u0, u1 = u_range
    v0, v1 = v_range
    n = len(surface.submobjects)
    vals = np.empty(n)
    for i in range(n):
        iu, iv = divmod(i, nv)
        u = u0 + (iu + 0.5) / nu * (u1 - u0)
        v = v0 + (iv + 0.5) / nv * (v1 - v0)
        vals[i] = field_uv(u, v)
    if vmax is None:
        vmax = np.max(np.abs(vals)) or 1.0
    for i, face in enumerate(surface.submobjects):
        face.set_fill(div_color(vals[i], vmax), opacity=opacity)
        face.set_stroke(width=0.0, opacity=0.0)
    return surface


# =========================== S3: SQUARE PATCH =========================== #
def patch_surf(t, side=3.0):
    """Flat patch that extrudes from a line (t=0) to a square (t=1).
    u,v in [0,2pi]; returns a function for Surface()."""
    half = side / 2.0

    def fn(u, v):
        return np.array([
            (u / TAU - 0.5) * side,
            (v / TAU - 0.5) * side * t,
            0.0,
        ])
    return fn


def make_patch(t, side=3.0, res=(16, 16), **kw):
    return Surface(
        patch_surf(max(t, 1e-3), side), u_range=[0, TAU], v_range=[0, TAU],
        resolution=res, checkerboard_colors=CHECKERS, stroke_width=SW_SURF,
        fill_opacity=1.0, **kw,
    )


def extrude_surf(h):
    """Square patch that extrudes from a flat line (h=0) to the full square (h=1).
    Stands in the x-z plane (vertical), so at h=1 it is IDENTICAL to torus_surf(0) /
    sphere_surf(0)'s flat square and Scene 3 hands the square straight to Scene 4 with
    no grid/size/orientation pop."""
    def fn(u, v):
        return np.array([
            (u / TAU - 0.5) * PATCH_SIDE,
            0.0,
            (v / TAU - 0.5) * PATCH_SIDE * h,
        ])
    return fn


def make_extrude(h, res=(36, 24), **kw):
    """Extruding square. Defaults to the SAME resolution as make_torus so the
    Scene 3 -> Scene 4 cut is seamless (make_extrude(1.0) == make_torus(0.0))."""
    return Surface(
        extrude_surf(max(h, 1e-3)), u_range=[0, TAU], v_range=[0, TAU],
        resolution=res, checkerboard_colors=CHECKERS, stroke_width=SW_SURF,
        fill_opacity=1.0, **kw,
    )


# =========================== SHARED SQUARE -> CYLINDER ROLL =========================== #
# Both the torus (S4) and the sphere (S5) glue the LEFT-RIGHT edges first, rolling the
# square into a VERTICAL cylinder.  That first roll is ONE shared transform so the two
# scenes look identical up to the cylinder.  It is a *physical* paper-roll (bend_point):
# the strip bends symmetrically and its edges travel together to meet at the seam -- no
# lopsided lerp that swings one edge across the interior.  Because it is non-linear in
# the morph parameter, the scenes drive it with a ValueTracker + always_redraw (NOT a
# keyframe Transform, which would re-introduce the straight-line lerp).
PATCH_SIDE = 3.0   # screen size of the flat square (continuity with S3)
ROLL_R = 1.1       # radius of the shared cylinder the square rolls into


def roll_point(u, s1, R=ROLL_R):
    """Symmetric roll of the u-strip (width PATCH_SIDE, along x) into a circle of
    radius R in the x-y plane (cylinder axis = z). s1=0 flat, s1=1 closed cylinder.
    Edges (u=0 and u=2pi) meet together at the seam; nothing sweeps through the body.
    Returns (x, y). The closed circle is (R*(-sin u), R*(-cos u)); stage-2 targets
    below reuse that same (cu, su) longitude convention so there is no twist."""
    if s1 < 1e-3:
        return (u / TAU - 0.5) * PATCH_SIDE, 0.0
    length = (1.0 - s1) * PATCH_SIDE + s1 * (TAU * R)   # arc length grows into 2*pi*R
    pt, _ = bend_point(u / TAU, s1, length)
    return pt[0], pt[1] + s1 * R


def _cu_su(u):
    """Longitude direction matching roll_point's closed circle (seam at u=0)."""
    return -np.sin(u), -np.cos(u)


# =========================== S4: SQUARE -> CYLINDER -> TORUS =========================== #
# THEN the top-bottom edges (v) bend the tube into a donut.
TORUS_RB = 2.0    # big (center) radius
TORUS_RT = 0.7    # tube radius


def torus_surf(t):
    """t in [0,2]: 0->1 flat square -> cylinder (shared symmetric roll, u wraps);
    1->2 cylinder -> torus (bend tube along v into the big ring, in the x-z plane so
    the tube's y-component is preserved and nothing tips through)."""
    Rb, rt = TORUS_RB, TORUS_RT

    def fn(u, v):
        s1 = np.clip(t, 0.0, 1.0)
        s2 = np.clip(t - 1.0, 0.0, 1.0)
        x, y = roll_point(u, s1)
        base = np.array([x, y, (v / TAU - 0.5) * PATCH_SIDE])
        cu, su = _cu_su(u)
        beta = v - np.pi
        tor = np.array([(Rb + rt * cu) * np.cos(beta),
                        rt * su,
                        (Rb + rt * cu) * np.sin(beta)])
        return (1 - s2) * base + s2 * tor
    return fn


def make_torus(t, res=(36, 24), checker=True, fill=1.0, **kw):
    return Surface(
        torus_surf(t), u_range=[0, TAU], v_range=[0, TAU], resolution=res,
        checkerboard_colors=(CHECKERS if checker else False),
        stroke_width=SW_SURF, fill_opacity=fill, **kw,
    )


def torus_mode(u, v):
    """A 2-D Fourier mode on the torus (signed field for diverging color)."""
    return np.sin(2 * u) * np.cos(3 * v)


# =========================== S5: SQUARE -> CYLINDER -> SPHERE =========================== #
SPHERE_R = 1.8


def sphere_surf(t):
    """t in [0,2]: 0->1 flat square -> cylinder (shared symmetric roll, u wraps);
    1->2 cylinder -> sphere (pinch top edge to N pole, bottom to S pole, inflating
    the thin roll-cylinder out to radius R). u longitude, v in [0,pi] colatitude.
    The sphere reuses roll_point's (cu, su) longitude convention so there's no twist."""
    R = SPHERE_R

    def fn(u, v):
        s1 = np.clip(t, 0.0, 1.0)
        s2 = np.clip(t - 1.0, 0.0, 1.0)
        x, y = roll_point(u, s1)
        base = np.array([x, y, (1.0 - 2.0 * v / np.pi) * (PATCH_SIDE / 2.0)])
        cu, su = _cu_su(u)
        sph = np.array([R * np.sin(v) * cu, R * np.sin(v) * su, R * np.cos(v)])
        return (1 - s2) * base + s2 * sph
    return fn


def make_sphere(t, res=(48, 24), checker=True, fill=1.0, **kw):
    return Surface(
        sphere_surf(t), u_range=[0, TAU], v_range=[0, np.pi], resolution=res,
        checkerboard_colors=(CHECKERS if checker else False),
        stroke_width=SW_SURF, fill_opacity=fill, **kw,
    )


def sh_radius_surf(terms, R=SPHERE_R, amp=0.45):
    """Sphere radially displaced by a (sum of) spherical harmonic(s).
    terms: list of (l, m, weight). radius = R*(1 + amp * sum w*Y_l^m).
    Returns a Surface function. u=azimuth, v=colatitude."""
    def fn(u, v):
        disp = 0.0
        for l, m, w in terms:
            disp += w * real_Y(l, m, v, u)
        r = R * (1 + amp * disp)
        cu, su = _cu_su(u)          # match sphere_surf's longitude so morphs don't flip
        return np.array([r * np.sin(v) * cu,
                         r * np.sin(v) * su,
                         r * np.cos(v)])
    return fn


def _heart_xy(u):
    """The classic 2-D heart outline (x, y) for parameter u in [0, 2pi]."""
    hx = 16 * np.sin(u) ** 3
    hy = 13 * np.cos(u) - 5 * np.cos(2 * u) - 2 * np.cos(3 * u) - np.cos(4 * u)
    return hx, hy


def _heart_radius(u):
    """Smooth, single-valued heart silhouette radius as a function of azimuth u
    (star-shaped about the origin -> no rendering slit). Cusp/point at the bottom
    (u=3pi/2), a gentle cleft at the top (u=pi/2) flanked by two lobes."""
    def bump(c, w):
        return np.exp(-(((u - c + np.pi) % TAU - np.pi) / w) ** 2)
    base = 1.0 - 0.55 * np.sin(u)                                  # teardrop, point down
    # lobes: wide, centered low on the sides, a touch taller
    lobes = 1.0 * bump(np.pi / 2 - 0.72, 0.8) + 1.0 * bump(np.pi / 2 + 0.72, 0.8)
    cleft = 0.42 * bump(np.pi / 2, 0.36)                           # notch between lobes
    cusp = 0.5 * bump(3 * np.pi / 2, 0.45)                         # rounded bottom point
    return base + lobes - cleft + cusp


def heart_surface(R=1.6, thickness=0.62):
    """A puffed 'pillow' 3-D heart, parametrized by AZIMUTH u (and v in [0,pi]) with
    poles along Z -- the SAME convention as an ordinary sphere -- so a NORMAL sphere
    morphs into it as a clean radial deformation (no flip/twist), and the sphere you
    morph from still looks like a normal sphere. Renders solid (star-shaped). View
    from a top-down-ish camera so the valentine reads (cusp points down)."""
    sx = 1.45 * R / 1.6              # widen x a touch for nicer lobes
    sy = 1.15 * R / 1.6
    yc = 0.78 * R / 1.6

    def fn(u, v):
        # match sphere_surf's longitude (cu, su) so a normal sphere morphs in radially
        # with no flip; shift the silhouette by -pi/2 so the cusp still points to -y.
        rr = _heart_radius(u - np.pi / 2)
        r = np.sin(v)
        cu, su = _cu_su(u)
        return np.array([sx * r * rr * cu,
                         yc + sy * r * rr * su,
                         np.cos(v) * thickness])
    return fn


def sh_lobes_surf(l, m, target=1.9):
    """The classic spherical-harmonic 3-D plot: radius = |Y_l^m| (normalized so the
    biggest lobe reaches `target`). The familiar lobed 'balloon' shape; pair with
    color_surface_by_field on real_Y to sign-color the lobes (red +, blue -).
    u = azimuth, v = colatitude."""
    th = np.linspace(0, TAU, 48)
    ph = np.linspace(1e-3, np.pi - 1e-3, 48)
    TH, PH = np.meshgrid(th, ph)
    vmax = float(np.max(np.abs(real_Y(l, m, PH, TH)))) + 1e-9

    def fn(u, v):
        r = target * abs(real_Y(l, m, v, u)) / vmax
        cu, su = _cu_su(u)          # match sphere_surf's longitude so morphs don't flip
        return np.array([r * np.sin(v) * cu,
                         r * np.sin(v) * su,
                         r * np.cos(v)])
    return fn


def sh_field(terms):
    """Matching signed field for coloring an sh_radius_surf (u=azimuth, v=colat)."""
    def field(u, v):
        s = 0.0
        for l, m, w in terms:
            s += w * real_Y(l, m, v, u)
        return s
    return field


# =========================== 3-D CAMERA HELPER =========================== #
def set_3d(scene, phi=68, theta=-50):
    """Standard 3/4 view on a ThreeDScene (degrees)."""
    scene.set_camera_orientation(phi=phi * DEGREES, theta=theta * DEGREES)


# =========================== VOICEOVER =========================== #
def _resolve_input_device(spec):
    """Resolve a VOICE_DEVICE spec to a Core-Audio (host-API 0) device index.

    spec may be an integer index or a case-insensitive name substring (e.g. "AirPods").
    Falls back to the first available input device so a headless render NEVER hits the
    interactive picker. Returns an int, or None if no input device exists.

    Pinning the device matters for more than convenience: manim-voiceover's picker also
    sets the sample rate from the chosen device, and it builds the cache key BEFORE that
    happens -- so the first line in a session caches at the default rate and later lines
    at the device rate. On a headless re-render everything is looked up at the default
    rate, so those later lines miss and it tries to record again. With the device pinned
    the picker never runs, the rate stays fixed, and cached takes are reused reliably.
    """
    import pyaudio
    pa = pyaudio.PyAudio()
    try:
        host = 0
        n = int(pa.get_host_api_info_by_index(host).get("deviceCount", 0) or 0)

        def inputs():
            for i in range(n):
                d = pa.get_device_info_by_host_api_device_index(host, i)
                if (d.get("maxInputChannels", 0) or 0) > 0:
                    yield i, str(d.get("name", ""))

        spec = (spec or "").strip()
        if spec.isdigit():
            return int(spec)
        if spec:
            for i, name in inputs():
                if spec.lower() in name.lower():
                    return i
        for i, _ in inputs():       # fallback: first input device
            return i
        return None
    finally:
        pa.terminate()


def setup_voice(scene):
    """Attach the speech service for a VoiceoverScene.

    Default: gTTS draft audio (robotic, needs internet) -- good for nailing timing.
    Set the env var VOICE=record to record your own voice via the microphone
    (RecorderService) for the final pass. Imports are lazy so non-voiceover scenes
    (e.g. the title card) don't need manim-voiceover.

    VOICE_DEVICE selects the mic by index or name substring (default "AirPods"); the
    device is pinned so the recorder never runs its interactive picker -- see
    _resolve_input_device for why that keeps the voiceover cache reusable.
    """
    import os
    mode = os.environ.get("VOICE", "gtts").lower()
    if mode in ("record", "rec", "mic"):
        from manim_voiceover.services.recorder import RecorderService
        dev = _resolve_input_device(os.environ.get("VOICE_DEVICE", "AirPods"))
        scene.set_speech_service(
            RecorderService(transcription_model=None, device_index=dev))
    else:
        from manim_voiceover.services.gtts import GTTSService
        scene.set_speech_service(GTTSService(transcription_model=None))
