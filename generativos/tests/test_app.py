from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


def test_app_loads_saved_decoder_and_changes_latent_point():
    root = Path(__file__).resolve().parents[1]
    if not (root / "models/decoder.keras").exists():
        pytest.skip("Requires trained decoder")
    app = AppTest.from_file(str(root / "app/streamlit_app.py")).run(timeout=60)
    assert not app.exception
    app.slider[0].set_value(1.0).run(timeout=30)
    app.number_input[0].set_value(7).run(timeout=30)
    assert not app.exception and "Fashion-MNIST" in app.caption[0].value
