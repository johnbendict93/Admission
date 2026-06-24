# config.py — Admission CRM (static constants only)
# All dropdown lists, fee structure, seat intake etc. are now in Supabase
# via db.get_lookup(), db.get_fee_structure(), db.get_seat_intake() etc.

# ── Brand ────────────────────────────────────────────────────
MAROON  = "#8B1A1A"
GOLD    = "#C9A84C"
CREAM   = "#F5F0E8"
WHITE   = "#FFFFFF"
DARK    = "#1A1A1A"

# ── App identity ──────────────────────────────────────────────
# College name, short name, and academic year are all dynamic —
# read from Supabase settings table via db.get_college_name(),
# db.get_college_short(), db.get_academic_year().
# These are safe fallbacks only (used before Supabase is reachable).
COLLEGE_NAME  = "Admission CRM"
COLLEGE_SHORT = "Admission CRM"
APP_TITLE     = "Admission CRM"   # browser tab — must be static (Streamlit limitation)
ACADEMIC_YEAR = "2026-27"

# ── Supabase table names ──────────────────────────────────────
TBL_USERS      = "users"
TBL_APPLICANTS = "applicants"
TBL_APPS       = "applications"
TBL_SESSIONS   = "counseling_sessions"
TBL_FOLLOWUPS  = "follow_ups"
TBL_FEES       = "fee_payments"
TBL_SCHOLAR    = "scholarships"
TBL_HOSTEL     = "hostel_allotments"
TBL_SETTINGS   = "settings"
TBL_LOOKUPS    = "lookup_values"
TBL_DOCTYPES   = "document_types"

# ── Applicant status workflow (structural — not a lookup) ─────
APPLICANT_STATUSES = [
    "New Lead", "Contacted", "Interested", "Documents Pending",
    "Documents Submitted", "Counseled", "Confirmed",
    "Fee Paid", "Enrolled", "Not Interested", "Dropped",
]

# ── Module registry (22 modules) ─────────────────────────────
MODULES = [
    ("Dashboard",              "🏠", "dashboard",             "Overview"),
    ("Analytics & Reports",    "📊", "analytics",             "Overview"),
    ("Walk-in Registration",   "🚶", "walkin_registration",   "Lead Management"),
    ("Lead Tracker",           "🎯", "lead_tracker",          "Lead Management"),
    ("Lead Source Analysis",   "📡", "lead_source",           "Lead Management"),
    ("Bulk Import Leads",      "📥", "bulk_import",           "Lead Management"),
    ("Applicant Profiles",     "👤", "applicant_profiles",    "Applicant"),
    ("Document Verification",  "📋", "document_verification", "Applicant"),
    ("Merit List",             "🏅", "merit_list",            "Applicant"),
    ("Counseling Sessions",    "🗣️", "counseling_sessions",   "Counseling"),
    ("Follow-up Manager",      "🔔", "followup_manager",      "Counseling"),
    ("My Tasks",               "✅", "my_tasks",              "Counseling"),
    ("Application Tracker",    "📝", "application_tracker",   "Admissions"),
    ("Seat Allotment",         "🪑", "seat_allotment",        "Admissions"),
    ("Fee Management",         "💰", "fee_management",        "Admissions"),
    ("Scholarship Management", "🎓", "scholarship",           "Admissions"),
    ("SMS / WhatsApp Blast",   "💬", "sms_blast",             "Communication"),
    ("Email Campaigns",        "📧", "email_campaigns",       "Communication"),
    ("Communication Log",      "🗒️", "comms_log",             "Communication"),
    ("Hostel Allotment",       "🏠", "hostel_allotment",      "Operations"),
    ("Calendar & Events",      "📅", "calendar_events",       "Operations"),
    ("Settings & Admin",       "⚙️", "settings_admin",        "Admin"),
]