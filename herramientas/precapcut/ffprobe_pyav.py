#!/usr/bin/env python3
"""ffprobe mínimo con PyAV, para capcut-cli cuando no hay un ffprobe que lea los MP4 de la Sony.

capcut-cli llama `ffprobe -v quiet -print_format json -show_streams -show_format <vídeo>` para saber
cuánto dura cada vídeo. Sin eso, el material de CapCut acaba donde acaba el corte y no se puede alargar.
Solo responde a eso y a `-version`; lo demás sale con error.
"""
import json
import sys


def fps(rate):
    return f"{rate.numerator}/{rate.denominator}" if rate else "0/0"


def sondear(ruta):
    import av
    with av.open(ruta) as c:
        streams = []
        for s in c.streams:
            if s.type not in ("video", "audio"):
                continue
            x = {"index": s.index, "codec_type": s.type, "codec_name": s.codec_context.name}
            if s.duration and s.time_base:
                x["duration"] = str(float(s.duration * s.time_base))
            if s.type == "video":
                x.update(width=s.codec_context.width, height=s.codec_context.height,
                         avg_frame_rate=fps(s.average_rate), r_frame_rate=fps(s.base_rate or s.average_rate))
                rot = s.metadata.get("rotate")
                if rot is None:
                    try:  # FFmpeg 5+: el giro va en el displaymatrix, PyAV lo da en el primer fotograma
                        rot = next(c.decode(s)).rotation or 0
                    except Exception:
                        rot = 0
                x["side_data_list"] = [{"side_data_type": "Display Matrix", "rotation": int(rot)}]
            else:
                x["channels"] = s.codec_context.channels
            streams.append(x)
        fmt = {"filename": ruta, "duration": str(c.duration / 1e6) if c.duration else None}
    return {"streams": streams, "format": fmt}


def main(args):
    if "-version" in args:
        print("ffprobe version pyav-shim (precapcut)")
        return 0
    if "-show_format" not in args or not args or args[-1].startswith("-"):
        return 1
    try:
        print(json.dumps(sondear(args[-1])))
    except Exception as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
