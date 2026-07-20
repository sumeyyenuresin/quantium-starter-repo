from app import app


def test_header_is_present(dash_duo):
    """Ana başlığın sayfada bulunduğunu doğrular."""

    dash_duo.start_server(app)

    header = dash_duo.wait_for_element(
        "#dashboard-title",
        timeout=15,
    )

    assert header.is_displayed()
    assert header.text == "Pink Morsel Bölgesel Satış Analizi"


def test_visualization_is_present(dash_duo):
    """Grafik bileşeninin sayfada mevcut olduğunu doğrular."""

    dash_duo.start_server(app)

    dash_duo.wait_for_element(
        "#sales-line-chart",
        timeout=15,
    )

    graphs = dash_duo.find_elements("#sales-line-chart")

    assert len(graphs) == 1


def test_region_selector_is_present(dash_duo):
    """Bölge seçicinin ve beş seçeneğin bulunduğunu doğrular."""

    dash_duo.start_server(app)

    region_selector = dash_duo.wait_for_element(
        "#region-filter",
        timeout=15,
    )

    assert region_selector.is_displayed()

    radio_buttons = dash_duo.find_elements(
        "#region-filter input[type='radio']"
    )

    assert len(radio_buttons) == 5