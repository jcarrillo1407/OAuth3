import random
from datetime import timedelta

from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

from OAuth3.models import MFAChallenge


def generate_6_digit_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def create_mfa_challenge(user, purpose="LOGIN"):
    code = generate_6_digit_code()

    MFAChallenge.objects.filter(
        user=user,
        purpose=purpose,
        consumed_at__isnull=True,
    ).update(consumed_at=timezone.now())

    challenge = MFAChallenge.objects.create(
        user=user,
        code_hash=make_password(code),
        purpose=purpose,
        expires_at=timezone.now() + timedelta(minutes=5),
    )

    return challenge, code


def verify_mfa_code(challenge: MFAChallenge, code: str) -> bool:
    if challenge.consumed_at is not None:
        return False

    if timezone.now() > challenge.expires_at:
        return False

    if challenge.attempts >= challenge.max_attempts:
        return False

    if not check_password(code, challenge.code_hash):
        challenge.attempts += 1
        challenge.save(update_fields=["attempts"])
        return False

    challenge.consumed_at = timezone.now()
    challenge.save(update_fields=["consumed_at"])
    return True