definitions = (
    (
        "FUBE_V2",
        {
            "REC001": ["Header", "^000"],
            "REC002": ["Body", "^444"],
            "REC003": ["Footer", "^999"]
        },
        r"^.{21}(FUBXM|FUBXE)"
    ),
    (
        "FUBE_V2_1",
        {
            "REC001": ["Header", "^000"],
            "REC002": ["Body", "^444"],
            "REC003": ["Footer", "^999"]
        },
        r"^.{21}(FUBYM|FUBYE)"
    ),
    (
        "FUBE_V2_2",
        {
            "REC001": ["Header", "^000"],
            "REC002": ["Body", "^444"],
            "REC003": ["Footer", "^999"]
        },
        r"^.{21}(FUBZM|FUBZE)"
    ),
    (
        "FUBE_V1",
        {
            "REC001": ["Body", "^.{2968}$"]
        },
        r"^.{2968}$"
    )
)
