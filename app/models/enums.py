from enum import Enum

class RegulationType(str, Enum):
    GDPR = "gdpr"
    HIPAA = "hipaa"
    CCPA = "ccpa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    FERPA = "ferpa"

class ClauseCategory(str, Enum):
    DATA_PRIVACY = "data_privacy"
    SECURITY = "security"
    LIABILITY = "liability"
    TERMINATION = "termination"
    PAYMENT = "payment"
    CONFIDENTIALITY = "confidentiality"
    IP_RIGHTS = "intellectual_property"
    COMPLIANCE = "compliance"
    FORCE_MAJEURE = "force_majeure"
    DISPUTE_RESOLUTION = "dispute_resolution"

class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"