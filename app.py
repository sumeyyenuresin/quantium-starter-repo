from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html


DATA_FILE = Path("data") / "pink_morsel_sales.csv"
PRICE_INCREASE_DATE = pd.Timestamp("2021-01-15")


def load_sales_data() -> pd.DataFrame:
    """Pink Morsel satış verilerini okur ve günlük toplamları hesaplar."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"{DATA_FILE} bulunamadı. Önce data_processing.py dosyasını çalıştırın."
        )

    sales_data = pd.read_csv(DATA_FILE)

    required_columns = {"sales", "date", "region"}
    missing_columns = required_columns - set(sales_data.columns)

    if missing_columns:
        raise ValueError(
            f"CSV dosyasında eksik sütunlar var: {sorted(missing_columns)}"
        )

    sales_data["date"] = pd.to_datetime(
        sales_data["date"],
        errors="raise",
    )

    sales_data["sales"] = pd.to_numeric(
        sales_data["sales"],
        errors="raise",
    )

    daily_sales = (
        sales_data.groupby("date", as_index=False)["sales"]
        .sum()
        .sort_values("date")
    )

    return daily_sales


def calculate_sales_summary(
    daily_sales: pd.DataFrame,
) -> tuple[float, float, float]:
    """Fiyat artışından önceki ve sonraki ortalama günlük satışları hesaplar."""

    before_increase = daily_sales[
        daily_sales["date"] < PRICE_INCREASE_DATE
    ]["sales"]

    after_increase = daily_sales[
        daily_sales["date"] >= PRICE_INCREASE_DATE
    ]["sales"]

    before_average = before_increase.mean()
    after_average = after_increase.mean()

    percentage_change = (
        (after_average - before_average) / before_average * 100
        if before_average
        else 0
    )

    return before_average, after_average, percentage_change


daily_sales = load_sales_data()

before_average, after_average, percentage_change = (
    calculate_sales_summary(daily_sales)
)

if percentage_change > 0:
    comparison_message = (
        f"Fiyat artışından sonra ortalama günlük satışlar "
        f"%{percentage_change:.1f} arttı."
    )
elif percentage_change < 0:
    comparison_message = (
        f"Fiyat artışından sonra ortalama günlük satışlar "
        f"%{abs(percentage_change):.1f} azaldı."
    )
else:
    comparison_message = (
        "Fiyat artışından sonra ortalama günlük satışlarda değişiklik olmadı."
    )

figure = px.line(
    daily_sales,
    x="date",
    y="sales",
    markers=True,
    title="Pink Morsel Günlük Satışları",
    labels={
        "date": "Tarih",
        "sales": "Toplam Satış",
    },
)

figure.add_vline(
    x=PRICE_INCREASE_DATE.timestamp() * 1000,
    line_dash="dash",
    annotation_text="15 Ocak 2021 fiyat artışı",
    annotation_position="top left",
)

figure.update_layout(
    hovermode="x unified",
    xaxis_title="Tarih",
    yaxis_title="Toplam Satış",
)

figure.update_yaxes(
    tickprefix="$",
    separatethousands=True,
)

app = Dash(__name__)

app.title = "Pink Morsel Satış Analizi"

app.layout = html.Div(
    [
        html.H1(
            "Pink Morsel Satış Analizi",
            style={"textAlign": "center"},
        ),
        html.P(
            (
                "15 Ocak 2021 tarihindeki fiyat artışından önceki ve "
                "sonraki satış performansının karşılaştırılması"
            ),
            style={"textAlign": "center"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H3("Artış Öncesi Ortalama"),
                        html.P(f"${before_average:,.2f}"),
                    ]
                ),
                html.Div(
                    [
                        html.H3("Artış Sonrası Ortalama"),
                        html.P(f"${after_average:,.2f}"),
                    ]
                ),
            ],
            style={
                "display": "flex",
                "justifyContent": "space-evenly",
                "textAlign": "center",
            },
        ),
        html.H3(
            comparison_message,
            style={"textAlign": "center"},
        ),
        dcc.Graph(
            id="sales-line-chart",
            figure=figure,
        ),
    ],
    style={
        "maxWidth": "1200px",
        "margin": "0 auto",
        "padding": "20px",
        "fontFamily": "Arial",
    },
)


if __name__ == "__main__":
    app.run(debug=True)