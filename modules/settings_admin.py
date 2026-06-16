"""
Settings & Admin — 100% Dynamic Control Panel
Manages: General Settings, Lookup Values, Fee Structure,
         Seat Intake, Document Types, Hostel Blocks
All data lives in Supabase. Cache cleared after every change.
"""

import streamlit as st
from db import get_supabase, get_lookup, clear_config_cache
from config import MAROON, GOLD, CREAM

# ── helpers ─────────────────────────────────────────────────────────────────

def _sb():
    return get_supabase()


def _success(msg: str):
    clear_config_cache()
    st.success(msg)
    st.rerun()


def _error(msg: str):
    st.error(msg)


# ════════════════════════════════════════════════════════════════════════════
#  TAB 1 — GENERAL SETTINGS
# ════════════════════════════════════════════════════════════════════════════

def tab_general():
    st.subheader("General Settings")

    rows = (_sb().table("settings")
            .select("*").eq("category", "general").eq("is_active", True)
            .order("key").execute().data)

    if not rows:
        st.info("No general settings found. Add one below.")

    for row in rows:
        col1, col2, col3 = st.columns([3, 4, 1])
        with col1:
            st.text(row["key"])
        with col2:
            new_val = st.text_input("", value=row["value"],
                                    key=f"gen_val_{row['id']}",
                                    label_visibility="collapsed")
        with col3:
            if st.button("💾", key=f"gen_save_{row['id']}"):
                _sb().table("settings").update({"value": new_val}).eq("id", row["id"]).execute()
                _success("Setting updated.")
            if st.button("🗑", key=f"gen_del_{row['id']}"):
                _sb().table("settings").update({"is_active": False}).eq("id", row["id"]).execute()
                _success("Setting removed.")

    st.divider()
    st.markdown("**Add New Setting**")
    c1, c2, c3 = st.columns([3, 4, 1])
    with c1:
        new_key = st.text_input("Key", key="gen_new_key")
    with c2:
        new_val2 = st.text_input("Value", key="gen_new_val")
    with c3:
        st.write("")
        st.write("")
        if st.button("Add", key="gen_add"):
            if new_key.strip():
                _sb().table("settings").insert({
                    "category": "general",
                    "key": new_key.strip(),
                    "value": new_val2.strip(),
                    "is_active": True
                }).execute()
                _success("Setting added.")
            else:
                _error("Key cannot be empty.")


# ════════════════════════════════════════════════════════════════════════════
#  TAB 2 — LOOKUP VALUES
# ════════════════════════════════════════════════════════════════════════════

