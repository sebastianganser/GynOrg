"""
PDF-Generator Service für GOÄ-Rechnungen.

Pipeline: Jinja2 → HTML → WeasyPrint → PDF → (optional) ZUGFeRD-Einbettung
"""
import os
from pathlib import Path
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from jinja2 import Environment, FileSystemLoader

try:
    from weasyprint import HTML as WeasyHTML
    HAS_WEASYPRINT = True
except ImportError:
    HAS_WEASYPRINT = False

from app.services.qr_service import generate_epc_qr_code
from app.services.zugferd_service import generate_zugferd_xml, embed_zugferd_in_pdf


# Jinja2 Environment
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=True
)


def generate_rechnung_pdf(
    rechnung,
    patient,
    positionen: list,
    praxis,
) -> bytes:
    """
    Generiert ein vollständiges Rechnungs-PDF.

    Args:
        rechnung: Rechnung SQLModel-Objekt
        patient: Patient SQLModel-Objekt
        positionen: Liste von RechnungsPosition-Objekten
        praxis: PraxisEinstellungen SQLModel-Objekt

    Returns:
        PDF-Bytes (ggf. mit ZUGFeRD-Metadaten)
    """
    if not HAS_WEASYPRINT:
        raise RuntimeError(
            "WeasyPrint ist nicht installiert. "
            "Bitte installieren Sie es mit: pip install weasyprint"
        )

    # Zahlungsziel berechnen
    zahlungsziel_datum = rechnung.rechnungsdatum + timedelta(days=rechnung.zahlungsziel_tage)

    # EPC-QR-Code generieren
    qr_code = ""
    if praxis.iban:
        empfaenger = praxis.kontoinhaber or f"{praxis.arzt_vorname} {praxis.arzt_nachname}"
        qr_code = generate_epc_qr_code(
            empfaenger=empfaenger,
            iban=praxis.iban,
            bic=praxis.bic or "",
            betrag=rechnung.gesamtbetrag,
            verwendungszweck=rechnung.rechnungsnummer,
        )

    # Template rendern
    template = jinja_env.get_template("rechnung.html")
    html_content = template.render(
        rechnung=rechnung,
        patient=patient,
        positionen=positionen,
        praxis=praxis,
        zahlungsziel_datum=zahlungsziel_datum,
        qr_code=qr_code,
        ust_befreit=praxis.ust_befreit,
    )

    # HTML → PDF
    pdf_bytes = WeasyHTML(string=html_content).write_pdf()

    # ZUGFeRD-XML generieren und einbetten
    arzt_name = f"{praxis.arzt_titel or ''} {praxis.arzt_vorname} {praxis.arzt_nachname}".strip()
    patient_name = f"{patient.titel or ''} {patient.vorname} {patient.nachname}".strip()

    zugferd_xml = generate_zugferd_xml(
        rechnungsnummer=rechnung.rechnungsnummer,
        rechnungsdatum=rechnung.rechnungsdatum,
        arzt_name=arzt_name,
        arzt_adresse={
            "strasse": praxis.strasse,
            "hausnummer": praxis.hausnummer,
            "plz": praxis.plz,
            "ort": praxis.ort,
        },
        patient_name=patient_name,
        patient_adresse={
            "strasse": patient.strasse,
            "hausnummer": patient.hausnummer,
            "plz": patient.plz,
            "ort": patient.ort,
        },
        positionen=positionen,
        gesamtbetrag=rechnung.gesamtbetrag,
        iban=praxis.iban,
        bic=praxis.bic or "",
        steuernummer=praxis.steuernummer or "",
        ust_befreit=praxis.ust_befreit,
    )

    pdf_bytes = embed_zugferd_in_pdf(pdf_bytes, zugferd_xml)

    return pdf_bytes
