from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class ReservationInput:
    customer_id: int
    vehicle_id: int
    start_time: str
    end_time: Optional[str]
    status: str
    placed_time: str
    channel: str
    promo_code: Optional[str]
    assigned_at: Optional[str]
    pickup_condition: Optional[str]
    pickup_odometer: Optional[int]

class CarSharingRepository:
    def __init__(self, database):
        self._db = database

    def select_latest_locations_by_zone_type(self, zone_type: str) -> List[Dict[str, Any]]:
        sql = """SELECT * FROM v_vehicle_latest_location
                 WHERE zone_type = %s
                 ORDER BY vehicle_id;"""
        with self._db.connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (zone_type,))
            rows = cur.fetchall()
            conn.commit()
            return rows

    def close_maintenance_ticket(self, vehicle_id: int, ticket_no: int, closed_at: str, status: str = "closed") -> int:
        sql = """UPDATE MaintenanceTicket
                 SET status = %s, closed_at = %s
                 WHERE vehicle_id = %s AND ticket_no = %s;"""
        with self._db.connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (status, closed_at, vehicle_id, ticket_no))
            affected = cur.rowcount
            conn.commit()
            return affected

    def get_vehicle_status(self, vehicle_id: int):
        sql = """SELECT vehicle_id, status FROM Vehicle WHERE vehicle_id = %s;"""
        with self._db.connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (vehicle_id,))
            row = cur.fetchone()
            conn.commit()
            return row

    def delete_reservation(self, customer_id: int, vehicle_id: int, start_time: str, status: str) -> int:
        sql = """DELETE FROM Reservation
                 WHERE customer_id=%s AND vehicle_id=%s AND start_time=%s AND status=%s;"""
        with self._db.connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (customer_id, vehicle_id, start_time, status))
            affected = cur.rowcount
            conn.commit()
            return affected
