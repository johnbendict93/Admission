"""Module 06 — Bulk Import Leads (CSV → validate → Supabase batch INSERT)"""
import streamlit as st
import pandas as pd
import io
from datetime import date
from db import get_supabase
from config import MAROON, GOLD, DEPARTMENTS, PROGRAMMES, LEAD_SOURCES, APPLICANT_STATUSES

# Columns we accept (CSV header → DB column)
COLUMN_MAP = {
    "full_name":              "full_name",
    "mobile":                 "mobile",
    "email":                  "email",
    "gender":                 "gender",
    "father_name":            "father_name",
    "programme_interested":   "programme_interested",
    "department_interested":  "department_interested",
    "category":               "category",
    "lead_source":            "lead_source",
    "hsc_percentage":         "hsc_percentage",
    "school_name":            "school_name",
    "address":                "address",
    "notes":                  "notes",
}
REQUIRED = ["full_name", "mobile", "programme_interested",
            "department_interested", "lead_source"]

SAMPLE_CSV = """full_name,mobile,email,gender,programme_interested,department_interested,lead_source,hsc_percentage,school_name
Arun Kumar,9876543210,arun@email.com,Male,B.E.,CSE,Walk-in,87.5,Sri Venkateswara Hr Sec School
Priya Devi,9876543211,,Female,B.E.,ECE,Phone,91.0,Government Girls Hr Sec School
Ramesh S,9876543212,,Male,B.Tech,AIDS,Social Media,78.0,
"""

def validate_row(row, idx):
    errors = []
    for col in REQUIRED:
        if col not in row or pd.isna(row[col]) or str(row[col]).strip() == "":
            errors.append(f"Row {idx+2}: '{col}' is required.")
    mob = str(row.get("mobile", "")).strip()
    if mob and (not mob.isdigit() or len(mob) != 10):
        errors.append(f"Row {idx+2}: Mobile '{mob}' must be 10 digits.")
    prog = str(row.get("programme_interested", "")).strip()
    if prog and prog not in PROGRAMMES:
        errors.append(f"Row {idx+2}: Programme '{prog}' not in allowed list.")
    dept = str(row.get("department_interested", "")).strip()
    if dept and dept not in DEPARTMENTS:
        errors.append(f"Row {idx+2}: Department '{dept}' not in allowed list.")
    src = str(row.get("lead_source", "")).strip()
    if src and src not in LEAD_SOURCES:
        errors.append(f"Row {idx+2}: Lead source '{src}' not in allowed list.")
    return errors


def show():
    sb = get_supabase()

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>📥 Bulk Import Leads</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Upload a CSV file to import multiple leads at once into Supabase.
        </p>
    </div>""", unsafe_allow_html=True)

    # ── Download sample ───────────────────────────────────────
    st.download_button(
        label="⬇️ Download Sample CSV Template",
        data=SAMPLE_CSV,
        file_name="dce_leads_template.csv",
        mime="text/csv"
    )

    st.markdown("**Required columns:** `full_name`, `mobile`, `programme_interested`, "
                "`department_interested`, `lead_source`")
    st.markdown("**Allowed values** → Programme: " + ", ".join(PROGRAMMES) +
                " | Department: " + ", ".join(DEPARTMENTS) +
                " | Lead Source: " + ", ".join(LEAD_SOURCES))

    st.divider()

    # ── File upload ───────────────────────────────────────────
    uploaded = st.file_uploader("Upload CSV file", type=["csv"])

    if not uploaded:
        st.info("Upload a CSV file to begin. Use the sample template above as a guide.")
        return

    try:
        df = pd.read_csv(uploaded)
    except Exception as e:
        st.error(f"Could not read CSV: {e}")
        return

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    st.subheader(f"📋 Preview — {len(df)} row(s) detected")
    st.dataframe(df.head(20), use_container_width=True, hide_index=True)

    # ── Validate ──────────────────────────────────────────────
    all_errors = []
    for i, row in df.iterrows():
        all_errors.extend(validate_row(row, i))

    if all_errors:
        st.error(f"❌ {len(all_errors)} validation error(s) found — fix and re-upload:")
        for err in all_errors[:20]:
            st.markdown(f"- {err}")
        if len(all_errors) > 20:
            st.caption(f"… and {len(all_errors)-20} more errors.")
        return

    st.success(f"✅ All {len(df)} rows passed validation.")

    # ── Duplicate check (mobile) ──────────────────────────────
    mobiles = df["mobile"].astype(str).str.strip().tolist()
    try:
        existing = sb.table("applicants").select("mobile")\
            .in_("mobile", mobiles).execute().data or []
        existing_mobs = {r["mobile"] for r in existing}
        dupes = [m for m in mobiles if m in existing_mobs]
        if dupes:
            st.warning(f"⚠️ {len(dupes)} mobile number(s) already exist in DB and will be skipped: "
                       + ", ".join(dupes[:10]))
            df = df[~df["mobile"].astype(str).str.strip().isin(existing_mobs)]
            st.info(f"{len(df)} new rows will be imported.")
    except Exception as e:
        st.warning(f"Could not check duplicates: {e}")

    if df.empty:
        st.warning("All rows are duplicates — nothing to import.")
        return

    # ── Import button ─────────────────────────────────────────
    if st.button(f"🚀 Import {len(df)} Lead(s) into Supabase", type="primary"):
        records = []
        for _, row in df.iterrows():
            rec = {"status": "New Lead"}
            for csv_col, db_col in COLUMN_MAP.items():
                if csv_col in row and not pd.isna(row[csv_col]):
                    val = str(row[csv_col]).strip()
                    if val:
                        if csv_col == "hsc_percentage":
                            try:
                                rec[db_col] = float(val)
                            except:
                                pass
                        else:
                            rec[db_col] = val
            records.append(rec)

        # Batch insert in chunks of 100
        success, failed = 0, 0
        bar = st.progress(0, text="Importing…")
        chunk_size = 100
        for i in range(0, len(records), chunk_size):
            chunk = records[i:i+chunk_size]
            try:
                sb.table("applicants").insert(chunk).execute()
                success += len(chunk)
            except Exception as e:
                failed += len(chunk)
                st.error(f"Chunk {i//chunk_size+1} failed: {e}")
            bar.progress(min((i + chunk_size) / len(records), 1.0),
                         text=f"Imported {success}/{len(records)}…")

        bar.empty()
        if success:
            st.success(f"✅ {success} lead(s) imported successfully!")
            st.balloons()
        if failed:
            st.error(f"❌ {failed} row(s) failed to import.")
