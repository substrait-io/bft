from datetime import datetime
import pytz
import re

# Define short names for various data types
short_name_map = {
    "string": "str",
    "boolean": "bool",
    "varbinary": "vbin",
    "timestamp": "ts",
    "timestamp_tz": "tstz",
    "interval_year": "iyear",
    "interval_day": "iday",
    "interval": "iday",
    "decimal": "dec",
    "precision_timestamp": "pts",
    "precision_timestamp_tz": "ptstz",
    "fixedchar": "fchar",
    "varchar": "vchar",
    "fixedbinary": "fbin",
}

long_name_map = {v: k for k, v in short_name_map.items()}

# Mapping of timezone abbreviations to pytz time zones
timezone_abbr_map = {
    "PST": "America/Los_Angeles",
    "EST": "America/New_York",
    "CST": "America/Chicago",
    "MST": "America/Denver",
    "HST": "Pacific/Honolulu",
    "UTC": "UTC",
}

SQUOTE = "\u200B"
DQUOTE = "&"

# Map timezone abbreviations to valid pytz timezone names
timediff_abbr_map = {
    "-0800": "US/Pacific",  # Pacific Standard Time
    "-0500": "US/Eastern",  # Eastern Standard Time
}

timediff_zone_map = {
    "-0800": "PST",  # Pacific Standard Time
    "-0500": "EST",  # Eastern Standard Time
}


def convert_type(type_str, mapping):
    """Helper function to convert a type string using the provided mapping."""
    if type_str.startswith("list<") and type_str.endswith(">"):
        # Extract the inner type and convert it
        inner_type = type_str[5:-1]  # Extract what's inside "list<...>"
        short_inner_type = mapping.get(inner_type.lower(), inner_type)
        return f"list<{short_inner_type}>"

    base_type, parameters = (type_str.split("<", 1) + [""])[:2]
    parameters = f"<{parameters}" if parameters else ""
    return mapping.get(base_type.lower(), base_type) + parameters


def convert_to_long_type(type_str):
    type_str = convert_type(type_str, long_name_map)
    if type_str == "interval_year" or type_str == "interval_day":
        type_str = "interval"
    return type_str


def match_sql_duration(value, value_type):
    """
    Check if a string is in the format of 'X days, HH:MM:SS'.
    Returns a match object if successful, or None if it doesn't match.
    """
    if value_type != "str":
        return None
    pattern = r"^(?:(\d+)\s+days?,\s*)?(\d+):(\d+):(\d+)$"
    return re.match(pattern, value)


def format_timestamp(value):
    """Format a timestamp value into ISO 8601 format, handling optional fractional seconds."""
    # Try parsing with fractional seconds first
    try:
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
        return dt.isoformat()
    except ValueError:
        pass  # Continue to the next format if parsing fails

    # Fallback to parsing without fractional seconds
    try:
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return dt.isoformat()
    except ValueError:
        # Return the original value if it doesn't match expected formats
        return value


def has_last_colon_after_last_dash(s):
    """
    Check if the last ':' comes after the last '-' in the string.

    Args:
        s (str): Input string, e.g., "-10:30".

    Returns:
        bool: True if the last ':' comes after the last '-', False otherwise.
    """
    last_dash_index = s.rfind("-")  # Find the last occurrence of '-'
    last_colon_index = s.rfind(":")  # Find the last occurrence of ':'

    # Check if both '-' and ':' exist and if last ':' comes after last '-'
    return (
        last_dash_index != -1
        and last_colon_index != -1
        and last_dash_index < last_colon_index
    )


def format_timestamp_tz(timestamp_with_tz):
    """Convert a timestamp with timezone abbreviation to ISO 8601 with offset."""
    if "-" in timestamp_with_tz and not has_last_colon_after_last_dash(
        timestamp_with_tz
    ):
        return timestamp_with_tz.replace(" ", "T") + ":00"
    datetime_str, tz_abbr = timestamp_with_tz.rsplit(" ", 1)
    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

    if tz_abbr in timezone_abbr_map:
        dt = pytz.timezone(timezone_abbr_map[tz_abbr]).localize(dt)
    else:
        return timestamp_with_tz
        # raise ValueError(f"Invalid timezone abbreviation: {tz_abbr}")

    return dt.isoformat()


