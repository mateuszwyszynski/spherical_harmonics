"""SCENE 1 - 1D Fourier & the Ring (voiceover-timed).

We meet the Fourier series as a sum of sines and cosines approximating a function
on a 1D line, then bend that line into a ring to reveal why periodicity is natural.
Each beat is wrapped in a voiceover block so the animation runs for as long as the
narration line takes (gTTS draft, or your own recording with VOICE=record).
"""
from style import *
from manim_voiceover import VoiceoverScene

configure()

# narration split per beat (verbatim from scenario.tex)
L1 = ("We usually first encounter the Fourier series as a sum of sines and cosines "
      "used to approximate a function on a 1D line.")
L2 = ("But why sines and cosines? According to Wikipedia, Joseph Fourier originally "
      "developed this theory while trying to understand how heat distributes itself "
      "around a metal ring.")
L3 = ("This shows why the choice of sines and cosines is actually quite natural. We "
      "need the value at the beginning of our interval to perfectly match the value "
      "at the end.")
L4 = ("This allows us to wrap the interval into a circle - the ring that Fourier was "
      "interested in.")


class S1FourierRing(VoiceoverScene, Scene):
    def construct(self):
        setup_voice(self)

        axes = make_axes()
        full_curve = wave(axes, target_f, CURVE)

        # ---- L1: axes + the target curve --------------------------------- #
        with self.voiceover(text=L1) as vo:
            self.play(Create(axes), run_time=vo.duration * 0.4)
            self.play(Create(full_curve), run_time=vo.duration * 0.6)

        # ---- L2: decompose into components, build the partial sum --------- #
        comp_colors = [COMP, COMP_2, COMP]
        comp_labels = [
            MathTex(r"0.55\,\sin x", color=COMP, font_size=FS_MATH),
            MathTex(r"0.30\,\cos 2x", color=COMP_2, font_size=FS_MATH),
            MathTex(r"0.18\,\sin 3x", color=COMP, font_size=FS_MATH),
        ]
        label_group = VGroup(*comp_labels).arrange(
            DOWN, aligned_edge=LEFT, buff=0.28).to_corner(UL, buff=0.5)

        with self.voiceover(text=L2) as vo:
            d = vo.duration
            self.play(full_curve.animate.set_stroke(opacity=0.25), run_time=d * 0.08)
            per = d * 0.84 / 3
            running_sum = None
            for k in range(1, 4):
                kind, n, a = COEFFS[k - 1]
                comp_wave = wave(axes, component(kind, n, a),
                                 color=comp_colors[k - 1], width=SW_COMP)
                self.play(Create(comp_wave), Write(comp_labels[k - 1]),
                          run_time=per * 0.45)
                new_sum = wave(axes, partial_sum(k), color=COMP, width=SW_PRIMARY)
                new_sum.set_stroke(opacity=0.9)
                if running_sum is None:
                    self.play(ReplacementTransform(comp_wave, new_sum),
                              run_time=per * 0.55)
                else:
                    self.play(ReplacementTransform(running_sum, new_sum),
                              FadeOut(comp_wave), run_time=per * 0.55)
                running_sum = new_sum
            self.play(full_curve.animate.set_stroke(opacity=1.0),
                      FadeOut(running_sum), FadeOut(label_group), run_time=d * 0.08)

        # ---- BEAT 3 set-up: hand off to a tracker-driven rolling curve ---- #
        t = ValueTracker(0.0)
        wave_amp = ValueTracker(1.0)
        rolling_curve = always_redraw(lambda: ParametricFunction(
            lambda x: ring_roll_point(x, t.get_value(), amp=wave_amp.get_value()),
            t_range=[0, TAU, 0.005], color=CURVE, stroke_width=SW_PRIMARY))
        base_ring = always_redraw(lambda: ParametricFunction(
            lambda x: ring_base_point(x, t.get_value()),
            t_range=[0, TAU, 0.005], color=AXIS, stroke_width=SW_AXIS))
        start_dot = always_redraw(lambda: Dot(
            ring_roll_point(0.0, t.get_value(), amp=wave_amp.get_value()),
            radius=DOT_R, color=ACCENT))
        end_dot = always_redraw(lambda: Dot(
            ring_roll_point(TAU, t.get_value(), amp=wave_amp.get_value()),
            radius=DOT_R, color=ACCENT))

        # ---- L3: match the endpoints (fade axes, reveal endpoint dots) ---- #
        with self.voiceover(text=L3) as vo:
            self.add(base_ring, rolling_curve, start_dot, end_dot)
            self.remove(full_curve)
            self.play(FadeOut(axes), run_time=vo.duration * 0.45)
            self.play(Indicate(start_dot, color=ACCENT, scale_factor=1.6),
                      Indicate(end_dot, color=ACCENT, scale_factor=1.6),
                      run_time=vo.duration * 0.55)

        # ---- L4: roll the line up into the ring + punchline --------------- #
        punch = MathTex(r"f(0)=f(2\pi)\;\Rightarrow\;\text{periodic}",
                        font_size=FS_MATH, color=TEXT).to_edge(DOWN, buff=0.7)
        with self.voiceover(text=L4) as vo:
            self.play(t.animate.set_value(1.0), run_time=vo.duration * 0.7,
                      rate_func=rate_functions.ease_in_out_sine)
            self.play(Flash(start_dot.get_center(), color=ACCENT, flash_radius=0.5),
                      run_time=vo.duration * 0.12)
            self.play(Write(punch), run_time=vo.duration * 0.18)
        self.wait(0.6)

        # End on the wavy ring (the function wrapped). Scene 2 picks this ring up
        # and introduces the heatmap there.
        for m in (base_ring, start_dot, end_dot):
            m.clear_updaters()
        rolling_curve.clear_updaters()
        self.play(FadeOut(base_ring), FadeOut(start_dot), FadeOut(end_dot),
                  FadeOut(punch), run_time=0.8)
        self.wait(0.5)
