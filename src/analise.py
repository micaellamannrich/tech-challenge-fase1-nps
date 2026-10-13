import pandas as pd


def contar_outliers_iqr(serie: pd.Series) -> int:
    """Conta valores fora do limite de 1.5x o intervalo interquartil.

    Usa a mesma regra do boxplot: valores abaixo de Q1 - 1.5*IQR
    ou acima de Q3 + 1.5*IQR são considerados outliers.

    Args:
        serie: coluna numérica a verificar.

    Returns:
        Quantidade de valores fora do limite.
    """
    q1, q3 = serie.quantile(0.25), serie.quantile(0.75)
    iqr = q3 - q1
    limite_baixo, limite_alto = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return ((serie < limite_baixo) | (serie > limite_alto)).sum()
