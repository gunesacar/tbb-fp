from __future__ import division
from math import log, floor
import matplotlib.pyplot as plt
import operator
from sys import maxint
TBB_COLOR_DEPTH = 24


class ResizeParams:
    def __init__(self, w_roundto=200, h_roundto=100,
                 max_w=1000, max_h=0):
        self.w_roundto = w_roundto  # round window width to multiples of this
        self.h_roundto = h_roundto  # round window height to multiples of this
        self.max_w = max_w  # max width for the inner screen
        self.max_h = max_h  # max height for the inner screen

# Parameters for torbutton screen resize algorithm
# w_roundto, h_roundto, max_w, max_h
# We calculate the new distribution as if
# torbutton resize the browser window with these parameters.

resize_params = ((200, 100, 1000, 0),  # ~default
                 (200, 100, 1200, 0),  # ~default
                 (200, 100, 1400, 0),  # ~default
                 (200, 100, 1600, 0),  # ~default
                 (200, 100, 1800, 0),  # ~default
                 (200, 100, 1000, 1000),  # ~default
                 (200, 200, 1000, 1000),  # ~default
                 (200, 100, 1200, 1000),  # ~default
                 (200, 200, 1200, 1000),  # ~default
                 (200, 100, 1400, 1000),  # ~default
                 (200, 100, 1600, 1000),  # ~default
                 (200, 100, 1800, 1000),  # ~default
                 (200, 100, 1000, 800),  # max h = 900px
                 (200, 100, 1000, 900),  # max h = 900px
                 (200, 100, 1000, 1000),  # max h = 1000px
                 (200, 100, 1000, 1100),  # max h = 1100px
                 (200, 100, 1000, 1200),  # max h = 1200px
                 (200, 100, 1000, 1300),  # max h = 1300px
                 (200, 100, 1000, 1400),  # max h = 1300px
                 (200, 100, 1000, 1500),  # max h = 1300px
                 (200, 100, 1000, 1600),  # max h = 1300px
                 (200, 100, 1000, 1700),  # max h = 1300px
                 )


def sort_by_value(d, reverse=True):
    """Sort a dict by value."""
    return sorted(d.iteritems(), key=operator.itemgetter(1), reverse=reverse)


def read_sql_output(filename):
    """Read the sql output from the Panopticlick database."""
    counts = {}
    for l in open(filename).readlines():
        try:
            #value, count = (s.strip() for s in l.split("|")[1:3])
            value, count = l.rsplit(None, 1)
            counts[value] = int(count)
        except:
            #print "Cannot find value and count:", l
            pass
    return counts


