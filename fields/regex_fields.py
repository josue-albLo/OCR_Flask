import re

nis = re.compile(r"NIR\s*:\s*0\.(\d+)")
fecha_emision = re.compile(r"Fecha\s*de\s*Emisi[oOÓÉé6]*n:\s*(\d{2}/\d{2}/\d{4})")
consumo_electricidad = re.compile(r"\s*(\d+)\s*KWh")
periodo_lectura = re.compile(
    r"PERIODO DE LECTURA: (\d{2}/\d{2}/202\d) al (\d{2}/\d{2}/202\d)"
)
pagar = re.compile(r"TOTAL?\s*Q\s*(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)")


def get_important_fields(text) -> dict[str, str]:
    nit_match = re.search(nis, text)
    date_match = re.search(fecha_emision, text)
    consumption_match = re.search(consumo_electricidad, text)
    reading_period_match = re.search(periodo_lectura, text)
    total_match = re.search(pagar, text)

    nit = nit_match.group(1) if nit_match else None
    date = date_match.group(1) if date_match else None
    consumption = (
        consumption_match.group(1) if consumption_match else None
    )
    reading_period = (
        reading_period_match.group(1)
        if reading_period_match
        else None
    )

    end_period = (
        reading_period_match.group(2)
        if reading_period_match
        else None
    )

    total = total_match.group(1) if total_match else None

    return {
        "nis": nit,
        "date_issue": date,
        "consumption_kwh": consumption,
        "start_period": reading_period,
        "end_period": end_period,
        "total_pay": total,
    }
