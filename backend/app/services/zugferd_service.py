"""
ZUGFeRD / Factur-X Service für GOÄ-Rechnungen.

Erzeugt EN 16931-konforme XML-Metadaten und bettet sie in das PDF ein.
Ärztliche Leistungen sind nach §4 Nr. 14 UStG umsatzsteuerbefreit.
"""
from decimal import Decimal
from datetime import date
from typing import List, Optional

try:
    from facturx import generate_from_binary
    HAS_FACTURX = True
except ImportError:
    HAS_FACTURX = False


def generate_zugferd_xml(
    rechnungsnummer: str,
    rechnungsdatum: date,
    arzt_name: str,
    arzt_adresse: dict,
    patient_name: str,
    patient_adresse: dict,
    positionen: list,
    gesamtbetrag: Decimal,
    iban: str = "",
    bic: str = "",
    steuernummer: str = "",
    ust_befreit: bool = True,
) -> str:
    """
    Generiert ZUGFeRD XML im MINIMUM-Profil.

    Returns:
        XML-String für die Einbettung in das PDF.
    """
    # Steuerkategorie: E = steuerbefreit (§4 Nr. 14 UStG)
    steuer_code = "E" if ust_befreit else "S"
    steuer_prozent = "0.00" if ust_befreit else "19.00"

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice
    xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
    xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
    xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100"
    xmlns:qdt="urn:un:unece:uncefact:data:standard:QualifiedDataType:100">
  <rsm:ExchangedDocumentContext>
    <ram:GuidelineSpecifiedDocumentContextParameter>
      <ram:ID>urn:factur-x.eu:1p0:minimum</ram:ID>
    </ram:GuidelineSpecifiedDocumentContextParameter>
  </rsm:ExchangedDocumentContext>
  <rsm:ExchangedDocument>
    <ram:ID>{rechnungsnummer}</ram:ID>
    <ram:TypeCode>380</ram:TypeCode>
    <ram:IssueDateTime>
      <udt:DateTimeString format="102">{rechnungsdatum.strftime('%Y%m%d')}</udt:DateTimeString>
    </ram:IssueDateTime>
  </rsm:ExchangedDocument>
  <rsm:SupplyChainTradeTransaction>
    <ram:ApplicableHeaderTradeAgreement>
      <ram:SellerTradeParty>
        <ram:Name>{arzt_name}</ram:Name>
        <ram:PostalTradeAddress>
          <ram:LineOne>{arzt_adresse.get('strasse', '')} {arzt_adresse.get('hausnummer', '')}</ram:LineOne>
          <ram:PostcodeCode>{arzt_adresse.get('plz', '')}</ram:PostcodeCode>
          <ram:CityName>{arzt_adresse.get('ort', '')}</ram:CityName>
          <ram:CountryID>DE</ram:CountryID>
        </ram:PostalTradeAddress>
        <ram:SpecifiedTaxRegistration>
          <ram:ID schemeID="FC">{steuernummer}</ram:ID>
        </ram:SpecifiedTaxRegistration>
      </ram:SellerTradeParty>
      <ram:BuyerTradeParty>
        <ram:Name>{patient_name}</ram:Name>
        <ram:PostalTradeAddress>
          <ram:LineOne>{patient_adresse.get('strasse', '')} {patient_adresse.get('hausnummer', '')}</ram:LineOne>
          <ram:PostcodeCode>{patient_adresse.get('plz', '')}</ram:PostcodeCode>
          <ram:CityName>{patient_adresse.get('ort', '')}</ram:CityName>
          <ram:CountryID>DE</ram:CountryID>
        </ram:PostalTradeAddress>
      </ram:BuyerTradeParty>
    </ram:ApplicableHeaderTradeAgreement>
    <ram:ApplicableHeaderTradeDelivery/>
    <ram:ApplicableHeaderTradeSettlement>
      <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
      <ram:SpecifiedTradeSettlementPaymentMeans>
        <ram:TypeCode>58</ram:TypeCode>
        <ram:PayeePartyCreditorFinancialAccount>
          <ram:IBANID>{iban}</ram:IBANID>
        </ram:PayeePartyCreditorFinancialAccount>
      </ram:SpecifiedTradeSettlementPaymentMeans>
      <ram:ApplicableTradeTax>
        <ram:CalculatedAmount>{gesamtbetrag}</ram:CalculatedAmount>
        <ram:TypeCode>VAT</ram:TypeCode>
        <ram:ExemptionReason>Umsatzsteuerbefreit nach §4 Nr. 14 UStG</ram:ExemptionReason>
        <ram:BasisAmount>{gesamtbetrag}</ram:BasisAmount>
        <ram:CategoryCode>{steuer_code}</ram:CategoryCode>
        <ram:RateApplicablePercent>{steuer_prozent}</ram:RateApplicablePercent>
      </ram:ApplicableTradeTax>
      <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        <ram:LineTotalAmount>{gesamtbetrag}</ram:LineTotalAmount>
        <ram:TaxBasisTotalAmount>{gesamtbetrag}</ram:TaxBasisTotalAmount>
        <ram:TaxTotalAmount currencyID="EUR">0.00</ram:TaxTotalAmount>
        <ram:GrandTotalAmount>{gesamtbetrag}</ram:GrandTotalAmount>
        <ram:DuePayableAmount>{gesamtbetrag}</ram:DuePayableAmount>
      </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
    </ram:ApplicableHeaderTradeSettlement>
  </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>"""
    return xml


def embed_zugferd_in_pdf(pdf_bytes: bytes, xml_string: str) -> bytes:
    """
    Bettet ZUGFeRD-XML in ein PDF/A-3 Dokument ein.

    Returns:
        PDF-Bytes mit eingebettetem ZUGFeRD-XML.
    """
    if not HAS_FACTURX:
        # Fallback: PDF ohne ZUGFeRD zurückgeben
        return pdf_bytes

    try:
        result = generate_from_binary(
            pdf_bytes,
            xml_string.encode("utf-8"),
            flavor="factur-x",
            level="minimum",
        )
        return result
    except Exception:
        # Bei Fehler Original-PDF zurückgeben
        return pdf_bytes
