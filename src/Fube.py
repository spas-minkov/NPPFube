import os

import pyodbc
import xml.etree.ElementTree as Et
import config.properties as prop
import config.fube_definitions as fube


def read_db(file_label, query_type):
    connection = pyodbc.connect(prop.DB_CONN_STRING)
    cursor = connection.cursor()
    query = """SELECT [format] FROM [dbo].[STRUCTURED_LINE_FORMAT] WHERE [id] = ?;"""

    # if query is header then get header
    if query_type == "Body":
        query_val = file_label
    else:
        query_val = file_label + "_" + str(query_type).upper()
    cursor.execute(query, query_val)

    row = cursor.fetchone()
    return row


def parse_record(fube_version, xml_string):
    # create element tree object
    tree = Et.ElementTree(Et.fromstring(xml_string))

    # get root element
    root = tree.getroot()

    # create empty list for news items
    field_labels_dict = {}
    field_widths_dict = {}

    for item in root:
        name = item.find("Name")
        widths = item.find("Length")
        index = item.find("BeginIndex")
        description = item.find("Description")
        # append name to fieldnames
        field_labels_dict.update({int(index.text): name.text + " - " + description.text})
        # append len to field widths
        field_widths_dict.update({int(index.text): widths.text})

    fild_starts = [i for i in sorted(field_labels_dict.keys())]
    # field_labels to sorted by keys list
    field_labels = [field_labels_dict[i] for i in sorted(field_labels_dict.keys())]
    # field_widths to sorted by keys list
    field_widths = [field_widths_dict[i] for i in sorted(field_widths_dict.keys())]

    # Add header field if missing
    if not fube_version == "FUBE_V1" and not field_labels[0].startswith("FETYLIGN") and not field_labels[0].startswith(
            "FUTYLIGN"):
        field_labels.insert(0, "FUTYLIGN")
        field_widths.insert(0, '3')
        fild_starts.insert(0, 1)

    # Add filler field in case of a hole in field description
    field_labels_with_fillers = []
    field_widths_with_fillers = []
    for i in range(len(fild_starts)):
        if i != 0 and (fild_starts[i] - fild_starts[i - 1] != int(field_widths[i - 1])):
            field_labels_with_fillers.append("FILLER")
            field_widths_with_fillers.append(str(fild_starts[i] - fild_starts[i - 1] - int(field_widths[i - 1])))
            field_labels_with_fillers.append(field_labels[i])
            field_widths_with_fillers.append(field_widths[i])
        else:
            field_labels_with_fillers.append(field_labels[i])
            field_widths_with_fillers.append(field_widths[i])

    return field_labels_with_fillers, field_widths_with_fillers


def main():
    #delete all files from output directory
    for file in os.listdir(prop.OUTPUT_DIR):
        os.remove(prop.OUTPUT_DIR + file)

    for fube_version, records_desc, file_regex in fube.definitions:
        ini_header = "[" + fube_version + "]"
        file_name = "NPP_" + fube_version + ".ini"

        file = {
            "FileLabel": fube_version,
            "FileTheme": "Spectrum",
            "RecordTerminator": "",
            "MultiByteChars": "Y",
            "ADFT_Line_01": "1",
            "ADFT_Regex_01": file_regex,
            "ADFT_Line_02": "",
            "ADFT_Regex_02": "",
            "ADFT_Line_03": "",
            "ADFT_Regex_03": "",
            "RecordTypes": ",".join(map(str, records_desc.keys())),
        }

        # empty records dictionary
        records = {}
        # loop through records
        for record_key in records_desc:
            # get record from db
            row = read_db(fube_version, records_desc[record_key][0])
            # parse record
            field_labels, field_widths = parse_record(fube_version, row[0])
            # add record to the records dictionary
            record = {
                record_key + "_Label": records_desc[record_key][0],
                record_key + "_Marker": records_desc[record_key][1],
                record_key + "_FieldLabels": ','.join(map(str, field_labels)),
                record_key + "_FieldWidths": ','.join(map(str, field_widths))
            }
            records.update(record)

        # append records to file
        file.update(records)

        # write file header properties to file each on a new line
        with open(prop.OUTPUT_DIR + file_name, "w") as f:
            f.write(ini_header + "\n")
            print("\n" + ini_header)
            for key, value in file.items():
                line = key + "=" + str(value)
                print(line)
                f.write(line + "\n")


if __name__ == "__main__":
    # calling main function
    main()
