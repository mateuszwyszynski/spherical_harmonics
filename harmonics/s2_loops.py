"""SCENE 2 - Deforming the Ring (voiceover-timed).

Inherits the wavy ring from Scene 1, reads it as a heatmap (red +, blue -), then as
a deformation of the base ring, and finally deforms it through clover -> blob ->
heart -- any continuous closed loop. Heatmap rides along the whole way.
"""
from style import *
from manim_voiceover import VoiceoverScene

configure()

A = ("Fourier was interested in heat on rings, but this whole approach turns out to "
     "be far more general.")
B = ("The result of adding these waves can be read as a heatmap on the ring - red "
     "where the function is positive, blue where it is negative.")
C = ("But we can equally see it as a physical deformation of the base ring into a "
     "new shape.")
D = ("And that is what makes it so powerful: by choosing the waves, we can draw "
     "essentially any continuous, closed loop in the plane - a clover, a squiggly "
     "blob, even a heart.")


def s2_point(x, stage):
    """stage 0 circle; [0,1] circle->clover; [1,2] clover->blob; [2,3] blob->heart."""
    R = RING_R
    if stage <= 1.0:
        return (R + stage * clover_radial(x)) * ring_dir(x)
    if stage <= 2.0:
        s = stage - 1.0
        return (R + (1 - s) * clover_radial(x) + s * blob_radial(x)) * ring_dir(x)
    s = min(stage - 2.0, 1.0)
    return (1 - s) * ((R + blob_radial(x)) * ring_dir(x)) + s * heart_aligned(x)


def shape_at(stage):
    return lambda x: s2_point(x, stage)


class S2DeformRing(VoiceoverScene, Scene):
    def construct(self):
        setup_voice(self)
        wavy_fn = lambda x: ring_roll_point(x, 1.0)
        circ_fn = shape_at(0.0)
        vf = loop_vmax(target_f)
        vdef = max(loop_vmax(radial_offset(shape_at(s))) for s in (1.0, 2.0, 3.0))

        # inherit Scene 1's wavy ring (plain blue), segmented so it can recolour
        loop = uniform_loop(wavy_fn, color=CURVE)
        self.add(loop)

        # ---- A: establish (hold the inherited ring) ---------------------- #
        with self.voiceover(text=A) as vo:
            self.wait(vo.duration)

        # ---- B: read it as a heatmap ------------------------------------- #
        with self.voiceover(text=B) as vo:
            heat_wavy = colored_loop(wavy_fn, target_f, vmax=vf)
            self.play(ReplacementTransform(loop, heat_wavy), run_time=vo.duration * 0.6)
            loop = heat_wavy
            self.wait(vo.duration * 0.4)

        # ---- C: see it as a deformation of the base ring ----------------- #
        with self.voiceover(text=C) as vo:
            heat_circle = colored_loop(circ_fn, target_f, vmax=vf)
            self.play(ReplacementTransform(loop, heat_circle),
                      run_time=vo.duration, rate_func=smooth)
            loop = heat_circle

        # ---- D: deform into any shape (clover -> blob -> heart) ----------- #
        clover = colored_loop(shape_at(1.0), radial_offset(shape_at(1.0)), vmax=vdef)
        blob = colored_loop(shape_at(2.0), radial_offset(shape_at(2.0)), vmax=vdef)
        heart = colored_loop(shape_at(3.0), radial_offset(shape_at(3.0)), vmax=vdef)
        with self.voiceover(text=D) as vo:
            seg = vo.duration / 3.0
            name = None
            for target_loop, text in [(clover, "clover"), (blob, "blob"),
                                      (heart, "heart")]:
                self.play(ReplacementTransform(loop, target_loop),
                          run_time=seg * 0.72, rate_func=smooth)
                loop = target_loop
                new_name = Text(text, color=TEXT, font_size=FS_NOTE).to_edge(
                    DOWN, buff=0.7)
                if name is None:
                    self.play(FadeIn(new_name, shift=UP * 0.15), run_time=seg * 0.28)
                else:
                    self.play(FadeTransform(name, new_name), run_time=seg * 0.28)
                name = new_name

        # ---- punchline ---------------------------------------------------- #
        punch = MathTex(r"\gamma(s)=\sum_k c_k\,e^{iks}\quad(\text{any closed loop})",
                        font_size=FS_MATH).to_edge(UP, buff=0.7)
        self.play(Write(punch), run_time=1.4)
        self.wait(1.0)
        self.play(FadeOut(loop), FadeOut(name), FadeOut(punch), run_time=1.0)
        self.wait(0.3)
