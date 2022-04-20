"""Transform dataset: select some columns."""
import click
import pandas as pd

TARGET_COLUMNS = [
    "Жилая площадь, м^2",
    "Площадь кухни, м^2",
    "Общая площадь, м^2",
    "Этаж",
    "Стоимость, р.",
    "Количество комнат",
    "Тип жилья",
    "Планировка",
    "Высота потолков",
    "Санузел",
    "Ремонт",
    "Вид из окон",
    "Балкон/лоджия",
    "Количество пассажирских лифтов",
    "Год постройки",
    "Количество грузовых лифтов",
    "Количество этажей",
    "Технология строительства",
    "Район",
    "Станция метро",
    "Широта",
    "Долгота",
]


@click.command()
@click.argument("input_filepath", type=click.Path(exists=True))
@click.argument("output_filepath", type=click.Path())
def main(input_filepath: str, output_filepath: str) -> None:
    """Drop some columns from external dataset and write interim dataset.

    @param input_filepath: path to external dataset
    @param output_filepath: path to int
    """
    df = pd.read_csv(input_filepath)
    df = df[TARGET_COLUMNS]
    df.to_csv(output_filepath, index=False)


if __name__ == "__main__":
    main()
