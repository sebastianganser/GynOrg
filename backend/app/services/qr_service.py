"""
EPC-QR-Code (GiroCode) Service für GOÄ-Rechnungen.

Generiert einen QR-Code nach dem EPC-Standard (European Payments Council),
damit Patienten die Rechnung direkt per Banking-App bezahlen können.
"""
import io
import base64
from decimal import Decimal

try:
    import qrcode
    from qrcode.image.pil import PilImage
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False


def generate_epc_qr_code(
    empfaenger: str,
    iban: str,
    bic: str,
    betrag: Decimal,
    verwendungszweck: str,
) -> str:
    """
    Generiert einen EPC-QR-Code (GiroCode) als Base64-PNG.

    Format nach EPC069-12 v2.1:
    - Service Tag: BCD
    - Version: 002
    - Encoding: 1 (UTF-8)
    - Transfer: SCT (SEPA Credit Transfer)

    Returns:
        Base64-kodierter PNG-String für die Einbettung in HTML.
    """
    if not HAS_QRCODE:
        return ""

    # EPC-QR-Code Payload
    lines = [
        "BCD",                    # Service Tag
        "002",                    # Version
        "1",                      # Zeichencodierung (UTF-8)
        "SCT",                    # SEPA Credit Transfer
        bic or "",                # BIC (optional seit SEPA 3.0)
        empfaenger[:70],          # Empfänger (max 70 Zeichen)
        iban.replace(" ", ""),    # IBAN ohne Leerzeichen
        f"EUR{betrag:.2f}",      # Betrag
        "",                      # Purpose (leer)
        "",                      # Referenz (leer)
        verwendungszweck[:140],  # Verwendungszweck (max 140 Zeichen)
        "",                      # Info an Nutzer (leer)
    ]
    payload = "\n".join(lines)

    # QR-Code generieren
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=2,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Als Base64 konvertieren
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode("utf-8")

    return f"data:image/png;base64,{b64}"
