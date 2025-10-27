# app/views/hiperparametros_dialog.py

from typing import List, Dict, Optional
import json
import numpy as np
import pandas as pd

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QWidget, QStackedLayout, QApplication
)

from PyQt5 import QtCore

# Mejora compatibilidad OpenGL (evita pantallas en negro en algunos drivers)
try:
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
except Exception:
    pass
try:
    # Si hay problemas de GPU, fuerza render por software:
    # (descomenta si sigues viendo pantalla negra)
    # QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseSoftwareOpenGL)
    pass
except Exception:
    pass


# IMPORTA WebEngine *después* de setear atributos y *antes* de instanciar QApplication
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView  # prueba de disponibilidad
    HAS_WEB = True
except Exception:
    HAS_WEB = False



# Fallback a Matplotlib si no hay WebEngine
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

# ML / métricas / modelos
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from umap import UMAP
from bertopic import BERTopic
import hdbscan
 
def _safe_hdbscan_params(n_docs: int, params: dict) -> dict:
    """Ajusta min_samples y min_cluster_size para no romper con pocos documentos."""
    base_mcs = int(params.get("min_cluster_size", 5))
    base_ms  = params.get("min_samples", None)

    # min_cluster_size ∈ [2, n_docs]
    mcs = max(2, min(base_mcs, max(2, n_docs)))

    # min_samples ∈ [1, n_docs-1]
    if base_ms is None:
        # si no lo pasan, usa algo razonable relativo a mcs
        ms = max(1, min(max(1, mcs // 2), max(1, n_docs - 1)))
    else:
        ms = max(1, min(int(base_ms), max(1, n_docs - 1)))

    return {
        "min_cluster_size": mcs,
        "min_samples": ms,
        "cluster_selection_epsilon": float(params.get("cluster_selection_epsilon", 0.0)),
        "metric": params.get("metric", "euclidean"),
    }

def _metrics_safe(X: np.ndarray, labels: np.ndarray, is_hdbscan: bool) -> dict:
    """Calcula métricas de forma segura. Devuelve np.nan si no aplica."""
    try:
        labels = np.asarray(labels)
        if is_hdbscan:
            core_mask = labels != -1
            Xm = X[core_mask]
            ym = labels[core_mask]
        else:
            Xm = X
            ym = labels

        # Deben existir al menos 2 clusters distintos y >= 3 muestras
        if Xm.shape[0] < 3 or len(np.unique(ym)) < 2:
            return {"silhouette": np.nan, "calinski_harabasz": np.nan, "davies_bouldin": np.nan}

        return {
            "silhouette": float(silhouette_score(Xm, ym)),
            "calinski_harabasz": float(calinski_harabasz_score(Xm, ym)),
            "davies_bouldin": float(davies_bouldin_score(Xm, ym)),
        }
    except Exception:
        return {"silhouette": np.nan, "calinski_harabasz": np.nan, "davies_bouldin": np.nan} 
    
 
# ---------- helpers de métricas ----------
def compute_silhouette_score(X: np.ndarray, labels: np.ndarray) -> float:
    try:
        # Requiere >=2 clusters y ≥2 muestras por cluster
        labs = np.asarray(labels)
        uniq = np.unique(labs)
        if len(uniq) < 2:
            return np.nan
        return float(silhouette_score(X, labs))
    except Exception:
        return np.nan

def compute_calinski_harabasz_score(X: np.ndarray, labels: np.ndarray) -> float:
    try:
        labs = np.asarray(labels)
        uniq = np.unique(labs)
        if len(uniq) < 2:
            return np.nan
        return float(calinski_harabasz_score(X, labs))
    except Exception:
        return np.nan

def compute_davies_bouldin_score(X: np.ndarray, labels: np.ndarray) -> float:
    try:
        labs = np.asarray(labels)
        uniq = np.unique(labs)
        if len(uniq) < 2:
            return np.nan
        return float(davies_bouldin_score(X, labs))
    except Exception:
        return np.nan


# ---------- genera un grid rápido de hiperparámetros ----------
def default_grid(algorithm: str) -> List[Dict]:
    if algorithm.upper() == "KMEANS":
        # Para 100 docs o menos, rangos pequeños
        grid = []
        for k in [3, 5, 7, 10]:
            grid.append({
                "algorithm": "KMEANS",
                "params": {"n_clusters": k, "init": "k-means++", "n_init": 10, "max_iter": 300}
            })
        return grid

    # HDBSCAN
    combos = [
        {"min_cluster_size": 3, "min_samples": 5, "cluster_selection_epsilon": 0.01, "metric": "euclidean"},
        {"min_cluster_size": 6, "min_samples": 5, "cluster_selection_epsilon": 0.01, "metric": "euclidean"},
        {"min_cluster_size": 8, "min_samples": 5, "cluster_selection_epsilon": 0.01, "metric": "euclidean"},
        {"min_cluster_size": 10, "min_samples": 5, "cluster_selection_epsilon": 0.01, "metric": "euclidean"},
    ]
    grid = []
    for p in combos:
        grid.append({
            "algorithm": "HDBSCAN",
            "params": p
        })
    return grid


# ---------- evalúa el grid con el algoritmo para llenar la tabla ----------
def eval_hyperparam_grid(X: np.ndarray, algorithm: str, grid: List[Dict]) -> List[Dict]:
    rows = []
    n = X.shape[0]
    for i, g in enumerate(grid):
        algo = g["algorithm"].upper()
        params = dict(g["params"])
        row = {"id": f"{algo}-{i+1}", "algorithm": algo, "params": params}
        try:
            if algo == "KMEANS":
                model = KMeans(**params)
                labels = model.fit_predict(X)
                row["labels"] = labels
                # n_clusters = clusters distintos
                row["n_clusters"] = int(len(np.unique(labels))) if n > 0 else 0
                # métricas seguras
                met = _metrics_safe(X, labels, is_hdbscan=False)
            else:
                safe_p = _safe_hdbscan_params(n, params)
                model = hdbscan.HDBSCAN(**safe_p)
                labels = model.fit_predict(X)
                row["labels"] = labels
                core = labels[labels != -1]
                row["n_clusters"] = int(len(np.unique(core))) if core.size > 0 else 0
                met = _metrics_safe(X, labels, is_hdbscan=True)

            row.update(met)
            row["status"] = ""
        except Exception as e:
            row["labels"] = None
            row["n_clusters"] = 0
            row["silhouette"] = np.nan
            row["calinski_harabasz"] = np.nan
            row["davies_bouldin"] = np.nan
            row["status"] = f"error: {e}"
        rows.append(row)
    return rows

# ---------- diálogo principal ----------
class ClusteringHyperparamsDialog(QDialog):
    params_selected = pyqtSignal(dict)  # {'algorithm': 'HDBSCAN'|'KMEANS', 'params': {...}}

    def __init__(self, X: np.ndarray, docs_texts: Optional[List[str]] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Visualizar hiperparámetros")
        self._web_views = [] 
        self.resize(1000, 700)

        try:
            from app.utils.styles import Styles
            self.setStyleSheet(Styles.DIALOG_RESULTS)
        except Exception:
            pass

        self.X = X                          # embeddings (n_docs, dim)
        self.docs_texts = docs_texts or []  # lista de textos, opcional (pero necesaria para BERTopic)
        self._rows: List[dict] = []
        self._algo = "HDBSCAN"

        self._setup_ui()
        self._populate_default_grid_and_eval()

    # ---------- UI ----------
    def _setup_ui(self):
        root = QVBoxLayout(self)

        info = QLabel("Explora combinaciones de hiperparámetros. Selecciona una fila para ver los plots de BERTopic con esos parámetros.")
        info.setWordWrap(True)
        root.addWidget(info)

        top = QHBoxLayout()
        self.cmb_algo = QComboBox()
        self.cmb_algo.addItems(["HDBSCAN", "KMEANS"])
        self.chk_umap = QCheckBox("Usar UMAP en BERTopic")
        self.chk_umap.setChecked(True)
        self.btn_update = QPushButton("Actualizar")
        self.btn_update.clicked.connect(self._populate_default_grid_and_eval)
        top.addWidget(QLabel("Algoritmo:"))
        top.addWidget(self.cmb_algo)
        top.addStretch()
        top.addWidget(self.chk_umap)
        top.addWidget(self.btn_update)
        root.addLayout(top)

        # Tabla
        self.tbl = QTableWidget(0, 6, self)
        self.tbl.setHorizontalHeaderLabels([
            "id",  "params", "n_clusters",
            "silhouette", "calinski_harabasz", "davies_bouldin", 
        ])
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl.setSortingEnabled(True)
        root.addWidget(self.tbl, stretch=2)

        # Botonera
        row = QHBoxLayout()
        self.btn_select = QPushButton("Seleccionar")
        self.btn_select.setEnabled(False)
        self.btn_select.clicked.connect(self._on_select)
        self.btn_close = QPushButton("Cerrar")
        self.btn_close.clicked.connect(self.reject)
        row.addStretch()
        row.addWidget(self.btn_select)
        row.addWidget(self.btn_close)
        root.addLayout(row)

        # Zona inferior: carrusel de plots
        nav = QHBoxLayout()
        self.btn_prev = QPushButton("Anterior")
        self.btn_next = QPushButton("Siguiente")
        self.lbl_idx = QLabel("0 / 0")
        self.btn_prev.clicked.connect(self._prev_plot)
        self.btn_next.clicked.connect(self._next_plot)
        nav.addWidget(self.btn_prev)
        nav.addWidget(self.btn_next)
        nav.addWidget(self.lbl_idx)
        nav.addStretch()
        root.addLayout(nav)

        # Contenedor de plots (stack)
        self.stack_container = QWidget(self)
        self.stack = QStackedLayout(self.stack_container)
        root.addWidget(self.stack_container, stretch=3)

        # Overlay “cargando…”
        self.loading = QLabel("Cargando visualizaciones")
        self.loading.setAlignment(Qt.AlignCenter)
        self.loading.setStyleSheet("background: rgba(0,0,0,0.55); color: white; padding: 16px; border-radius: 8px;")
        self.loading.setVisible(False)
        root.addWidget(self.loading)

        # Eventos tabla
        self.tbl.itemSelectionChanged.connect(self._on_table_selection_changed)
        self.tbl.cellDoubleClicked.connect(lambda r, c: self._on_select())

    # ---------- grid + métricas ----------
    def _populate_default_grid_and_eval(self):
        self._algo = self.cmb_algo.currentText().upper()
        grid = default_grid(self._algo)
        self._rows = eval_hyperparam_grid(self.X, self._algo, grid)
        self._fill_table(self._rows)
        self._clear_plots()

    def _fill_table(self, rows: List[dict]):
        self.tbl.setSortingEnabled(False)
        self.tbl.setRowCount(len(rows))
        for r, row in enumerate(rows):
            vals = [
                row.get("id", ""),
                
                json.dumps(row.get("params", {}), ensure_ascii=False),
                str(row.get("n_clusters", 0)),
                self._fmt(row.get("silhouette")),
                self._fmt(row.get("calinski_harabasz")),
                self._fmt(row.get("davies_bouldin")),
               
            ]
            for c, v in enumerate(vals):
                it = QTableWidgetItem(v)
                if c in (3,4,5,6):
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tbl.setItem(r, c, it)
        self.tbl.setSortingEnabled(True)
        self.btn_select.setEnabled(False)

    # ---------- selección ----------
    def _on_table_selection_changed(self):
        has_sel = bool(self.tbl.selectedIndexes())
        self.btn_select.setEnabled(has_sel)
        if not has_sel:
            self._clear_plots()
            return
        # muestra plots de la fila seleccionada
        self._build_plots_for_current_row()

    def _on_select(self):
        row = self.tbl.currentRow()
        if row < 0 or row >= len(self._rows):
            return
        selected = self._rows[row]
        payload = {
            "algorithm": selected.get("algorithm", "HDBSCAN"),
            "params": dict(selected.get("params", {}))
        }
        self.params_selected.emit(payload)

    # ---------- plots ----------
    def _clear_plots(self):
        while self.stack.count():
            w = self.stack.widget(0)
            self.stack.removeWidget(w)
            w.setParent(None)
        self._plot_count = 0
        self._plot_index = 0
        self._update_index_label()

    def _prev_plot(self):
        if self._plot_count == 0:
            return
        self._plot_index = (self._plot_index - 1) % self._plot_count
        self.stack.setCurrentIndex(self._plot_index)
        self._update_index_label()

    def _next_plot(self):
        if self._plot_count == 0:
            return
        self._plot_index = (self._plot_index + 1) % self._plot_count
        self.stack.setCurrentIndex(self._plot_index)
        self._update_index_label()

    def _update_index_label(self):
        if self._plot_count == 0:
            self.lbl_idx.setText("0 / 0")
        else:
            self.lbl_idx.setText(f"{self._plot_index+1} / {self._plot_count}")

    def _build_plots_for_current_row(self):
        if not self.docs_texts or len(self.docs_texts) != len(self.X):
            self._build_fallback_matplotlib(rowd, err="Longitudes X/docs no coinciden")
            return
        row = self.tbl.currentRow()
        if row < 0 or row >= len(self._rows):
            self._clear_plots()
            return

        rowd = self._rows[row]
        algo = rowd.get("algorithm", "HDBSCAN").upper()
        params = dict(rowd.get("params", {}))
        use_umap = self.chk_umap.isChecked()

        # Si no hay textos, no se pueden hacer los plots de BERTopic
        if not self.docs_texts or len(self.docs_texts) != len(self.X):
            # fallback: scatter + barras con matplotlib (sin nombres de tópico)
            self._build_fallback_matplotlib(rowd)
            return

        # Mostrar overlay de carga
        self.loading.setVisible(True)
        QApplication.processEvents()

        try:
            # 1) Construir el BERTopic con los hiperparámetros del usuario
            topic_model = self._build_bertopic(algo, params, use_umap)

            # 2) Fit con los embeddings y docs ya dados (no bloquea mucho; si tu dataset crece, pásalo a un worker)
            topics, probs = topic_model.fit_transform(self.docs_texts, embeddings=self.X)

            # 3) Plots BERTopic (Plotly) — intentamos QWebEngine
            figs = []

            # visualize_documents: con reduced_embeddings si hay UMAP
            if use_umap:
                reducer = UMAP(n_neighbors=10, n_components=2, min_dist=0.0, metric='cosine')
                red = reducer.fit_transform(self.X)
                figs.append(topic_model.visualize_documents(self.docs_texts, reduced_embeddings=red))
            else:
                figs.append(topic_model.visualize_documents(self.docs_texts, embeddings=self.X))

            # visualize_barchart
            figs.append(topic_model.visualize_barchart())

            # hierarchy (más robusto que topics_per_class si no tienes “classes”)
            figs.append(topic_model.visualize_hierarchy())

            # 4) Pintar en el stack
            self._clear_plots()
            for fig in figs:
                self._add_plotly(fig)
            self.stack.setCurrentIndex(0)
            self._plot_count = len(figs)
            self._plot_index = 0
            self._update_index_label()

        except Exception as e:
            # Si algo falla (p.ej. sin WebEngine), caemos a fallback matplotlib
            self._build_fallback_matplotlib(rowd, err=str(e))
        finally:
            self.loading.setVisible(False)

    def _build_bertopic(self, algorithm: str, params: Dict, use_umap: bool) -> BERTopic:
        umap_model = None
        if use_umap:
            # Esta UMAP se usa dentro del pipeline de BERTopic (recomendable si luego usas visualize_documents sin pasar reduced_embeddings)
            umap_model = UMAP(n_neighbors=10, n_components=2, min_dist=0.0, metric="cosine", random_state=42)

        if algorithm == "KMEANS":
            cluster_model = KMeans(**params)
            topic_model = BERTopic(
                embedding_model=None,      # ya tenemos embeddings
                cluster_model=cluster_model,
                umap_model=umap_model,
                verbose=False
            )
        else:
            # HDBSCAN: usar hdbscan_model
            
            n_docs = self.X.shape[0]  # o X.shape[0] según tu contexto
            safe_p = _safe_hdbscan_params(n_docs, params) 
           
            hdbscan_model = hdbscan.HDBSCAN(**safe_p)
            topic_model = BERTopic(
                embedding_model=None,
                hdbscan_model=hdbscan_model,
                umap_model=umap_model,
                verbose=False
            )
        return topic_model

    # ---------- render helpers ----------
    def _add_plotly(self, fig):
        """Inserta un plotly Figure en el stack, usando QWebEngineView si existe."""
        if HAS_WEB:
            html = fig.to_html(include_plotlyjs="cdn", full_html=False)
            view = QWebEngineView(self)
            view.setHtml(html)
            self.stack.addWidget(view)
          
            self._web_views.append(view) 
        else:
            # Fallback simple: exportar a imagen estática en matplotlib (menos bonito)
            can = FigureCanvas(plt.Figure(figsize=(6,4)))
            ax = can.figure.add_subplot(111)
            ax.text(0.5, 0.5, "Plotly no disponible.\nInstala PyQtWebEngine.", ha="center", va="center")
            ax.set_axis_off()
            self.stack.addWidget(can)

    def _build_fallback_matplotlib(self, rowd: dict, err: Optional[str]=None):
        """Scatter PCA por clúster y barras de tamaños + métricas (sin BERTopic)."""
        self._clear_plots()

        labels = rowd.get("labels")
        if labels is None:
            can = FigureCanvas(plt.Figure(figsize=(6,4)))
            ax = can.figure.add_subplot(111)
            ax.text(0.5, 0.5, f"No hay labels. {err or ''}", ha="center", va="center")
            ax.set_axis_off()
            self.stack.addWidget(can)
            self._plot_count = 1
            self._plot_index = 0
            self._update_index_label()
            return

        # 1) scatter PCA
        X2 = self._pca2(self.X)
        can1 = FigureCanvas(plt.Figure(figsize=(6,4)))
        ax1 = can1.figure.add_subplot(111)
        labs = np.asarray(labels)
        uniq = np.unique(labs)
        for lab in uniq:
            m = labs == lab
            if lab == -1:
                ax1.scatter(X2[m,0], X2[m,1], s=10, alpha=0.3, c="lightgray", label="ruido (-1)")
            else:
                ax1.scatter(X2[m,0], X2[m,1], s=16, alpha=0.85, label=f"cluster {lab}")
        ax1.set_title("Proyección 2D (PCA)")
        ax1.legend(loc="best", fontsize=8, ncol=2)
        self.stack.addWidget(can1)

        # 2) barras tamaño clusters
        can2 = FigureCanvas(plt.Figure(figsize=(6,3)))
        ax2 = can2.figure.add_subplot(111)
        core = labs[labs != -1]
        if core.size > 0:
            u, c = np.unique(core, return_counts=True)
            ax2.bar([str(int(x)) for x in u], c)
            ax2.set_title("Tamaño de clúster (sin ruido)")
            ax2.set_xlabel("cluster")
            ax2.set_ylabel("#docs")
        else:
            ax2.text(0.5, 0.5, "Todos ruido (-1).", ha="center", va="center")
            ax2.set_axis_off()
        self.stack.addWidget(can2)

        # 3) barras métricas
        can3 = FigureCanvas(plt.Figure(figsize=(6,3)))
        ax3 = can3.figure.add_subplot(111)
        sil = rowd.get("silhouette", np.nan)
        cal = rowd.get("calinski_harabasz", np.nan)
        dav = rowd.get("davies_bouldin", np.nan)
        xs = ["silhouette", "calinski", "davies"]
        vals = [0 if np.isnan(sil) else sil, 0 if np.isnan(cal) else cal, 0 if np.isnan(dav) else dav]
        ax3.bar(xs, vals)
        ax3.set_title("Métricas (0 si no aplica)")
        self.stack.addWidget(can3)

        self._plot_count = 3
        self._plot_index = 0
        self.stack.setCurrentIndex(0)
        self._update_index_label()

    @staticmethod
    def _pca2(X):
        from sklearn.decomposition import PCA
        return PCA(n_components=2, random_state=42).fit_transform(X)

    @staticmethod
    def _fmt(x):
        try:
            if x is None or np.isnan(x):
                return ""
            return f"{float(x):.4f}"
        except Exception:
            return ""
