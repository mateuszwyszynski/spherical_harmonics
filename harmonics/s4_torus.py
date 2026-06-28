"""SCENE 4 - Torus & 2D Fourier (voiceover-timed).

Glue opposite edges of a square: left~right, top~bottom -> torus. The natural basis
becomes a 2D Fourier series.
"""
from style import *
from manim_voiceover import VoiceoverScene

configure()

L1 = ("One option is to glue the opposite edges together. We attach the left edge to "
      "the right edge, and the top edge to the bottom edge. Mathematically, we define "
      "this with an equivalence class.")
L2 = "This specific geometric gluing creates a torus."
L3 = ("Because the boundaries seamlessly wrap around in both directions, the natural "
      "basis functions for this shape are just standard sines and cosines in two "
      "directions.")
L4 = "This gives us the 2D Fourier series."


def _edge_curve(t, fix_u=None, fix_v=None, color=GLUE, width=SW_GLUE, n=120):
    fn = torus_surf(t)
    param = (lambda s: fn(fix_u, s)) if fix_u is not None else (lambda s: fn(s, fix_v))
    return ParametricFunction(param, t_range=[0, TAU, TAU / n], color=color,
                              stroke_width=width)


class S4Torus(VoiceoverScene, ThreeDScene):
    def construct(self):
        setup_voice(self)
        set_3d(self)
        S = make_torus(0.0)
        self.add(S)
        left_edge = _edge_curve(0.0, fix_u=1e-3)
        right_edge = _edge_curve(0.0, fix_u=TAU - 1e-3)
        rel_lr = MathTex(r"(0,y)\sim(2\pi,y)", font_size=FS_REL).to_corner(UL)
        rel_tb = MathTex(r"(x,0)\sim(x,2\pi)", font_size=FS_REL)
        rel_tb.next_to(rel_lr, DOWN, aligned_edge=LEFT, buff=0.3)

        # ---- L1: glue left-right -> cylinder, then top-bottom -> torus ---- #
        with self.voiceover(text=L1) as vo:
            d = vo.duration
            self.add_fixed_in_frame_mobjects(rel_lr)
            self.play(Create(left_edge), Create(right_edge), Write(rel_lr),
                      run_time=d * 0.16)
            # SAME symmetric roll as the sphere scene (shared roll_point), driven by
            # the true parametrization each frame so the flat->cylinder roll stays
            # symmetric instead of lerp-crumpling. Stage 1: glue left/right -> cylinder.
            self.play(
                UpdateFromAlphaFunc(S, lambda m, a: m.become(make_torus(a))),
                UpdateFromAlphaFunc(left_edge,
                                    lambda m, a: m.become(_edge_curve(a, fix_u=1e-3))),
                UpdateFromAlphaFunc(right_edge,
                                    lambda m, a: m.become(_edge_curve(a, fix_u=TAU - 1e-3))),
                run_time=d * 0.28, rate_func=rate_functions.ease_in_out_sine)
            self.play(FadeOut(left_edge), FadeOut(right_edge), run_time=d * 0.06)
            top_edge = _edge_curve(1.0, fix_v=TAU - 1e-3)
            bot_edge = _edge_curve(1.0, fix_v=1e-3)
            self.add_fixed_in_frame_mobjects(rel_tb)
            self.play(Create(top_edge), Create(bot_edge), Write(rel_tb),
                      run_time=d * 0.16)
            # Stage 2: bend the cylinder (top/bottom edges) into the donut.
            self.play(
                UpdateFromAlphaFunc(S, lambda m, a: m.become(make_torus(1.0 + a))),
                UpdateFromAlphaFunc(top_edge,
                                    lambda m, a: m.become(_edge_curve(1.0 + a, fix_v=TAU - 1e-3))),
                UpdateFromAlphaFunc(bot_edge,
                                    lambda m, a: m.become(_edge_curve(1.0 + a, fix_v=1e-3))),
                run_time=d * 0.28, rate_func=rate_functions.ease_in_out_sine)
            self.play(FadeOut(top_edge), FadeOut(bot_edge), run_time=d * 0.06)

        # ---- L2: it's a torus -- show the two independent loops ----------- #
        u_loop = _edge_curve(2.0, fix_v=0.0, color=COMP_2, width=SW_GLUE)
        v_loop = _edge_curve(2.0, fix_u=0.0, color=GLUE, width=SW_GLUE)
        with self.voiceover(text=L2) as vo:
            self.play(Create(u_loop), Create(v_loop), run_time=vo.duration * 0.7)
            self.wait(vo.duration * 0.3)
        self.play(FadeOut(u_loop), FadeOut(v_loop), run_time=0.5)

        # ---- L3: 2D Fourier mode (heatmap in both directions) ------------- #
        torus_static = make_torus(2.0, res=(48, 24), checker=False)
        color_surface_by_field(torus_static, torus_mode, nu=48, nv=24)
        with self.voiceover(text=L3) as vo:
            d = vo.duration
            self.play(FadeTransform(S, torus_static), run_time=d * 0.35)
            S = torus_static
            # arrow pointing at the equivalence-class formulas (the "sines & cosines
            # in two directions" come from these two gluings)
            fg = VGroup(rel_lr, rel_tb)
            tip = fg.get_corner(DR) + RIGHT * 0.15
            arrow = Arrow(tip + RIGHT * 1.7 + DOWN * 1.0, tip, color=ACCENT,
                          buff=0.0, stroke_width=6)
            self.add_fixed_in_frame_mobjects(arrow)
            self.play(GrowArrow(arrow), Indicate(rel_lr, color=ACCENT),
                      Indicate(rel_tb, color=ACCENT), run_time=d * 0.25)
            self.wait(d * 0.4)
        self.play(FadeOut(arrow), run_time=0.4)

        # ---- L4: punchline ----------------------------------------------- #
        punch = MathTex(r"f(x,y)=\sum_{p,q} c_{pq}\,e^{i(px+qy)}",
                        font_size=FS_MATH).to_edge(DOWN)
        with self.voiceover(text=L4) as vo:
            self.add_fixed_in_frame_mobjects(punch)
            self.play(Write(punch), run_time=vo.duration * 0.7)
            self.wait(vo.duration * 0.3)

        self.begin_ambient_camera_rotation(rate=0.06)
        self.wait(2.5)
        self.stop_ambient_camera_rotation()
        self.wait(0.3)
