import streamlit as st

from inf8239_u03.config import MOVIELENS_DIR, MOVIELENS_URL, ROOT
from inf8239_u03.data import download_zip, load_movielens
from inf8239_u03.recommenders import ContentRecommender

st.title("INF-8239 · Recomendador de películas")
st.caption("Fuente: MovieLens Latest Small · GroupLens, University of Minnesota.")
st.markdown(
    "[Fuente y condiciones de uso](https://files.grouplens.org/datasets/movielens/ml-latest-small-README.html)"
)
st.info(
    "Método: TF-IDF de géneros y similitud coseno. Compartir géneros no garantiza satisfacción. Riesgo: sobre-especialización y empates."
)
if not (MOVIELENS_DIR / "ratings.csv").exists():
    st.write("Descarga para uso académico bajo las condiciones oficiales de MovieLens.")
    if st.button("Descargar dataset oficial"):
        with st.spinner("Descargando y validando..."):
            download_zip(MOVIELENS_URL, ROOT / "data/raw")
        st.rerun()
    st.stop()


@st.cache_resource
def load_model():
    _, movies = load_movielens(MOVIELENS_DIR)
    return ContentRecommender().fit(movies), movies


model, movies = load_model()
title = st.selectbox("Película de referencia", movies.title.sort_values())
st.dataframe(model.recommend(title, 10), hide_index=True, use_container_width=True)
st.caption(
    "No utiliza demografía ni historial personal. Los datos reflejan autoselección."
)
