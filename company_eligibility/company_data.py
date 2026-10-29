"""Company data access for the eligibility engine."""
import logging

log = logging.getLogger("spp")


def load_companies(active_only=True):
    """Companies as rule dicts. Reads the database; falls back to the seed list."""
    try:
        from models.company import Company
        rows = Company.all(active_only=active_only)
        return [Company.as_rule(r) for r in rows]
    except Exception as error:  # noqa: BLE001 - never break eligibility on DB trouble
        log.warning("Falling back to seed companies: %s", error)
        from company_eligibility.company_rules import COMPANIES
        return COMPANIES