def tab_lookups():
    st.subheader("Lookup Values")
    st.caption("Manages all dropdowns: departments, programmes, categories, lead sources, genders, blood groups, payment modes, scholarship types, etc.")

    all_rows = (_sb().table("lookup_values")
                .select("*").eq("is_active", True)
                .order("type").order("sort_order").execute().data)
    all_types = sorted(set(r["type"] for r in all_rows))

    # add a new type
    with st.expander("➕ Create new lookup type"):
        nt1, nt2 = st.columns(2)
        with nt1:
            new_type_name = st.text_input("Type name (snake_case)", key="new_type_name")
        with nt2:
            new_type_val = st.text_input("First value", key="new_type_val")
        if st.button("Create", key="new_type_btn"):
            if new_type_name.strip() and new_type_val.strip():
                _sb().table("lookup_values").insert({
                    "type": new_type_name.strip().lower().replace(" ", "_"),
                    "value": new_type_val.strip(),
                    "sort_order": 1,
                    "is_active": True
                }).execute()
                _success("New lookup type created.")
            else:
                _error("Both type name and first value are required.")

    st.divider()

    if not all_types:
        st.info("No lookup types yet. Create one above.")
        return

    selected_type = st.selectbox("Lookup type", all_types, key="sel_lookup_type")
    type_rows = [r for r in all_rows if r["type"] == selected_type]

    # header row
    hc1, hc2, hc3, hc4 = st.columns([5, 2, 1, 1])
    hc1.markdown("**Value**")
    hc2.markdown("**Order**")

    for row in type_rows:
        c1, c2, c3, c4 = st.columns([5, 2, 1, 1])
        with c1:
            new_v = st.text_input("", value=row["value"],
                                   key=f"lv_val_{row['id']}",
                                   label_visibility="collapsed")
        with c2:
            new_so = st.number_input("", value=row["sort_order"], min_value=1,
                                      key=f"lv_so_{row['id']}",
                                      label_visibility="collapsed")
        with c3:
            if st.button("💾", key=f"lv_save_{row['id']}"):
                _sb().table("lookup_values").update({
                    "value": new_v.strip(),
                    "sort_order": int(new_so)
                }).eq("id", row["id"]).execute()
                _success("Value updated.")
        with c4:
            if st.button("🗑", key=f"lv_del_{row['id']}"):
                _sb().table("lookup_values").update({"is_active": False}).eq("id", row["id"]).execute()
                _success("Value removed.")

    st.divider()
    st.markdown(f"**Add value to `{selected_type}`**")
    ca, cb, cc = st.columns([5, 2, 1])
    with ca:
        add_val = st.text_input("Value", key="lv_add_val")
    with cb:
        add_so = st.number_input("Order", value=len(type_rows) + 1, min_value=1, key="lv_add_so")
    with cc:
        st.write("")
        st.write("")
        if st.button("Add", key="lv_add_btn"):
            if add_val.strip():
                _sb().table("lookup_values").insert({
                    "type": selected_type,
                    "value": add_val.strip(),
                    "sort_order": int(add_so),
                    "is_active": True
                }).execute()
                _success("Value added.")
            else:
                _error("Value cannot be empty.")


# ════════════════════════════════════════════════════════════════════════════
#  TAB 3 — FEE STRUCTURE
# ════════════════════════════════════════════════════════════════════════════

def tab_fees():
    st.subheader("Fee Structure")
    st.caption("Key stored as `Programme|Department|Component` → Amount (₹)")

    rows = (_sb().table("settings")
            .select("*").eq("category", "fee").eq("is_active", True)
            .order("key").execute().data)

    parsed = []
    for r in rows:
        parts = r["key"].split("|")
        if len(parts) == 3:
            parsed.append({**r, "prog": parts[0], "dept": parts[1], "comp": parts[2]})

    progs = sorted(set(p["prog"] for p in parsed))
    sel_prog = st.selectbox("Filter by Programme", ["All"] + progs, key="fee_filter_prog")
    filtered = parsed if sel_prog == "All" else [p for p in parsed if p["prog"] == sel_prog]

    if filtered:
        hf1, hf2, hf3, hf4, hf5 = st.columns([3, 3, 3, 2, 1])
        hf1.markdown("**Programme**")
        hf2.markdown("**Department**")
        hf3.markdown("**Component**")
        hf4.markdown("**Amount ₹**")

        for row in filtered:
            c1, c2, c3, c4, c5 = st.columns([3, 3, 3, 2, 1])
            c1.text(row["prog"])
            c2.text(row["dept"])
            c3.text(row["comp"])
            with c4:
                new_amt = st.text_input("", value=row["value"],
                                         key=f"fee_amt_{row['id']}",
                                         label_visibility="collapsed")
            with c5:
                if st.button("💾", key=f"fee_save_{row['id']}"):
                    try:
                        float(new_amt)
                        _sb().table("settings").update({"value": new_amt.strip()}).eq("id", row["id"]).execute()
                        _success("Fee updated.")
                    except ValueError:
                        _error("Amount must be a number.")
                if st.button("🗑", key=f"fee_del_{row['id']}"):
                    _sb().table("settings").update({"is_active": False}).eq("id", row["id"]).execute()
                    _success("Fee entry removed.")
    else:
        st.info("No fee entries found.")

    st.divider()
    st.markdown("**Add Fee Entry**")
    progs_all = get_lookup("programme")
    depts_all = get_lookup("department")
    # components fetched from lookup if exist, else default list
    comps_all = get_lookup("fee_component") or ["Tuition", "Hostel", "Transport", "Exam", "Lab", "Library", "Miscellaneous"]

    col1, col2, col3, col4, col5 = st.columns([3, 3, 3, 2, 1])
    with col1:
        fp = st.selectbox("Programme", progs_all, key="fee_new_prog")
    with col2:
        fd = st.selectbox("Department", depts_all, key="fee_new_dept")
    with col3:
        fc = st.selectbox("Component", comps_all, key="fee_new_comp")
    with col4:
        fa = st.text_input("Amount ₹", key="fee_new_amt")
    with col5:
        st.write("")
        st.write("")
        if st.button("Add", key="fee_add_btn"):
            key_str = f"{fp}|{fd}|{fc}"
            try:
                float(fa)
                exists = (_sb().table("settings")
                          .select("id").eq("category", "fee").eq("key", key_str).eq("is_active", True)
                          .execute().data)
                if exists:
                    _error("Entry already exists. Edit it above.")
                else:
                    _sb().table("settings").insert({
                        "category": "fee", "key": key_str,
                        "value": fa.strip(), "is_active": True
                    }).execute()
                    _success("Fee entry added.")
            except ValueError:
                _error("Amount must be a number.")


