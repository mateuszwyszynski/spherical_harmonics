"""Scene 5 - Sphere & Spherical Harmonics (voiceover-timed).

Same square, new gluing -> sphere; then the spherical-harmonics story mirroring the
1-D Fourier case: three basis harmonics, add them up, read as heatmap or deformation,
and deform into any shape (a 3-D heart).
"""
from style import *
from manim_voiceover import VoiceoverScene

configure()

RES = (48, 24)
SMALL_R = 1.2
SIDE_X = 3.7
BIG_R = 1.6
HEART_RED = "#E8455F"
SUM_TERMS = [(2, 0, 1.0), (3, 2, 1.0), (4, 4, 1.0)]
BASIS = [(2, 0), (3, 2), (4, 4)]

LA = "But there is another option. We can glue the vertical edges together,"
LB = ("but then take the entire top edge, pinch it into a single point, and do the "
      "same thing with the bottom edge.")
LC = "This topological transformation creates a sphere."
LD = ("Choosing this different transformation introduces completely different "
      "boundary conditions - specifically at those pinched poles - which means we "
      "need a new set of basis functions. This choice leads us to spherical harmonics.")
LE = ("While we could dive into the heavy differential equations used to derive them, "
      "the core idea is exactly the same as the 1D Fourier case. We are simply finding "
      "a set of wavy functions that automatically align to the topology of our base shape.")
LF = "By scaling and summing these spherical basis functions,"
LG = "we can deform our smooth base sphere into any lumpy, complex 3D shape we want."


def _checker_sphere(R):
    return make_sphere(2.0, res=RES).scale(R / SPHERE_R)


def _field_sphere(field, R):
    s = make_sphere(2.0, res=RES, checker=False).scale(R / SPHERE_R)
    color_surface_by_field(s, field, nu=RES[0], nv=RES[1], v_range=(0, np.pi))
    return s


def _ylm_field(l, m):
    return lambda u, v: real_Y(l, m, v, u)


def _sedge(t, fix_u):
    """A left/right gluing edge traced on sphere_surf(t), so it follows the morph."""
    return ParametricFunction(lambda v: sphere_surf(t)(fix_u, v),
                              t_range=[0, np.pi, 0.02], color=GLUE,
                              stroke_width=SW_GLUE)


def _rim(t, fix_v):
    """A top/bottom edge circle traced on sphere_surf(t): at the cylinder it is the
    rim circle; as the sphere pinches it shrinks down onto the pole point."""
    return ParametricFunction(lambda u: sphere_surf(t)(u, fix_v),
                              t_range=[0, TAU, 0.02], color=POLE,
                              stroke_width=SW_GLUE)


