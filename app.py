from flask import Flask, request, jsonify, render_template
from croniter import croniter
from cron_descriptor import get_description, Options
from datetime import datetime
from app_values import text_values

app = Flask(__name__)

# Utility function to check if a year is a leap year
def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

# Additional validation for days and months
def validate_days_and_months(day_value, month_value):
    """
    Validate that the day of month is valid for the given month.
    This is only applied when both day_value and month_value are numeric and have no operators.
    """
    if "*" in [day_value, month_value]:  # Skip validation if any value is '*'
        return True, None

    if not day_value.isdigit() or not month_value.isdigit():
        return False, "Day of month or month contains invalid operators or non-numeric values."

    day = int(day_value)
    month = int(month_value)

    if month < 1 or month > 12:
        return False, "Month value is out of range (1-12)."

    # Determine the maximum number of days in the month
    year = datetime.now().year  # Use the current year
    days_in_month = {
        1: 31, 2: 29 if is_leap_year(year) else 28, 3: 31, 4: 30,
        5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    }

    if day < 1 or day > days_in_month[month]:
        return False, f"Day value {day} is invalid for month {month}."

    return True, None

# Generic field validation function
def validate_field(value, min_val, max_val, allow_special=True, allow_question=False):
    """
    Validate individual cron field values.
    """
    special_chars = {"*", ",", "-", "/"} if allow_special else set()
    if allow_question:
        special_chars.add("?")
    for val in value.split(","):
        val = val.strip()
        if val in special_chars or val == "*":
            continue
        if "-" in val or "/" in val:
            try:
                parts = val.replace("/", "-").split("-")
                parts = [int(x) for x in parts if x.isdigit()]
                if any(p < min_val or p > max_val for p in parts):
                    return False
            except ValueError:
                return False
        elif not val.isdigit() or int(val) < min_val or int(val) > max_val:
            return False
    return True

# Validation functions for each format
def validate_standard_cron(expression):
    parts = expression.split()
    if len(parts) != 5:
        return False, ["Invalid number of fields for Standard cron format (requires 5 fields)."]
    
    errors = []
    if not validate_field(parts[0], 0, 59):  # Minutes
        errors.append("Invalid value for minutes (0-59 or *).")
    if not validate_field(parts[1], 0, 23):  # Hours
        errors.append("Invalid value for hours (0-23 or *).")
    if not validate_field(parts[2], 1, 31):  # Day of Month
        errors.append("Invalid value for day of month (1-31 or *).")
    if not validate_field(parts[3], 1, 12):  # Month
        errors.append("Invalid value for month (1-12 or *).")
    if not validate_field(parts[4], 0, 6):  # Day of Week
        errors.append("Invalid value for day of week (0-6 or *).")

    # Validate days and months together
    valid, error = validate_days_and_months(parts[2], parts[3])
    if not valid:
        errors.append(error)
    
    return len(errors) == 0, errors

def validate_quartz_cron(expression):
    parts = expression.split()
    if len(parts) not in [6, 7]:
        return False, ["Invalid number of fields for Quartz cron format (requires 6 or 7 fields)."]
    
    errors = []
    if not validate_field(parts[0], 0, 59):  # Seconds
        errors.append("Invalid value for seconds (0-59 or *).")
    if not validate_field(parts[1], 0, 59):  # Minutes
        errors.append("Invalid value for minutes (0-59 or *).")
    if not validate_field(parts[2], 0, 23):  # Hours
        errors.append("Invalid value for hours (0-23 or *).")
    if not validate_field(parts[3], 1, 31):  # Day of Month
        errors.append("Invalid value for day of month (1-31 or *).")
    if not validate_field(parts[4], 1, 12):  # Month
        errors.append("Invalid value for month (1-12 or *).")
    if not validate_field(parts[5], 0, 6, allow_question=True):  # Day of Week
        errors.append("Invalid value for day of week (0-6, *, or ?).")
    if len(parts) == 7 and not validate_field(parts[6], 1970, 2099):  # Year (optional)
        errors.append("Invalid value for year (1970-2099 or *).")

    # Validate days and months together
    valid, error = validate_days_and_months(parts[3], parts[4])
    if not valid:
        errors.append(error)
    
    return len(errors) == 0, errors

def validate_aws_cron(expression):
    return validate_quartz_cron(expression)  # AWS cron uses the same format as Quartz

def validate_spring_cron(expression):
    return validate_quartz_cron(expression)  # Spring cron uses the same format as Quartz

# Explanation functions for each format
def explain_standard_cron(expression):
    options = Options()
    options.throw_exception_on_parse_error = True
    options.verbose = True
    return get_description(expression, options)

def explain_quartz_cron(expression):
    options = Options()
    options.throw_exception_on_parse_error = True
    options.verbose = True
    return get_description(expression, options)

def explain_aws_cron(expression):
    return explain_quartz_cron(expression)  # AWS cron explanation is the same as Quartz

def explain_spring_cron(expression):
    return explain_quartz_cron(expression)  # Spring cron explanation is the same as Quartz

# Next occurrence calculation
def get_next_occurrence(expression):
    try:
        iter = croniter(expression, datetime.now())
        next_time = iter.get_next(datetime)
        return next_time.strftime("%I:%M:%S %p on %d-%b-%Y")
    except Exception as e:
        return f"Error calculating next occurrence: {e}"

# Route for the welcome page
@app.route('/')
def index():
    return render_template('index.html', content=text_values)

@app.route('/instructions')
def readme():
    return render_template('readme.html', content=text_values)

@app.route('/explain', methods=['POST'])
def explain():
    """
    Handle POST requests to validate, explain, and calculate next occurrence of cron expressions.
    """
    data = request.get_json()
    expression = data.get('expression', "").strip()
    format_type = data.get('format_type', "").strip().lower()

    # Validate based on format type
    if format_type == "standard":
        is_valid, errors = validate_standard_cron(expression)
    elif format_type == "quartz":
        is_valid, errors = validate_quartz_cron(expression)
    elif format_type == "aws":
        is_valid, errors = validate_aws_cron(expression)
    elif format_type == "spring":
        is_valid, errors = validate_spring_cron(expression)
    else:
        return jsonify({"error": "Unsupported cron format type."}), 400

    if not is_valid:
        return jsonify({"error": "Invalid cron expression", "details": errors}), 400

    # Generate explanation based on format type
    if format_type == "standard":
        explanation = explain_standard_cron(expression)
    elif format_type == "quartz":
        explanation = explain_quartz_cron(expression)
    elif format_type == "aws":
        explanation = explain_aws_cron(expression)
    elif format_type == "spring":
        explanation = explain_spring_cron(expression)
    
    # Calculate next occurrence
    next_occurrence = get_next_occurrence(expression)

    return jsonify({
        "explanation": explanation,
        "next_occurrence": next_occurrence
    })

if __name__ == '__main__':
    app.run(debug=True)
