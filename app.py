from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html


DATA_FILE = Path("data") / "pink_morsel_sales.csv"
PRICE_INCREASE_DATE = pd.Timestamp("2021-01-15")


def load_sales_data() -> pd.DataFrame:
    """Pink Morsel satış verilerini yükler ve temizler."""

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

    sales_data["region"] = (
        sales_data["region"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    return sales_data.sort_values("date")


sales_data = load_sales_data()

region_labels = {
    "all": "Tümü",
    "north": "Kuzey",
    "east": "Doğu",
    "south": "Güney",
    "west": "Batı",
}


def create_sales_figure(selected_region: str):
    """Seçilen bölgeye göre günlük satış grafiğini oluşturur."""

    if selected_region == "all":
        filtered_data = sales_data.copy()
        chart_title = "Tüm Bölgelerde Pink Morsel Günlük Satışları"
    else:
        filtered_data = sales_data[
            sales_data["region"] == selected_region
        ].copy()

        chart_title = (
            f"{region_labels[selected_region]} Bölgesi "
            "Pink Morsel Günlük Satışları"
        )

    daily_sales = (
        filtered_data.groupby("date", as_index=False)["sales"]
        .sum()
        .sort_values("date")
    )

    figure = px.line(
        daily_sales,
        x="date",
        y="sales",
        markers=True,
        title=chart_title,
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
        paper_bgcolor="white",
        plot_bgcolor="#f8fafc",
        margin={
            "l": 60,
            "r": 30,
            "t": 80,
            "b": 60,
        },
    )

    figure.update_xaxes(
        showgrid=True,
        gridcolor="#e2e8f0",
    )

    figure.update_yaxes(
        tickprefix="$",
        separatethousands=True,
        showgrid=True,
        gridcolor="#e2e8f0",
    )

    return figure, daily_sales


def calculate_summary(daily_sales: pd.DataFrame):
    """Fiyat artışından önceki ve sonraki ortalamaları hesaplar."""

    before_sales = daily_sales[
        daily_sales["date"] < PRICE_INCREASE_DATE
    ]["sales"]

    after_sales = daily_sales[
        daily_sales["date"] >= PRICE_INCREASE_DATE
    ]["sales"]

    before_average = before_sales.mean()
    after_average = after_sales.mean()

    if pd.isna(before_average):
        before_average = 0

    if pd.isna(after_average):
        after_average = 0

    percentage_change = (
        (after_average - before_average) / before_average * 100
        if before_average != 0
        else 0
    )

    return before_average, after_average, percentage_change


app = Dash(__name__)
app.title = "Pink Morsel Bölgesel Satış Analizi"

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    "Pink Morsel Bölgesel Satış Analizi",
                    style={
                        "marginBottom": "8px",
                        "fontSize": "36px",
                    },
                ),
                html.P(
                    (
                        "15 Ocak 2021 fiyat artışından önceki ve sonraki "
                        "satış performansını bölgelere göre inceleyin."
                    ),
                    style={
                        "marginTop": "0",
                        "fontSize": "17px",
                        "color": "#475569",
                    },
                ),
            ],
            style={
                "textAlign": "center",
                "marginBottom": "30px",
            },
        ),

        html.Div(
            [
                html.H3(
                    "Bölge seçin",
                    style={
                        "marginBottom": "14px",
                        "color": "#1e293b",
                    },
                ),
                dcc.RadioItems(
                    id="region-filter",
                    options=[
                        {"label": "Tümü", "value": "all"},
                        {"label": "Kuzey", "value": "north"},
                        {"label": "Doğu", "value": "east"},
                        {"label": "Güney", "value": "south"},
                        {"label": "Batı", "value": "west"},
                    ],
                    value="all",
                    inline=True,
                    labelStyle={
                        "marginRight": "24px",
                        "cursor": "pointer",
                        "fontWeight": "600",
                    },
                    inputStyle={
                        "marginRight": "7px",
                    },
                ),
            ],
            style={
                "backgroundColor": "white",
                "padding": "22px",
                "borderRadius": "14px",
                "boxShadow": "0 6px 20px rgba(15, 23, 42, 0.08)",
                "marginBottom": "24px",
            },
        ),

        html.Div(
            id="summary-cards",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(3, 1fr)",
                "gap": "18px",
                "marginBottom": "24px",
            },
        ),

        html.Div(
            [
                dcc.Graph(
                    id="sales-line-chart",
                    config={
                        "displayModeBar": True,
                        "displaylogo": False,
                    },
                ),
            ],
            style={
                "backgroundColor": "white",
                "padding": "18px",
                "borderRadius": "14px",
                "boxShadow": "0 6px 20px rgba(15, 23, 42, 0.08)",
            },
        ),
    ],
    style={
        "maxWidth": "1250px",
        "margin": "0 auto",
        "padding": "36px 24px",
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#f1f5f9",
        "minHeight": "100vh",
    },
)


@app.callback(
    Output("sales-line-chart", "figure"),
    Output("summary-cards", "children"),
    Input("region-filter", "value"),
)
def update_dashboard(selected_region: str):
    """Radyo düğmesine göre grafiği ve özet kartlarını günceller."""

    figure, daily_sales = create_sales_figure(selected_region)

    before_average, after_average, percentage_change = calculate_summary(
        daily_sales
    )

    if percentage_change > 0:
        change_text = f"%{percentage_change:.1f} artış"
    elif percentage_change < 0:
        change_text = f"%{abs(percentage_change):.1f} azalış"
    else:
        change_text = "Değişiklik yok"

    card_style = {
        "backgroundColor": "white",
        "padding": "22px",
        "borderRadius": "14px",
        "textAlign": "center",
        "boxShadow": "0 6px 20px rgba(15, 23, 42, 0.08)",
    }

    cards = [
        html.Div(
            [
                html.P(
                    "Artış Öncesi Ortalama",
                    style={
                        "margin": "0 0 10px",
                        "color": "#64748b",
                        "fontWeight": "600",
                    },
                ),
                html.H2(
                    f"${before_average:,.2f}",
                    style={
                        "margin": "0",
                        "color": "#0f172a",
                    },
                ),
            ],
            style=card_style,
        ),
        html.Div(
            [
                html.P(
                    "Artış Sonrası Ortalama",
                    style={
                        "margin": "0 0 10px",
                        "color": "#64748b",
                        "fontWeight": "600",
                    },
                ),
                html.H2(
                    f"${after_average:,.2f}",
                    style={
                        "margin": "0",
                        "color": "#0f172a",
                    },
                ),
            ],
            style=card_style,
        ),
        html.Div(
            [
                html.P(
                    "Satış Değişimi",
                    style={
                        "margin": "0 0 10px",
                        "color": "#64748b",
                        "fontWeight": "600",
                    },
                ),
                html.H2(
                    change_text,
                    style={
                        "margin": "0",
                        "color": "#0f172a",
                    },
                ),
            ],
            style=card_style,
        ),
    ]

    return figure, cards


if __name__ == "__main__":
    app.run(debug=True)