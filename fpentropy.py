from __future__ import division
from math import log, floor
from random import uniform
import operator

TBB_COLOR_DEPTH = 24

# Parameters for torbutton screen resize algorithm
# Basically we'll calculate the amount of entropy of the screen resolution as
# if torbutton resized the browser window with these parameters.
# We'll use Panopticlick data from a 2yrs old dump and assume Tor uses have the
# same resolution distribution. We remove values such as undefined to allow
# torbutton to resize all the data points (resolutions)
# w_roundto, h_roundto, min_aspect_ratio, max_h_offset, toolbar_h
resize_params = ((200, 100, 140, 0, 0, 0),  # ~default
                 (150, 100, 140, 0, 0, 0),  # w_roundto 150
                 (100, 100, 140, 0, 0, 0),  # w_roundto 100
                 (200, 150, 140, 0, 0, 0),  # h_roundto 150
                 (200, 200, 140, 0, 0, 0),  # h_roundto 200
                 (200, 100, 140, 0, 1.1, 800),  # min_asp_ratio 1.1
                 (200, 200, 140, 0, 1.1, 800),  # min_asp_ratio 1.1 & h_roundto 200
                 (200, 200, 140, 10, 1.1, 800),  # previous + some toolbar_h noise
                 (200, 200, 140, 20, 1.1, 800),  # previous + more toolbar_h noise
                 (200, 100, 140, 0, 1.2, 800),  # min_asp_ratio 1.2
                 (200, 200, 140, 0, 1.2, 800),  # min_asp_ratio 1.2 & h_roundto 200
                 (200, 100, 140, 10, 1.2, 800),  # previous + some toolbar_h noise
                 (200, 100, 140, 20, 1.2, 800),  # previous + more toolbar_h noise

                 (200, 100, 140, 0, 1.1, 900),  # min_asp_ratio 1.1
                 (200, 200, 140, 0, 1.1, 900),  # min_asp_ratio 1.1 & h_roundto 200
                 (200, 200, 140, 10, 1.1, 900),  # previous + 10px toolbar_h noise
                 (200, 200, 140, 20, 1.1, 900),  # previous + 20px toolbar_h noise
                 (200, 100, 140, 0, 1.2, 900),  # min_asp_ratio 1.2
                 (200, 200, 140, 0, 1.2, 900),  # min_asp_ratio 1.2 & h_roundto 200
                 (200, 100, 140, 10, 1.2, 900),  # previous + 10px toolbar_h noise
                 (200, 100, 140, 20, 1.2, 900),  # previous + 20px toolbar_h noise

                 (200, 100, 140, 0, 1.1, 1000),  # min_asp_ratio 1.1
                 (200, 200, 140, 0, 1.1, 1000),  # min_asp_ratio 1.1 & h_roundto 200
                 (200, 200, 140, 10, 1.1, 1000),  # previous + 10px toolbar_h noise
                 (200, 200, 140, 20, 1.1, 1000),  # previous + 20px toolbar_h noise

                 (200, 100, 140, 0, 1.2, 1000),  # min_asp_ratio 1.2
                 (200, 200, 140, 0, 1.2, 1000),  # min_asp_ratio 1.2 & h_roundto 200
                 (200, 100, 140, 10, 1.2, 1000),  # previous + 10px toolbar_h noise
                 (200, 100, 140, 20, 1.2, 1000),  # previous + 20px toolbar_h noise

                 (200, 100, 140, 10, 0, 0),  # h_roundto 200 + 10px tbar_h noise
                 (200, 200, 140, 10, 0, 0),  # h_roundto 200 + 10px tbar_h noise
                 (200, 100, 140, 20, 0, 0),  # h_roundto 100 + 20px tbar_h noise
                 (200, 200, 140, 20, 0, 0),  # h_roundto 200 + 20px tbar_h noise
                 )


# Parameters for screen resize operation
# Default values mimick those of torbutton's.

# We assume toolbar etc. height is 140px
# This is what torbutton calculates for Gnome on Ubuntu
# max_h_offset can be used add some noise to toolbar height
# TODO: check if we can find a better value
class ResizeParams:
    def __init__(self, w_roundto=200, h_roundto=100,
                 toolbar_h=140, max_h_offset=0,
                 min_aspect_ratio=0, min_aspect_ratio_force_h=800):
        self.w_roundto = w_roundto  # round window width to multiples of this
        self.h_roundto = h_roundto  # round window height to multiples of this
        self.min_aspect_ratio = min_aspect_ratio  # min w/h ratio, experimental
        self.min_aspect_ratio_force_h = min_aspect_ratio_force_h
        self.max_h_offset = max_h_offset    # noise for toolbar height
        self.toolbar_h = toolbar_h     # toolbar etc. height.


def sort_by_value(d, reverse=True):
    """Sort a dict by value."""
    return sorted(d.iteritems(), key=operator.itemgetter(1), reverse=reverse)


def read_sql_output(filename):
    """Read the sql output from the Panopticlick database."""
    counts = {}
    with open(filename) as f:
        for l in f.readlines():
            try:
                value, count = (s.strip() for s in l.split("|")[1:3])
                counts[value] = int(count)
            except:
                #print "Cannot find value and count:", l
                pass
    return counts


def surprisal(prob, log_base=2):
    """Return surprisal (self-information) of an observation.

    For an observation x the surprise is  log(1/p(x)) = -log(p(x))
    http://en.wikipedia.org/wiki/Self-information

    log_base determines the unit of the returned result
    (2 for bits, 10 for bans, e for nats)

    """
    return -log(prob, log_base)


