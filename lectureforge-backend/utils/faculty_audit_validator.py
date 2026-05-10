from models.schemas import FacultyAuditReport


def validate_faculty_audit(report: FacultyAuditReport) -> FacultyAuditReport:
    """
    Keeps the faculty audit safe for the frontend.
    Pydantic already validates the schema, so this function is intentionally light.
    """

    if not report.priority_fixes:
        report.priority_fixes = []

    if not report.timestamped_rewrites:
        report.timestamped_rewrites = []

    return report