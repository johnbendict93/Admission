# config.py — DCE Admission CRM global constants

# ── Brand ────────────────────────────────────────────────────
MAROON  = "#8B1A1A"
GOLD    = "#C9A84C"
CREAM   = "#F5F0E8"
WHITE   = "#FFFFFF"
DARK    = "#1A1A1A"

COLLEGE_NAME      = "Dhanalakshmi College of Engineering"
COLLEGE_SHORT     = "DCE"
APP_TITLE         = "DCE Admission CRM"
ACADEMIC_YEAR     = "2026-27"

# ── Supabase tables ──────────────────────────────────────────
TBL_USERS         = "users"
TBL_APPLICANTS    = "applicants"
TBL_APPLICATIONS  = "applications"
TBL_SESSIONS      = "counseling_sessions"
TBL_FOLLOWUPS     = "follow_ups"

# ── Module registry (22 modules) ─────────────────────────────
# Each entry: (display_name, icon, module_file, section)
MODULES = [
    # ── Overview ────────────────────────────────────────────
    ("Dashboard",               "🏠", "dashboard",            "Overview"),
    ("Analytics & Reports",     "📊", "analytics",            "Overview"),

    # ── Lead Management ─────────────────────────────────────
    ("Walk-in Registration",    "🚶", "walkin_registration",  "Lead Management"),
    ("Lead Tracker",            "🎯", "lead_tracker",         "Lead Management"),
    ("Lead Source Analysis",    "📡", "lead_source",          "Lead Management"),
    ("Bulk Import Leads",       "📥", "bulk_import",          "Lead Management"),

    # ── Applicant ───────────────────────────────────────────
    ("Applicant Profiles",      "👤", "applicant_profiles",   "Applicant"),
    ("Document Verification",   "📋", "document_verification","Applicant"),
    ("Merit List",              "🏅", "merit_list",           "Applicant"),

    # ── Counseling ──────────────────────────────────────────
    ("Counseling Sessions",     "🗣️", "counseling_sessions",  "Counseling"),
    ("Follow-up Manager",       "🔔", "followup_manager",     "Counseling"),
    ("My Tasks",                "✅", "my_tasks",             "Counseling"),

    # ── Admissions ──────────────────────────────────────────
    ("Application Tracker",     "📝", "application_tracker",  "Admissions"),
    ("Seat Allotment",          "🪑", "seat_allotment",       "Admissions"),
    ("Fee Management",          "💰", "fee_management",       "Admissions"),
    ("Scholarship Management",  "🎓", "scholarship",          "Admissions"),

    # ── Communication ───────────────────────────────────────
    ("SMS / WhatsApp Blast",    "💬", "sms_blast",            "Communication"),
    ("Email Campaigns",         "📧", "email_campaigns",      "Communication"),
    ("Communication Log",       "🗒️", "comms_log",            "Communication"),

    # ── Operations ──────────────────────────────────────────
    ("Hostel Allotment",        "🏠", "hostel_allotment",     "Operations"),
    ("Calendar & Events",       "📅", "calendar_events",      "Operations"),

    # ── Admin ───────────────────────────────────────────────
    ("Settings & Admin",        "⚙️", "settings_admin",       "Admin"),
]

# ── Applicant status flow ────────────────────────────────────
APPLICANT_STATUSES = [
    "New Lead", "Contacted", "Interested", "Documents Pending",
    "Documents Submitted", "Counseled", "Confirmed",
    "Fee Paid", "Enrolled", "Not Interested", "Dropped",
]

DEPARTMENTS = ["CSE", "ECE", "EEE", "MECH", "CIVIL", "IT", "AIDS", "AIML", "CSD", "MBA", "MCA"]
PROGRAMMES  = ["B.E.", "B.Tech", "M.E.", "M.Tech", "MBA", "MCA"]
CATEGORIES  = ["OC", "BC", "BCM", "MBC", "SC", "SCA", "ST"]
LEAD_SOURCES = ["Walk-in", "Phone", "Website", "Social Media", "Reference", "School Visit", "Camp", "Ad", "Other"]