class S5Sphere(VoiceoverScene, ThreeDScene):
    def construct(self):
        setup_voice(self)
        set_3d(self)
        caption = Text("same square — new gluing", font_size=FS_NOTE).to_corner(UL)
        S = make_sphere(0.0)
        left_edge = ParametricFunction(lambda v: sphere_surf(0.0)(1e-3, v),
                                       t_range=[0, np.pi, 0.02], color=GLUE,
                                       stroke_width=SW_GLUE)
        right_edge = ParametricFunction(lambda v: sphere_surf(0.0)(TAU - 1e-3, v),
                                        t_range=[0, np.pi, 0.02], color=GLUE,
                                        stroke_width=SW_GLUE)
        glue_rel = MathTex(r"(0,y)\sim(2\pi,y)", font_size=FS_REL).to_corner(UR)

        # ---- LA: the square + left/right edges --------------------------- #
        with self.voiceover(text=LA) as vo:
            d = vo.duration
            self.add_fixed_in_frame_mobjects(caption)
            self.play(FadeIn(S), Write(caption), run_time=d * 0.4)
            self.add_fixed_in_frame_mobjects(glue_rel)
            self.play(Create(left_edge), Create(right_edge), Write(glue_rel),
                      run_time=d * 0.5)

        # ---- LB: glue -> cylinder, pinch -> sphere ----------------------- #
        north = Dot3D(point=1.02 * SPHERE_R * OUT, radius=POLE_R, color=POLE)
        south = Dot3D(point=-1.02 * SPHERE_R * OUT, radius=POLE_R, color=POLE)
        n_lbl = MathTex(r"(x,0)\sim N", font_size=FS_REL).to_corner(UR)
        s_lbl = MathTex(r"(x,\pi)\sim S", font_size=FS_REL).to_corner(DR)
        top_rim = _rim(1.0, 1e-3)
        bot_rim = _rim(1.0, np.pi - 1e-3)
        with self.voiceover(text=LB) as vo:
            d = vo.duration
            # Drive the morph with the TRUE parametrization each frame (become), not a
            # keyframe Transform -- the flat->cylinder roll is a non-linear paper-roll,
            # so a straight-line lerp would crumple it lopsidedly. The gluing edges
            # ride the same roll and meet at the seam, then drop.
            self.play(
                UpdateFromAlphaFunc(S, lambda m, a: m.become(make_sphere(a))),
                UpdateFromAlphaFunc(left_edge, lambda m, a: m.become(_sedge(a, 1e-3))),
                UpdateFromAlphaFunc(right_edge,
                                    lambda m, a: m.become(_sedge(a, TAU - 1e-3))),
                run_time=d * 0.38, rate_func=rate_functions.ease_in_out_sine)
            self.play(FadeOut(left_edge), FadeOut(right_edge), FadeOut(glue_rel),
                      run_time=d * 0.05)
            # FIRST highlight the top & bottom edge CIRCLES (what will pinch to poles)
            self.play(Create(top_rim), Create(bot_rim), run_time=d * 0.12)
            # THEN pinch: the colored circles shrink onto the poles WITH the surface
            self.add_fixed_in_frame_mobjects(n_lbl, s_lbl)
            self.play(
                UpdateFromAlphaFunc(S, lambda m, a: m.become(make_sphere(1.0 + a))),
                UpdateFromAlphaFunc(top_rim, lambda m, a: m.become(_rim(1.0 + a, 1e-3))),
                UpdateFromAlphaFunc(bot_rim,
                                    lambda m, a: m.become(_rim(1.0 + a, np.pi - 1e-3))),
                Write(n_lbl), Write(s_lbl),
                run_time=d * 0.37, rate_func=rate_functions.ease_in_out_sine)
            # the circles are now points on the poles; settle into clean pole dots
            self.play(FadeIn(north), FadeIn(south),
                      FadeOut(top_rim), FadeOut(bot_rim), run_time=d * 0.08)

        # ---- LC: it is a sphere (hold) ----------------------------------- #
        with self.voiceover(text=LC) as vo:
            self.wait(vo.duration)

        # ---- LD: new boundary conditions -> copy into three components --- #
        center0 = _checker_sphere(SMALL_R)
        left0 = _checker_sphere(SMALL_R).move_to(LEFT * SIDE_X)
        right0 = _checker_sphere(SMALL_R).move_to(RIGHT * SIDE_X)
        with self.voiceover(text=LD) as vo:
            d = vo.duration
            self.play(FadeOut(north), FadeOut(south), FadeOut(n_lbl), FadeOut(s_lbl),
                      FadeOut(caption), run_time=d * 0.2)
            self.move_camera(phi=72 * DEGREES, theta=-90 * DEGREES,
                             added_anims=[Transform(S, center0),
                                          TransformFromCopy(S, left0),
                                          TransformFromCopy(S, right0)],
                             run_time=d * 0.45)
            self.wait(d * 0.35)

        # ---- LE: the three basis harmonics (like sin & cos) -------------- #
        left_c = _field_sphere(_ylm_field(*BASIS[0]), SMALL_R).move_to(LEFT * SIDE_X)
        center_c = _field_sphere(_ylm_field(*BASIS[1]), SMALL_R)
        right_c = _field_sphere(_ylm_field(*BASIS[2]), SMALL_R).move_to(RIGHT * SIDE_X)
        labels = VGroup()
        for (l, m), x in zip(BASIS, (-SIDE_X, 0, SIDE_X)):
            labels.add(MathTex(rf"Y_{{{l}}}^{{{m}}}", font_size=FS_MATH)
                       .move_to([x, 0, -SMALL_R - 0.5]))
        with self.voiceover(text=LE) as vo:
            d = vo.duration
            self.play(Transform(left0, left_c), Transform(S, center_c),
                      Transform(right0, right_c), run_time=d * 0.35)
            self.add_fixed_orientation_mobjects(*labels)
            self.play(*[FadeIn(lab) for lab in labels], run_time=d * 0.15)
            self.wait(d * 0.5)

        # ---- LF: add them up -> summed field ----------------------------- #
        plus_l = MathTex("+", font_size=FS_TITLE).move_to([-SIDE_X / 2, 0, 0])
        plus_r = MathTex("+", font_size=FS_TITLE).move_to([SIDE_X / 2, 0, 0])
        summed = _field_sphere(sh_field(SUM_TERMS), BIG_R)
        with self.voiceover(text=LF) as vo:
            d = vo.duration
            self.add_fixed_orientation_mobjects(plus_l, plus_r)
            self.play(Write(plus_l), Write(plus_r), run_time=d * 0.3)
            self.play(left0.animate.move_to(ORIGIN).set_opacity(0.0),
                      right0.animate.move_to(ORIGIN).set_opacity(0.0),
                      Transform(S, summed), FadeOut(plus_l), FadeOut(plus_r),
                      *[FadeOut(lab) for lab in labels],
                      run_time=d * 0.7, rate_func=smooth)
            self.remove(left0, right0)

        # ---- LG: deform into any shape (heatmap -> deformation -> heart) -- #
        bulge = Surface(sh_radius_surf(SUM_TERMS, R=BIG_R, amp=0.42),
                        u_range=[0, TAU], v_range=[0, np.pi], resolution=RES,
                        checkerboard_colors=False, stroke_width=SW_SURF,
                        fill_opacity=1.0)
        color_surface_by_field(bulge, sh_field(SUM_TERMS), nu=RES[0], nv=RES[1],
                               v_range=(0, np.pi))
        heart = Surface(heart_surface(R=BIG_R), u_range=[0, TAU], v_range=[0, np.pi],
                        resolution=RES, checkerboard_colors=False,
                        stroke_width=SW_SURF, fill_opacity=1.0)
        heart.set_fill(ManimColor(HEART_RED), opacity=1.0)
        heart.set_stroke(ManimColor(HEART_RED), width=0.3, opacity=0.4)
        with self.voiceover(text=LG) as vo:
            d = vo.duration
            self.move_camera(phi=66 * DEGREES, theta=-58 * DEGREES,
                             added_anims=[Transform(S, bulge)], run_time=d * 0.4)
            sphere_again = _checker_sphere(BIG_R)
            self.play(Transform(S, sphere_again), run_time=d * 0.2, rate_func=smooth)
            self.move_camera(phi=32 * DEGREES, theta=-90 * DEGREES,
                             added_anims=[Transform(S, heart)],
                             run_time=d * 0.4, rate_func=smooth)
        self.wait(1.5)
