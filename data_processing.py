from pathlib import Path

import pandas as pd


DATA_DIRECTORY = Path("data")
OUTPUT_FILE = DATA_DIRECTORY / "pink_morsel_sales.csv"


def process_sales_data() -> None:
    """Üç satış CSV'sini birleştirip Pink Morsel satışlarını hazırlar."""

    input_files = sorted(DATA_DIRECTORY.glob("daily_sales_data_*.csv"))

    if not input_files:
        raise FileNotFoundError(
            "data klasöründe daily_sales_data_*.csv dosyaları bulunamadı."
        )

    dataframes = []

    for file_path in input_files:
        dataframe = pd.read_csv(file_path)
        dataframes.append(dataframe)
        print(f"Okundu: {file_path.name} - {len(dataframe)} satır")

    combined_data = pd.concat(dataframes, ignore_index=True)

    # Yalnızca Pink Morsel ürününe ait satırları seç.
    pink_morsel_data = combined_data[
        combined_data["product"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("pink morsel")
    ].copy()

    # "$3.00" gibi fiyatları sayısal değere dönüştür.
    pink_morsel_data["price"] = pd.to_numeric(
        pink_morsel_data["price"]
        .astype(str)
        .str.replace(r"[$,]", "", regex=True),
        errors="raise",
    )

    pink_morsel_data["quantity"] = pd.to_numeric(
        pink_morsel_data["quantity"],
        errors="raise",
    )

    # Satış tutarı = fiyat × miktar
    pink_morsel_data["sales"] = (
        pink_morsel_data["price"] * pink_morsel_data["quantity"]
    ).round(2)

    # Çıktıda yalnızca görevde istenen sütunları bırak.
    output_data = pink_morsel_data[["sales", "date", "region"]]

    output_data.to_csv(OUTPUT_FILE, index=False)

    print("\nVeri işleme tamamlandı.")
    print(f"Çıktı dosyası: {OUTPUT_FILE}")
    print(f"Pink Morsel satır sayısı: {len(output_data)}")


if __name__ == "__main__":
    process_sales_data()