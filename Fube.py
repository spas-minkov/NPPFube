import pyodbc
import xml.etree.ElementTree as Et
import configparser as cp


def read_db(query_type):
    config = cp.RawConfigParser()
    config.read('config.properties')
    db_string = config.get('Database', 'database.string')
    connection = pyodbc.connect(db_string)
    cursor = connection.cursor()
    # if query is header then get header
    if query_type == "Header":
        cursor.execute("SELECT format from STRUCTURED_LINE_FORMAT where id = 'FUBE_V2_HEADER';")
    # if query is footer then get footer
    elif query_type == "Footer":
        cursor.execute("SELECT format from STRUCTURED_LINE_FORMAT where id = 'FUBE_V2_FOOTER';")
    # if query is empty then get body
    else:
        cursor.execute("SELECT format from STRUCTURED_LINE_FORMAT where id = 'FUBE_V2';")
    row = cursor.fetchone()
    return row


def parse_record(xml_string):
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
        field_labels_dict.update({int(index.text): name.text + "--" + description.text.replace(" ", "_")})
        # append len to fieldwidths
        field_widths_dict.update({int(index.text): widths.text})

    fild_starts = [i for i in sorted(field_labels_dict.keys())]
    # field_labels to sorted by keys list
    field_labels = [field_labels_dict[i] for i in sorted(field_labels_dict.keys())]
    # field_widths to sorted by keys list
    field_widths = [field_widths_dict[i] for i in sorted(field_widths_dict.keys())]

    # Add header field if missing
    if not field_labels[0].startswith("FETYLIGN") and not field_labels[0].startswith("FUTYLIGN"):
        field_labels.insert(0, "FUTYLIGN")
        field_widths.insert(0, '3')
        fild_starts.insert(0, 1)

    # Add filler field in case of a hole in field description
    field_labels_with_fillers = []
    field_widths_with_fillers = []
    for i in range(len(fild_starts)):
        if i != 0 and (fild_starts[i] - fild_starts[i-1] != int(field_widths[i-1])):
            field_labels_with_fillers.append("FILLER")
            field_widths_with_fillers.append(str(fild_starts[i] - fild_starts[i-1] - int(field_widths[i-1])))
            field_labels_with_fillers.append(field_labels[i])
            field_widths_with_fillers.append(field_widths[i])
        else:
            field_labels_with_fillers.append(field_labels[i])
            field_widths_with_fillers.append(field_widths[i])

    return field_labels_with_fillers, field_widths_with_fillers


def main():
    records_desc = {"REC001": ["Header", "000"], "REC002": ["Body", "444"], "REC003": ["Footer", "999"]}
    file_label = "FUBE_V2"
    file_regex = r"^.{21}(FUBXM|FUBXE)"
    ini_header = "["+file_label+"]"

    #####################################################

    file = {
        "FileLabel": file_label,
        "FileTheme": "Spectrum",
        "RecordTerminator": "",
        "MultiByteChars": "Y",
        "ADFT_Line_01": "1",
        "ADFT_Regex_01": file_regex,
        "ADFT_Line_02": "",
        "ADFT_Regex_02": "",
        "ADFT_Line_03": "",
        "ADFT_Regex_03": "",
        "RecordTypes": list(records_desc.keys()),
    }

    # empty records dictionary
    records = {}
    # loop through records
    for record_key in records_desc:
        # get record from db
        row = read_db(records_desc[record_key][0])
        # parse record
        field_labels, field_widths = parse_record(row[0])
        # add record to the records dictionary
        record = {
            record_key + "_Label": records_desc[record_key][0],
            record_key + "_Marker": "^" + records_desc[record_key][1],
            record_key + "_FieldLabels": field_labels,
            record_key + "_FieldWidths": field_widths
        }
        records.update(record)

    # print record
    print(records)

    # append records to file
    file.update(records)
    print(file)
    # remove spaces from string
    file = {k.replace(" ", ""): v for k, v in file.items()}

    # write file header properties to file each on a new line
    with open("file_header_properties.txt", "w") as f:
        f.write(ini_header + "\n")
        for key, value in file.items():
            f.write(key + "=" + str(value).replace("'", "").replace("[", "").replace("]", "").replace(" ", "") + "\n")


if __name__ == "__main__":
    # calling main function
    main()
