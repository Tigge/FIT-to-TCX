#!/usr/bin/python
#
# Fit to TCX
#
# Copyright (c) 2012, Gustav Tiger <gustav@tiger.name>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""Convert a FIT file to a TCX file"""

from __future__ import absolute_import, division, print_function

import argparse
import sys
import lxml.etree
from . import unitconvert

from fitparse import FitFile, FitParseError

TCD_NAMESPACE = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
TCD = "{%s}" % TCD_NAMESPACE

XML_SCHEMA_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
XML_SCHEMA = "{%s}" % XML_SCHEMA_NAMESPACE

SCHEMA_LOCATION = \
    "http://www.garmin.com/xmlschemas/ActivityExtension/v2 " + \
    "http://www.garmin.com/xmlschemas/ActivityExtensionv2.xsd " + \
    "http://www.garmin.com/xmlschemas/FatCalories/v1 " + \
    "http://www.garmin.com/xmlschemas/fatcalorieextensionv1.xsd " + \
    "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 " + \
    "http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"

NSMAP = {
    None: TCD_NAMESPACE,
    "xsi": XML_SCHEMA_NAMESPACE}

# FIT to TCX values mapping

LAP_TRIGGER_MAP = {
    "manual": "Manual",
    "time": "Time",
    "distance": "Distance",
    "position_start": "Location",
    "position_lap": "Location",
    "position_waypoint": "Location",
    "position_marked": "Location",
    "session_end": "Manual",
    "fitness_equipment": "Manual"}

INTENSITY_MAP = {
    "active": "Active",
    "warmup": "Active",
    "cooldown": "Active",
    "rest": "Resting"}

SPORT_MAP = {
    "running": "Running",
    "cycling": "Biking"}


def ff(number):
    return '{:.10f}'.format(number).rstrip('0').rstrip('.')


def create_element(tag, text=None, namespace=None):
    namespace = NSMAP[namespace]
    tag = "{%s}%s" % (namespace, tag)
    element = lxml.etree.Element(tag, nsmap=NSMAP)

    if text is not None:
        element.text = text

    return element


def create_sub_element(parent, tag, text=None, namespace=None):
    element = create_element(tag, text, namespace)
    parent.append(element)
    return element


def create_document():
    document = create_element("TrainingCenterDatabase")
    document.set(XML_SCHEMA + "schemaLocation", SCHEMA_LOCATION)
    document = lxml.etree.ElementTree(document)

    return document


def add_creator(element, device_info):
    creatorelem = create_sub_element(element, "Creator")
    creatorelem.set(XML_SCHEMA + "type", "Device_t")
    if device_info.get_value("product_name"):
        create_sub_element(creatorelem, "Name", device_info.get_value("product_name"))
    else:
        prod, manuf = device_info.get_value("product"), device_info.get_value("manufacturer")
        if manuf and prod:
            create_sub_element(creatorelem, "Name", manuf + ' ' + prod)
        elif prod:
            create_sub_element(creatorelem, "Name", prod)
        elif manuf:
            create_sub_element(creatorelem, "Name", manuf)

    if device_info.get_raw_value("serial_number"):
        create_sub_element(creatorelem, "UnitID", str(device_info.get_raw_value("serial_number")))
    if device_info.get_raw_value("product"):
        create_sub_element(creatorelem, "ProductID", str(device_info.get_raw_value("product")))

    # Garmin Connect always includes two digits in <VersionMinor>
    v = create_sub_element(creatorelem, "Version")
    sv = ('%.2f' % (device_info.get_value("software_version") or 0.0)).split('.')
    create_sub_element(v, 'VersionMajor', sv[0])
    create_sub_element(v, 'VersionMinor', sv[1])
    create_sub_element(v, 'BuildMajor', '0')
    create_sub_element(v, 'BuildMinor', '0')


def add_author(document):
    """Add author"""
    author = create_sub_element(document.getroot(), "Author")
    author.set(XML_SCHEMA + "type", "Application_t")
    create_sub_element(author, "Name", "FIT-to-TCX")
    create_sub_element(author, "LangID", "en")

    v = create_sub_element(author, "Version")
    b = create_sub_element(v, "Build")
    create_sub_element(b, 'VersionMajor', '0')
    create_sub_element(b, 'VersionMinor', '0')
    create_sub_element(b, 'BuildMajor', '0')
    create_sub_element(b, 'BuildMinor', '0')


