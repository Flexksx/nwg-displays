import os
import socket


def hyprctl(cmd):
    # /tmp/hypr moved to $XDG_RUNTIME_DIR/hypr in #5788
    xdg_runtime_dir = os.getenv("XDG_RUNTIME_DIR")
    hypr_dir = (
        f"{xdg_runtime_dir}/hypr"
        if xdg_runtime_dir and os.path.isdir(f"{xdg_runtime_dir}/hypr")
        else "/tmp/hypr"
    )

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(f"{hypr_dir}/{os.getenv('HYPRLAND_INSTANCE_SIGNATURE')}/.socket.sock")

    s.send(cmd.encode("utf-8"))
    output = s.recv(20480).decode("utf-8")
    s.close()

    return output