# ════════════════════════════════════════════════════════════════════════════
#  TAB 4 — SEAT INTAKE
# ════════════════════════════════════════════════════════════════════════════

def tab_seats():
    st.subheader("Seat Intake")
    st.caption("Approved seat capacity per department.")

    rows = (_sb().table("settings")
            .select("*").eq("category", "seat_intake").eq("is_active", True)
            .order("key").execute().data)

    for row in rows:
        c1, c2, c3 = st.columns([5, 3, 1])
        with c1:
            st.text(row["key"])
        with c2:
            cap_val = int(row["value"]) if str(row["value"]).isdigit() else 60
            new_cap = st.number_input("", value=cap_val, min_value=0,
                                       key=f"seat_{row['id']}",
                                       label_visibility="collapsed")
        with c3:
            if st.button("💾", key=f"seat_save_{row['id']}"):
                _sb().table("settings").update({"value": str(new_cap)}).eq("id", row["id"]).execute()
                _success("Seat intake updated.")
            if st.button("🗑", key=f"seat_del_{row['id']}"):
                _sb().table("settings").update({"is_active": False}).eq("id", row["id"]).execute()
                _success("Entry removed.")

    st.divider()
    st.markdown("**Add Department**")
    depts_all = get_lookup("department")
    existing_depts = {r["key"] for r in rows}
    available = [d for d in depts_all if d not in existing_depts]

    if available:
        sa1, sa2, sa3 = st.columns([5, 3, 1])
        with sa1:
            new_dept = st.selectbox("Department", available, key="seat_new_dept")
        with sa2:
            new_cap2 = st.number_input("Seats", value=60, min_value=0, key="seat_new_cap")
        with sa3:
            st.write("")
            st.write("")
            if st.button("Add", key="seat_add_btn"):
                _sb().table("settings").insert({
                    "category": "seat_intake", "key": new_dept,
                    "value": str(new_cap2), "is_active": True
                }).execute()
                _success("Seat intake added.")
    else:
        st.info("All departments already have seat intake defined.")


# ════════════════════════════════════════════════════════════════════════════
#  TAB 5 — DOCUMENT TYPES
# ════════════════════════════════════════════════════════════════════════════

