from flask import Flask, render_template, request, jsonify
from cronsim import CronSim
from cron_descriptor import get_description
from datetime import datetime

app = Flask(__name__)

# Define functions to explain each format with descriptions
def explain_standard_cron(expression):
    try:
        fields = expression.split()
        if len(fields) != 5:
            raise ValueError("Invalid format. Standard Linux cron requires 5 fields.")
        
        # Use cronsim directly with 5 fields
        cron_sim = CronSim(expression, datetime.now())
        description = cron_sim.explain()
        
        return description
    
    except Exception as e:
        return f"Invalid format for Standard Linux cron. Error: {str(e)}"

def explain_quartz_cron(expression):
    try:
        fields = expression.split()
        if len(fields) not in [6, 7]:
            raise ValueError("Invalid format. Quartz cron requires 6 or 7 fields.")
        
        # Generate description using cron-expression-descriptor
        description = get_description(expression)
        return description
    except Exception as e:
        return f"Invalid format for Quartz cron. Error: {str(e)}"

def explain_aws_cron(expression):
    try:
        fields = expression.split()
        if len(fields) != 6:
            raise ValueError("Invalid format. AWS cron requires 6 fields.")
        
        # Generate description using cron-expression-descriptor (customized for AWS format)
        standard_cron = " ".join(fields[:5])  # AWS is similar to standard cron but includes year
        description = get_description(standard_cron)
        year = fields[5]
        return f"{description}, in year(s): {year}."
    except Exception as e:
        return f"Invalid format for AWS cron. Error: {str(e)}"

def explain_spring_cron(expression):
    try:
        fields = expression.split()
        if len(fields) != 6:
            raise ValueError("Invalid format. Spring cron requires 6 fields.")
        
        # Generate description using cron-expression-descriptor (customized for Spring format)
        description = get_description(expression)
        return description
    except Exception as e:
        return f"Invalid format for Spring cron. Error: {str(e)}"

# Route for the welcome page
@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/readme')
def readme():
    return render_template('readme.html')

# API endpoint for real-time explanation
@app.route('/explain', methods=['POST'])
def explain():
    data = request.get_json()
    expression = data.get('expression', "")
    format_type = data.get('format_type', "")

    try:
        if format_type == 'standard':
            explanation = explain_standard_cron(expression)
        elif format_type == 'quartz':
            explanation = explain_quartz_cron(expression)
        elif format_type == 'aws':
            explanation = explain_aws_cron(expression)
        elif format_type == 'spring':
            explanation = explain_spring_cron(expression)
        else:
            explanation = "Unknown format type."
    except Exception as e:
        explanation = f"Invalid format. Error: {str(e)}"

    return jsonify({"explanation": explanation})

if __name__ == '__main__':
    app.run(debug=True)
