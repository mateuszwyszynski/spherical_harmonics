"""Scene 0 - Introduction & Motivation (voiceover-timed).

Montage of classic SH lobe shapes (the 'intriguing 3D representations'), then a
smooth Earth that morphs into an exaggerated lumpy geoid with a gravity heatmap.
"""
from style import *
from manim_voiceover import VoiceoverScene

configure()

RES = (64, 32)
GALLERY = [(4, 0), (3, 2), (6, 5)]
GEOID = [(2, 0, 0.8), (2, 2, 0.7), (3, 1, -0.9), (3, 2, 0.6),
         (4, 3, 0.5), (5, 2, -0.4)]

P1 = ("For some time, I wanted to get familiar with spherical harmonics. I've seen "
      "the formulas and the intriguing 3D representations, but I really didn't feel "
      "friends with the concept.")
P2 = ("Most resources I've encountered refer to angular momentum when introducing "
      "them. But if you read Wikipedia, you can see that they were actually "
      "developed much earlier than quantum mechanics came around.")
P3 = ("In this video, I'll try to give a brief, intuitive explanation, using just "
      "geometrical visualizations and 1D Fourier series as a starting point.")


def _lobes(l, m):
    s = Surface(sh_lobes_surf(l, m), u_range=[0, TAU], v_range=[0, np.pi],
                resolution=RES, checkerboard_colors=False, stroke_width=0.0,
                fill_opacity=1.0)
    color_surface_by_field(s, lambda u, v: real_Y(l, m, v, u),
                           nu=RES[0], nv=RES[1], v_range=(0, np.pi))
    return s


class S0Intro(VoiceoverScene, ThreeDScene):
    def construct(self):
        setup_voice(self)
        set_3d(self, phi=66, theta=-50)

        # ---- P1: montage of classic SH lobe shapes, rotating gently ------- #
        self.begin_ambient_camera_rotation(rate=0.20)
        S = _lobes(*GALLERY[0])
        with self.voiceover(text=P1) as vo:
            seg = vo.duration / 3.0
            self.play(FadeIn(S), run_time=seg * 0.4)
            self.wait(seg * 0.6)
            for l, m in GALLERY[1:]:
                nxt = _lobes(l, m)
                self.play(FadeTransform(S, nxt), run_time=seg * 0.4)
                S = nxt
                self.wait(seg * 0.6)
        self.stop_ambient_camera_rotation()

        # ---- P2: smooth Earth, then morph into the lumpy geoid ------------ #
        # Earth and geoid share the SAME resolution so the morph is a clean radial
        # deformation (no "cut into pieces" face-matching artifact).
        earth = Surface(sphere_surf(2.0), u_range=[0, TAU], v_range=[0, np.pi],
                        resolution=RES, checkerboard_colors=False,
                        stroke_width=0.6, fill_opacity=1.0)
        earth.set_fill(ManimColor("#2E6FB0"), opacity=1.0)
        earth.set_stroke(ManimColor("#7FB2DD"), width=0.6, opacity=0.45)
        geoid = Surface(sh_radius_surf(GEOID, R=SPHERE_R, amp=0.22),
                        u_range=[0, TAU], v_range=[0, np.pi], resolution=RES,
                        checkerboard_colors=False, stroke_width=0.0, fill_opacity=1.0)
        color_surface_by_field(geoid, sh_field(GEOID), nu=RES[0], nv=RES[1],
                               v_range=(0, np.pi))
        with self.voiceover(text=P2) as vo:
            self.play(FadeTransform(S, earth), run_time=vo.duration * 0.45)
            self.play(Transform(earth, geoid),
                      run_time=vo.duration * 0.55, rate_func=smooth)

        # ---- P3: hold the geoid, gently rotating -------------------------- #
        with self.voiceover(text=P3) as vo:
            self.begin_ambient_camera_rotation(rate=0.14)
            self.wait(vo.duration)
            self.stop_ambient_camera_rotation()
        self.wait(0.3)
