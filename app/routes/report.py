from flask import Blueprint, request, jsonify
from ..supabase_service import get_supabase_client

bp = Blueprint('issue_reports_routes', __name__)
supabase = get_supabase_client()

@bp.route('/createIssueReport', methods=['POST'])
def create_issue_report():
    issue_data = request.get_json()
    try:
        # Insert the issue data into the 'IssueReports' table
        issue_response = supabase.table('IssueReports').insert(issue_data).execute()
        if len(issue_response.data) > 0:
            return jsonify({"message": "Issue report created successfully!", "issue": issue_response.data[0]}), 201
        else:
            return jsonify({"error": "Failed to create issue report"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/getAllIssueReports', methods=['GET'])
def get_all_issue_reports():
    try:
        # Fetch all issue reports from the 'IssueReports' table
        response = supabase.table('IssueReports').select('*').execute()
        if len(response.data) > 0:
            return jsonify({"issues": response.data}), 200
        else:
            return jsonify({"message": "No issue reports found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500