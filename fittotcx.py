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

import sys
import lxml.etree
import unitconvert

from fitparse import Activity, FitParseError

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

NSMAP = {\
    None : TCD_NAMESPACE, \
    "xsi": XML_SCHEMA_NAMESPACE}

# FIT to TCX values mapping

LAP_TRIGGER_MAP = {\
    "manual":             "Manual", \
    "time":               "Time", \
    "distance":           "Distance", \
    "position_start":     "Location", \
    "position_lap":       "Location", \
    "position_waypoint":  "Location", \
    "position_marked":    "Location", \
    "session_end":        "Manual", \
    "fitness_equipment":  "Manual"}

INTENSITY_MAP = {\
    "active":             "Active", \
    "warmup":             "Active", \
    "cooldown":           "Active", \
    "rest":               "Resting", \
    None:                 "Resting"}


def create_element(tag, text=None, namespace=None):
    namespace = NSMAP[namespace]
    tag       = "{%s}%s" % (namespace, tag)
    element   = lxml.etree.Element(tag, nsmap=NSMAP)

    if text != None:
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



def add_author(document):
    """Add author"""
    author = create_sub_element(document.getroot(), "Author")
    author.set(XML_SCHEMA + "type", "Application_t")
    create_sub_element(author, "Name", "Fit to TCX")
    create_sub_element(author, "LangID", "EN")



def add_trackpoint(element, trackpoint):
    timestamp  = unitconvert.local_date_to_utc(trackpoint.get_data("timestamp"))
    pos_lat    = trackpoint.get_data("position_lat")
    pos_long   = trackpoint.get_data("position_long")
    distance   = trackpoint.get_data("distance")
    altitude   = trackpoint.get_data("altitude")
    speed      = trackpoint.get_data("speed")
    heart_rate = trackpoint.get_data("heart_rate")
    cadence    = trackpoint.get_data("cadence")

    create_sub_element(element, "Time", timestamp.isoformat() + "Z")

    if pos_lat != None and pos_long != None:
        pos = create_sub_element(element, "Position")
        create_sub_element(pos, "LatitudeDegrees", 
            str(unitconvert.semicircle_to_degrees(pos_lat)))
        create_sub_element(pos, "LongitudeDegrees",
            str(unitconvert.semicircle_to_degrees(pos_long)))

    if altitude != None:
        create_sub_element(element, "AltitudeMeters", str(altitude))
    if distance != None:    
        create_sub_element(element, "DistanceMeters", str(distance))

    if heart_rate != None:
        heartrateelem = create_sub_element(element, "HeartRateBpm")
        heartrateelem.set(XML_SCHEMA + "type", "HeartRateInBeatsPerMinute_t")
        create_sub_element(heartrateelem, "Value", str(heart_rate))

    if cadence != None:
        create_sub_element(element, "Cadence", str(cadence))

    if speed != None:
        exelem  = create_sub_element(element, "Extensions")
        tpx = create_sub_element(exelem, "TPX")
        tpx.set("xmlns", 
            "http://www.garmin.com/xmlschemas/ActivityExtension/v2")
        tpx.set("CadenceSensor", "Footpod")
        create_sub_element(tpx, "Speed", str(speed))

def add_lap(element, activity, lap):

    start_time = unitconvert.local_date_to_utc(lap.get_data("start_time"))
    end_time   = unitconvert.local_date_to_utc(lap.get_data("timestamp"))

    totaltime  = lap.get_data("total_elapsed_time")
    distance   = lap.get_data("total_distance")
    max_speed  = lap.get_data("max_speed") # opt
    calories   = lap.get_data("total_calories")

    #avg_heart  = lap.get_data("avg_heart_rate") #opt
    #max_heart  = lap.get_data("max_heart_rate") #opt

    intensity  = INTENSITY_MAP[lap.get_data("intensity")]

    cadence    = lap.get_data("avg_cadence") # XXX: or max?

    triggermet = LAP_TRIGGER_MAP[lap.get_data("lap_trigger")]

    #extensions

    lapelem = create_sub_element(element, "Lap")
    lapelem.set("StartTime", start_time.isoformat() + "Z")


    create_sub_element(lapelem, "TotalTimeSeconds", str(totaltime))
    create_sub_element(lapelem, "DistanceMeters", str(distance))
    create_sub_element(lapelem, "MaximumSpeed", str(max_speed))
    create_sub_element(lapelem, "Calories", str(calories))
    #create_sub_element(lapelem, "AverageHeartRateBpm", avg_heart)
    #create_sub_element(lapelem, "MaximumHeartRateBpm", max_heart)
    create_sub_element(lapelem, "Intensity", intensity)
    if cadence != None:
        create_sub_element(lapelem, "Cadence", str(cadence))
    create_sub_element(lapelem, "TriggerMethod", triggermet)

    # Add track points to lap
    trackelem = create_sub_element(lapelem, "Track")
    for trackpoint in activity.get_records_by_type('record'):
        tts = unitconvert.local_date_to_utc(trackpoint.get_data("timestamp"))
        if tts >= start_time and tts <= end_time:
            trackpointelem = create_sub_element(trackelem, "Trackpoint")
            add_trackpoint(trackpointelem, trackpoint)


def add_activity(element, activity):

    session = next(activity.get_records_by_type('session'))

    # Sport type
    sport = session.get_data("sport")
    sport_mapping = {"running": "Running", "cycling": "Biking"}
    sport = sport_mapping[sport] if sport in sport_mapping else "Other"
    # Identity (in UTC)
    identity = unitconvert.local_date_to_utc(session.get_data("start_time"))


    actelem = create_sub_element(element, "Activity")
    actelem.set("Sport", sport)
    create_sub_element(actelem, "Id", identity.isoformat() + "Z")

    for lap in activity.get_records_by_type('lap'):
        add_lap(actelem, activity, lap)



def convert(filename):

    document = create_document()
    element = create_sub_element(document.getroot(), "Activities")

    activity = Activity(filename)
    activity.parse()
    add_activity(element, activity)

    return document


def printhelp():
    print "usage: python" + sys.argv[0] + " FILE"
    print ""
    print "This program takes a FIT file and converts it into an TCX file" + \
          "and output the result to the standard output."

def main():

    if len(sys.argv) == 1:
        printhelp()
        return 0

    try:
        document = convert(sys.argv[1])
        print lxml.etree.tostring(document.getroot(), pretty_print=True, \
                                  xml_declaration=True, encoding="UTF-8")
        return 0
    except FitParseError, exception:
        sys.stderr.write(str(exception) + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())

