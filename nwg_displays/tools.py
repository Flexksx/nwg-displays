# !/usr/bin/env python3
import datetime
import json
import os
import socket
import subprocess
import sys

import gi
from nwg_displays.logger import logger
from nwg_displays.hyprland.hyprctl import hyprctl
from nwg_displays.monitor.hyprland.hyprland_monitor_service import (
    HyprlandMonitorService,
)
from nwg_displays.monitor.monitor import Monitor
from nwg_displays.monitor.monitor_service import MonitorService
from nwg_displays.monitor.sway.sway_monitor_service import SwayMonitorService

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk

if os.getenv("SWAYSOCK"):
    from i3ipc import Connection


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_config_home():
    xdg_config_home = os.getenv("XDG_CONFIG_HOME")
    config_home = (
        xdg_config_home
        if xdg_config_home
        else os.path.join(os.getenv("HOME"), ".config")
    )

    return config_home


def is_command(cmd):
    cmd = cmd.split()[0]
    cmd = "command -v {}".format(cmd)
    try:
        is_cmd = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        if is_cmd:
            return True

    except subprocess.CalledProcessError:
        return False


def list_outputs() -> dict[str, Monitor]:
    """
    Return a dictionary keyed by monitor name whose values are **Monitor**
    objects (either SwayMonitor or HyprlandMonitor).  All downstream code
    continues to work because every monitor implements the same interface.
    """
    service: MonitorService = None
    if os.getenv("SWAYSOCK"):
        service = SwayMonitorService()
        logger.info("Running on sway")
    elif os.getenv("HYPRLAND_INSTANCE_SIGNATURE"):
        service = HyprlandMonitorService()
        logger.info("Running on Hyprland")
    else:
        logger.error(
            "This program only supports sway and Hyprland, "
            "and we seem to be elsewhere, terminating."
        )
        sys.exit(1)

    monitors: list[Monitor] = service.list()

    gdk_display = Gdk.Display.get_default()
    gdk_monitors = [
        gdk_display.get_monitor(i) for i in range(gdk_display.get_n_monitors())
    ]
    logger.debug("Gdk monitors: %s", gdk_monitors)

    for i, monitor in enumerate(monitors):
        try:
            # The concrete Monitor classes expose .config.gdk_monitor for convenience;
            # we attach the Gdk.Monitor there so UI code can query DPI, geometry…
            monitor.set_gdk_monitor(gdk_monitors[i])
        except IndexError:
            logger.error(
                f"Couldn't assign a Gdk.Monitor object to {monitor.get_name()}"
            )

    logger.debug("Got monitors: %s", monitors)
    return {mon.get_name(): mon for mon in monitors}