def tab_documents():
    st.subheader("Document Types")
    st.caption("Required / optional documents for applicant verification.")

    rows = (_sb().table("document_types")
            .select("*").eq("is_active", True)
            .order("sort_order").execute().data)

    for row in rows:
        c1, c2, c3, c4 = st.columns([5, 2, 1, 1])
        with c1:
            new_name = st.text_input("", value=row["name"],
                                      key=f"doc_name_{row['id']}",
                                      label_visibility="collapsed")
        with c2:
            new_req = st.checkbox("Required", value=row.get("is_required", False),
                                   key=f"doc_req_{row['id']}")
        with c3:
            if st.button("💾", key=f"doc_save_{row['id']}"):
                _sb().table("document_types").update({
                    "name": new_name.strip(), "is_required": new_req
                }).eq("id", row["id"]).execute()
                _success("Document type updated.")
        with c4:
            if st.button("🗑", key=f"doc_del_{row['id']}"):
                _sb().table("document_types").update({"is_active": False}).eq("id", row["id"]).execute()
                _success("Document type removed.")

    st.divider()
    st.markdown("**Add Document Type**")
    da1, da2, da3 = st.columns([5, 2, 1])
    with da1:
        add_doc_name = st.text_input("Document name", key="doc_add_name")
    with da2:
        add_doc_req = st.checkbox("Required", key="doc_add_req")
    with da3:
        st.write("")
        st.write("")
        if st.button("Add", key="doc_add_btn"):
            if add_doc_name.strip():
                next_order = max((r["sort_order"] for r in rows), default=0) + 1
                _sb().table("document_types").insert({
                    "name": add_doc_name.strip(),
                    "is_required": add_doc_req,
                    "sort_order": next_order,
                    "is_active": True
                }).execute()
                _success("Document type added.")
            else:
                _error("Document name cannot be empty.")


# ════════════════════════════════════════════════════════════════════════════
#  TAB 6 — HOSTEL BLOCKS
# ════════════════════════════════════════════════════════════════════════════

def tab_hostel():
    st.subheader("Hostel Blocks")
    st.caption("Key: `Block Name|Gender` → Capacity")

    rows = (_sb().table("settings")
            .select("*").eq("category", "hostel_block").eq("is_active", True)
            .order("key").execute().data)

    for row in rows:
        parts = row["key"].split("|")
        block_name = parts[0] if len(parts) > 0 else row["key"]
        gender = parts[1] if len(parts) > 1 else "Male"
        gender_opts = ["Male", "Female", "Mixed"]
        gender_idx = gender_opts.index(gender) if gender in gender_opts else 0

        c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 1, 1])
        with c1:
            new_block = st.text_input("", value=block_name,
                                       key=f"hb_name_{row['id']}",
                                       label_visibility="collapsed")
        with c2:
            new_gender = st.selectbox("", gender_opts, index=gender_idx,
                                       key=f"hb_gender_{row['id']}",
                                       label_visibility="collapsed")
        with c3:
            cap_val = int(row["value"]) if str(row["value"]).isdigit() else 0
            new_cap = st.number_input("", value=cap_val, min_value=0,
                                       key=f"hb_cap_{row['id']}",
                                       label_visibility="collapsed")
        with c4:
            if st.button("💾", key=f"hb_save_{row['id']}"):
                _sb().table("settings").update({
                    "key": f"{new_block.strip()}|{new_gender}",
                    "value": str(new_cap)
                }).eq("id", row["id"]).execute()
                _success("Hostel block updated.")
        with c5:
            if st.button("🗑", key=f"hb_del_{row['id']}"):
                _sb().table("settings").update({"is_active": False}).eq("id", row["id"]).execute()
                _success("Hostel block removed.")

    st.divider()
    st.markdown("**Add Hostel Block**")
    hb1, hb2, hb3, hb4 = st.columns([3, 2, 2, 1])
    with hb1:
        hb_name = st.text_input("Block Name", key="hb_add_name")
    with hb2:
        hb_gender = st.selectbox("Gender", ["Male", "Female", "Mixed"], key="hb_add_gender")
    with hb3:
        hb_cap = st.number_input("Capacity", value=100, min_value=0, key="hb_add_cap")
    with hb4:
        st.write("")
        st.write("")
        if st.button("Add", key="hb_add_btn"):
            if hb_name.strip():
                key_str = f"{hb_name.strip()}|{hb_gender}"
                exists = (_sb().table("settings")
                          .select("id").eq("category", "hostel_block").eq("key", key_str).eq("is_active", True)
                          .execute().data)
                if exists:
                    _error(f"Block '{key_str}' already exists.")
                else:
                    _sb().table("settings").insert({
                        "category": "hostel_block", "key": key_str,
                        "value": str(hb_cap), "is_active": True
                    }).execute()
                    _success("Hostel block added.")
            else:
                _error("Block name cannot be empty.")


