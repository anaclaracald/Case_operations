"""
config.py — Constantes, listas canônicas e mapeamentos do case.
Fonte da verdade: case.md
"""

# Identificadores
OPP_ID_COL = "Opportunity_ID"
RAW_DATA_PATH = "data/raw/opps_corrupted.xlsx"
PROCESSED_DATA_PATH = "data/processed/opps_corrigido.xlsx"
REPORT_ERRORS_PATH = "reports/relatorio_erros.html"
REPORT_ANALYSIS_PATH = "reports/analise.html"
PRESENTATION_PATH = "reports/apresentacao.pdf"
REFERENCE_DATE = "2026-04-29"  # data atual para cálculo de idade do pipeline

# Listas canônicas (case.md)
CANONICAL_LEAD_SOURCE = [
    "Inbound Current Client (DEPRECATED)",
    "Inbound Website Media. Monks (DEPRECATED)",
    "Inbound Marketing (DEPRECATED)",
    "Inbound Website (DEPRECATED)",
    "Marketing Lead Scoring/Nurturing",
    "Website Sales Form",
    "Prospecting Personal (DEPRECATED)",
    "Prospecting Current Client (DEPRECATED)",
    "Referral Internal",
    "Referral Personal",
    "Referral S4 Company",
    "Referral Partner",
    "Google Marketing Platform Referral",
    "Partner Google Cloud",
    "Existing Client Account/Growth Activity",
    "Industry Event",
    "MH Lead (DEPRECATED)",
    "Don't Know/Other (DEPRECATED)",
]

CANONICAL_LEAD_OFFICE = [
    "Sao Carlos, BR",
    "Votorantim, BR",
    "Sao Paulo, BR",
]

CANONICAL_STAGE = [
    "Opportunity Identified",
    "Qualified",
    "Registration",
    "Pitching",
    "Pitched",
    "Negotiation",
    "Closed Won",
]

VALID_TYPES = [
    "Project - Not Competitive",
    "Project - Competitive",
    "Change Order/Upsell",
]

# Estágios em que nulos de valor/produto são aceitáveis
EARLY_STAGES = ["Opportunity Identified", "Qualified"]

# ---------------------------------------------------------------------------
# Mapeamento de Lead_Source bruto → valor canônico
# Normaliza: separadores, maiúsculas/minúsculas, espaços e typos
# ---------------------------------------------------------------------------

LEAD_SOURCE_RAW_TO_CANONICAL = {
    # Inbound
    "inbound - current client (deprecated)": "Inbound Current Client (DEPRECATED)",
    "inbound - website - media.monks (deprecated)": "Inbound Website Media. Monks (DEPRECATED)",
    "inbound - marketing (deprecated)": "Inbound Marketing (DEPRECATED)",
    "inbound - website (deprecated)": "Inbound Website (DEPRECATED)",
    "marketing - lead scoring/nurturing": "Marketing Lead Scoring/Nurturing",
    "website - sales form": "Website Sales Form",
    # Outbound / Prospecting
    "prospecting - personal (deprecated)": "Prospecting Personal (DEPRECATED)",
    "prospecting - current client (deprecated)": "Prospecting Current Client (DEPRECATED)",
    # Referral
    "referral - internal": "Referral Internal",
    "refferal - internal": "Referral Internal",          # typo
    "referral - personal": "Referral Personal",
    "referral - s4 company": "Referral S4 Company",
    "referral - partner - google marketing platform": "Google Marketing Platform Referral",
    "referral - partner - google cloud": "Partner Google Cloud",
    # Customer Success
    "existing client - account/growth activity": "Existing Client Account/Growth Activity",
    "existing client-account/growth activity": "Existing Client Account/Growth Activity",
    # Event
    "industry event": "Industry Event",
    # Unknown
    "mh lead (deprecated)": "MH Lead (DEPRECATED)",
    "don't know/other (deprecated)": "Don't Know/Other (DEPRECATED)",
    "don't know-other": "Don't Know/Other (DEPRECATED)",
}

# Mapeamento de valor canônico → categoria de Lead_Source
# ATENÇÃO: "Inbound Current Client (DEPRECATED)" → Customer Success
LEAD_SOURCE_TO_CATEGORY = {
    "Inbound Current Client (DEPRECATED)": "Customer Success",      # não é Inbound!
    "Inbound Website Media. Monks (DEPRECATED)": "Inbound",
    "Inbound Marketing (DEPRECATED)": "Inbound",
    "Inbound Website (DEPRECATED)": "Inbound",
    "Marketing Lead Scoring/Nurturing": "Inbound",
    "Website Sales Form": "Inbound",
    "Prospecting Personal (DEPRECATED)": "Outbound",
    "Prospecting Current Client (DEPRECATED)": "Customer Success",
    "Referral Internal": "Referral",
    "Referral Personal": "Referral",
    "Referral S4 Company": "Referral",
    "Referral Partner": "Referral",
    "Google Marketing Platform Referral": "Referral",
    "Partner Google Cloud": "Referral",
    "Existing Client Account/Growth Activity": "Customer Success",
    "Industry Event": "Event",
    "MH Lead (DEPRECATED)": "Unknown",
    "Don't Know/Other (DEPRECATED)": "Unknown",
}

LEAD_SOURCE_CATEGORIES = ["Inbound", "Outbound", "Referral", "Customer Success", "Event", "Unknown"]

# Mapeamento de Stage com typos → canônico
STAGE_TYPO_MAP = {
    "closed wonn": "Closed Won",
    "clossed won": "Closed Won",
    "negociation": "Negotiation",
    "pitchinng": "Pitching",
    "pithced": "Pitched",
    "qualifyed": "Qualified",
    "registrationn": "Registration",
}

# Mapeamento de Lead_Office com variações → canônico
LEAD_OFFICE_NORM_MAP = {
    "sp": "Sao Paulo, BR",
    "sao paulo": "Sao Paulo, BR",
    "são paulo": "Sao Paulo, BR",
    "sao paulo, br": "Sao Paulo, BR",
    "saõ paulo, br": "Sao Paulo, BR",
    "sao carlos, br": "Sao Carlos, BR",
    "votorantim, br": "Votorantim, BR",
}
