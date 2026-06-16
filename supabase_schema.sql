-- ============================================================
--  DCE Admission CRM — Supabase Schema
--  Database: PostgreSQL (Supabase)
--  Created: 2026-06-16
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- TABLE 1: users
-- CRM staff, counselors, admins
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           TEXT UNIQUE NOT NULL,
    full_name       TEXT NOT NULL,
    phone           TEXT,
    role            TEXT NOT NULL CHECK (role IN ('admin', 'counselor', 'staff', 'viewer')),
    department      TEXT,
    is_active       BOOLEAN DEFAULT TRUE,
    avatar_url      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can read own record" ON users
    FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Admins can read all users" ON users
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')
    );


-- ============================================================
-- TABLE 2: applicants
-- Core student/lead profile — one row per person
-- ============================================================
CREATE TABLE IF NOT EXISTS applicants (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reg_number          TEXT UNIQUE,                     -- Auto-generated or manual
    first_name          TEXT NOT NULL,
    last_name           TEXT NOT NULL,
    date_of_birth       DATE,
    gender              TEXT CHECK (gender IN ('Male', 'Female', 'Other', 'Prefer not to say')),
    phone               TEXT NOT NULL,
    alternate_phone     TEXT,
    email               TEXT,
    address_line1       TEXT,
    address_line2       TEXT,
    city                TEXT,
    state               TEXT DEFAULT 'Tamil Nadu',
    pincode             TEXT,
    aadhaar_number      TEXT,
    category            TEXT CHECK (category IN ('OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST')),
    community_cert_no   TEXT,
    twelfth_school      TEXT,
    twelfth_board       TEXT,
    twelfth_year        INTEGER,
    twelfth_percentage  NUMERIC(5,2),
    twelfth_group       TEXT,                            -- Bio Maths / Computer Science etc.
    pcm_marks           NUMERIC(5,2),
    cutoff_marks        NUMERIC(5,2),
    entrance_exam       TEXT,                            -- JEE / TNEA / KEAM etc.
    entrance_rank       INTEGER,
    entrance_score      NUMERIC(7,2),
    parent_name         TEXT,
    parent_phone        TEXT,
    parent_occupation   TEXT,
    annual_income       NUMERIC(12,2),
    lead_source         TEXT CHECK (lead_source IN (
                            'Walk-in', 'Phone', 'Website', 'Social Media',
                            'Reference', 'School Visit', 'Camp', 'Ad', 'Other'
                        )),
    referred_by         TEXT,
    assigned_counselor  UUID REFERENCES users(id),
    status              TEXT DEFAULT 'New Lead' CHECK (status IN (
                            'New Lead', 'Contacted', 'Interested', 'Documents Pending',
                            'Documents Submitted', 'Counseled', 'Confirmed',
                            'Fee Paid', 'Enrolled', 'Not Interested', 'Dropped'
                        )),
    priority            TEXT DEFAULT 'Normal' CHECK (priority IN ('High', 'Normal', 'Low')),
    notes               TEXT,
    created_by          UUID REFERENCES users(id),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Auto-generate reg_number trigger
CREATE OR REPLACE FUNCTION generate_reg_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.reg_number IS NULL THEN
        NEW.reg_number := 'DCE-' || TO_CHAR(NOW(), 'YYYY') || '-' ||
                          LPAD(NEXTVAL('applicant_reg_seq')::TEXT, 5, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE SEQUENCE IF NOT EXISTS applicant_reg_seq START 1;

CREATE TRIGGER set_reg_number
    BEFORE INSERT ON applicants
    FOR EACH ROW EXECUTE FUNCTION generate_reg_number();

ALTER TABLE applicants ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Counselors see assigned applicants" ON applicants
    FOR ALL USING (
        assigned_counselor = auth.uid()
        OR EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role IN ('admin', 'staff'))
    );


-- ============================================================
-- TABLE 3: applications
-- One applicant can apply for multiple courses/years
-- ============================================================
CREATE TABLE IF NOT EXISTS applications (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    applicant_id        UUID NOT NULL REFERENCES applicants(id) ON DELETE CASCADE,
    application_no      TEXT UNIQUE,
    academic_year       TEXT NOT NULL DEFAULT '2026-27',
    programme           TEXT NOT NULL CHECK (programme IN ('B.E.', 'B.Tech', 'M.E.', 'M.Tech', 'MBA', 'MCA')),
    department          TEXT NOT NULL,                   -- CSE, ECE, MECH, CIVIL, EEE, IT etc.
    branch              TEXT,
    preferred_hostel    BOOLEAN DEFAULT FALSE,
    preferred_transport BOOLEAN DEFAULT FALSE,
    transport_route     TEXT,
    application_stage   TEXT DEFAULT 'Draft' CHECK (application_stage IN (
                            'Draft', 'Submitted', 'Under Review', 'Documents Verified',
                            'Merit Listed', 'Seat Allotted', 'Fee Pending',
                            'Provisionally Admitted', 'Admitted', 'Rejected', 'Withdrawn'
                        )),
    merit_rank          INTEGER,
    allotted_seat_type  TEXT CHECK (allotted_seat_type IN (
                            'Management', 'Government', 'NRI', 'Lateral Entry', 'Spot'
                        )),
    remarks             TEXT,
    submitted_at        TIMESTAMPTZ,
    reviewed_by         UUID REFERENCES users(id),
    reviewed_at         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Auto-generate application_no
CREATE OR REPLACE FUNCTION generate_application_no()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.application_no IS NULL THEN
        NEW.application_no := 'APP-' || TO_CHAR(NOW(), 'YYYY') || '-' ||
                               LPAD(NEXTVAL('application_no_seq')::TEXT, 6, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE SEQUENCE IF NOT EXISTS application_no_seq START 1;

CREATE TRIGGER set_application_no
    BEFORE INSERT ON applications
    FOR EACH ROW EXECUTE FUNCTION generate_application_no();

ALTER TABLE applications ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Staff can manage applications" ON applications
    FOR ALL USING (
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role IN ('admin', 'staff', 'counselor'))
    );


-- ============================================================
-- TABLE 4: counseling_sessions
-- Each interaction/meeting with an applicant
-- ============================================================
CREATE TABLE IF NOT EXISTS counseling_sessions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    applicant_id    UUID NOT NULL REFERENCES applicants(id) ON DELETE CASCADE,
    application_id  UUID REFERENCES applications(id),
    counselor_id    UUID NOT NULL REFERENCES users(id),
    session_type    TEXT NOT NULL CHECK (session_type IN (
                        'Walk-in', 'Phone Call', 'Video Call', 'WhatsApp',
                        'Email', 'Home Visit', 'School Visit', 'Camp', 'Follow-up'
                    )),
    session_date    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duration_mins   INTEGER,
    topics_discussed TEXT[],                            -- Array of topics
    outcome         TEXT CHECK (outcome IN (
                        'Interested', 'Not Interested', 'Need More Time',
                        'Documents Requested', 'Fee Discussed', 'Confirmed',
                        'Dropped', 'Callback Scheduled', 'Other'
                    )),
    next_action     TEXT,
    next_action_date DATE,
    notes           TEXT,
    mode            TEXT DEFAULT 'In-Person' CHECK (mode IN ('In-Person', 'Remote')),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE counseling_sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Counselors manage own sessions" ON counseling_sessions
    FOR ALL USING (
        counselor_id = auth.uid()
        OR EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role IN ('admin', 'staff'))
    );


-- ============================================================
-- TABLE 5: follow_ups
-- Scheduled tasks, reminders, to-dos linked to applicants
-- ============================================================
CREATE TABLE IF NOT EXISTS follow_ups (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    applicant_id    UUID NOT NULL REFERENCES applicants(id) ON DELETE CASCADE,
    assigned_to     UUID NOT NULL REFERENCES users(id),
    created_by      UUID REFERENCES users(id),
    title           TEXT NOT NULL,
    description     TEXT,
    follow_up_type  TEXT NOT NULL CHECK (follow_up_type IN (
                        'Call', 'WhatsApp', 'Email', 'SMS', 'Visit',
                        'Document Collection', 'Fee Reminder', 'General', 'Other'
                    )),
    priority        TEXT DEFAULT 'Normal' CHECK (priority IN ('Urgent', 'High', 'Normal', 'Low')),
    due_date        TIMESTAMPTZ NOT NULL,
    completed_at    TIMESTAMPTZ,
    status          TEXT DEFAULT 'Pending' CHECK (status IN (
                        'Pending', 'In Progress', 'Completed', 'Overdue', 'Cancelled'
                    )),
    outcome_notes   TEXT,
    reminder_sent   BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Index for common queries
CREATE INDEX IF NOT EXISTS idx_follow_ups_due_date ON follow_ups(due_date);
CREATE INDEX IF NOT EXISTS idx_follow_ups_assigned ON follow_ups(assigned_to, status);
CREATE INDEX IF NOT EXISTS idx_applicants_status ON applicants(status);
CREATE INDEX IF NOT EXISTS idx_applicants_counselor ON applicants(assigned_counselor);
CREATE INDEX IF NOT EXISTS idx_applications_stage ON applications(application_stage);
CREATE INDEX IF NOT EXISTS idx_sessions_date ON counseling_sessions(session_date);

ALTER TABLE follow_ups ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users manage own follow-ups" ON follow_ups
    FOR ALL USING (
        assigned_to = auth.uid()
        OR created_by = auth.uid()
        OR EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role IN ('admin', 'staff'))
    );


-- ============================================================
-- updated_at auto-trigger (applied to all tables)
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_applicants_updated_at
    BEFORE UPDATE ON applicants FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_applications_updated_at
    BEFORE UPDATE ON applications FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_sessions_updated_at
    BEFORE UPDATE ON counseling_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_followups_updated_at
    BEFORE UPDATE ON follow_ups FOR EACH ROW EXECUTE FUNCTION update_updated_at();