def convert_sql_interval_to_iso_duration(interval: str):
    """Convert SQL-style interval to ISO 8601 format."""
    # Regular expression to match interval components (e.g., '1 DAY 10 HOUR' or '360 DAY, 1 HOUR')
    match = re.match(
        r"INTERVAL\s*'((\d+)\s*(YEAR|MONTH|DAY|HOUR|MINUTE|SECOND)(\s+\d+\s*(YEAR|MONTH|DAY|HOUR|MINUTE|SECOND))*)'",
        interval.strip(),
    )
    if not match:
        raise ValueError(f"Invalid SQL interval format: {interval}")

    # Capture all parts of the interval, including multiple parts (space-separated)
    parts = match.group(1).split()

    iso_parts = []
    unit_map = {
        "YEAR": "P{}Y",
        "MONTH": "P{}M",
        "DAY": "P{}D",
        "HOUR": "PT{}H",
        "MINUTE": "PT{}M",
        "SECOND": "PT{}S",
    }

    i = 0
    iyear = False
    while i < len(parts):
        num = int(parts[i])  # The number part
        unit = parts[i + 1]  # The unit part
        if unit in ["YEAR", "MONTH"]:
            iyear = True
        iso_parts.append(unit_map[unit].format(num))
        i += 2  # Skip to the next number-unit pair

    # Join the components together to form the final ISO 8601 duration string
    iso_interval = "".join(iso_parts)

    # Determine whether it's a 'iyear' or 'iday' based on units
    if iyear:
        return iso_interval, "iyear"
    else:
        return iso_interval, "iday"


def convert_sql_duration_to_iso_duration(match):
    """
    Convert a valid "X days, HH:MM:SS" string to ISO 8601 duration format.
    If the input does not match, return the original string.
    """

    days, hours, minutes, seconds = match.groups(default="0")

    # Construct the ISO 8601 duration format
    iso_duration = f"P{int(days)}D"  # Add days
    if int(hours) or int(minutes) or int(seconds):
        iso_duration += f"T{int(hours)}H{int(minutes)}M{int(seconds)}S"

    return iso_duration


def iso_format_type(s):
    # Define regex patterns for each ISO 8601 format
    iso_patterns = {
        "time": r"^\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$",
        "iday": r"^P(\d+D)?(T(\d+H)?(\d+M)?(\d+S)?)?$",  # Day-based duration, specifically for day/time-only formats
        "iyear": r"^P(\d+Y)?(\d+M)?(\d+W)?(\d+D)?(T(\d+H)?(\d+M)?(\d+S)?)?$",
        # Full ISO duration format, can include year/month and day/time components
    }

    # Check against each pattern and return the type if it matches
    for fmt, pattern in iso_patterns.items():
        if re.match(pattern, s):
            return fmt  # Return the matching format type

    # Return None if no pattern matches
    return None


def format_null(value_type, value, level):
    """Handle null values, with special handling for interval types."""
    if value_type == "interval":
        # Special handling for null intervals
        return "null::iday" if level == 0 else "null"
    if value_type:
        return f"null::{value_type}" if level == 0 else value
    return "null"


def is_list_type(value_type):
    return bool(
        value_type and value_type.startswith("list<") and value_type.endswith(">")
    )


def needs_quotes(type_str):
    quote_types = {
        "str",
        "string",
        "fchar",
        "vchar",
        "date",
        "time",
        "list<str>",
        "iday",
        "iyear",
        "timestamp_tz",
        "timestamp",
    }

    """Check if the type requires quotes around its values."""
    # Extract base type, ignoring any <...> parameters, and lowercase for case-insensitive comparison
    base_type = type_str.split("<", 1)[0].lower()
    # Check against short and long versions of each type in quote_types
    if base_type not in quote_types and type_str not in quote_types:
        return False
    return True


def iso_to_sql_interval(iso_duration):
    # Match ISO 8601 duration format
    match = re.match(
        r"P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?",
        iso_duration,
    )

    if not match:
        raise ValueError("Invalid ISO 8601 duration format")

    # Create interval parts by pairing matched values with corresponding units
    units = ["YEAR", "MONTH", "DAY", "HOUR", "MINUTE", "SECOND"]
    parts = [f"{value} {unit}" for value, unit in zip(match.groups(), units) if value]
    interval = " ".join(parts)

    return "INTERVAL " + SQUOTE + interval + SQUOTE