# ════════════════════════════════════════════════════════════════════════════
#  TAB 7 — MESSAGE TEMPLATES
# ════════════════════════════════════════════════════════════════════════════

def tab_message_templates():
    st.subheader("Message Templates")
    st.caption("Manage SMS and Email templates used in Blast / Campaigns modules.")

    import json

    msg_tab1, msg_tab2 = st.tabs(["💬 SMS Templates", "📧 Email Templates"])

    # ── SMS ───────────────────────────────────────────────────
    with msg_tab1:
        sms_rows = (_sb().table("settings")
                    .select("*").eq("category", "sms_template").eq("is_active", True)
                    .order("key").execute().data)

        for row in sms_rows:
            st.markdown(f"**{row['key']}**")
            c1, c2 = st.columns([8, 1])
            with c1:
                new_body = st.text_area("", value=row["value"],
                                         key=f"sms_body_{row['id']}",
                                         height=80,
                                         label_visibility="collapsed",
                                         help="Use {name}, {programme}, {dept}, {date}")
            with c2:
                st.write("")
                if st.button("💾", key=f"sms_save_{row['id']}"):
                    _sb().table("settings").update({"value": new_body}).eq("id", row["id"]).execute()
                    _success("SMS template updated.")
                if st.button("🗑", key=f"sms_del_{row['id']}"):
                    _sb().table("settings").update({"is_active": False}).eq("id", row["id"]).execute()
                    _success("SMS template removed.")

        st.divider()
        st.markdown("**Add SMS Template**")
        sa1, sa2 = st.columns([3, 1])
        with sa1:
            sms_new_name = st.text_input("Template name", key="sms_new_name")
        sms_new_body = st.text_area("Message body", key="sms_new_body", height=80,
                                     help="Use {name}, {programme}, {dept}, {date}")
        if st.button("Add SMS Template", key="sms_add_btn"):
            if sms_new_name.strip():
                _sb().table("settings").insert({
                    "category": "sms_template",
                    "key": sms_new_name.strip(),
                    "value": sms_new_body.strip(),
                    "is_active": True
                }).execute()
                _success("SMS template added.")
            else:
                _error("Template name cannot be empty.")

    # ── Email ─────────────────────────────────────────────────
    with msg_tab2:
        email_rows = (_sb().table("settings")
                      .select("*").eq("category", "email_template").eq("is_active", True)
                      .order("key").execute().data)

        for row in email_rows:
            st.markdown(f"**{row['key']}**")
            try:
                tpl = json.loads(row["value"])
            except Exception:
                tpl = {"subject": "", "body": row["value"]}

            ec1, ec2 = st.columns([8, 1])
            with ec1:
                new_subj = st.text_input("Subject", value=tpl.get("subject", ""),
                                          key=f"email_subj_{row['id']}")
                new_body = st.text_area("Body", value=tpl.get("body", ""),
                                         key=f"email_body_{row['id']}", height=120,
                                         help="Use {name}, {programme}, {date}")
            with ec2:
                st.write("")
                st.write("")
                st.write("")
                if st.button("💾", key=f"email_save_{row['id']}"):
                    payload = json.dumps({"subject": new_subj, "body": new_body})
                    _sb().table("settings").update({"value": payload}).eq("id", row["id"]).execute()
                    _success("Email template updated.")
                if st.button("🗑", key=f"email_del_{row['id']}"):
                    _sb().table("settings").update({"is_active": False}).eq("id", row["id"]).execute()
                    _success("Email template removed.")
            st.divider()

        st.markdown("**Add Email Template**")
        email_new_name = st.text_input("Template name", key="email_new_name")
        email_new_subj = st.text_input("Subject", key="email_new_subj")
        email_new_body = st.text_area("Body", key="email_new_body", height=120,
                                       help="Use {name}, {programme}, {date}")
        if st.button("Add Email Template", key="email_add_btn"):
            if email_new_name.strip():
                payload = json.dumps({"subject": email_new_subj.strip(),
                                      "body": email_new_body.strip()})
                _sb().table("settings").insert({
                    "category": "email_template",
                    "key": email_new_name.strip(),
                    "value": payload,
                    "is_active": True
                }).execute()
                _success("Email template added.")
            else:
                _error("Template name cannot be empty.")


