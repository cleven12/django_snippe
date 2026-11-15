"""Webhook endpoint view for Snippe 2026-01-25 events with HMAC verification and idempotency."""

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional
