// Función para parsear la fecha y obtener una clave de "MM-YYYY"
function parseDate(dateStr) {
  const [day, month, year] = dateStr.split("/");
  return `${month}/${year}`;
}

const monthNames = {
  "01": "Enero",
  "02": "Febrero",
  "03": "Marzo",
  "04": "Abril",
  "05": "Mayo",
  "06": "Junio",
  "07": "Julio",
  "08": "Agosto",
  "09": "Septiembre",
  "10": "Octubre",
  "11": "Noviembre",
  "12": "Diciembre",
};

// Agrupar datos por mes para consumo
const consumoPorMes = registros.reduce((acc, curr) => {
  const monthYear = parseDate(curr.start_period);
  if (!acc[monthYear]) {
    acc[monthYear] = 0;
  }
  acc[monthYear] += parseFloat(curr.consumption_kwh);
  return acc;
}, {});

// Agrupar datos por mes para pagos
const pagoPorMes = registros.reduce((acc, curr) => {
  const monthYear = parseDate(curr.start_period);
  if (!acc[monthYear]) {
    acc[monthYear] = 0;
  }
  acc[monthYear] += parseFloat(curr.total_pay);
  return acc;
}, {});

const maxPagoPorMes = registros.reduce((acc, curr) => {
  const monthYear = parseDate(curr.start_period);
  const pago = parseFloat(curr.total_pay);
  if (!acc[monthYear] || acc[monthYear].pago < pago) {
    acc[monthYear] = { pago: pago, nis: curr.nis };
  }
  return acc;
}, {});

// Ordenar y convertir las claves de meses
const sortedMonths = Object.keys(consumoPorMes).sort((a, b) => {
  const [monthA, yearA] = a.split("/");
  const [monthB, yearB] = b.split("/");
  return new Date(yearA, monthA) - new Date(yearB, monthB);
});

const labels = sortedMonths.map((monthYear) => {
  const [month, year] = monthYear.split("/");
  return `${monthNames[month]}`;
});

const year = sortedMonths.map((monthYear) => {
  const [month, year] = monthYear.split("/");
  return `${year}`;
});

// Asegúrate de hacer lo mismo con los datos para mantener el orden correcto
const consumoData = sortedMonths.map((month) => consumoPorMes[month]);
const pagoData = sortedMonths.map((month) => pagoPorMes[month]);
const maxPagoData = sortedMonths.map((month) => maxPagoPorMes[month].pago);
const nisMaxPago = sortedMonths.map((month) => maxPagoPorMes[month].nis);


/// Gráfico de Consumo

var ctxConsumo = document.getElementById("graficoConsumo").getContext("2d");
var graficoConsumo = new Chart(ctxConsumo, {
  type: "bar",
  data: {
    labels: labels,
    datasets: [
      {
        label: `Consumo kWh por Mes ${year[0]}`,
        data: consumoData,
        backgroundColor: "rgba(75, 192, 192, 0.2)",
        borderColor: "rgba(75, 192, 192, 1)",
        borderWidth: 2,
        borderRadius: 5,
        borderSkipped: "bottom",
      },
    ],
  },
  options: {
    responsive: true,
    scales: {
      x: {
        ticks: {
        },
      },
      y: {
        ticks: {
        },
      },
    },
    plugins: {
      legend: {
        labels: {
        },
      },
      title: {
        display: true,
        text: "Gráfico de Consumo por Mes",
        font: {
          size: 20,
        },
      },
      tooltip: {
      },
    },
  },
});

// Gráfico de Pago
var ctxPago = document.getElementById("graficoPago").getContext("2d");
var graficoPago = new Chart(ctxPago, {
  type: "line",
  data: {
    labels: labels,
    datasets: [
      {
        label: `Total Pagado por Mes ${year[0]}`,
        data: pagoData,
        backgroundColor: "rgba(255, 99, 132, 0.2)",
        borderColor: "rgba(255, 99, 132, 1)",
        borderWidth: 2,
        tension: 0.3,
      },
    ],
  },
  options: {
    responsive: true,
    scales: {
      x: {
        ticks: {
        },
      },
      y: {
        ticks: {
        },
      },
    },
    plugins: {
      legend: {
        labels: {
         
        },
      },
      title: {
        display: true,
        text: `Gráfico de Pagos por Mes de ${year[0]} `,
        font: {
          size: 20,
        },
      },
      tooltip: {

        
      },
    },
  },
});

// Gráfico de Quién Paga Más por Mes
var ctxMaxPago = document.getElementById("graficoMaxPago").getContext("2d");
var graficoMaxPago = new Chart(ctxMaxPago, {
  type: "bar",
  data: {
    labels: labels,
    datasets: [
      {
        label: "Pago Máximo por Mes",
        data: maxPagoData,
        backgroundColor: "rgba(153, 102, 255, 0.2)",
        borderColor: "rgba(153, 102, 255, 1)",
        borderWidth: 2,
      },
    ],
  },
  options: {
    responsive: true,
    scales: {
      x: {
        ticks: {
          
        },
      },
      y: {
        ticks: {
          
        },
      },
    },
    plugins: {
      legend: {
        labels: {
          
        },
      },
      title: {
        display: true,
        text: `Pago Máximo por Mes con NIS de ${year[0]}`,
        font: {
          size: 20,
        },
      },
      tooltip: {
        callbacks: {
          label: function (tooltipItem) {
            return `NIS: ${nisMaxPago[tooltipItem.dataIndex]}, Pago: Q${
              tooltipItem.raw
            }`;
          },
        },
      },
    },
  },
});
