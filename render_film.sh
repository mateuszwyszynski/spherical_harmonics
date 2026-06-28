#!/usr/bin/env bash
# Render all scenes (with synced voiceover audio) and concatenate the full film.
#
#   ./render_film.sh           # 720p30 (good default for review)
#   ./render_film.sh -ql       # 480p15 (fast draft)
#   ./render_film.sh -qh       # 1080p60 (final)
#
# Voice: by default scenes use the gTTS draft voice. To record your own voice,
# render the individual scenes with VOICE=record (interactive) first, then run this
# script (the cached recordings are reused).
#
# Output: media/film/from_rings_to_spheres.mp4
set -euo pipefail
cd "$(dirname "$0")"

QFLAG="${1:--qm}"
case "$QFLAG" in
  -ql) QDIR="480p15" ;;
  -qm) QDIR="720p30" ;;
  -qh) QDIR="1080p60" ;;
  -qk) QDIR="2160p60" ;;
  *) echo "Unknown quality flag: $QFLAG (use -ql/-qm/-qh/-qk)"; exit 1 ;;
esac

# scene file : scene class, in playback order
SCENES=(
  "s0_intro.py:S0Intro"
  "title_card.py:TitleCard"
  "s1_ring.py:S1FourierRing"
  "s2_loops.py:S2DeformRing"
  "s3_square.py:S3IntoSquare"
  "s4_torus.py:S4Torus"
  "s5_sphere.py:S5Sphere"
  "s6_radial.py:S6Radial"
)

WORK="$(mktemp -d)"
LIST="$WORK/list.txt"
echo "==> Rendering ${#SCENES[@]} scenes at $QFLAG ($QDIR)"
idx=0
for entry in "${SCENES[@]}"; do
  file="${entry%%:*}"; cls="${entry##*:}"
  echo "--- $cls ($file)"
  uv run manim "$QFLAG" --disable_caching "harmonics/$file" "$cls"
  mp4="media/videos/${file%.py}/$QDIR/$cls.mp4"
  [[ -f "$mp4" ]] || { echo "ERROR: expected $mp4 not found"; exit 1; }

  # Normalize each clip to a uniform stream layout (h264 + AAC 48k stereo), adding a
  # silent audio track where the scene has none (e.g. the title card), so the clips
  # concatenate cleanly.
  norm="$WORK/$(printf '%02d' "$idx")_$cls.mp4"
  if ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$mp4" | grep -q .; then
    ffmpeg -y -loglevel error -i "$mp4" \
      -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium -c:a aac -ar 48000 -ac 2 "$norm"
  else
    ffmpeg -y -loglevel error -i "$mp4" -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 \
      -map 0:v:0 -map 1:a:0 -shortest \
      -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium -c:a aac "$norm"
  fi
  echo "file '$norm'" >> "$LIST"
  idx=$((idx + 1))
done

mkdir -p media/film
OUT="media/film/from_rings_to_spheres.mp4"
echo "==> Concatenating into $OUT"
ffmpeg -y -loglevel error -f concat -safe 0 -i "$LIST" -c copy "$OUT"
rm -rf "$WORK"
echo "==> Done: $OUT  ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s)"
