"""Scene 3 - Stepping into 3D (voiceover-timed): the 1D interval extrudes into a
2D square domain, then we ask what to do with its boundary."""
from style import *
from manim_voiceover import VoiceoverScene

configure()

L1 = ("But why limit ourselves to 2D loops? What if we want to model complex "
      "surfaces in 3D space?")
L2 = ("We can follow the exact same logic as for the 1D Fourier case. Instead of "
      "starting with a line segment, we step up a dimension and start with a 2D "
      "square domain.")
L3 = ("Now, just as we had to decide what to do with the two endpoints of our "
      "segment, we have to decide what to do with the boundary of this square to "
      "create the base 3D shape.")


class S3IntoSquare(VoiceoverScene, ThreeDScene):
    def construct(self):
        setup_voice(self)
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)

        half_dom = np.pi * RING_R
        interval = Line(LEFT * half_dom, RIGHT * half_dom,
                        color=AXIS, stroke_width=SW_AXIS)
        axes = make_axes()
        recall = wave(axes, target_f, color=CURVE)
        recall.set_stroke(opacity=0.5)

        # ---- L1: recall the 1D domain ------------------------------------ #
        with self.voiceover(text=L1) as vo:
            d = vo.duration
            self.play(FadeIn(interval), run_time=d * 0.2)
            self.play(FadeIn(axes), Create(recall), run_time=d * 0.35)
            self.wait(d * 0.25)
            self.play(FadeOut(axes), FadeOut(recall), run_time=d * 0.2)

        # ---- L2: squeeze, then extrude into a square ---------------------- #
        target_half = PATCH_SIDE / 2.0
        squeezed = Line(LEFT * target_half, RIGHT * target_half,
                        color=AXIS, stroke_width=SW_AXIS)
        strip = make_extrude(1e-3)
        with self.voiceover(text=L2) as vo:
            d = vo.duration
            self.play(Transform(interval, squeezed), run_time=d * 0.28,
                      rate_func=smooth)
            self.play(FadeIn(strip), FadeOut(interval), run_time=d * 0.12)
            self.move_camera(phi=68 * DEGREES, theta=-50 * DEGREES,
                             added_anims=[Transform(strip, make_extrude(1.0))],
                             run_time=d * 0.6, rate_func=smooth)

        # ---- L3: pose the boundary question (labels + glued edges) -------- #
        half = PATCH_SIDE / 2.0
        # the square stands in the x-z plane: u -> world-x (horizontal), v -> world-z
        # (vertical). Labels sit beside those two edges.
        x_lab = MathTex("x", color=AXIS_LABEL, font_size=FS_MATH)
        x_lab.move_to([half + 0.5, 0.0, -half - 0.3])
        y_lab = MathTex("y", color=AXIS_LABEL, font_size=FS_MATH)
        y_lab.move_to([-half - 0.5, 0.0, half + 0.3])
        fn = extrude_surf(1.0)
        edges = VGroup(*[
            ParametricFunction(f, t_range=[0, TAU, 0.05], color=GLUE,
                               stroke_width=SW_GLUE)
            for f in (lambda v: fn(0.0, v), lambda v: fn(TAU, v),
                      lambda u: fn(u, 0.0), lambda u: fn(u, TAU))
        ])
        with self.voiceover(text=L3) as vo:
            d = vo.duration
            self.add_fixed_orientation_mobjects(x_lab, y_lab)
            self.play(FadeIn(x_lab), FadeIn(y_lab), run_time=d * 0.18)
            self.play(Create(edges), run_time=d * 0.42)
            self.wait(d * 0.4)

        # leave the bare square to hand off to Scene 4
        self.play(FadeOut(edges), FadeOut(x_lab), FadeOut(y_lab), run_time=0.8)
        self.wait(0.3)