def surprisal(prob, log_base=2):
    """Return surprisal (self-information) of an observation.

    For an observation x the surprise is  log(1/p(x)) = -log(p(x))
    http://en.wikipedia.org/wiki/Self-information

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


def get_min_entropy_from_counts(count_dict):
    """Return min entropy of a random variable given values and frequencies."""
    total_observations = sum(count_dict.itervalues())
    worst_case_count = min(count_dict.itervalues())
    return surprisal(worst_case_count / total_observations)


def tor_button_resize(resolution, resize_param):
    """Change screen resolution using the parameters in resize_param.

    This can be used simulate Torbutton's screen manipulation and
    try different resize parameters.
    """
    # We assume toolbar height is 140px
    # This is what torbutton calculates for Gnome on Ubuntu
    TOOLBAR_H = 140
    rp = resize_param
    try:
        w, h = map(int, resolution.split("x")[:2])
        orig_area = w * h
        # torbutton code for resizing window width
        if rp.max_w and w > rp.max_w:
            new_w = rp.max_w
        else:
            new_w = int(floor(w / rp.w_roundto) * rp.w_roundto)

        # torbutton code for resizing window height
        new_h = int(floor((h - TOOLBAR_H) / rp.h_roundto) * rp.h_roundto)
        # this is to cap window height
        if rp.max_h and new_h > rp.max_h:
            new_h = rp.max_h
        utilization = (new_w * new_h / orig_area) if orig_area else 1
        return "%sx%sx%s" % (new_w, new_h, TBB_COLOR_DEPTH), utilization
    except ValueError:
        # print "Unexpected value", resolution
        return None, None


def filter_resolution_data(screen_counts, min_w=640, min_h=480,
                           max_w=maxint, max_h=maxint):
    """Filter resolutions dict using the minimal values."""
    filtered = {}
    for resolution, count in screen_counts.iteritems():
        try:
            w, h = map(int, resolution.split("x")[:2])
            if w >= min_w and h >= min_h and w <= max_w and h <= max_h:
                filtered[resolution] = count
        except:  # filter other junk resolution data e.g. undefined etc.
            pass
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
            resized[torb_resolution] = resized.get(torb_resolution, 0) + count
    return resized, total_utilization / no_of_points


def measure_entropy_for_resize_params(counts, resize_param):
    """Return entropy for transformed screen resolutions."""
    resized, util = torb_resize_all(counts, ResizeParams(*resize_param))
    entropy = get_entropy_from_counts(resized)
    min_entropy = get_min_entropy_from_counts(resized)
    return {"resized": resized, "entropy": entropy,
            "min_entropy":min_entropy,
            "utilization": util, "resize_params": resize_param}


def print_entropy_for_resize_exp(result, prefix=""):
    # plot_dist(result["resized"])
    csv_name = "_".join(str(p) for p in result["resize_params"])
    write_csv(csv_name, result["resized"])
    print "%s Entropy: %0.2f bits, Min-Entropy: %0.2f bits, "\
            "Util: %%%0.2f Bins: %s Resize params: %s - %s" %\
        (prefix, result["entropy"], result["min_entropy"],
         result["utilization"] * 100, len(result["resized"]),
         result["resize_params"], sort_by_value(result["resized"]))


def print_entropy_for_resize_exps(results, prefix=""):
    for result in results:
        print_entropy_for_resize_exp(result)


def print_entropy_for_counts(counts, prefix=""):
    # TODO merge with other prin function
    entropy = get_entropy_from_counts(counts)
    min_entropy = get_min_entropy_from_counts(counts)
    print "%s Entropy: %0.2f bits, Min-Entropy: %0.2f bits, Bins: %s, "\
            "on avg. one in %0.2f share the same value %s"\
            % (prefix, entropy, min_entropy, len(counts), 2 ** entropy,
               sort_by_value(counts)[:100])  # only print first 100 bins


def write_csv(prefix, dist_dict):
    csv_name = "%s.csv" % prefix
    print "Writing to", csv_name
    fout = open(csv_name, "w")
    for k, v in sort_by_value(dist_dict):
        fout.write("%s,%s\n" % (k, v))


def metric1(x):
    """Metric 1: entropy * (1 - utilization)."""
    return x["entropy"] * (1 - x["utilization"])


# We'll use Panopticlick data from a 2yrs old dump and assume Tor uses have the
# same resolution distribution. We remove values such as undefined to allow
# torbutton to resize all the data points (resolutions)
# max_h_offset can be used add some noise to toolbar height
# TODO: check if we can find a better value


def run_resolution_entropy_exp(data_file):
    exp_results = []
    counts = read_sql_output(data_file)
    print "Total data points: %s" % sum(counts.itervalues())
    print_entropy_for_counts(counts, "Original data")
    MAX_W = MAX_H = 16384  # to filter out unrealistic resolutions
    min_800_600 = filter_resolution_data(counts, 800, 600, MAX_W, MAX_H)
    print "\nTotal data points above 800x600 and below %sx%s: %s" %\
        (MAX_W, MAX_H, sum(min_800_600.itervalues()))
    print_entropy_for_counts(min_800_600, "Screen above 800x600")

    for resize_param in resize_params:
        r = measure_entropy_for_resize_params(min_800_600, resize_param)
        exp_results.append(r)

    print "\n***Results for different resize parameters***"
    print_entropy_for_resize_exps(exp_results)

def write_list_to_csv(lines, dump_file):
    with open(dump_file, "w") as f:
        f.write("\n".join(lines))

def convert_screen_sql_dump_to_csv(dump_file):
    resols = []
    counts = read_sql_output(dump_file)
    print "Total data points: %s" % sum(counts.itervalues())
    for res, count in counts.iteritems():
        try:
            w, h, bit_depth = map(int, res.split("x")[:3])
            if w > 0 and w < 5000 and h > 0 and h < 5000 and bit_depth > 0 and bit_depth <= 48: 
                resols.append("%s,%s,%s,%s" % (w, h, bit_depth, count))
        except:
            # print " Exc!"
            pass
    write_list_to_csv(resols, dump_file+".csv")

if __name__ == '__main__':
    filename = "panopticlick-screen-resolution.txt"  # original DB dump
    filename = "../scr.txt"  # 2014-8 data
    convert_screen_sql_dump_to_csv(filename)
    # run_resolution_entropy_exp(filename)
