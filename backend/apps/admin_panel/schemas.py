"""
Schemas for the admin panel API
"""
from ninja import Schema
from typing import Optional


class AdminDashboardStatsSchema(Schema):
    total_users: int
    total_workers: int
    active_jobs: int
    verified_users: int


class WorkerApprovalSchema(Schema):
    approved: bool
    notes: Optional[str] = None