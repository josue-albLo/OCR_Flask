

def transform(data: dict[str, str]):
    if data is None:
        return None

    data["consumption_kwh"] = f'{data["consumption_kwh"]} kWh'
    data["total_pay"] = f'Q.{data["total_pay"]}'

    label = {
        "nis": "NIS",
        "date_issue": "Fecha de Emisión",
        "consumption_kwh": "Consumo de Electricidad",
        "start_period": "Periodo de Inicio",
        "end_period": "Periodo de Fin",
        "total_pay": "Total a Pagar",
    }

    return {label[key]: value for key, value in data.items()}
