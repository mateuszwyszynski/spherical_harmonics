"""Title card shown right after Scene 0: 'Spherical Harmonics', with a small,
gently rotating spherical-harmonic shape as decoration."""
from style import *

configure()


class TitleCard(ThreeDScene):
    def construct(self):
        set_3d(self, phi=68, theta=-45)

        # decorative rotating SH shape, up top
        shape = Surface(sh_lobes_surf(3, 2, target=1.0),
                        u_range=[0, TAU], v_range=[0, np.pi], resolution=(48, 24),
                        checkerboard_colors=False, stroke_width=0.0, fill_opacity=1.0)
        color_surface_by_field(shape, lambda u, v: real_Y(3, 2, v, u),
                               nu=48, nv=24, v_range=(0, np.pi))
        shape.shift(UP * 1.4)

        title = Text("Spherical Harmonics", font_size=56, color=TEXT)
        title.move_to(DOWN * 0.5)

        self.begin_ambient_camera_rotation(rate=0.28)
        self.play(FadeIn(shape), run_time=1.0)
        # Register as fixed-in-frame only right before animating it in, otherwise it
        # shows during the FadeIn(shape) beat and then Write() re-draws it (flash).
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1.3)
        self.wait(2.2)
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(shape), FadeOut(title), run_time=1.0)
        self.wait(0.2)
