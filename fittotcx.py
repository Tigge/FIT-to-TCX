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

import sys
import lxml.etree
import unitconvert

from fitparse import Activity, FitParseError

TCD_NAMESPACE = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
TCD = "{%s}" % TCD_NAMESPACE

XML_SCHEMA_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
XML_SCHEMA = "{%s}" % XML_SCHEMA_NAMESPACE

SCHEMA_LOCATION = "http://www.garmin.com/xmlschemas/ActivityExtension/v2 " + \
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


def createElement(tag, text=None, ns=None):
    namespace = NSMAP[ns]
    tag       = "{%s}%s" % (namespace, tag)
    element   = lxml.etree.Element(tag, nsmap=NSMAP)

    if text != None:
        element.text = text

    return element

def createSubElement(parent, tag, text=None, ns=None):
    element = createElement(tag, text, ns)
    parent.append(element)
    return element


def createDocument():
    document = createElement("TrainingCenterDatabase")
    document.set(XML_SCHEMA + "schemaLocation", SCHEMA_LOCATION)
    document = lxml.etree.ElementTree(document)

    return document


'''
Add author
'''
def addAuthor(document):

    author = createSubElement(document.getroot(), "Author")
    author.set(XML_SCHEMA + "type", "Application_t")
    name   = createSubElement(author, "Name", "Fit to TCX")
    lang   = createSubElement(author, "LangID", "EN")



def addTrackpoint(element, activity, trackpoint):
    timestamp  = unitconvert.local_date_to_utc(trackpoint.get_data("timestamp"))
    pos_lat    = trackpoint.get_data("position_lat")
    pos_long   = trackpoint.get_data("position_long")
    distance   = trackpoint.get_data("distance")
    altitude   = trackpoint.get_data("altitude")
    speed      = trackpoint.get_data("speed")
    heart_rate = trackpoint.get_data("heart_rate")

    createSubElement(element, "Time", timestamp.isoformat() + "Z")

    if pos_lat != None and pos_long != None:
        pos = createSubElement(element, "Position")
        createSubElement(pos, "LatitudeDegrees", str(unitconvert.semicircle_to_degrees(pos_lat)))
        createSubElement(pos, "LongitudeDegrees", str(unitconvert.semicircle_to_degrees(pos_long)))

    if altitude != None:
        createSubElement(element, "AltitudeMeters", str(altitude))
    if distance != None:
        createSubElement(element, "DistanceMeters", str(distance))

    if heart_rate != None:
        hr = createSubElement(element, "HeartRateBpm")
        hr.set(XML_SCHEMA + "type", "HeartRateInBeatsPerMinute_t")
        createSubElement(hr, "Value", str(heart_rate))

    if speed != None:
        ex  = createSubElement(element, "Extensions")
        tpx = createSubElement(ex, "TPX")
        tpx.set("xmlns", "http://www.garmin.com/xmlschemas/ActivityExtension/v2")
        tpx.set("CadenceSensor", "Footpod")
        createSubElement(tpx, "Speed", str(speed))

def addLap(element, activity, lap):

    start_time = unitconvert.local_date_to_utc(lap.get_data("start_time"))
    end_time   = unitconvert.local_date_to_utc(lap.get_data("timestamp"))

    totaltime  = lap.get_data("total_elapsed_time")
    distance   = lap.get_data("total_distance")
    max_speed  = lap.get_data("max_speed") # opt
    calories   = lap.get_data("total_calories")

    avg_heart  = lap.get_data("avg_heart_rate") #opt
    max_heart  = lap.get_data("max_heart_rate") #opt

    intensity  = INTENSITY_MAP[lap.get_data("intensity")]

    #cadence    = #opt

    triggermet = LAP_TRIGGER_MAP[lap.get_data("lap_trigger")]

    #extensions

    lapelem = createSubElement(element, "Lap")
    lapelem.set("StartTime", start_time.isoformat() + "Z")


    createSubElement(lapelem, "TotalTimeSeconds", str(totaltime))
    createSubElement(lapelem, "DistanceMeters", str(distance))
    createSubElement(lapelem, "MaximumSpeed", str(max_speed))
    createSubElement(lapelem, "Calories", str(calories))
    #createSubElement(lapelem, "AverageHeartRateBpm", avg_heart)
    #createSubElement(lapelem, "MaximumHeartRateBpm", max_heart)
    createSubElement(lapelem, "Intensity", intensity)
    #createSubElement(lapelem, "Cadence", cadence)
    createSubElement(lapelem, "TriggerMethod", triggermet)

    # Add track points to lap
    trackelem = createSubElement(lapelem, "Track")
    for trackpoint in activity.get_records_by_type('record'):
        dt = unitconvert.local_date_to_utc(trackpoint.get_data("timestamp"))
        if dt >= start_time and dt <= end_time:
            trackpointelem = createSubElement(trackelem, "Trackpoint")
            addTrackpoint(trackpointelem, activity, trackpoint)


def addActivity(element, activity):

    session = next(activity.get_records_by_type('session'))

    # Sport type
    sport = session.get_data("sport")
    sport_mapping = {"running": "Running", "cycling": "Biking"}
    sport = sport_mapping[sport] if sport in sport_mapping else "Other"
    # Identity (in UTC)
    identity = unitconvert.local_date_to_utc(session.get_data("start_time"))


    actelem = createSubElement(element, "Activity")
    actelem.set("Sport", sport)
    actidelem = createSubElement(actelem, "Id", identity.isoformat() + "Z")

    for lap in activity.get_records_by_type('lap'):
        addLap(actelem, activity, lap)



def convert(filename):

    document = createDocument()
    element = createSubElement(document.getroot(), "Activities")

    activity = Activity(filename)
    activity.parse()
    addActivity(element, activity)

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
    except FitParseError, e:
        sys.stderr.write(str(e) + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())