def add_trackpoint(element, trackpoint):
    timestamp = trackpoint.get_value("timestamp")
    pos_lat = trackpoint.get_value("position_lat")
    pos_long = trackpoint.get_value("position_long")
    distance = trackpoint.get_value("distance")
    altitude = trackpoint.get_value("altitude")
    speed = trackpoint.get_value("speed")
    heart_rate = trackpoint.get_value("heart_rate")
    cadence = trackpoint.get_value("cadence")

    create_sub_element(element, "Time", timestamp.isoformat() + "Z")

    if pos_lat is not None and pos_long is not None:
        pos = create_sub_element(element, "Position")
        create_sub_element(pos, "LatitudeDegrees",
                           ff(unitconvert.semicircle_to_degrees(pos_lat)))
        create_sub_element(pos, "LongitudeDegrees",
                           ff(unitconvert.semicircle_to_degrees(pos_long)))

    if altitude is not None:
        create_sub_element(element, "AltitudeMeters", ff(altitude))
    if distance is not None:
        create_sub_element(element, "DistanceMeters", ff(distance))

    if heart_rate is not None:
        heartrateelem = create_sub_element(element, "HeartRateBpm")
        heartrateelem.set(XML_SCHEMA + "type", "HeartRateInBeatsPerMinute_t")
        create_sub_element(heartrateelem, "Value", ff(heart_rate))

    if cadence is not None:
        create_sub_element(element, "Cadence", ff(cadence))

    if speed is not None:
        exelem = create_sub_element(element, "Extensions")
        tpx = create_sub_element(exelem, "TPX")
        tpx.set("xmlns",
                "http://www.garmin.com/xmlschemas/ActivityExtension/v2")
        tpx.set("CadenceSensor", "Footpod")
        create_sub_element(tpx, "Speed", ff(speed))


def add_lap(element, activity, lap):
    start_time = lap.get_value("start_time")
    end_time = lap.get_value("timestamp")

    totaltime = lap.get_value("total_elapsed_time")
    if totaltime is None:
        totaltime = lap.get_value("")
    distance = lap.get_value("total_distance")
    max_speed = lap.get_value("max_speed")  # opt
    calories = lap.get_value("total_calories")

    # avg_heart  = lap.get_value("avg_heart_rate") #opt
    # max_heart  = lap.get_value("max_heart_rate") #opt

    intensity = INTENSITY_MAP.get(lap.get_value("intensity"), "Resting")

    cadence = lap.get_value("avg_cadence")  # XXX: or max?

    triggermet = LAP_TRIGGER_MAP.get(lap.get_value("lap_trigger"), "Manual")

    # extensions

    lapelem = create_sub_element(element, "Lap")
    lapelem.set("StartTime", start_time.isoformat() + "Z")

    create_sub_element(lapelem, "TotalTimeSeconds", ff(totaltime))
    create_sub_element(lapelem, "DistanceMeters", ff(distance))
    if max_speed is not None:
        create_sub_element(lapelem, "MaximumSpeed", ff(max_speed))
    create_sub_element(lapelem, "Calories", ff(calories))
    # create_sub_element(lapelem, "AverageHeartRateBpm", avg_heart)
    # create_sub_element(lapelem, "MaximumHeartRateBpm", max_heart)
    create_sub_element(lapelem, "Intensity", intensity)
    if cadence is not None:
        create_sub_element(lapelem, "Cadence", ff(cadence))
    create_sub_element(lapelem, "TriggerMethod", triggermet)

    # Add track points to lap
    trackelem = create_sub_element(lapelem, "Track")
    for trackpoint in activity.get_messages(name="record"):
        tts = trackpoint.get_value("timestamp")
        if start_time <= tts <= end_time:
            trackpointelem = create_sub_element(trackelem, "Trackpoint")
            add_trackpoint(trackpointelem, trackpoint)


def add_activity(element, activity):
    session = next(activity.get_messages(name='session'))

    # Sport type
    sport = SPORT_MAP.get(session.get_value("sport"), "Other")

    # Identity (in UTC)
    identity = session.get_value("start_time")

    actelem = create_sub_element(element, "Activity")
    actelem.set("Sport", sport)
    create_sub_element(actelem, "Id", identity.isoformat() + "Z")

    for lap in activity.get_messages("lap"):
        add_lap(actelem, activity, lap)

    device_info = next(activity.get_messages(name='device_info'))
    if device_info is not None:
        add_creator(actelem, device_info)

def convert(filename):
    document = create_document()
    element = create_sub_element(document.getroot(), "Activities")

    activity = FitFile(filename)
    activity.parse()
    add_activity(element, activity)
    add_author(document)

    return document


def documenttostring(document):
    return lxml.etree.tostring(document.getroot(), pretty_print=True,
                               xml_declaration=True, encoding="UTF-8")


def main():
    parser = argparse.ArgumentParser(
            description="This program takes a FIT file and converts it " +
                        "into an TCX file and output the result to the " +
                        "standard output.")
    parser.add_argument('file', metavar='FILE', type=argparse.FileType('r'))
    args = parser.parse_args()

    try:
        document = convert(sys.argv[1])
        sys.stdout.write(documenttostring(document).decode('utf-8'))
        return 0
    except FitParseError as exception:
        sys.stderr.write(str(exception) + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
