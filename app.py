from __future__ import annotations
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

from config import get_config
from db import Database, DbSettings
from repositories.carsharing_repo import CarSharingRepository
from services.transactions_service import TransactionsService

def create_app() -> Flask:
    cfg = get_config()
    app = Flask(__name__)
    app.secret_key = cfg.flask_secret_key

    db = Database(DbSettings(
        host=cfg.db_host,
        port=cfg.db_port,
        user=cfg.db_user,
        password=cfg.db_password,
        database=cfg.db_name
    ))

    repo = CarSharingRepository(db)
    service = TransactionsService(repo)

    @app.get("/")
    def index():
        zone_type = request.args.get("zone_type", "SERVICE_AREA")
        try:
            latest = repo.select_latest_locations_by_zone_type(zone_type)
        except Exception as e:
            latest = []
            flash(f"DB error while reading view: {e}", "error")
        return render_template("index.html", zone_type=zone_type, latest=latest)

    @app.post("/txn1")
    def txn1():
        zone_type = request.form.get("zone_type", "SERVICE_AREA")
        customer_id = int(request.form["customer_id"])
        vehicle_id = int(request.form["vehicle_id"])
        start_time = request.form["start_time"]
        end_time = request.form.get("end_time") or None
        status = request.form.get("status", "confirmed")
        placed_time = request.form["placed_time"]
        channel = request.form.get("channel", "app")
        promo_code = request.form.get("promo_code") or None
        assigned_at = request.form.get("assigned_at") or None
        pickup_condition = request.form.get("pickup_condition") or None
        pickup_odometer = request.form.get("pickup_odometer") or None
        pickup_odometer = int(pickup_odometer) if pickup_odometer not in (None, "") else None

        try:
            # Txn 1 in ONE transaction: SELECT from VIEW + INSERT Reservation + COMMIT
            with db.connection() as conn:
                cur = conn.cursor(dictionary=True)
                cur.execute(
                    """SELECT * FROM v_vehicle_latest_location
                         WHERE zone_type=%s
                         ORDER BY vehicle_id""",
                    (zone_type,)
                )
                latest = cur.fetchall()

                cur2 = conn.cursor()
                cur2.execute(
                    """INSERT INTO Reservation (
                          customer_id, vehicle_id, start_time, end_time, status,
                          placed_time, channel, promo_code, assigned_at, pickup_condition, pickup_odometer
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (customer_id, vehicle_id, start_time, end_time, status,
                     placed_time, channel, promo_code, assigned_at, pickup_condition, pickup_odometer)
                )
                new_id = cur2.lastrowid
                conn.commit()

            flash(f"Txn1 OK: inserted Reservation (reservation_id={new_id}).", "success")
            return render_template("index.html", zone_type=zone_type, latest=latest)

        except Exception as e:
            flash(f"Txn1 failed (rolled back): {e}", "error")
            return redirect(url_for("index", zone_type=zone_type))

    @app.post("/txn2")
    def txn2():
        vehicle_id = int(request.form["vehicle_id"])
        ticket_no = int(request.form["ticket_no"])
        closed_at = request.form.get("closed_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            result = service.run_txn2_close_maintenance_ticket(vehicle_id, ticket_no, closed_at)
            flash(
                f"Txn2 OK: updated MaintenanceTicket rows={result.maintenance_rows_affected}. "
                f"Vehicle status now: {result.vehicle_status_after}",
                "success"
            )
        except Exception as e:
            flash(f"Txn2 failed: {e}", "error")

        return redirect(url_for("index"))

    @app.post("/txn3")
    def txn3():
        customer_id = int(request.form["customer_id"])
        vehicle_id = int(request.form["vehicle_id"])
        start_time = request.form["start_time"]
        status = request.form.get("status", "confirmed")

        try:
            result = service.run_txn3_delete_reservation(customer_id, vehicle_id, start_time, status)
            flash(f"Txn3 OK: deleted rows={result.deleted_rows}.", "success")
        except Exception as e:
            flash(f"Txn3 failed: {e}", "error")

        return redirect(url_for("index"))

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)