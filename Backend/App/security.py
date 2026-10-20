"""ECM-style access control: roles map to the access levels they may read.

This mirrors ACL / security-level checks in Documentum and OpenText xECM.
The filter is applied inside the vector query, so restricted chunks are never
retrieved and can never leak into an LLM prompt.
"""

ACCESS_LEVELS = ("public", "internal", "confidential")

ROLE_PERMISSIONS: dict[str, tuple[str, ...]] = {
    "employee": ("public",),
    "manager": ("public", "internal"),
    "admin": ("public", "internal", "confidential"),
}


def allowed_levels(role: str) -> list[str]:
    if role not in ROLE_PERMISSIONS:
        raise ValueError(f"Unknown role: {role!r}")
    return list(ROLE_PERMISSIONS[role])


def can_read(role: str, access_level: str) -> bool:
    return access_level in allowed_levels(role)
