from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_three_content_queries():
    root = Path(__file__).resolve().parents[1]
    if not (root / "data/raw/ml-latest-small/ratings.csv").exists():
        import pytest

        pytest.skip("Prueba de integración requiere descarga oficial de MovieLens")
    app = AppTest.from_file(str(root / "app/streamlit_app.py")).run(timeout=30)
    for title in [
        "Toy Story (1995)",
        "Shawshank Redemption, The (1994)",
        "Exorcist, The (1973)",
    ]:
        app.selectbox[0].select(title).run()
        assert not app.exception
        assert title not in set(app.dataframe[0].value.title)
        assert len(app.dataframe[0].value) == 10
        assert "GroupLens" in app.caption[0].value
