import pyodbc
import xml.etree.ElementTree as ET


def read_db(query_type):
    connection = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};Server=192.168.100.65;port=1433;Database=Viamedis_DEV_MCO_F;uid=batch'
        ';pwd=hq41oy5t;')
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
    tree = ET.ElementTree(ET.fromstring(xml_string))

    # get root element
    root = tree.getroot()

    # create empty list for news items
    field_labels = {}
    field_widths = {}

    for item in root:
        name = item.find("Name")
        widths = item.find("Length")
        index = item.find("BeginIndex")
        # append name to fieldnames
        field_labels.update({int(index.text): name.text})
        # append len to fieldwidths
        field_widths.update({int(index.text): widths.text})

    # field_labels to list
    field_labels = [field_labels[i] for i in sorted(field_labels.keys())]
    # field_widths to list
    field_widths = [field_widths[i] for i in sorted(field_widths.keys())]

    if field_labels[0] != "FETYLIGN" and field_labels[0] != "FUTYLIGN":
        field_labels.insert(0, "FUTYLIGN")
        field_widths.insert(0, '3')

    return field_labels, field_widths


def main():
    records_desc = {"REC001": ["Header", "000"], "REC002": ["Body", "444"], "REC003": ["Footer", "999"]}
    file_num = 13
    file_label = "FUBE_V2"
    file_regex = r"^.{21}(FUBXM|FUBXE)"
    # ini_header = "[FT0"+str(file_num)+"_"+file_label+"]"
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
        # add record to records dictionary
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
