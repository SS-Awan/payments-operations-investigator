from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone


CUSTOMER_SEGMENTS = ("smb", "mid_market", "enterprise")
COUNTRIES = ("US", "CA", "GB")

MERCHANT_INDUSTRIES = ("retail", "software", "travel", "food")
REGIONS = ("north_america", "europe")

PAYMENT_METHODS = ("card", "bank_transfer")
PROCESSORS = ("processor_a", "processor_b")

FAILURE_CODES = (
    "network_timeout",
    "insufficient_funds",
    "issuer_declined",
)


def generate_world(
    *,
    seed: int = 42,
    n_customers: int = 20,
    n_merchants: int = 10,
    n_payments: int = 200,
) -> dict[str, list[dict]]:
    rng = random.Random(seed)

    customers = [
        {
            "customer_id": f"C{i:04d}",
            "segment": rng.choice(CUSTOMER_SEGMENTS),
            "country": rng.choice(COUNTRIES),
        }
        for i in range(1, n_customers + 1)
    ]

    merchants = [
        {
            "merchant_id": f"M{i:04d}",
            "industry": rng.choice(MERCHANT_INDUSTRIES),
            "region": rng.choice(REGIONS),
        }
        for i in range(1, n_merchants + 1)
    ]

    payments: list[dict] = []
    payment_attempts: list[dict] = []

    start_time = datetime(2026, 1, 1, tzinfo=timezone.utc)

    for payment_number in range(1, n_payments + 1):
        payment_id = f"P{payment_number:06d}"
        customer = rng.choice(customers)
        merchant = rng.choice(merchants)

        created_at = start_time + timedelta(
            minutes=rng.randint(0, 60 * 24 * 30)
        )

        amount_minor = rng.randint(500, 50_000)
        payment_method = rng.choice(PAYMENT_METHODS)

        final_status = "failed"
        final_attempt_id = None

        for attempt_number in range(1, 4):
            attempt_id = f"A{payment_number:06d}-{attempt_number}"
            processor = rng.choice(PROCESSORS)

            success_probability = 0.88 if payment_method == "card" else 0.93
            succeeded = rng.random() < success_probability

            status = "succeeded" if succeeded else "failed"
            failure_code = None if succeeded else rng.choice(FAILURE_CODES)

            payment_attempts.append(
                {
                    "attempt_id": attempt_id,
                    "payment_id": payment_id,
                    "attempt_number": attempt_number,
                    "attempted_at": created_at
                    + timedelta(minutes=attempt_number - 1),
                    "processor": processor,
                    "status": status,
                    "failure_code": failure_code,
                }
            )

            final_attempt_id = attempt_id

            if succeeded:
                final_status = "succeeded"
                break

            should_retry = rng.random() < 0.65
            if not should_retry:
                break

        payments.append(
            {
                "payment_id": payment_id,
                "customer_id": customer["customer_id"],
                "merchant_id": merchant["merchant_id"],
                "created_at": created_at,
                "amount_minor": amount_minor,
                "currency": "USD",
                "payment_method": payment_method,
                "final_status": final_status,
                "final_attempt_id": final_attempt_id,
            }
        )

    return {
        "customers": customers,
        "merchants": merchants,
        "payments": payments,
        "payment_attempts": payment_attempts,
    }