# ════════════════════════════════════════════════════════════════════════════
#  TAB 8 — USER MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════

def tab_users():
    st.subheader("User Management")
    st.caption("View and manage counselor/admin accounts. To create a new user, they must sign up via Supabase Auth first, then assign their role here.")

    from db import get_lookup as _gl
    ROLES = _gl("user_role") or ["admin", "counselor", "viewer"]

    users = (_sb().table("users")
             .select("id, email, full_name, role, is_active, created_at")
             .order("created_at", desc=True).execute().data)

    if not users:
        st.info("No users found.")
        return

    # ── User table ────────────────────────────────────────────
    for u in users:
        active_icon = "🟢" if u.get("is_active") else "🔴"
        c1, c2, c3, c4, c5 = st.columns([3, 3, 2, 1, 1])
        with c1:
            name_display = u.get("full_name") or ""
            email_display = u.get("email") or ""
            st.markdown(f"{active_icon} **{name_display}**<br><small>{email_display}</small>", unsafe_allow_html=True)
        with c2:
            new_name = st.text_input("", value=u.get("full_name") or "",
                                      key=f"usr_name_{u['id']}",
                                      label_visibility="collapsed")
        with c3:
            current_role = u.get("role", "counselor")
            role_idx = ROLES.index(current_role) if current_role in ROLES else 1
            new_role = st.selectbox("", ROLES, index=role_idx,
                                     key=f"usr_role_{u['id']}",
                                     label_visibility="collapsed")
        with c4:
            if st.button("💾", key=f"usr_save_{u['id']}"):
                _sb().table("users").update({
                    "full_name": new_name.strip(),
                    "role": new_role
                }).eq("id", u["id"]).execute()
                _success("User updated.")
        with c5:
            is_active = u.get("is_active", True)
            label = "🔴" if is_active else "🟢"
            help_txt = "Deactivate" if is_active else "Activate"
            if st.button(label, key=f"usr_toggle_{u['id']}", help=help_txt):
                _sb().table("users").update({"is_active": not is_active}).eq("id", u["id"]).execute()
                _success(f"User {'deactivated' if is_active else 'activated'}.")

    st.divider()
    st.markdown("**Invite New User**")
    st.info(
        "New users sign up at the app login page. "
        "Once they register, they appear here and you can assign their role. "
        "By default all new sign-ups are assigned the `counselor` role."
    )


# ════════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════

def show():
    st.markdown(f"""
        <h2 style='color:{MAROON}; border-bottom: 2px solid {GOLD}; padding-bottom:8px;'>
            ⚙️ Settings & Admin
        </h2>
    """, unsafe_allow_html=True)

    user = st.session_state.get("auth_user", {})
    if user.get("role") != "admin":
        st.warning("⚠️ This section is restricted to admins only.")
        return

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🏫 General",
        "📋 Lookup Values",
        "💰 Fee Structure",
        "🪑 Seat Intake",
        "📄 Document Types",
        "🏨 Hostel Blocks",
        "💬 Message Templates",
        "👥 User Management"
    ])

    with tab1:
        tab_general()
    with tab2:
        tab_lookups()
    with tab3:
        tab_fee_structure()
    with tab4:
        tab_seat_intake()
    with tab5:
        tab_documents()
    with tab6:
        tab_hostel_blocks()
    with tab7:
        tab_templates()
    with tab8:
        tab_users()
