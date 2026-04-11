"""add goae billing module tables

Revision ID: i9j0k1l2m3n4
Revises: h8i9j0k1l2m3
Create Date: 2026-04-02 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'i9j0k1l2m3n4'
down_revision: Union[str, None] = 'h8i9j0k1l2m3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ─── GOÄ-Ziffern ───
    op.create_table('goae_ziffern',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ziffer', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.Column('beschreibung', sa.Text(), nullable=False),
        sa.Column('punkte', sa.Integer(), nullable=False),
        sa.Column('abschnitt', sqlmodel.sql.sqltypes.AutoString(length=5), nullable=False),
        sa.Column('faktor_regelhöchst', sa.Numeric(precision=4, scale=2), nullable=False, server_default='2.3'),
        sa.Column('faktor_höchst', sa.Numeric(precision=4, scale=2), nullable=False, server_default='3.5'),
        sa.Column('aktiv', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_goae_ziffern_ziffer', 'goae_ziffern', ['ziffer'], unique=True)

    # ─── Patienten ───
    op.create_table('patienten',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('anrede', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('titel', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column('vorname', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('nachname', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('geburtsdatum', sa.Date(), nullable=False),
        sa.Column('strasse', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
        sa.Column('hausnummer', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.Column('plz', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.Column('ort', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('telefon', sqlmodel.sql.sqltypes.AutoString(length=30), nullable=True),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(length=150), nullable=True),
        sa.Column('versicherung', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=True),
        sa.Column('versicherungsnummer', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column('notizen', sa.Text(), nullable=True),
        sa.Column('aktiv', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_patienten_nachname', 'patienten', ['nachname'])

    # ─── Rechnungen ───
    op.create_table('rechnungen',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('rechnungsnummer', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column('rechnungsdatum', sa.Date(), nullable=False),
        sa.Column('leistungszeitraum_von', sa.Date(), nullable=False),
        sa.Column('leistungszeitraum_bis', sa.Date(), nullable=False),
        sa.Column('diagnose', sa.Text(), nullable=False),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default='entwurf'),
        sa.Column('gesamtbetrag', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('zahlungsziel_tage', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('bezahlt_am', sa.Date(), nullable=True),
        sa.Column('storniert_am', sa.Date(), nullable=True),
        sa.Column('storno_grund', sa.Text(), nullable=True),
        sa.Column('notizen', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['patienten.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_rechnungen_rechnungsnummer', 'rechnungen', ['rechnungsnummer'], unique=True)
    op.create_index('ix_rechnungen_patient_id', 'rechnungen', ['patient_id'])

    # ─── Rechnungspositionen ───
    op.create_table('rechnungs_positionen',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rechnung_id', sa.Integer(), nullable=False),
        sa.Column('goae_ziffer', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.Column('beschreibung', sa.Text(), nullable=False),
        sa.Column('datum', sa.Date(), nullable=False),
        sa.Column('anzahl', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('punkte', sa.Integer(), nullable=False),
        sa.Column('faktor', sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column('betrag', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('begruendung', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['rechnung_id'], ['rechnungen.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_rechnungs_positionen_rechnung_id', 'rechnungs_positionen', ['rechnung_id'])

    # ─── Rechnungsdokumente (PDF-Speicher) ───
    op.create_table('rechnungs_dokumente',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rechnung_id', sa.Integer(), nullable=False),
        sa.Column('dateiname', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
        sa.Column('mime_type', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False, server_default='application/pdf'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('pdf_daten', sa.LargeBinary(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['rechnung_id'], ['rechnungen.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_rechnungs_dokumente_rechnung_id', 'rechnungs_dokumente', ['rechnung_id'])

    # ─── Praxiseinstellungen ───
    op.create_table('praxis_einstellungen',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('arzt_titel', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column('arzt_vorname', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False, server_default=''),
        sa.Column('arzt_nachname', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False, server_default=''),
        sa.Column('fachrichtung', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False, server_default=''),
        sa.Column('praxis_name', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=True),
        sa.Column('strasse', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False, server_default=''),
        sa.Column('hausnummer', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False, server_default=''),
        sa.Column('plz', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False, server_default=''),
        sa.Column('ort', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False, server_default=''),
        sa.Column('telefon', sqlmodel.sql.sqltypes.AutoString(length=30), nullable=False, server_default=''),
        sa.Column('fax', sqlmodel.sql.sqltypes.AutoString(length=30), nullable=True),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(length=150), nullable=False, server_default=''),
        sa.Column('website', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=True),
        sa.Column('lanr', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
        sa.Column('steuernummer', sqlmodel.sql.sqltypes.AutoString(length=30), nullable=True),
        sa.Column('ust_befreit', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('bank_name', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False, server_default=''),
        sa.Column('iban', sqlmodel.sql.sqltypes.AutoString(length=34), nullable=False, server_default=''),
        sa.Column('bic', sqlmodel.sql.sqltypes.AutoString(length=11), nullable=True),
        sa.Column('kontoinhaber', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=True),
        sa.Column('standard_zahlungsziel_tage', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('rechnungsnummer_praefix', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False, server_default='RE'),
        sa.Column('naechste_rechnungsnummer', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('praxis_einstellungen')
    op.drop_table('rechnungs_dokumente')
    op.drop_table('rechnungs_positionen')
    op.drop_table('rechnungen')
    op.drop_table('patienten')
    op.drop_table('goae_ziffern')