def convert_iso_to_timezone_format(iso_string):
    # Parse the ISO 8601 string into a datetime object with timezone info
    dt = datetime.fromisoformat(iso_string)

    # Handle timezone-aware datetime
    if dt.tzinfo is not None:
        # Get the UTC offset
        offset_str = dt.strftime("%z")

        # Look up the timezone abbreviation from the offset
        timezone_name = timediff_abbr_map.get(offset_str, None)

        if timezone_name:
            # Convert the datetime object to the local time based on the timezone info
            tz = pytz.timezone(timezone_name)
            dt_in_timezone = dt.astimezone(tz)

            # Format the datetime into the required format (without the UTC offset and with time zone abbreviation)
            return dt_in_timezone.strftime(
                f"%Y-%m-%d %H:%M:%S {timediff_zone_map[offset_str]}"
            )
        else:
            return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    else:
        return dt.strftime("%Y-%m-%d %H:%M:%S")


def iso_duration_to_timedelta(iso_duration):
    # Match ISO 8601 duration pattern
    match = re.match(
        r"^P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?$", iso_duration
    )

    if not match:
        return iso_duration  # Return the original string if it's not a valid duration format

    days = int(match.group(1) or 0)
    hours = int(match.group(2) or 0)
    minutes = int(match.group(3) or 0)
    seconds = int(match.group(4) or 0)

    # Use singular/plural for "day" and handle zero days
    day_str = f"{days} day{'s' if days != 1 else ''}" if days > 0 else ""
    time_str = f"{hours}:{minutes:02}:{seconds:02}"

    return f"{day_str}, {time_str}" if day_str else time_str


def convert_to_old_value(value, value_type, level=0):
    if value_type is not None:
        value_type = convert_to_long_type(value_type)

    if isinstance(value, list):
        formatted_values = f"[{', '.join(convert_to_old_value(v, value_type, level + 1) for v in value)}]"
        return (
            f"!decimallist {formatted_values}"
            if value_type.startswith("decimal") and level == 0
            else formatted_values
        )

    if value_type is None and value.lower() == "null":
        return DQUOTE + "NULL" + DQUOTE
    if value_type is None and value.upper() == "IYEAR_360DAYS":
        return "360"
    if value_type is None and value.upper() == "IYEAR_365DAYS":
        return "365"
    if value in {None, "'Null'"}:
        return str("Null")
    value = str(value)
    if value == "NaN":
        return str("NAN")
    if value_type is not None:
        if value_type.startswith("decimal") and level == 0:
            value = "!decimal " + value
        if value_type == "interval":
            value = iso_to_sql_interval(str(value))
        if value_type == "timestamp":
            value = value.replace("T", " ")
            if "." in value:
                # Strip only the trailing zeros in the subsecond field
                value = value.rstrip("0").rstrip(".")
        if value_type == "timestamp_tz":
            value = convert_iso_to_timezone_format(value)
        if needs_quotes(value_type):
            value = DQUOTE + value + DQUOTE
            return value
    return str(value)


def convert_to_new_value(value, value_type, level=0):
    """Format a value based on its type, if specified."""
    if value_type:
        value_type = convert_type(value_type, short_name_map)

    # Handle list values recursively
    if isinstance(value, list):
        left_delim, right_delim = ("[", "]") if is_list_type(value_type) else ("(", ")")
        formatted_values = [
            convert_to_new_value(x, value_type, level + 1) for x in value
        ]
        return (
            f"{left_delim}"
            + ", ".join(map(str, formatted_values))
            + f"{right_delim}::{value_type}"
        )

    if (value is None) or str(value).lower() == "null":
        return format_null(value_type, value, level)

    if value_type is None:
        if value == "360":
            return "IYEAR_360DAYS"
        if value == "365":
            return "IYEAR_365DAYS"
        return str(value)

    # convert duration
    if value_type in ("iday", "iyear"):
        value, value_type = convert_sql_interval_to_iso_duration(str(value))
    match = match_sql_duration(value, value_type)
    if match:
        value = convert_sql_duration_to_iso_duration(match)
        value_type = iso_format_type(value)

    if value_type == "time":
        value = value.split("+")[0]
    if value_type == "ts":
        value = f"'{format_timestamp(str(value))}'"
    if value_type == "tstz":
        value = f"'{format_timestamp_tz(str(value))}'"
    if value_type == "bool":
        value = str(value).lower()

    if needs_quotes(value_type):
        value = f"'{value}'"

    return f"{value}::{value_type}" if level == 0 else value
