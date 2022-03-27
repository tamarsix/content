from CommonServerPython import *  # noqa: F401
import demistomock as demisto  # noqa: F401
import geopy.distance
import itertools
requests.packages.urllib3.disable_warnings()


def main():
    try:
        existing = demisto.get(demisto.context(), "ImpossibleTraveler.Events")
        events_dict = {}
        for o in existing:
            events_dict[o["location"]] = o
        distance_list = []
        args = demisto.args()
        src_coords_list = argToList(args['src_coords'])
        dest_coords_list = argToList(args['dest_coords'])

        # verify the two lists are identical - we receive two lists (and not one) for BC reasons
        if not set(src_coords_list) == set(dest_coords_list):
            raise DemistoException('The source coordination list and the destination coordination list '
                                   'should be identical.')

        for unique_pair in itertools.combinations(src_coords_list, 2):
            geo_distance = round(geopy.distance.geodesic(unique_pair[0], unique_pair[1]).miles, 2)
            hr = 'Calculated Distance: {} miles.'.format(str(geo_distance))
            context = {
                "distance": geo_distance,
                "src_coords": unique_pair[0],
                "dest_coords": unique_pair[1],
                "source_ip": events_dict[unique_pair[0]]["ip"],
                "source_country": events_dict[unique_pair[0]]["Country"],
                "dest_ip": events_dict[unique_pair[1]]["ip"],
                "dest_country": events_dict[unique_pair[1]]["Country"],
                "timestamp": events_dict[unique_pair[0]]["event_timestamp"],
                "identity": events_dict[unique_pair[0]]["identity_display_name"]
            }
            distance_list.append(CommandResults(readable_output=hr, outputs=context,
                                                outputs_prefix="GeoEvents", outputs_key_field=""))

        return_results(distance_list)

    except Exception as e:
        return_error('Error occurred while parsing output from command. Exception info:\n' + str(e))


if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()
