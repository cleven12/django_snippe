"""Input validation utilities for Snippe payments, payouts, and sessions (API 2026-01-25)."""

from typing import List, Optional, Sequence, Tuple

from django.core.exceptions import ValidationError

from .conf import get_min_payment_amount, get_min_payout_amount

SUPPORTED_CURRENCIES = {"TZS", "KES", "UGX"}

SUPPORTED_PAYMENT_TYPES = {"mobile", "card", "dynamic-qr"}

SUPPORTED_PAYOUT_CHANNELS = {"mobile", "bank"}

SUPPORTED_SESSION_METHODS = {"mobile_money", "card", "qr", "mobile", "dynamic-qr"}

SUPPORTED_BANK_CODES = {
    "ABSA",
    "ACCESS",
    "AKIBA",
    "AMANA",
    "AZANIA",
    "BOA",
    "BARODA",
    "BANCABC",
    "CITIBANK",
    "CRDB",
    "DCB",
    "DTB",
    "ECOBANK",
    "EQUITY",
    "EXIM",
    "FINCA",
    "GTBANK",
    "HABIB",
    "ICBANK",
    "IMBANK",
    "KCB",
    "LETSHEGO",
    "MKOMBOZI",
    "MWALIMU",
    "MWANGA",
    "NBC",
    "NCBA",
    "NMB",
    "PBZ",
    "SELCOM",
    "STANBIC",
    "SCB",
    "TCB",
    "TPB",
    "UBA",
    "UCHUMI",
    "YETU",
