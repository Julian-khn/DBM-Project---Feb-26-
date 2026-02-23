from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from repositories.carsharing_repo import CarSharingRepository

@dataclass
class Txn2Result:
    maintenance_rows_affected: int
    vehicle_status_after: Optional[Dict[str, Any]]

@dataclass
class Txn3Result:
    deleted_rows: int

class TransactionsService:
    def __init__(self, repo: CarSharingRepository):
        self._repo = repo

    def run_txn2_close_maintenance_ticket(self, vehicle_id: int, ticket_no: int, closed_at: str) -> Txn2Result:
        affected = self._repo.close_maintenance_ticket(vehicle_id, ticket_no, closed_at)
        status_after = self._repo.get_vehicle_status(vehicle_id)
        return Txn2Result(maintenance_rows_affected=affected, vehicle_status_after=status_after)

    def run_txn3_delete_reservation(self, customer_id: int, vehicle_id: int, start_time: str, status: str) -> Txn3Result:
        deleted = self._repo.delete_reservation(customer_id, vehicle_id, start_time, status)
        return Txn3Result(deleted_rows=deleted)
