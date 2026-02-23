# CarSharing App — Feature Guide & Demo Script

Step-by-step explanation of what each feature does and how to present it in a demo.

---

## Before the demo

1. **Start the app**
   ```bash
   source .venv/bin/activate
   flask --app app run --debug
   ```
2. Open **http://127.0.0.1:5000**
3. Ensure MySQL is running and `.env` has the correct DB credentials.

---

## Feature 1 — View + Insert Reservation

### What it does (technical)

1. **Read from view**  
   The app runs a single transaction that:
   - **SELECTs** from the view `v_vehicle_latest_location` filtered by **zone_type** (e.g. SERVICE_AREA).
   - **INSERTs** one row into the table **Reservation** with: customer_id, vehicle_id, start_time, end_time, status, placed_time, channel, promo_code, assigned_at, pickup_condition, pickup_odometer.
   - **COMMITs** so both the read and the insert are in one transaction.

2. **Persistence**  
   After the insert, the app:
   - Fetches the new row from `Reservation` by `reservation_id` and shows it under **“Data persistence verified”**.
   - Loads the full **Reservation** table (newest first) and shows it under **“Table: Reservation”** so you can see the new record in the table.

3. **UI**  
   The section **“View output: v_vehicle_latest_location”** shows the view result (filtered by zone type) used in the same transaction.

### How to present it

1. **Say:** “Feature 1 runs one transaction: it reads from the view `v_vehicle_latest_location` and inserts a new reservation.”
2. **Optional:** Click **“Fill demo data”** to fill the form with random values.
3. **Do:** Choose zone type, customer, vehicle (from dropdowns if available), adjust times if needed, then click **“Run Feature 1”**.
4. **Show:**
   - The green **“Data persistence verified”** box: “This is the row we just inserted, re-read from the database.”
   - The **“Table: Reservation”** section: “Here is the full Reservation table; the new row appears at the top (newest first).”
   - The **“View output: v_vehicle_latest_location”** table: “This is the view we used in the same transaction, filtered by zone type.”

---

## Feature 2 — Close Maintenance Ticket (trigger)

### What it does (technical)

1. **UPDATE**  
   The app runs:
   - **UPDATE MaintenanceTicket**  
     SET `status = 'closed'`, `closed_at = <timestamp>`  
     WHERE `vehicle_id = ?` AND `ticket_no = ?`.
   - **COMMIT**.

2. **Trigger**  
   Your database trigger (from Assignment 6) runs when a maintenance ticket is closed and updates the **Vehicle** row (e.g. sets `status` to `'available'`).

3. **Persistence & trigger proof**  
   After the update, the app:
   - Fetches the updated **MaintenanceTicket** row and shows it under **“Feature 2 — Data persistence & trigger verification”**.
   - Fetches the **Vehicle** row and shows the new `status` (e.g. “Trigger executed: vehicle status set to 'available'.”).

### How to present it

1. **Say:** “Feature 2 closes a maintenance ticket. When we do that, a trigger in the database runs and updates the vehicle status.”
2. **Do:**  
   - Either pick an **“Open ticket”** from the dropdown (it fills vehicle_id and ticket_no), or type vehicle_id and ticket_no.  
   - Optionally set **Closed at**, then click **“Run Feature 2”**.
3. **Show:** After the redirect, point to the **“Feature 2 — Data persistence & trigger verification”** section:
   - “This is the updated row in **MaintenanceTicket**: status and closed_at are updated and persisted.”
   - “This is the **Vehicle** status after the update — it changed because of the trigger.”
   - “Here it says: **Trigger executed: vehicle status set to 'available'.** So the trigger ran and the data change is visible.”

---

## Feature 3 — Delete Reservation

### What it does (technical)

1. **Read then DELETE**  
   The app:
   - **SELECTs** the matching row from **Reservation** (customer_id, vehicle_id, start_time, status) to keep a copy for the proof.
   - **DELETEs** from **Reservation** WHERE the same four columns match.
   - **COMMITs**.

2. **Verification**  
   After the delete, the app runs another **SELECT** with the same keys and checks that no row is found, so **“Verified: this record no longer exists in the database”** is correct.

3. **Proof shown**  
   The **“Feature 3 — Deletion verified”** section shows the row that was deleted and the verification message.

### How to present it

1. **Say:** “Feature 3 deletes one reservation by customer_id, vehicle_id, start_time, and status. We then verify the row is gone.”
2. **Do:**  
   - Either use **“Pre-fill from reservation”** and pick a reservation (it fills the form), or enter customer_id, vehicle_id, start_time, and status.  
   - Click **“Run Feature 3”**.
3. **Show:** After the redirect, point to **“Feature 3 — Deletion verified”**:
   - “This is the row we deleted — we read it before the DELETE.”
   - “And here it says: **Verified: this record no longer exists in the database.** So the delete persisted and we confirmed it.”

---

## Suggested demo order (for “all members participate”)

| Step | Who    | Action |
|------|--------|--------|
| 1    | Person A | Start app, open browser, briefly explain the three features. |
| 2    | Person B | Run **Feature 1**, explain the transaction (view + insert), show persistence and full Reservation table. |
| 3    | Person C | Run **Feature 2**, explain UPDATE + trigger, show the verification section. |
| 4    | Person D | Run **Feature 3**, explain DELETE + verification, show the deletion proof. |
| 5    | All    | Optional: show **Feature 1** again and point out the new reservation in the full table; or run **Feature 3** on that row and show it disappear. |

---

## Quick reference — DB objects used

| Feature | Tables/View | Operation |
|---------|-------------|------------|
| 1       | `v_vehicle_latest_location` (view) | SELECT (filtered by zone_type) |
| 1       | `Reservation` | INSERT |
| 2       | `MaintenanceTicket` | UPDATE (status, closed_at) |
| 2       | `Vehicle` (via trigger) | Trigger updates status |
| 3       | `Reservation` | DELETE (by customer_id, vehicle_id, start_time, status) |

---

## Database error message bar

When the database rejects an operation (constraint, trigger, or other error), the app shows a **database error bar** at the top of the page:

- **Label:** “Database error:”
- **Message:** The exact message from the database (e.g. foreign key violation, duplicate entry, trigger error).

Use this in the demo to show that constraints and triggers are enforced and that the error is visible to the user.

---

## If something fails

- **DB connection:** Check MySQL is running and `.env` (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME) is correct.
- **Feature 1:** Ensure the view `v_vehicle_latest_location` exists and the zone_type has rows; ensure `Reservation` table and columns match the insert.
- **Feature 2:** Ensure the maintenance ticket exists and is open; ensure your trigger is created on the database.
- **Feature 3:** Ensure the reservation exists and start_time format matches (use “Pre-fill from reservation” to avoid typing errors).
- **Database errors:** All DB errors (constraints, triggers) are shown in the **Database error** bar at the top; no need for debug mode.