def get_entropy_from_counts(count_dict):
    """Return entropy of a random variable given values and frequencies."""
    total_surprisal = 0  # to calculate the expected value
    total_observations = sum(count_dict.itervalues())
    for count in count_dict.itervalues():
        total_surprisal += count * surprisal(count / total_observations)
    # compute entropy as the expected value of the surprisal
    entropy = total_surprisal / total_observations
    return entropy


def tor_button_resize(resolution, resize_param):
    """Change screen resolution using the parameters in resize_param.

    This can be used simulate Torbutton's screen manipulation and
    try different resize parameters.
    """
    
    rp = resize_param
    try:
        w, h = map(int, resolution.split("x")[:2])
        orig_area = w * h
        # torbutton code for resizing window width
        if w > 1000:
            new_w = 1000
        else:
            new_w = int(floor(w / rp.w_roundto) * rp.w_roundto)
        # try to force a minimal aspect ratio on vertical screens #11439
        if rp.min_aspect_ratio and h > rp.min_aspect_ratio_force_h:
            max_h = new_w / rp.min_aspect_ratio
            if h > max_h:
                h = max_h

        if rp.max_h_offset:  # if we want to add some noise to toolbar height
            toolbar_h = rp.toolbar_h + uniform(-1, 1) * rp.max_h_offset
        else:
            toolbar_h = rp.toolbar_h
        # torbutton code for resizing window height
        new_h = int(floor((h - toolbar_h) / rp.h_roundto) * rp.h_roundto)
        utilization = (new_w * new_h / orig_area) if orig_area else 1
        #utilization = 0 if new_h < 700 else 1  # a naive metric that track who gets height< 600px
        return "%sx%sx%s" % (new_w, new_h, TBB_COLOR_DEPTH), utilization
    except ValueError:
        # print "Unexpected value", resolution
        return None, None


def filter_resolution_data(screen_counts, min_width=640, min_height=480):
    """Filter resolutions dict using the minimal values."""
    filtered = {}
    for resolution, count in screen_counts.iteritems():
        try:
            w, h = map(int, resolution.split("x")[:2])
            if w >= min_width and h >= min_height:
                filtered[resolution] = count
        except:  # also filter other junk resolution data
            pass  # (undefined, permission denied etc.)
    return filtered


def torb_resize_all(screen_counts, resize_param):
    """Resize given dictionary of screen resolutions."""
    resized = {}
    no_of_points = 0
    total_utilization = 0
    for resolution, count in screen_counts.iteritems():
        torb_resolution, utilization = tor_button_resize(resolution,
                                                         resize_param)
        if torb_resolution is not None:
            no_of_points += 1
            total_utilization += utilization
            if torb_resolution in resized:  # resized values will collide
                resized[torb_resolution] += count
            else:
                resized[torb_resolution] = count
    return resized, total_utilization / no_of_points


def measure_entropy_for_resize_params(counts, resize_param):
    """Return entropy for transformed screen resolutions."""
    resized, util = torb_resize_all(counts, ResizeParams(*resize_param))
    entropy = get_entropy_from_counts(resized)
    return {"resized": resized, "entropy": entropy,
            "utilization": util, "resize_params": resize_param}


def print_entropy_for_resize_exp(result, prefix=""):
    print "%s Entropy: %0.2f bits, "\
            "Util: %%%0.2f Resize params: %s Bins: %s - %s" %\
        (prefix, result["entropy"],
         result["utilization"] * 100, result["resize_params"],
         len(result["resized"]), sort_by_value(result["resized"]))


def print_entropy_for_resize_exps(results, prefix=""):
    for result in results:
        print_entropy_for_resize_exp(result)


def print_entropy_for_counts(counts, prefix=""):
    # TODO merge with other prin function
    entropy = get_entropy_from_counts(counts)
    print "%s Entropy: %0.2f bits, Bins: %s, "\
            "on avg. one in %0.2f share the same value %s"\
            % (prefix, entropy, len(counts), 2 ** entropy, sort_by_value(counts)[:100])


def metric1(x):
    """Metric 1: entropy * (1 - utilization)."""
    return x["entropy"] * (1 - x["utilization"])


def run_resolution_entropy_exp(data_file):
    exp_results = []
    counts = read_sql_output(data_file)
    print "Total data points: %s" % sum(counts.itervalues())
    print_entropy_for_counts(counts, "Original data")

    min_640_480 = filter_resolution_data(counts, min_width=640, min_height=480)
    print "Total data points above 640x480: %s" % sum(min_640_480.itervalues())
    print_entropy_for_counts(min_640_480, "Screen above 640x480")

    for resize_param in resize_params:
        r = measure_entropy_for_resize_params(min_640_480, resize_param)
        exp_results.append(r)

    print "\n***Results for different resize parameters***"
    print_entropy_for_resize_exps(exp_results)

    sorted_by_entropy = sorted(exp_results, key=lambda x: x["entropy"])
    print "\n***Results for different resize parameters - Sorted by entropy***"
    print_entropy_for_resize_exps(sorted_by_entropy)

    sorted_by_util = sorted(exp_results, key=lambda x: 1 - x["utilization"])
    print "\n***Results for different resize parameters - Sorted by utilization***"
    print_entropy_for_resize_exps(sorted_by_util)

    sorted_by_metric1 = sorted(exp_results, key=metric1)
    print "\n***Results for different resize parameters - Sorted by metric 1***"
    print_entropy_for_resize_exps(sorted_by_metric1)


if __name__ == '__main__':
    filename = "panopticlick-screen-resolution.txt"  # original DB dump
    run_resolution_entropy_exp(filename)
