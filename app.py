import csv
import io
import json
import os
import re

import streamlit as st

CONTACTS_FILE = "contacts.json"

st.set_page_config(page_title="Contact List Management System", page_icon="📇")
st.title("📇 CONTACT LIST MANAGEMENT SYSTEM")


def load_contacts():
    if not os.path.exists(CONTACTS_FILE):
        return {}
    try:
        with open(CONTACTS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
        return {}


def save_contacts(contacts):
    try:
        with open(CONTACTS_FILE, "w", encoding="utf-8") as file:
            json.dump(contacts, file, indent=4)
    except IOError as e:
        st.error(f"Error saving contacts to file: {e}")


def validate_mobile(mobile):
    return bool(re.match(r"^\d{10}$", mobile.strip()))


def validate_email(email):
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email.strip()))


contacts = load_contacts()

tab_add, tab_view, tab_search, tab_update, tab_delete, tab_csv = st.tabs(
    ["➕ Add", "📋 View", "🔍 Search", "✏️ Update", "🗑️ Delete", "📁 CSV"]
)

# ---------------- ADD ----------------
with tab_add:
    st.subheader("Add New Contact")
    with st.form("add_form"):
        name = st.text_input("Name")
        mobile = st.text_input("10-digit Mobile Number")
        email = st.text_input("Email Address")
        address = st.text_input("Address")
        organization = st.text_input("Organization")
        submitted = st.form_submit_button("Add Contact", type="primary")

    if submitted:
        name = name.strip()
        if not name:
            st.error("Name cannot be empty.")
        elif name in contacts:
            st.error(f"Contact with name '{name}' already exists.")
        elif not validate_mobile(mobile):
            st.error("Invalid mobile number! Please enter exactly 10 digits.")
        elif not validate_email(email):
            st.error("Invalid email format! (e.g., user@domain.com)")
        else:
            contacts[name] = {
                "Mobile": mobile.strip(),
                "Email": email.strip(),
                "Address": address.strip(),
                "Organization": organization.strip(),
            }
            save_contacts(contacts)
            st.success(f"Contact '{name}' added successfully!")

# ---------------- VIEW ----------------
with tab_view:
    st.subheader("All Contacts")
    if not contacts:
        st.info("No contacts found.")
    else:
        rows = [
            {
                "Name": n,
                "Mobile": i.get("Mobile", ""),
                "Email": i.get("Email", ""),
                "Address": i.get("Address", ""),
                "Organization": i.get("Organization", ""),
            }
            for n, i in sorted(contacts.items())
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)
        st.caption(f"Total contacts: {len(rows)}")

# ---------------- SEARCH ----------------
with tab_search:
    st.subheader("Search Contact")
    query = st.text_input("Enter Name or Mobile Number to search").strip().lower()
    if query:
        matches = [
            (n, i)
            for n, i in contacts.items()
            if query in n.lower() or query in i.get("Mobile", "")
        ]
        if not matches:
            st.warning("No matching contact found.")
        for n, i in matches:
            st.markdown(
                f"**Name:** {n}  \n"
                f"**Mobile:** {i.get('Mobile', 'N/A')}  \n"
                f"**Email:** {i.get('Email', 'N/A')}  \n"
                f"**Address:** {i.get('Address', 'N/A')}  \n"
                f"**Organization:** {i.get('Organization', 'N/A')}"
            )
            st.divider()

# ---------------- UPDATE ----------------
with tab_update:
    st.subheader("Update Contact")
    if not contacts:
        st.info("No contacts to update.")
    else:
        selected = st.selectbox("Select contact", sorted(contacts), key="upd_select")
        info = contacts[selected]
        with st.form("update_form"):
            new_mobile = st.text_input("Mobile", value=info.get("Mobile", ""), key=f"um_{selected}")
            new_email = st.text_input("Email", value=info.get("Email", ""), key=f"ue_{selected}")
            new_address = st.text_input("Address", value=info.get("Address", ""), key=f"ua_{selected}")
            new_org = st.text_input("Organization", value=info.get("Organization", ""), key=f"uo_{selected}")
            update_clicked = st.form_submit_button("Update Contact", type="primary")

        if update_clicked:
            if not validate_mobile(new_mobile):
                st.error("Invalid mobile number! Please enter exactly 10 digits.")
            elif not validate_email(new_email):
                st.error("Invalid email format!")
            else:
                contacts[selected] = {
                    "Mobile": new_mobile.strip(),
                    "Email": new_email.strip(),
                    "Address": new_address.strip(),
                    "Organization": new_org.strip(),
                }
                save_contacts(contacts)
                st.success(f"Contact '{selected}' updated successfully!")

# ---------------- DELETE ----------------
with tab_delete:
    st.subheader("Delete Contact")
    if not contacts:
        st.info("No contacts to delete.")
    else:
        to_delete = st.selectbox("Select contact", sorted(contacts), key="del_select")
        confirm = st.checkbox(f"Yes, I want to delete '{to_delete}'")
        if st.button("Delete Contact"):
            if not confirm:
                st.warning("Please tick the confirmation box first.")
            elif to_delete not in contacts:
                st.error("Contact not found.")
            else:
                del contacts[to_delete]
                save_contacts(contacts)
                st.success(f"Contact '{to_delete}' deleted successfully!")

# ---------------- CSV ----------------
with tab_csv:
    st.subheader("Export Contacts to CSV")
    if not contacts:
        st.info("No contacts available to export.")
    else:
        buffer = io.StringIO()
        writer = csv.DictWriter(
            buffer, fieldnames=["Name", "Mobile", "Email", "Address", "Organization"]
        )
        writer.writeheader()
        for n, i in sorted(contacts.items()):
            writer.writerow(
                {
                    "Name": n,
                    "Mobile": i.get("Mobile", ""),
                    "Email": i.get("Email", ""),
                    "Address": i.get("Address", ""),
                    "Organization": i.get("Organization", ""),
                }
            )
        st.download_button(
            "Download contacts.csv",
            data=buffer.getvalue(),
            file_name="contacts_export.csv",
            mime="text/csv",
        )

    st.divider()
    st.subheader("Import Contacts from CSV")
    uploaded = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded is not None and st.button("Import Contacts"):
        try:
            text = uploaded.getvalue().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text))
            imported, skipped = 0, 0
            for row in reader:
                n = (row.get("Name") or "").strip()
                m = (row.get("Mobile") or "").strip()
                e = (row.get("Email") or "").strip()
                a = (row.get("Address") or "").strip()
                o = (row.get("Organization") or "").strip()
                if not n or not validate_mobile(m):
                    skipped += 1
                    continue
                contacts[n] = {
                    "Mobile": m,
                    "Email": e if validate_email(e) else "N/A",
                    "Address": a if a else "N/A",
                    "Organization": o if o else "N/A",
                }
                imported += 1
            if imported:
                save_contacts(contacts)
                st.success(f"Imported {imported} contact(s).")
            if skipped:
                st.warning(f"Skipped {skipped} row(s) due to missing name or invalid mobile.")
            if not imported and not skipped:
                st.info("The file had no rows.")
        except Exception as err:
            st.error(f"Error reading CSV file: {err}")