def list_hyprland_monitors():
    monitors_all = json.loads(hyprctl("j/monitors all"))
    monitors = json.loads(hyprctl("j/monitors"))
    active = []
    for item in monitors:
        active.append(item["name"])
    outputs_dict = {}
    for mon in monitors_all:
        name = mon["name"]
        outputs_dict[name] = {"active": True} if name in active else {"active": False}

    eprint("Running on Hyprland")

    # 1. Mirroring is impossible to check in any way. We need to parse back the monitors.conf file, and it sucks.
    mirrors = {}
    hypr_config_dir = os.path.join(get_config_home(), "hypr")
    monitors_file = os.path.join(hypr_config_dir, "monitors.conf")
    if os.path.isfile(monitors_file):
        lines = load_text_file(monitors_file).splitlines()
        for line in lines:
            if line and not line.startswith("#"):  # skip comments
                if "mirror" in line:
                    settings = line.split("=")[1].split(",")
                    mirrors[settings[0].strip()] = settings[-1].strip()

        # 2. This won't work w/ Hyprland <= 0.36.0
    output = hyprctl("j/monitors all")
    monitors = json.loads(output)
    transforms = {
        0: "normal",
        1: "90",
        2: "180",
        3: "270",
        4: "flipped",
        5: "flipped-90",
        6: "flipped-180",
        7: "flipped-270",
    }
    for m in monitors:
        outputs_dict[m["name"]]["mirror"] = mirrors[name] if name in mirrors else ""

        outputs_dict[m["name"]]["scale_filter"] = None
        outputs_dict[m["name"]]["modes"] = []
        outputs_dict[m["name"]]["focused"] = m["focused"]
        outputs_dict[m["name"]]["adaptive_sync_status"] = (
            "enabled" if m["vrr"] else "disabled"
        )

        outputs_dict[m["name"]]["description"] = f'{m["description"]}'
        outputs_dict[m["name"]]["x"] = int(m["x"])
        outputs_dict[m["name"]]["y"] = int(m["y"])

        outputs_dict[m["name"]]["refresh"] = round(m["refreshRate"], 2)

        outputs_dict[m["name"]]["logical-width"] = m["width"] / m["scale"]
        outputs_dict[m["name"]]["logical-height"] = m["height"] / m["scale"]

        outputs_dict[m["name"]]["physical-width"] = m["width"]
        outputs_dict[m["name"]]["physical-height"] = m["height"]

        outputs_dict[m["name"]]["transform"] = transforms[m["transform"]]
        outputs_dict[m["name"]]["scale"] = m["scale"]
        outputs_dict[m["name"]]["focused"] = m["focused"]
        outputs_dict[m["name"]]["dpms"] = m["dpmsStatus"]

        outputs_dict[name]["modes"] = []

        for item in m["availableModes"]:
            line = item[:-2]  # split "Hz"
            w_h, r = line.split("@")
            w, h = w_h.split("x")
            try:
                mode = {
                    "width": int(w),
                    "height": int(h),
                    "refresh": float(r) * 1000,
                }
            except ValueError as e:
                eprint(e)
            outputs_dict[m["name"]]["modes"].append(mode)

        outputs_dict[m["name"]]["ten_bit"] = (
            True if m["currentFormat"] in ["XRGB2101010", "XBGR2101010"] else False
        )

        # to identify Gdk.Monitor
        outputs_dict[m["name"]]["model"] = m["model"]

        outputs_dict[m["name"]]["monitor"] = None
    return outputs_dict


def list_outputs_activity():
    result = {}
    if os.getenv("SWAYSOCK"):
        i3 = Connection()
        outputs = i3.get_outputs()
        for o in outputs:
            result[o.name] = o.active

    elif os.getenv("HYPRLAND_INSTANCE_SIGNATURE"):
        monitors_all = json.loads(hyprctl("j/monitors all"))
        monitors = json.loads(hyprctl("j/monitors"))
        active = []
        for item in monitors:
            active.append(item["name"])

        for mon in monitors_all:
            name = mon["name"]
            result[name] = True if name in active else False

    return result


def max_window_height():
    if os.getenv("SWAYSOCK"):
        i3 = Connection()
        outputs = i3.get_outputs()
        for o in outputs:
            if o.focused:
                if o.rect.width > o.rect.height:
                    return o.rect.height * 0.9
                else:
                    return o.rect.height / 2 * 0.9
    return None


def scale_if_floating():
    pid = os.getpid()
    if os.getenv("SWAYSOCK"):
        i3 = Connection()
        node = i3.get_tree().find_by_pid(pid)[0]
        if node.type == "floating_con":
            h = int(max_window_height())
            if h:
                i3.command("resize set height {}".format(h))


def min_val(a, b):
    if b < a:
        return b
    return a


def max_val(a, b):
    if b > a:
        return b
    return a


def round_down_to_multiple(i, m):
    return i / m * m


def round_to_nearest_multiple(i, m):
    if i % m > m / 2:
        return (i / m + 1) * m
    return i / m * m


def orientation_changed(transform, transform_old):
    return (is_rotated(transform) and not is_rotated(transform_old)) or (
        is_rotated(transform_old) and not is_rotated(transform)
    )


def is_rotated(transform):
    return "90" in transform or "270" in transform


def inactive_output_description(name):
    if os.getenv("SWAYSOCK"):
        i3 = Connection()
        for item in i3.get_outputs():
            if item.name == name:
                return "{} {} {}".format(
                    item.ipc_data["make"],
                    item.ipc_data["model"],
                    item.ipc_data["serial"],
                )
    return None


def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print("Error loading json: {}".format(e))
        return None


def save_json(src_dict, path):
    with open(path, "w") as f:
        json.dump(src_dict, f, indent=2)


def save_list_to_text_file(data, file_path):
    text_file = open(file_path, "w")
    for line in data:
        text_file.write(line + "\n")
    text_file.close()


def create_empty_file(file_path):
    if not os.path.isfile(file_path):
        with open(file_path, "w") as file:
            pass


def load_text_file(path):
    try:
        with open(path, "r") as file:
            data = file.read()
            return data
    except Exception as e:
        print(e)
        return None


def load_workspaces(path, use_desc=False):
    result = {}
    try:
        with open(path, "r") as file:
            data = file.read().splitlines()
            for i in range(len(data)):
                if data[i] and not data[i].startswith("#"):  # skip comments
                    info = data[i].split("workspace ")[1].split()
                    num = int(info[0])
                    if not use_desc:
                        result[num] = info[2]
                    else:
                        result[num] = data[i].split("output ")[1][1:-1]
            return result
    except Exception as e:
        print(e)
        return result


# We will read all the meaningful lines if -n argument not given or >= number of lines.
def load_workspaces_hypr(path, num_ws=0):
    ws_binds = {}
    meaningful_lines_read = 0
    try:
        with open(path, "r") as file:
            data = file.read().splitlines()
            r = len(data)
            for i in range(r):
                line = data[i]
                if line and not line.startswith("#"):  # skip comments
                    meaningful_lines_read += 1
                    # Binding workspaces to a monitor, e.g.:
                    # 'workspace=1,monitor:desc:AOC 2475WR F17H4QA000449' or
                    # 'workspace=1,monitor:HDMI-A-1'
                    ws_num = None
                    parts = line.split(",")
                    try:
                        ws_num = int(parts[0].split("=")[1])
                    except:
                        pass
                    mon = parts[1].split(":")[-1]
                    if ws_num:
                        ws_binds[ws_num] = mon

                    if num_ws > 0:
                        if meaningful_lines_read == num_ws:
                            break

            return ws_binds

    except Exception as e:
        eprint("Error parsing workspaces.conf file: {}".format(e))
        return {}


def save_workspaces(data_dict, path, use_desc=False):
    text_file = open(path, "w")
    now = datetime.datetime.now()
    line = "# Generated by nwg-displays on {} at {}. Do not edit manually.\n".format(
        datetime.datetime.strftime(now, "%Y-%m-%d"),
        datetime.datetime.strftime(now, "%H:%M:%S"),
    )
    text_file.write(line + "\n")
    for key in data_dict:
        if not use_desc:
            line = "workspace {} output {}".format(key, data_dict[key])
        else:
            line = "workspace {} output '{}'".format(key, data_dict[key])
        text_file.write(line + "\n")
    text_file.close()


def notify(summary, body, timeout=3000):
    cmd = "notify-send '{}' '{}' -i /usr/share/pixmaps/nwg-displays.svg -t {}".format(
        summary, body, timeout
    )
    subprocess.call(cmd, shell=True)


def get_shell_data_dir():
    data_dir = ""
    home = os.getenv("HOME")
    xdg_data_home = os.getenv("XDG_DATA_HOME")

    if xdg_data_home:
        data_dir = os.path.join(xdg_data_home, "nwg-shell/")
    else:
        if home:
            data_dir = os.path.join(home, ".local/share/nwg-shell/")

    return data_dir


def load_shell_data():
    shell_data_file = os.path.join(get_shell_data_dir(), "data")
    shell_data = load_json(shell_data_file) if os.path.isfile(shell_data_file) else {}

    defaults = {"interface-locale": ""}

    for key in defaults:
        if key not in shell_data:
            shell_data[key] = defaults[key]

    return shell_data
