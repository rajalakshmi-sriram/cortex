"""
Cortex Desktop Application - PyQt6 GUI
General-purpose AI-assisted research workspace
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QTextBrowser, QComboBox,
    QFrame, QMessageBox, QProgressBar, QButtonGroup, QStackedWidget,
    QListWidget, QListWidgetItem, QCheckBox, QScrollArea, QColorDialog,
    QAbstractItemView, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QSize, QUrl, QRect, QPoint
from PyQt6.QtWidgets import QLayout, QSizePolicy
from PyQt6.QtGui import QIcon, QDesktopServices, QPixmap, QColor

import requests
from requests.exceptions import RequestException

ICONS_DIR = Path(__file__).parent / "resources" / "icons"

# --- Warm, pastel, paper-like palette. Each section carries its own accent
# color rather than one repeated brand color everywhere. ---
PAGE_BG = "#faf6ef"
SIDEBAR_BG = "#f3ede0"
CARD_BG = "#fffdf8"
BORDER = "#e6dcc8"
TEXT = "#3d372e"
TEXT_MUTED = "#8c8172"

ROSE, ROSE_TINT = "#c97b66", "#f3ddd0"
SAGE, SAGE_TINT = "#7c9a72", "#e2ebda"
BLUE, BLUE_TINT = "#6f93b3", "#dce8f0"
SAND, SAND_TINT = "#b8923f", "#f1e6c9"

ACCENTS = {
    'rose': (ROSE, ROSE_TINT),
    'sage': (SAGE, SAGE_TINT),
    'blue': (BLUE, BLUE_TINT),
    'sand': (SAND, SAND_TINT),
}

GOOD, GOOD_TINT = SAGE, SAGE_TINT
WARN, WARN_TINT = SAND, SAND_TINT
BAD, BAD_TINT = ROSE, ROSE_TINT

SERIF = '"Iowan Old Style", Georgia, "Times New Roman", serif'
SANS = '-apple-system, "Helvetica Neue", sans-serif'

RESEARCH_TYPE_CHOICES = [
    ('theoretical', 'Theoretical Research'),
    ('experimental', 'Experimental Research'),
    ('exploratory', 'Exploratory Research'),
    ('pilot', 'Pilot Research'),
    ('literature_review', 'Literature Review'),
    ('clinical', 'Clinical Research'),
]

# Static, curated external tool suggestions shown on each page - independent
# of research type or methodology step. These are reference chips (open a
# URL); they don't require a server round-trip since they never change per
# project.
PAGE_TOOLS = {
    'literature': [
        {'name': 'Semantic Scholar', 'url': 'https://www.semanticscholar.org', 'description': 'AI-powered search across 200M+ papers with TL;DR summaries'},
        {'name': 'Consensus', 'url': 'https://consensus.app', 'description': 'Answers research questions from peer-reviewed evidence'},
        {'name': 'Elicit', 'url': 'https://elicit.com', 'description': 'AI research assistant - automates systematic reviews, extracts data'},
        {'name': 'Google Scholar', 'url': 'https://scholar.google.com', 'description': 'General academic search'},
        {'name': 'Research Rabbit', 'url': 'https://www.researchrabbit.ai', 'description': 'Visual maps of related papers/authors'},
        {'name': 'Litmaps', 'url': 'https://www.litmaps.com', 'description': 'Visualize citation networks, find gaps'},
        {'name': 'Connected Papers', 'url': 'https://www.connectedpapers.com', 'description': 'Visual citation graph explorer'},
    ],
    'paper_library': [
        {'name': 'Zotero', 'url': 'https://www.zotero.org', 'description': 'Reference manager & citation library'},
        {'name': 'EndNote', 'url': 'https://endnote.com', 'description': 'Reference manager for large libraries & team sharing'},
        {'name': 'SciSpace', 'url': 'https://scispace.com', 'description': 'AI PDF reader - explains text, equations, and methods'},
        {'name': 'NotebookLM', 'url': 'https://notebooklm.google.com', 'description': 'Upload PDFs to build study guides & explore sources'},
    ],
    'hypotheses': [
        {'name': 'Elicit', 'url': 'https://elicit.com', 'description': 'AI research assistant for idea generation & hypothesis brainstorming'},
        {'name': 'Consensus', 'url': 'https://consensus.app', 'description': 'Check the evidence base before committing to a hypothesis'},
    ],
    'tasks': [
        {'name': 'Trello', 'url': 'https://trello.com', 'description': 'Simple Kanban-style task boards'},
        {'name': 'Notion', 'url': 'https://www.notion.so', 'description': 'All-in-one docs, tasks, and project tracking'},
        {'name': 'Asana', 'url': 'https://asana.com', 'description': 'Team task & project management'},
    ],
    'data_analysis': [
        {'name': 'JASP', 'url': 'https://jasp-stats.org', 'description': 'Free spreadsheet-style stats software - no coding required'},
        {'name': 'jamovi', 'url': 'https://www.jamovi.org', 'description': 'Free stats software built on R - no coding required'},
        {'name': 'RStudio', 'url': 'https://posit.co/products/open-source/rstudio/', 'description': 'R programming IDE for statistics'},
    ],
    'manuscript': [
        {'name': 'Overleaf', 'url': 'https://www.overleaf.com', 'description': 'Collaborative LaTeX manuscript editor'},
        {'name': 'Scite', 'url': 'https://scite.ai', 'description': 'Smart Citations - shows support/contradiction across papers'},
        {'name': 'Jenni AI', 'url': 'https://jenni.ai', 'description': 'AI writing editor with suggested in-text citations'},
        {'name': 'Paperpal', 'url': 'https://paperpal.com', 'description': 'Grammar, tone, and journal submission readiness'},
        {'name': 'Grammarly', 'url': 'https://www.grammarly.com', 'description': 'Writing/grammar assistant'},
    ],
    'journals': [
        {'name': 'Think. Check. Submit.', 'url': 'https://thinkchecksubmit.org', 'description': 'Checklist to verify a journal is legitimate before submitting'},
        {'name': 'DOAJ', 'url': 'https://doaj.org', 'description': 'Directory of Open Access Journals - verify legitimate OA journals'},
    ],
}

STYLESHEET = f"""
QWidget {{
    background-color: {PAGE_BG};
    color: {TEXT};
    font-family: {SANS};
    font-size: 13px;
}}

QLabel {{
    background-color: transparent;
}}

#sidebar {{
    background-color: {SIDEBAR_BG};
    border-right: 1px solid {BORDER};
}}

#sidebarBrand {{
    font-family: {SERIF};
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1.5px;
}}

#sidebarTagline {{
    color: {TEXT_MUTED};
    font-size: 11px;
    font-style: italic;
}}

QPushButton#navButton {{
    text-align: left;
    padding: 9px 12px;
    border-radius: 10px;
    border: none;
    background-color: transparent;
    color: {TEXT_MUTED};
    font-size: 12px;
    font-weight: 600;
}}

QPushButton#navButton:hover {{
    background-color: #ece3d1;
    color: {TEXT};
}}

QPushButton#navButton[accent="rose"]:checked {{ background-color: {ROSE_TINT}; color: #8a4c3a; }}
QPushButton#navButton[accent="sage"]:checked {{ background-color: {SAGE_TINT}; color: #4c6444; }}
QPushButton#navButton[accent="blue"]:checked {{ background-color: {BLUE_TINT}; color: #3f5e77; }}
QPushButton#navButton[accent="sand"]:checked {{ background-color: {SAND_TINT}; color: #7a5f1f; }}

QPushButton#backButton {{
    text-align: left;
    padding: 6px 8px;
    border-radius: 8px;
    border: none;
    background-color: transparent;
    color: {TEXT_MUTED};
    font-size: 11px;
    font-weight: 600;
}}
QPushButton#backButton:hover {{ background-color: #ece3d1; color: {TEXT}; }}

#topBar {{
    background-color: {PAGE_BG};
    border-bottom: 1px solid {BORDER};
}}

#pageTitle {{
    font-family: {SERIF};
    font-size: 21px;
    font-weight: 700;
}}

#pageSubtitle {{
    color: {TEXT_MUTED};
    font-size: 12px;
    font-style: italic;
}}

#cardShadow {{ border-radius: 14px; }}

#card {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 14px;
}}

#cardTitle {{
    font-family: {SERIF};
    font-size: 15px;
    font-weight: 700;
}}

#cardHint {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}

QLineEdit, QTextEdit {{
    background-color: #fbf8f2;
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 10px 12px;
    color: {TEXT};
    selection-background-color: {SAND_TINT};
}}

QTextBrowser {{
    background-color: #fbf8f2;
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 8px;
}}

QListWidget {{
    background-color: #fbf8f2;
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 4px;
    outline: none;
}}
QListWidget::item {{
    padding: 9px 10px;
    border-radius: 8px;
    margin: 2px 0px;
}}
QListWidget::item:selected {{
    background-color: {SAND_TINT};
    color: {TEXT};
}}

QCheckBox {{ spacing: 10px; padding: 4px 0px; }}
QCheckBox::indicator {{
    width: 17px; height: 17px; border-radius: 5px;
    border: 1.5px solid {BORDER}; background-color: #fbf8f2;
}}
QCheckBox::indicator:checked {{ background-color: {SAGE}; border-color: {SAGE}; }}

QComboBox {{
    background-color: #fbf8f2;
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 9px 12px;
    color: {TEXT};
}}

QComboBox::drop-down {{ border: none; width: 28px; }}

QComboBox::down-arrow {{
    image: url({(ICONS_DIR / 'chevron_down.svg').as_posix()});
    width: 12px; height: 12px;
}}

QComboBox QAbstractItemView {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 8px;
    selection-background-color: {SAND_TINT};
    selection-color: {TEXT};
    outline: none;
    padding: 4px;
}}

QPushButton#primaryButton {{
    color: white; border: none; border-radius: 10px;
    padding: 11px 18px; font-size: 13px; font-weight: 700;
}}
QPushButton#primaryButton[accent="rose"] {{ background-color: {ROSE}; }}
QPushButton#primaryButton[accent="rose"]:hover {{ background-color: #b96952; }}
QPushButton#primaryButton[accent="sage"] {{ background-color: {SAGE}; }}
QPushButton#primaryButton[accent="sage"]:hover {{ background-color: #6a8862; }}
QPushButton#primaryButton[accent="blue"] {{ background-color: {BLUE}; }}
QPushButton#primaryButton[accent="blue"]:hover {{ background-color: #5c81a1; }}
QPushButton#primaryButton[accent="sand"] {{ background-color: {SAND}; }}
QPushButton#primaryButton[accent="sand"]:hover {{ background-color: #a17f34; }}

QPushButton#linkButton {{
    background-color: #fbf8f2;
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 10px 12px;
    text-align: left;
    font-weight: 600;
}}
QPushButton#linkButton:hover {{ border: 1px solid {SAND}; background-color: {SAND_TINT}; }}

QPushButton#toolChip {{
    background-color: transparent;
    border: 1px dashed {BORDER};
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
    color: {TEXT_MUTED};
}}
QPushButton#toolChip:hover {{ border: 1px dashed {BLUE}; color: {BLUE}; }}

QPushButton#toolChipCustom {{
    background-color: {SAGE_TINT};
    border: 1px solid {SAGE};
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
    color: #4c6444;
    font-weight: 600;
}}
QPushButton#toolChipCustom:hover {{ background-color: {SAGE}; color: white; }}

QPushButton#toolChipRemove {{
    background-color: transparent;
    border: none;
    color: {TEXT_MUTED};
    font-size: 13px;
    font-weight: 700;
    padding: 0;
}}
QPushButton#toolChipRemove:hover {{ color: {BAD}; }}

QProgressBar {{
    background-color: #ece3d1; border: none; border-radius: 4px; height: 6px;
}}
QProgressBar::chunk {{ background-color: {SAND}; border-radius: 4px; }}

QLabel#charCount {{ color: {TEXT_MUTED}; font-size: 11px; }}
QLabel#fieldLabel {{ color: {TEXT_MUTED}; font-size: 11px; font-weight: 600; margin-top: 4px; }}

QScrollBar:vertical {{ background: transparent; width: 10px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 5px; min-height: 24px; }}
QScrollBar::handle:vertical:hover {{ background: {SAND}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

QStatusBar {{
    background-color: {SIDEBAR_BG};
    border-top: 1px solid {BORDER};
    color: {TEXT_MUTED};
}}
"""


def make_card(title: str, hint: str = "", accent: str = "sand") -> tuple:
    """Card with a flat offset 'sticker' shadow in the section's accent tint."""
    _, tint = ACCENTS.get(accent, (SAND, SAND_TINT))

    shadow = QFrame()
    shadow.setObjectName("cardShadow")
    shadow.setStyleSheet(f"#cardShadow {{ background-color: {tint}; border-radius: 14px; }}")
    shadow_layout = QVBoxLayout(shadow)
    shadow_layout.setContentsMargins(0, 0, 6, 6)
    shadow_layout.setSpacing(0)

    card = QFrame()
    card.setObjectName("card")
    shadow_layout.addWidget(card)

    outer = QVBoxLayout(card)
    outer.setContentsMargins(20, 18, 20, 20)
    outer.setSpacing(12)

    if title:
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        outer.addWidget(title_label)

    if hint:
        hint_label = QLabel(hint)
        hint_label.setObjectName("cardHint")
        hint_label.setWordWrap(True)
        outer.addWidget(hint_label)

    return shadow, outer


def make_tool_chip(name: str, url: str, description: str = "", custom: bool = False, on_remove=None) -> QWidget:
    """A small pill button that opens an external tool link. 'custom' chips
    (user-attached) render solid with a remove button; curated suggestions
    render dashed/muted since they're recommendations, not the user's data."""
    chip = QWidget()
    chip_layout = QHBoxLayout(chip)
    chip_layout.setContentsMargins(0, 0, 0, 0)
    chip_layout.setSpacing(2)

    btn = QPushButton(name)
    btn.setObjectName("toolChipCustom" if custom else "toolChip")
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    if description:
        btn.setToolTip(description)
    if url:
        btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
    else:
        btn.setEnabled(False)
    chip_layout.addWidget(btn)

    if custom and on_remove:
        remove_btn = QPushButton("×")
        remove_btn.setObjectName("toolChipRemove")
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.setFixedWidth(18)
        remove_btn.clicked.connect(on_remove)
        chip_layout.addWidget(remove_btn)

    return chip


def build_tools_card(title: str, hint: str, tools: List[Dict], accent: str) -> QWidget:
    """A card showing a wrapping row of curated tool-link chips - used to give
    every page its own set of relevant external tool suggestions."""
    card, card_layout = make_card(title, hint, accent=accent)
    flow = FlowLayout(margin=0, spacing=6)
    for tool in tools:
        flow.addWidget(make_tool_chip(tool['name'], tool.get('url', ''), tool.get('description', '')))
    card_layout.addLayout(flow)
    return card


def icon(name: str) -> QIcon:
    return QIcon((ICONS_DIR / name).as_posix())


def primary_button(text: str, accent: str, icon_name: str = "send.svg") -> QPushButton:
    btn = QPushButton(f"  {text}")
    btn.setObjectName("primaryButton")
    btn.setProperty("accent", accent)
    btn.setIcon(icon(icon_name))
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn


def scrollable(widget: QWidget) -> QScrollArea:
    """Wrap a widget in a borderless, resizable scroll area so tall content
    (long forms, many list items) is always reachable regardless of window size."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setWidget(widget)
    return scroll


class FlowLayout(QLayout):
    """A layout that wraps child widgets onto new lines as needed - used for
    tool-chip rows where the number of chips varies and can't fit on one line."""

    def __init__(self, parent=None, margin=0, spacing=6):
        super().__init__(parent)
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect, test_only):
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(left, top, -right, -bottom)
        x, y = effective_rect.x(), effective_rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self._items:
            widget = item.widget()
            next_x = x + item.sizeHint().width() + spacing
            if next_x - spacing > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y += line_height + spacing
                next_x = x + item.sizeHint().width() + spacing
                line_height = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y() + bottom


class APIWorker(QThread):
    """Worker thread for API calls (GET/POST/PUT/DELETE)"""

    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, url: str, method: str = "GET", data: dict = None):
        super().__init__()
        self.url = url
        self.method = method.upper()
        self.data = data

    def run(self):
        try:
            if self.method == "POST":
                response = requests.post(self.url, json=self.data, timeout=30)
            elif self.method == "PUT":
                response = requests.put(self.url, json=self.data, timeout=30)
            elif self.method == "DELETE":
                response = requests.delete(self.url, timeout=30)
            else:
                response = requests.get(self.url, timeout=30)

            if response.status_code >= 400:
                # The server is reachable and responded - surface its actual
                # error message (e.g. "needs exactly 2 groups...") instead of
                # a generic "is the server running?" message, which would be
                # actively misleading here.
                try:
                    server_message = response.json().get('message', response.text)
                except ValueError:
                    server_message = response.text or f"HTTP {response.status_code}"
                self.error_occurred.emit(server_message)
                return

            self.result_ready.emit(response.json() if response.content else {})
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            self.error_occurred.emit(f"Could not reach the Cortex server: {str(e)}\n\nMake sure it's running:\npython run.py")
        except RequestException as e:
            self.error_occurred.emit(f"API Error: {str(e)}")
        except Exception as e:
            self.error_occurred.emit(f"Error: {str(e)}")


def error_html(message: str) -> str:
    return (
        f"<div style='color:{BAD}; font-weight:600;'>&#9888; Error</div>"
        f"<div style='color:{TEXT_MUTED}; margin-top:6px;'>{message}</div>"
    )


def metric_bar_html(label: str, value: float, color: str) -> str:
    pct = max(0, min(100, round(value * 100)))
    return f"""
        <table width='100%' cellspacing='0' cellpadding='0' style='margin-top:4px;'>
        <tr>
            <td style='font-size:11px; color:{TEXT_MUTED}; width:120px;'>{label}</td>
            <td style='font-size:11px; color:{TEXT_MUTED};'>
                <table width='100%' cellspacing='0' cellpadding='0'><tr>
                    <td style='background-color:{color}; height:6px; width:{pct}%;'></td>
                    <td style='background-color:#ece3d1; height:6px;'></td>
                </tr></table>
            </td>
            <td style='font-size:11px; color:{TEXT_MUTED}; width:42px; text-align:right;'>{pct}%</td>
        </tr>
        </table>
    """


# ============================================================================
# Generic CRUD list widget: powers Tasks, Paper Library, Hypotheses, Journals
# ============================================================================

class CrudListTab(QWidget):
    """A reusable 'add form + list + delete' page bound to a project sub-resource"""

    def __init__(self, api_base_url: str, resource: str, title: str, hint: str,
                 accent: str, fields: List[Dict], renderer, tools: Optional[List[Dict]] = None,
                 tools_title: str = "Related Tools"):
        super().__init__()
        self.api_base_url = api_base_url
        self.resource = resource
        self.fields = fields
        self.renderer = renderer
        self.project_id: Optional[str] = None
        self.inputs = {}
        self._workers = []
        self.init_ui(title, hint, accent, tools, tools_title)

    def init_ui(self, title, hint, accent, tools=None, tools_title="Related Tools"):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(16)

        if tools:
            layout.addWidget(build_tools_card(tools_title, "", tools, accent=accent))

        form_card, form_layout = make_card(title, hint, accent=accent)

        for f in self.fields:
            label = QLabel(f['label'])
            label.setObjectName("fieldLabel")
            form_layout.addWidget(label)

            if f['kind'] == 'combo':
                w = QComboBox()
                w.addItems(f['options'])
            elif f['kind'] == 'multiline':
                w = QTextEdit()
                w.setFixedHeight(60)
                w.setPlaceholderText(f.get('placeholder', ''))
            else:
                w = QLineEdit()
                w.setPlaceholderText(f.get('placeholder', ''))

            self.inputs[f['key']] = w
            form_layout.addWidget(w)

        row = QHBoxLayout()
        add_btn = primary_button(f"Add", accent)
        add_btn.clicked.connect(self.add_item)
        row.addWidget(add_btn)
        row.addStretch()
        form_layout.addLayout(row)

        layout.addWidget(form_card)

        list_card, list_layout = make_card(f"Saved Entries", accent=accent)
        self.list_widget = QListWidget()
        list_layout.addWidget(self.list_widget)

        del_row = QHBoxLayout()
        del_btn = QPushButton("  Delete Selected")
        del_btn.setObjectName("linkButton")
        del_btn.setIcon(icon("trash.svg"))
        del_btn.setIconSize(QSize(15, 15))
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.clicked.connect(self.delete_selected)
        del_row.addWidget(del_btn)
        del_row.addStretch()
        list_layout.addLayout(del_row)

        layout.addWidget(list_card, stretch=1)

    def set_project(self, project_id: str):
        self.project_id = project_id
        self.refresh()

    def refresh(self):
        if not self.project_id:
            return
        self._refresh_worker = APIWorker(f"{self.api_base_url}/api/v1/projects/{self.project_id}/{self.resource}")
        self._refresh_worker.result_ready.connect(self._populate)
        self._refresh_worker.start()

    def _populate(self, result: Dict[str, Any]):
        items = result.get(self.resource, [])
        self.list_widget.clear()
        for item in items:
            list_item = QListWidgetItem(self.renderer(item))
            list_item.setData(Qt.ItemDataRole.UserRole, item.get('id'))
            self.list_widget.addItem(list_item)

    def _gather_payload(self) -> Dict:
        payload = {}
        for f in self.fields:
            w = self.inputs[f['key']]
            if isinstance(w, QComboBox):
                payload[f['key']] = w.currentText()
            elif isinstance(w, QTextEdit):
                payload[f['key']] = w.toPlainText().strip()
            else:
                payload[f['key']] = w.text().strip()
        return payload

    def _clear_form(self):
        for f in self.fields:
            w = self.inputs[f['key']]
            if isinstance(w, QComboBox):
                w.setCurrentIndex(0)
            elif isinstance(w, QTextEdit):
                w.clear()
            else:
                w.clear()

    def add_item(self):
        if not self.project_id:
            return
        payload = self._gather_payload()
        first_key = self.fields[0]['key']
        if not payload.get(first_key):
            QMessageBox.warning(self, "Input Error", f"Please enter {self.fields[0]['label'].lower()}")
            return

        worker = APIWorker(
            f"{self.api_base_url}/api/v1/projects/{self.project_id}/{self.resource}",
            method="POST", data=payload
        )
        self._workers.append(worker)
        worker.result_ready.connect(lambda _r: (self._clear_form(), self.refresh()))
        worker.error_occurred.connect(lambda e: QMessageBox.critical(self, "Error", e))
        worker.start()

    def delete_selected(self):
        row = self.list_widget.currentRow()
        if row < 0:
            return
        item_id = self.list_widget.item(row).data(Qt.ItemDataRole.UserRole)

        worker = APIWorker(
            f"{self.api_base_url}/api/v1/projects/{self.project_id}/{self.resource}/{item_id}",
            method="DELETE"
        )
        self._workers.append(worker)
        worker.result_ready.connect(lambda _r: self.refresh())
        worker.start()


# ============================================================================
# Literature / idea validation page (project-aware: can save results to library)
# ============================================================================

class IdeaValidationTab(QWidget):
    """Search and validate a research idea against real published literature"""

    def __init__(self, api_base_url: str):
        super().__init__()
        self.api_base_url = api_base_url
        self.project_id: Optional[str] = None
        self._last_papers: List[Dict] = []
        self._pending_saves = 0
        self._workers = []
        self.init_ui()

    def set_project(self, project_id: str):
        self.project_id = project_id
        self._last_papers = []
        self.results_display.setHtml(
            f"<div style='color:{TEXT_MUTED};'>Results will appear here after validation.</div>"
        )

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(build_tools_card(
            "External Literature Tools",
            "Discovery, mapping, and reading tools beyond Cortex's own search.",
            PAGE_TOOLS['literature'], accent="blue"
        ))

        input_card, input_layout = make_card(
            "Search & Validate a Research Idea",
            "Enter a research idea (max 500 characters) to check its novelty against "
            "real, live-fetched literature across Europe PMC/PubMed, CrossRef, arXiv, ERIC, and Semantic Scholar "
            "(plus Scopus/ScienceDirect/Web of Science if you've configured an API key) - across any discipline.",
            accent="blue"
        )

        self.idea_input = QTextEdit()
        self.idea_input.setPlaceholderText(
            "e.g. Investigate the effect of remote work policies on employee retention in tech startups"
        )
        self.idea_input.setFixedHeight(90)
        input_layout.addWidget(self.idea_input)

        self.char_count = QLabel("0 / 500 characters")
        self.char_count.setObjectName("charCount")
        self.idea_input.textChanged.connect(self.update_char_count)
        input_layout.addWidget(self.char_count)

        row = QHBoxLayout()
        validate_btn = primary_button("Validate Idea", "blue")
        validate_btn.clicked.connect(self.validate_idea)
        row.addWidget(validate_btn)

        self.save_btn = QPushButton("  Save Results to Paper Library")
        self.save_btn.setObjectName("linkButton")
        self.save_btn.setIcon(icon("folder.svg"))
        self.save_btn.setIconSize(QSize(15, 15))
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_to_library)
        row.addWidget(self.save_btn)
        row.addStretch()
        input_layout.addLayout(row)

        self.save_status = QLabel("")
        self.save_status.setObjectName("cardHint")
        input_layout.addWidget(self.save_status)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setVisible(False)
        input_layout.addWidget(self.progress)

        layout.addWidget(input_card)

        results_card, results_layout = make_card("Validation Results", accent="blue")
        self.results_display = QTextBrowser()
        self.results_display.setOpenExternalLinks(True)
        self.results_display.setMinimumHeight(280)
        self.results_display.setHtml(
            f"<div style='color:{TEXT_MUTED};'>Results will appear here after validation.</div>"
        )
        results_layout.addWidget(self.results_display)
        layout.addWidget(results_card, stretch=1)

    def update_char_count(self):
        text = self.idea_input.toPlainText()
        self.char_count.setText(f"{len(text)} / 500 characters")
        self.char_count.setStyleSheet(f"color: {BAD};" if len(text) > 500 else "")

    def validate_idea(self):
        idea = self.idea_input.toPlainText().strip()

        if not idea:
            QMessageBox.warning(self, "Input Error", "Please enter a research idea")
            return
        if len(idea) < 10:
            QMessageBox.warning(self, "Input Error", "Idea must be at least 10 characters")
            return
        if len(idea) > 500:
            QMessageBox.warning(self, "Input Error", "Idea must not exceed 500 characters")
            return

        self.progress.setVisible(True)
        self.save_status.setText("")
        self.results_display.setHtml(
            f"<div style='color:{TEXT_MUTED};'>Searching Europe PMC, CrossRef, arXiv, ERIC, and Semantic Scholar&hellip;</div>"
        )

        self.worker = APIWorker(
            f"{self.api_base_url}/api/v1/ideas/validate",
            method="POST",
            data={"idea": idea}
        )
        self.worker.result_ready.connect(self.show_validation_results)
        self.worker.error_occurred.connect(self.show_error)
        self.worker.start()

    def _paper_html(self, papers: list, preview_limit: int = 10) -> str:
        rows = []
        for i, paper in enumerate(papers[:preview_limit], 1):
            score = paper.get('similarity_score', 0)
            tfidf = paper.get('tfidf_score', 0)
            overlap = paper.get('keyword_overlap', 0)
            authors = ", ".join(paper.get('authors', [])[:3])
            link = paper.get('url') or (f"https://doi.org/{paper.get('doi')}" if paper.get('doi') else '')
            link_html = f" &middot; <a href='{link}' style='color:{BLUE};'>Open Paper</a>" if link else ""

            rows.append(
                f"<table width='100%' cellspacing='0' cellpadding='0' "
                f"style='background-color:#fbf8f2; border:1px solid {BORDER}; margin-bottom:10px;'>"
                f"<tr><td style='padding:10px 12px;'>"
                f"<span style='font-weight:600;'>{i}. {paper.get('title', 'Unknown Title')}</span><br/>"
                f"<span style='color:{TEXT_MUTED}; font-size:11px;'>{authors} &middot; {paper.get('year', 'N/A')} &middot; {paper.get('source', 'N/A')}{link_html}</span><br/>"
                f"<span style='color:{ROSE}; font-size:11px; font-weight:600;'>Match score: {score:.1%}</span>"
                f"<span style='color:{TEXT_MUTED}; font-size:11px;'> (topic overlap {tfidf:.1%}, shared terms {overlap:.1%})</span>"
                f"</td></tr></table>"
            )
        if len(papers) > preview_limit:
            rows.append(
                f"<div style='color:{TEXT_MUTED}; font-size:11px;'>&hellip; and {len(papers) - preview_limit} more "
                f"(use \"Save Results to Paper Library\" to store all of them)</div>"
            )
        return "".join(rows)

    def show_validation_results(self, result: Dict[str, Any]):
        self.progress.setVisible(False)
        status = result.get('status', 'unknown')
        confidence = result.get('confidence', '')
        breakdown = result.get('top_match_breakdown', {})

        if status == 'unique':
            badge = f"<span style='color:{GOOD}; font-weight:700;'>&#10003; UNIQUE</span>"
            papers = result.get('related_papers', [])
            papers_title = "Related Papers (Recommended Reading)"
            next_step = "Select a research methodology for your idea"
        elif status == 'similar':
            badge = f"<span style='color:{WARN}; font-weight:700;'>&#9888; SIMILAR</span>"
            papers = result.get('similar_papers', [])
            papers_title = "Most Similar Papers"
            next_step = "Refine your idea to be more specific and unique"
        else:
            badge = f"<span style='color:{TEXT_MUTED}; font-weight:700;'>{status.upper()}</span>"
            papers = []
            papers_title = ""
            next_step = ""

        self._last_papers = papers

        score = result.get('max_similarity_score', 0)
        html = f"""
            <div style='font-size:14px;'>{badge}</div>
            <div style='color:{TEXT_MUTED}; margin-top:6px;'>{result.get('message', '')}</div>
            <div style='margin-top:4px; font-size:11px; color:{TEXT_MUTED};'>{confidence}</div>
        """
        if breakdown:
            html += f"<div style='margin-top:10px;'>{metric_bar_html('Overall similarity', score, ROSE)}"
            html += metric_bar_html('Topic overlap (TF-IDF)', breakdown.get('tfidf_score', 0), BLUE)
            html += metric_bar_html('Shared terminology', breakdown.get('keyword_overlap', 0), SAGE) + "</div>"

        if papers:
            html += f"<div style='margin-top:16px; font-weight:600;'>{papers_title}</div><div style='margin-top:8px;'>{self._paper_html(papers)}</div>"
        if next_step:
            html += f"<div style='margin-top:12px; color:{BLUE};'>&rarr; Next step: {next_step}</div>"

        self.results_display.setHtml(html)

    def save_to_library(self):
        if not self.project_id:
            QMessageBox.information(self, "No Project", "Open a project first.")
            return
        if not self._last_papers:
            QMessageBox.information(self, "Nothing to Save", "Validate an idea first to get papers you can save.")
            return

        matched_idea = self.idea_input.toPlainText().strip()
        self._pending_saves = len(self._last_papers)
        self.save_status.setText(f"Saving {self._pending_saves} paper(s) to library&hellip;")

        for paper in self._last_papers:
            payload = {
                'title': paper.get('title', ''),
                'authors': ', '.join(paper.get('authors', [])),
                'year': str(paper.get('year', '')),
                'source': paper.get('source', ''),
                'doi': paper.get('doi', ''),
                'url': paper.get('url') or (f"https://doi.org/{paper.get('doi')}" if paper.get('doi') else ''),
                'match_score': paper.get('similarity_score', 0),
                'tfidf_score': paper.get('tfidf_score', 0),
                'keyword_overlap': paper.get('keyword_overlap', 0),
                'matched_idea': matched_idea,
                'annotations': '',
            }
            worker = APIWorker(
                f"{self.api_base_url}/api/v1/projects/{self.project_id}/papers",
                method="POST", data=payload
            )
            self._workers.append(worker)
            worker.result_ready.connect(self._on_paper_saved)
            worker.start()

    def _on_paper_saved(self, _result):
        self._pending_saves = max(0, self._pending_saves - 1)
        if self._pending_saves == 0:
            self.save_status.setText("Saved to Paper Library ✓")

    def show_error(self, error: str):
        self.progress.setVisible(False)
        self.results_display.setHtml(error_html(error))
        QMessageBox.critical(self, "Error", error)


# ============================================================================
# Paper Library: match-score sorted list, direct paper access, annotations
# ============================================================================

class PaperLibraryTab(QWidget):
    """Saved papers with match-score tracking, one-click access, and annotations"""

    def __init__(self, api_base_url: str):
        super().__init__()
        self.api_base_url = api_base_url
        self.project_id: Optional[str] = None
        self._papers: List[Dict] = []
        self._selected_id: Optional[str] = None
        self._workers = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(build_tools_card(
            "Reference & Reading Tools",
            "Citation management and AI-assisted reading tools for papers in your library.",
            PAGE_TOOLS['paper_library'], accent="sand"
        ))

        list_card, list_layout = make_card(
            "Paper Library",
            "Papers saved from literature search (sorted by match score) or added manually. "
            "Select a paper to open it or add annotations.",
            accent="sand"
        )
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(180)
        self.list_widget.itemSelectionChanged.connect(self.on_select)
        list_layout.addWidget(self.list_widget)
        layout.addWidget(list_card)

        detail_card, detail_layout = make_card("Paper Details & Annotations", accent="sand")
        self.detail_display = QTextBrowser()
        self.detail_display.setMinimumHeight(110)
        self.detail_display.setHtml(f"<div style='color:{TEXT_MUTED};'>Select a paper to see details.</div>")
        detail_layout.addWidget(self.detail_display)

        btn_row = QHBoxLayout()
        self.open_btn = primary_button("Open Paper", "sand", icon_name="send.svg")
        self.open_btn.clicked.connect(self.open_paper)
        btn_row.addWidget(self.open_btn)

        del_btn = QPushButton("  Remove from Library")
        del_btn.setObjectName("linkButton")
        del_btn.setIcon(icon("trash.svg"))
        del_btn.setIconSize(QSize(15, 15))
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.clicked.connect(self.delete_selected)
        btn_row.addWidget(del_btn)
        btn_row.addStretch()
        detail_layout.addLayout(btn_row)

        annotation_label = QLabel("Your Annotations")
        annotation_label.setObjectName("fieldLabel")
        detail_layout.addWidget(annotation_label)

        self.annotation_edit = QTextEdit()
        self.annotation_edit.setFixedHeight(110)
        self.annotation_edit.setPlaceholderText("Add notes, quotes, or thoughts about this paper...")
        detail_layout.addWidget(self.annotation_edit)

        save_row = QHBoxLayout()
        save_ann_btn = primary_button("Save Annotation", "sand")
        save_ann_btn.clicked.connect(self.save_annotation)
        save_row.addWidget(save_ann_btn)
        self.save_status = QLabel("")
        self.save_status.setObjectName("cardHint")
        save_row.addWidget(self.save_status)
        save_row.addStretch()
        detail_layout.addLayout(save_row)

        layout.addWidget(detail_card)

        add_card, add_layout = make_card(
            "Add Paper Manually",
            "For papers found through subscription databases (Scopus, Web of Science, "
            "JSTOR, EBSCO, ProQuest, Google Scholar) that Cortex can't query directly.",
            accent="sand"
        )
        self.inputs = {}
        for key, label, placeholder in [
            ('title', 'Title', ''),
            ('authors', 'Authors', 'comma-separated'),
            ('year', 'Year', ''),
            ('source', 'Source', 'e.g. Scopus, Web of Science, JSTOR'),
            ('doi', 'DOI or URL', ''),
        ]:
            lbl = QLabel(label)
            lbl.setObjectName("fieldLabel")
            add_layout.addWidget(lbl)
            w = QLineEdit()
            w.setPlaceholderText(placeholder)
            self.inputs[key] = w
            add_layout.addWidget(w)

        add_row = QHBoxLayout()
        add_btn = primary_button("Add Paper", "sand")
        add_btn.clicked.connect(self.add_manual_paper)
        add_row.addWidget(add_btn)
        add_row.addStretch()
        add_layout.addLayout(add_row)

        layout.addWidget(add_card, stretch=1)

    def set_project(self, project_id: str):
        self.project_id = project_id
        self.refresh()

    def refresh(self):
        if not self.project_id:
            return
        worker = APIWorker(f"{self.api_base_url}/api/v1/projects/{self.project_id}/papers")
        self._workers.append(worker)
        worker.result_ready.connect(self._populate)
        worker.start()

    def _populate(self, result: Dict[str, Any]):
        self._papers = sorted(
            result.get('papers', []),
            key=lambda p: p.get('match_score') or 0,
            reverse=True
        )
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        for paper in self._papers:
            score = paper.get('match_score')
            score_text = f"{score:.0%}" if isinstance(score, (int, float)) and score else "—"
            item = QListWidgetItem(f"[{score_text}]  {paper.get('title', 'Untitled')}")
            item.setData(Qt.ItemDataRole.UserRole, paper.get('id'))
            self.list_widget.addItem(item)
        self.list_widget.blockSignals(False)

        self._selected_id = None
        self.detail_display.setHtml(f"<div style='color:{TEXT_MUTED};'>Select a paper to see details.</div>")
        self.annotation_edit.clear()
        self.save_status.setText("")

    def _selected_paper(self) -> Optional[Dict]:
        return next((p for p in self._papers if p.get('id') == self._selected_id), None)

    def on_select(self):
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self._papers):
            return
        paper = self._papers[row]
        self._selected_id = paper.get('id')
        self.save_status.setText("")

        score = paper.get('match_score')
        score_html = (
            f"<div style='color:{ROSE}; font-weight:600; margin-top:4px;'>Match score: {score:.1%} "
            f"(topic overlap {paper.get('tfidf_score', 0):.1%}, shared terms {paper.get('keyword_overlap', 0):.1%})</div>"
            if isinstance(score, (int, float)) and score else ""
        )
        matched_idea_html = (
            f"<div style='margin-top:6px; color:{TEXT_MUTED}; font-size:11px;'>Matched against: &ldquo;{paper['matched_idea']}&rdquo;</div>"
            if paper.get('matched_idea') else ""
        )

        html = f"""
            <div style='font-weight:700; font-size:14px;'>{paper.get('title', 'Untitled')}</div>
            <div style='color:{TEXT_MUTED}; margin-top:4px;'>{paper.get('authors', '')} &middot; {paper.get('year', '')} &middot; {paper.get('source', '')}</div>
            {score_html}
            {matched_idea_html}
        """
        self.detail_display.setHtml(html)
        self.annotation_edit.setPlainText(paper.get('annotations', ''))

    def open_paper(self):
        paper = self._selected_paper()
        if not paper:
            QMessageBox.information(self, "No Selection", "Select a paper first.")
            return

        url = paper.get('url') or (f"https://doi.org/{paper['doi']}" if paper.get('doi') else '')
        if not url:
            QMessageBox.information(self, "No Link", "This paper has no DOI or URL on file.")
            return

        QDesktopServices.openUrl(QUrl(url))

    def save_annotation(self):
        if not self._selected_id:
            QMessageBox.information(self, "No Selection", "Select a paper first.")
            return

        worker = APIWorker(
            f"{self.api_base_url}/api/v1/projects/{self.project_id}/papers/{self._selected_id}",
            method="PUT", data={"annotations": self.annotation_edit.toPlainText()}
        )
        self._workers.append(worker)
        worker.result_ready.connect(lambda _r: self.save_status.setText("Saved ✓"))
        worker.error_occurred.connect(lambda e: QMessageBox.critical(self, "Error", e))
        worker.start()

    def delete_selected(self):
        if not self._selected_id:
            QMessageBox.information(self, "No Selection", "Select a paper first.")
            return

        worker = APIWorker(
            f"{self.api_base_url}/api/v1/projects/{self.project_id}/papers/{self._selected_id}",
            method="DELETE"
        )
        self._workers.append(worker)
        worker.result_ready.connect(lambda _r: self.refresh())
        worker.start()

    def add_manual_paper(self):
        title = self.inputs['title'].text().strip()
        if not title:
            QMessageBox.warning(self, "Input Error", "Please enter a title")
            return

        doi_or_url = self.inputs['doi'].text().strip()
        url = doi_or_url if doi_or_url.startswith('http') else (f"https://doi.org/{doi_or_url}" if doi_or_url else '')

        payload = {
            'title': title,
            'authors': self.inputs['authors'].text().strip(),
            'year': self.inputs['year'].text().strip(),
            'source': self.inputs['source'].text().strip(),
            'doi': '' if doi_or_url.startswith('http') else doi_or_url,
            'url': url,
            'annotations': '',
        }

        worker = APIWorker(
            f"{self.api_base_url}/api/v1/projects/{self.project_id}/papers",
            method="POST", data=payload
        )
        self._workers.append(worker)
        worker.result_ready.connect(lambda _r: (self._clear_add_form(), self.refresh()))
        worker.error_occurred.connect(lambda e: QMessageBox.critical(self, "Error", e))
        worker.start()

    def _clear_add_form(self):
        for w in self.inputs.values():
            w.clear()


# ============================================================================
# Methodology checklist (project-scoped, driven by research_type)
# ============================================================================

class ProjectMethodologyTab(QWidget):
    """Step-by-step methodology checklist for the project's research type"""

    def __init__(self, api_base_url: str):
        super().__init__()
        self.api_base_url = api_base_url
        self.project_id: Optional[str] = None
        self._workers = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(16)

        guidelines_card, guidelines_layout = make_card(
            "Methodology & Reporting Guidelines",
            "Standards and regulatory guidance for this project's study design (e.g. PRISMA for a "
            "literature review, IRB/GCP/CONSORT for clinical research) - independent of which step below is active.",
            accent="blue"
        )
        self.guidelines_flow = FlowLayout(margin=0, spacing=6)
        guidelines_layout.addLayout(self.guidelines_flow)
        layout.addWidget(guidelines_card)

        card, card_layout = make_card(
            "Methodology Checklist",
            "The standard process steps for this project's research type. Check off each step as you complete it.",
            accent="sage"
        )
        self.progress_label = QLabel("")
        self.progress_label.setObjectName("cardHint")
        card_layout.addWidget(self.progress_label)

        self.steps_layout = QVBoxLayout()
        self.steps_layout.setSpacing(2)
        card_layout.addLayout(self.steps_layout)

        layout.addWidget(card)
        layout.addStretch()

    def set_project(self, project_id: str):
        self.project_id = project_id
        self.refresh()

    def refresh(self):
        if not self.project_id:
            return
        self._refresh_worker = APIWorker(f"{self.api_base_url}/api/v1/projects/{self.project_id}/methodology")
        self._refresh_worker.result_ready.connect(self._populate)
        self._refresh_worker.start()

    def _populate(self, result: Dict[str, Any]):
        methodology = result.get('methodology', {})

        self._clear_layout(self.guidelines_flow)
        guidelines = methodology.get('methodology_guidelines', [])
        if guidelines:
            for tool in guidelines:
                self.guidelines_flow.addWidget(make_tool_chip(tool['name'], tool.get('url', ''), tool.get('description', '')))
        else:
            none_label = QLabel("No curated guidelines for this research type yet.")
            none_label.setObjectName("cardHint")
            self.guidelines_flow.addWidget(none_label)

        while self.steps_layout.count():
            child = self.steps_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())

        for step in methodology.get('steps', []):
            step_block = QVBoxLayout()
            step_block.setSpacing(4)
            step_block.setContentsMargins(0, 6, 0, 6)

            cb = QCheckBox(f"{step['index'] + 1}. {step['text']}")
            cb.setChecked(step['completed'])
            cb.toggled.connect(lambda checked, idx=step['index']: self.toggle_step(idx, checked))
            step_block.addWidget(cb)

            tools_row = FlowLayout(margin=0, spacing=6)
            tools_row.setContentsMargins(24, 0, 0, 0)

            for tool in step.get('recommended_tools', []):
                tools_row.addWidget(make_tool_chip(tool['name'], tool.get('url', ''), tool.get('description', ''), custom=False))

            for tool in step.get('custom_tools', []):
                tools_row.addWidget(make_tool_chip(
                    tool['name'], tool.get('url', ''), '', custom=True,
                    on_remove=lambda idx=step['index'], tid=tool['id']: self.remove_tool(idx, tid)
                ))

            add_btn = QPushButton("+ Add Tool")
            add_btn.setObjectName("linkButton")
            add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            add_btn.clicked.connect(lambda _c=False, idx=step['index']: self.prompt_add_tool(idx))
            tools_row.addWidget(add_btn)

            step_block.addLayout(tools_row)
            self.steps_layout.addLayout(step_block)

        self.progress_label.setText(
            f"{methodology.get('research_type_name', '')} \u2014 "
            f"{methodology.get('completed_count', 0)} / {methodology.get('total_steps', 0)} steps completed"
        )

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())

    def prompt_add_tool(self, step_index: int):
        name, ok = QInputDialog.getText(self, "Add Tool", "Tool name:")
        if not ok or not name.strip():
            return
        url, ok = QInputDialog.getText(self, "Add Tool", "Tool URL (optional):")
        if not ok:
            return

        worker = APIWorker(
            f"{self.api_base_url}/api/v1/projects/{self.project_id}/methodology/{step_index}/tools",
            method="POST", data={"name": name.strip(), "url": url.strip()}
        )
        self._workers.append(worker)
        worker.result_ready.connect(lambda _r: self.refresh())
        worker.error_occurred.connect(lambda e: QMessageBox.critical(self, "Error", e))
        worker.start()

    def remove_tool(self, step_index: int, tool_id: str):
        worker = APIWorker(
            f"{self.api_base_url}/api/v1/projects/{self.project_id}/methodology/{step_index}/tools/{tool_id}",
            method="DELETE"
        )
        self._workers.append(worker)
        worker.result_ready.connect(lambda _r: self.refresh())
        worker.start()

    def toggle_step(self, step_index: int, completed: bool):
        worker = APIWorker(
            f"{self.api_base_url}/api/v1/projects/{self.project_id}/methodology/{step_index}",
            method="PUT", data={"completed": completed}
        )
        self._workers.append(worker)
        worker.result_ready.connect(self._on_toggled)
        worker.start()

    def _on_toggled(self, result: Dict[str, Any]):
        methodology = result.get('methodology', {})
        self.progress_label.setText(
            f"{methodology.get('research_type_name', '')} \u2014 "
            f"{methodology.get('completed_count', 0)} / {methodology.get('total_steps', 0)} steps completed"
        )


# ============================================================================
# Manuscript editor (project-scoped)
# ============================================================================

class ManuscriptTab(QWidget):
    """Sectioned manuscript draft editor"""

    SECTIONS = ['abstract', 'introduction', 'methods', 'results', 'discussion', 'references']

    def __init__(self, api_base_url: str):
        super().__init__()
        self.api_base_url = api_base_url
        self.project_id: Optional[str] = None
        self.editors = {}
        self._workers = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(build_tools_card(
            "Writing & Synthesis Tools",
            "Manuscript editors, citation-support, and writing assistants.",
            PAGE_TOOLS['manuscript'], accent="blue"
        ))

        card, card_layout = make_card(
            "Manuscript Draft",
            "Draft each section of your manuscript. Saved locally to this project.",
            accent="blue"
        )

        for section in self.SECTIONS:
            label = QLabel(section.replace('_', ' ').title())
            label.setObjectName("fieldLabel")
            card_layout.addWidget(label)

            editor = QTextEdit()
            editor.setFixedHeight(90)
            editor.setPlaceholderText(f"Write your {section}...")
            self.editors[section] = editor
            card_layout.addWidget(editor)

        row = QHBoxLayout()
        save_btn = primary_button("Save Manuscript", "blue")
        save_btn.clicked.connect(self.save_manuscript)
        row.addWidget(save_btn)

        self.save_status = QLabel("")
        self.save_status.setObjectName("cardHint")
        row.addWidget(self.save_status)
        row.addStretch()
        card_layout.addLayout(row)

        layout.addWidget(card)

        scroll_note = QLabel("Tip: scroll within the card above to see all sections.")
        scroll_note.setObjectName("cardHint")
        layout.addWidget(scroll_note)
        layout.addStretch()

    def set_project(self, project_id: str):
        self.project_id = project_id
        self.refresh()

    def refresh(self):
        if not self.project_id:
            return
        self._refresh_worker = APIWorker(f"{self.api_base_url}/api/v1/projects/{self.project_id}/manuscript")
        self._refresh_worker.result_ready.connect(self._populate)
        self._refresh_worker.start()

    def _populate(self, result: Dict[str, Any]):
        manuscript = result.get('manuscript', {})
        for section, editor in self.editors.items():
            editor.setPlainText(manuscript.get(section, ''))

    def save_manuscript(self):
        if not self.project_id:
            return
        payload = {section: editor.toPlainText() for section, editor in self.editors.items()}
        worker = APIWorker(
            f"{self.api_base_url}/api/v1/projects/{self.project_id}/manuscript",
            method="PUT", data=payload
        )
        self._workers.append(worker)
        worker.result_ready.connect(lambda _r: self.save_status.setText("Saved ✓"))
        worker.error_occurred.connect(lambda e: QMessageBox.critical(self, "Error", e))
        worker.start()


import base64

# ============================================================================
# Data & Analysis: manual dataset import, statistical tests, and charts
# ============================================================================

# Each test declares a 'kind' describing which input widgets it needs:
#   one_col            -> field1 only (single column)
#   two_col             -> field1 + field2 (two single columns)
#   one_col_plus_value  -> field1 (column) + a literal numeric value
#   multi_col           -> a multi-select list of columns only
#   multi_col_plus_y    -> a multi-select list (predictors) + field2 (single Y column)
STAT_TESTS = [
    ('descriptive', 'Descriptive Statistics', 'one_col', 'Column', None),
    ('ttest_ind', 'Independent Samples t-test', 'two_col', 'Value Column', 'Group Column (2 groups)'),
    ('ttest_paired', 'Paired Samples t-test', 'two_col', 'Column A', 'Column B'),
    ('one_sample_ttest', 'One-Sample t-test', 'one_col_plus_value', 'Column', 'Test Value (number)'),
    ('anova', 'One-Way ANOVA', 'two_col', 'Value Column', 'Group Column'),
    ('mann_whitney', 'Mann-Whitney U Test (non-parametric)', 'two_col', 'Value Column', 'Group Column (2 groups)'),
    ('wilcoxon', 'Wilcoxon Signed-Rank Test (non-parametric)', 'two_col', 'Column A', 'Column B'),
    ('kruskal', 'Kruskal-Wallis Test (non-parametric)', 'two_col', 'Value Column', 'Group Column'),
    ('pearson', 'Pearson Correlation', 'two_col', 'Column A', 'Column B'),
    ('spearman', 'Spearman Correlation', 'two_col', 'Column A', 'Column B'),
    ('correlation_matrix', 'Correlation Matrix (3+ columns)', 'multi_col', 'Columns (ctrl/cmd-click to select multiple)', None),
    ('chi2', 'Chi-Square Test of Independence', 'two_col', 'Column A', 'Column B'),
    ('linregress', 'Simple Linear Regression', 'two_col', 'X Column', 'Y Column'),
    ('multiple_regression', 'Multiple Linear Regression (2+ predictors)', 'multi_col_plus_y',
     'Predictor Columns (ctrl/cmd-click to select multiple)', 'Y Column (outcome)'),
]

# Params keys expected by the backend for each 'two_col'-kind test
TWO_COL_PARAM_KEYS = {
    'ttest_ind': ('value_column', 'group_column'),
    'ttest_paired': ('column_a', 'column_b'),
    'anova': ('value_column', 'group_column'),
    'mann_whitney': ('value_column', 'group_column'),
    'wilcoxon': ('column_a', 'column_b'),
    'kruskal': ('value_column', 'group_column'),
    'pearson': ('column_a', 'column_b'),
    'spearman': ('column_a', 'column_b'),
    'chi2': ('column_a', 'column_b'),
    'linregress': ('x_column', 'y_column'),
}

CHART_TYPES = [
    ('bar', 'Bar Chart', 'X Column (category)', 'Y Column (numeric, optional = count)', False, False),
    ('line', 'Line Chart', 'X Column', 'Y Column(s) - select 1 or more', True, False),
    ('scatter', 'Scatter Plot', 'X Column', 'Y Column(s) - select 1 or more', True, False),
    ('histogram', 'Histogram', 'Column', None, False, False),
    ('box', 'Box Plot', 'Value Column', None, False, True),
]


class DataAnalysisTab(QWidget):
    """Manual data import, statistical test runner, and chart generator - the
    user always picks the test/chart type and which columns/rows it runs on,
    nothing here is decided automatically."""

    def __init__(self, api_base_url: str):
        super().__init__()
        self.api_base_url = api_base_url
        self.project_id: Optional[str] = None
        self._datasets: List[Dict] = []
        self._selected_dataset: Optional[Dict] = None
        self._workers = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(build_tools_card(
            "External Analysis Tools",
            "JASP and jamovi are free, point-and-click stats software - no coding required. "
            "RStudio if you want to script your own analysis in R.",
            PAGE_TOOLS['data_analysis'], accent="blue"
        ))

        # --- Import ---
        import_card, import_layout = make_card(
            "Import Data",
            "Paste CSV or tab-separated data (first row = column headers). Nothing is sent anywhere except your own local Cortex server.",
            accent="blue"
        )
        self.import_name = QLineEdit()
        self.import_name.setPlaceholderText("Dataset name, e.g. \"Experiment 1 raw data\"")
        import_layout.addWidget(self.import_name)

        self.import_text = QTextEdit()
        self.import_text.setPlaceholderText("subject,group,score\n1,control,88\n2,treatment,95\n...")
        self.import_text.setFixedHeight(90)
        import_layout.addWidget(self.import_text)

        import_row = QHBoxLayout()
        import_btn = primary_button("Import Dataset", "blue")
        import_btn.clicked.connect(self.import_dataset)
        import_row.addWidget(import_btn)
        self.import_status = QLabel("")
        self.import_status.setObjectName("cardHint")
        import_row.addWidget(self.import_status)
        import_row.addStretch()
        import_layout.addLayout(import_row)
        layout.addWidget(import_card)

        # --- Dataset list ---
        list_card, list_layout = make_card("Your Datasets", "Select a dataset to run a test or make a chart from it.", accent="blue")
        self.dataset_list = QListWidget()
        self.dataset_list.setMinimumHeight(110)
        self.dataset_list.itemSelectionChanged.connect(self.on_select_dataset)
        list_layout.addWidget(self.dataset_list)

        row_range_row = QHBoxLayout()
        row_range_row.addWidget(QLabel("Row range (optional):"))
        self.row_start = QLineEdit()
        self.row_start.setPlaceholderText("start")
        self.row_start.setFixedWidth(70)
        self.row_end = QLineEdit()
        self.row_end.setPlaceholderText("end")
        self.row_end.setFixedWidth(70)
        row_range_row.addWidget(self.row_start)
        row_range_row.addWidget(QLabel("to"))
        row_range_row.addWidget(self.row_end)
        row_range_row.addStretch()

        del_btn = QPushButton("  Delete Dataset")
        del_btn.setObjectName("linkButton")
        del_btn.setIcon(icon("trash.svg"))
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.clicked.connect(self.delete_dataset)
        row_range_row.addWidget(del_btn)
        list_layout.addLayout(row_range_row)
        layout.addWidget(list_card)

        # --- Statistical analysis ---
        stats_card, stats_layout = make_card(
            "Run a Statistical Test",
            "Pick the test and which columns it should run on - you choose everything.",
            accent="sage"
        )
        self.test_combo = QComboBox()
        for key, name, _kind, _l1, _l2 in STAT_TESTS:
            self.test_combo.addItem(name, key)
        self.test_combo.currentIndexChanged.connect(self.on_test_changed)
        stats_layout.addWidget(self.test_combo)

        self.field1_label = QLabel("Column")
        self.field1_label.setObjectName("fieldLabel")
        stats_layout.addWidget(self.field1_label)
        self.field1_combo = QComboBox()
        stats_layout.addWidget(self.field1_combo)

        self.multi_columns_list = QListWidget()
        self.multi_columns_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.multi_columns_list.setFixedHeight(100)
        stats_layout.addWidget(self.multi_columns_list)

        self.test_value_input = QLineEdit()
        self.test_value_input.setPlaceholderText("e.g. 0")
        stats_layout.addWidget(self.test_value_input)

        self.field2_label = QLabel("")
        self.field2_label.setObjectName("fieldLabel")
        stats_layout.addWidget(self.field2_label)
        self.field2_combo = QComboBox()
        stats_layout.addWidget(self.field2_combo)

        run_row = QHBoxLayout()
        run_btn = primary_button("Run Test", "sage")
        run_btn.clicked.connect(self.run_test)
        run_row.addWidget(run_btn)
        run_row.addStretch()
        stats_layout.addLayout(run_row)

        self.stats_result = QTextBrowser()
        self.stats_result.setMinimumHeight(110)
        self.stats_result.setHtml(f"<div style='color:{TEXT_MUTED};'>Results will appear here.</div>")
        stats_layout.addWidget(self.stats_result)
        layout.addWidget(stats_card)

        # --- Charts ---
        chart_card, chart_layout = make_card(
            "Generate a Chart",
            "Pick a chart type and which columns to plot.",
            accent="sand"
        )
        self.chart_combo = QComboBox()
        for key, name, _x, _y, _multi, _g in CHART_TYPES:
            self.chart_combo.addItem(name, key)
        self.chart_combo.currentIndexChanged.connect(self.on_chart_type_changed)
        chart_layout.addWidget(self.chart_combo)

        self.chart_x_label = QLabel("X Column")
        self.chart_x_label.setObjectName("fieldLabel")
        chart_layout.addWidget(self.chart_x_label)
        self.chart_x_combo = QComboBox()
        chart_layout.addWidget(self.chart_x_combo)

        self.chart_y_label = QLabel("Y Column")
        self.chart_y_label.setObjectName("fieldLabel")
        chart_layout.addWidget(self.chart_y_label)
        self.chart_y_combo = QComboBox()
        chart_layout.addWidget(self.chart_y_combo)

        self.chart_y_multi_list = QListWidget()
        self.chart_y_multi_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.chart_y_multi_list.setFixedHeight(90)
        chart_layout.addWidget(self.chart_y_multi_list)

        self.chart_group_label = QLabel("Group Column (optional)")
        self.chart_group_label.setObjectName("fieldLabel")
        chart_layout.addWidget(self.chart_group_label)
        self.chart_group_combo = QComboBox()
        chart_layout.addWidget(self.chart_group_combo)

        self.chart_title = QLineEdit()
        self.chart_title.setPlaceholderText("Chart title (optional)")
        chart_layout.addWidget(self.chart_title)

        # --- Axis limits ---
        axis_label = QLabel("Axis Range (optional)")
        axis_label.setObjectName("fieldLabel")
        chart_layout.addWidget(axis_label)

        axis_row = QHBoxLayout()
        self.x_min_input = QLineEdit()
        self.x_min_input.setPlaceholderText("x min")
        self.x_max_input = QLineEdit()
        self.x_max_input.setPlaceholderText("x max")
        self.y_min_input = QLineEdit()
        self.y_min_input.setPlaceholderText("y min")
        self.y_max_input = QLineEdit()
        self.y_max_input.setPlaceholderText("y max")
        for w in (self.x_min_input, self.x_max_input, self.y_min_input, self.y_max_input):
            axis_row.addWidget(w)
        chart_layout.addLayout(axis_row)

        # --- Tick preferences ---
        tick_label = QLabel("Tick Marks (optional)")
        tick_label.setObjectName("fieldLabel")
        chart_layout.addWidget(tick_label)

        tick_row = QHBoxLayout()
        self.x_tick_input = QLineEdit()
        self.x_tick_input.setPlaceholderText("x tick spacing")
        self.y_tick_input = QLineEdit()
        self.y_tick_input.setPlaceholderText("y tick spacing")
        self.tick_rotation_input = QLineEdit()
        self.tick_rotation_input.setPlaceholderText("x label rotation (°)")
        for w in (self.x_tick_input, self.y_tick_input, self.tick_rotation_input):
            tick_row.addWidget(w)
        chart_layout.addLayout(tick_row)

        # --- Color ---
        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("Color:"))
        self._chart_color: Optional[str] = None
        self.color_swatch = QLabel()
        self.color_swatch.setFixedSize(22, 22)
        self.color_swatch.setStyleSheet(f"background-color: transparent; border: 1px solid {BORDER}; border-radius: 4px;")
        color_row.addWidget(self.color_swatch)
        pick_color_btn = QPushButton("Pick Color")
        pick_color_btn.setObjectName("linkButton")
        pick_color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pick_color_btn.clicked.connect(self.pick_color)
        color_row.addWidget(pick_color_btn)
        reset_color_btn = QPushButton("Auto")
        reset_color_btn.setObjectName("linkButton")
        reset_color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_color_btn.clicked.connect(self.reset_color)
        color_row.addWidget(reset_color_btn)
        color_row.addStretch()
        chart_layout.addLayout(color_row)

        chart_row = QHBoxLayout()
        chart_btn = primary_button("Generate Chart", "sand")
        chart_btn.clicked.connect(self.generate_chart)
        chart_row.addWidget(chart_btn)
        chart_row.addStretch()
        chart_layout.addLayout(chart_row)

        self.chart_image_label = QLabel("Chart will appear here.")
        self.chart_image_label.setObjectName("cardHint")
        self.chart_image_label.setMinimumHeight(200)
        self.chart_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_layout.addWidget(self.chart_image_label)
        layout.addWidget(chart_card, stretch=1)

        self.on_test_changed()
        self.on_chart_type_changed()

    # --- lifecycle ---

    def set_project(self, project_id: str):
        self.project_id = project_id
        self.refresh()

    def refresh(self):
        if not self.project_id:
            return
        worker = APIWorker(f"{self.api_base_url}/api/v1/projects/{self.project_id}/datasets")
        self._workers.append(worker)
        worker.result_ready.connect(self._populate_datasets)
        worker.start()

    def _populate_datasets(self, result: Dict[str, Any]):
        self._datasets = result.get('datasets', [])
        self.dataset_list.blockSignals(True)
        self.dataset_list.clear()
        for ds in self._datasets:
            item = QListWidgetItem(f"{ds.get('name', 'Untitled')}  ({ds.get('row_count', 0)} rows x {ds.get('col_count', 0)} cols)")
            item.setData(Qt.ItemDataRole.UserRole, ds.get('id'))
            self.dataset_list.addItem(item)
        self.dataset_list.blockSignals(False)

    def _row_range(self) -> Optional[List[int]]:
        start, end = self.row_start.text().strip(), self.row_end.text().strip()
        if not start and not end:
            return None
        try:
            return [int(start) if start else 0, int(end) if end else 10 ** 9]
        except ValueError:
            return None

    # --- dataset selection ---

    def on_select_dataset(self):
        row = self.dataset_list.currentRow()
        if row < 0 or row >= len(self._datasets):
            return
        self._selected_dataset = self._datasets[row]
        columns = self._selected_dataset.get('columns', [])

        for combo in [self.field1_combo, self.field2_combo, self.chart_x_combo, self.chart_y_combo]:
            combo.clear()
            combo.addItems(columns)

        self.chart_group_combo.clear()
        self.chart_group_combo.addItems(['(none)'] + columns)

        for multi_list in [self.multi_columns_list, self.chart_y_multi_list]:
            multi_list.clear()
            multi_list.addItems(columns)

    def import_dataset(self):
        if not self.project_id:
            return
        name = self.import_name.text().strip() or "Untitled Dataset"
        csv_text = self.import_text.toPlainText().strip()
        if not csv_text:
            QMessageBox.warning(self, "Input Error", "Paste some CSV/TSV data first")
            return

        worker = APIWorker(
            f"{self.api_base_url}/api/v1/projects/{self.project_id}/datasets/import",
            method="POST", data={"name": name, "csv_text": csv_text}
        )
        self._workers.append(worker)
        worker.result_ready.connect(lambda _r: (self._clear_import_form(), self.refresh()))
        worker.error_occurred.connect(lambda e: QMessageBox.critical(self, "Import Error", e))
        worker.start()

    def _clear_import_form(self):
        self.import_name.clear()
        self.import_text.clear()
        self.import_status.setText("Imported ✓")

    def delete_dataset(self):
        if not self._selected_dataset:
            QMessageBox.information(self, "No Selection", "Select a dataset first.")
            return
        worker = APIWorker(
            f"{self.api_base_url}/api/v1/projects/{self.project_id}/datasets/{self._selected_dataset['id']}",
            method="DELETE"
        )
        self._workers.append(worker)
        worker.result_ready.connect(lambda _r: (setattr(self, '_selected_dataset', None), self.refresh()))
        worker.start()

    # --- statistical tests ---

    def on_test_changed(self):
        idx = self.test_combo.currentIndex()
        if idx < 0 or idx >= len(STAT_TESTS):
            return
        _key, _name, kind, label1, label2 = STAT_TESTS[idx]

        show_field1 = kind in ('one_col', 'two_col', 'one_col_plus_value')
        show_multi = kind in ('multi_col', 'multi_col_plus_y')
        show_test_value = kind == 'one_col_plus_value'
        show_field2 = kind in ('two_col', 'multi_col_plus_y')

        self.field1_label.setText(label1)
        self.field1_label.setVisible(show_field1)
        self.field1_combo.setVisible(show_field1)

        self.multi_columns_list.setVisible(show_multi)
        if show_multi:
            self.field1_label.setText(label1)
            self.field1_label.setVisible(True)

        self.test_value_input.setVisible(show_test_value)

        self.field2_label.setVisible(show_field2)
        self.field2_combo.setVisible(show_field2)
        if show_field2:
            self.field2_label.setText(label2)

    def run_test(self):
        if not self.project_id or not self._selected_dataset:
            QMessageBox.information(self, "No Dataset", "Import and select a dataset first.")
            return

        test_key = self.test_combo.currentData()
        idx = self.test_combo.currentIndex()
        _key, _name, kind, _l1, _l2 = STAT_TESTS[idx]

        field1 = self.field1_combo.currentText()
        field2 = self.field2_combo.currentText()
        selected_columns = [item.text() for item in self.multi_columns_list.selectedItems()]

        params = {}

        if kind == 'one_col':
            if not field1:
                QMessageBox.warning(self, "Input Error", "This dataset has no columns to select.")
                return
            params = {'value_columns': [field1]}

        elif kind == 'two_col':
            if not field1 or not field2:
                QMessageBox.warning(self, "Input Error", "Select both columns.")
                return
            key1, key2 = TWO_COL_PARAM_KEYS[test_key]
            params = {key1: field1, key2: field2}

        elif kind == 'one_col_plus_value':
            if not field1:
                QMessageBox.warning(self, "Input Error", "Select a column.")
                return
            try:
                test_value = float(self.test_value_input.text().strip())
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Enter a numeric test value.")
                return
            params = {'value_column': field1, 'test_value': test_value}

        elif kind == 'multi_col':
            if len(selected_columns) < 2:
                QMessageBox.warning(self, "Input Error", "Select at least 2 columns (ctrl/cmd-click to multi-select).")
                return
            params = {'columns': selected_columns}

        elif kind == 'multi_col_plus_y':
            if len(selected_columns) < 1 or not field2:
                QMessageBox.warning(self, "Input Error", "Select at least 1 predictor column and a Y column.")
                return
            params = {'x_columns': selected_columns, 'y_column': field2}

        row_range = self._row_range()
        if row_range:
            params['row_range'] = row_range

        self.stats_result.setHtml(f"<div style='color:{TEXT_MUTED};'>Running test&hellip;</div>")

        worker = APIWorker(
            f"{self.api_base_url}/api/v1/projects/{self.project_id}/datasets/{self._selected_dataset['id']}/analyze",
            method="POST", data={"test": test_key, "params": params}
        )
        self._workers.append(worker)
        worker.result_ready.connect(self.show_test_result)
        worker.error_occurred.connect(lambda e: self.stats_result.setHtml(error_html(e)))
        worker.start()

    def show_test_result(self, result: Dict[str, Any]):
        analysis = result.get('analysis', {})
        test_result = analysis.get('result', {})
        interpretation = test_result.get('interpretation', 'No interpretation available.')

        html = f"<div style='color:{SAGE}; font-weight:600;'>{interpretation}</div>"

        stat = test_result.get('statistic')
        p_value = test_result.get('p_value')
        if stat is not None:
            html += f"<div style='margin-top:8px; color:{TEXT_MUTED}; font-size:12px;'>statistic = {stat:.4f}"
            if p_value is not None:
                html += f", p = {p_value:.4f}"
            html += "</div>"

        if test_result.get('groups'):
            rows = "".join(
                f"<tr><td style='padding:2px 10px 2px 0;'>{name}</td>" +
                "".join(f"<td style='padding:2px 10px;'>{k}={v:.3g}</td>" if isinstance(v, float) else f"<td style='padding:2px 10px;'>{k}={v}</td>" for k, v in stats.items()) +
                "</tr>"
                for name, stats in test_result['groups'].items()
            )
            html += f"<table style='margin-top:8px; font-size:12px; color:{TEXT_MUTED};'>{rows}</table>"

        if test_result.get('coefficients'):
            rows = "".join(
                f"<tr><td style='padding:2px 10px 2px 0; font-weight:600;'>{name}</td>"
                f"<td style='padding:2px 10px;'>coef={c['coef']:.4g}</td>"
                f"<td style='padding:2px 10px;'>se={c['se']:.4g}</td>"
                f"<td style='padding:2px 10px;'>t={c['t']:.3f}</td>"
                f"<td style='padding:2px 10px;'>p={c['p_value']:.4f}</td></tr>"
                for name, c in test_result['coefficients'].items()
            )
            html += f"<table style='margin-top:8px; font-size:12px; color:{TEXT_MUTED};'>{rows}</table>"

        if test_result.get('matrix'):
            columns = list(test_result['matrix'].keys())
            header = "".join(f"<th style='padding:2px 8px; text-align:left;'>{c}</th>" for c in columns)
            rows = ""
            for row_col in columns:
                cells = "".join(f"<td style='padding:2px 8px;'>{test_result['matrix'][col].get(row_col, ''):.2f}</td>" for col in columns)
                rows += f"<tr><td style='padding:2px 8px; font-weight:600;'>{row_col}</td>{cells}</tr>"
            html += f"<table style='margin-top:8px; font-size:12px; color:{TEXT_MUTED}; border-collapse:collapse;'><tr><th></th>{header}</tr>{rows}</table>"

        if test_result.get('columns') and isinstance(test_result['columns'], dict):
            rows = "".join(
                f"<tr><td style='padding:2px 10px 2px 0; font-weight:600;'>{col}</td>" +
                "".join(f"<td style='padding:2px 10px;'>{k}={v:.3g}</td>" if isinstance(v, float) else f"<td style='padding:2px 10px;'>{k}={v}</td>" for k, v in stats.items() if k != 'error') +
                "</tr>"
                for col, stats in test_result['columns'].items()
            )
            html += f"<table style='margin-top:8px; font-size:12px; color:{TEXT_MUTED};'>{rows}</table>"

        self.stats_result.setHtml(html)

    # --- charts ---

    def on_chart_type_changed(self):
        idx = self.chart_combo.currentIndex()
        if idx < 0 or idx >= len(CHART_TYPES):
            return
        _key, _name, x_label, y_label, multi_y, show_group = CHART_TYPES[idx]
        self.chart_x_label.setText(x_label)

        show_y = y_label is not None
        self.chart_y_label.setText(y_label or "")
        self.chart_y_label.setVisible(show_y and not multi_y)
        self.chart_y_combo.setVisible(show_y and not multi_y)
        self.chart_y_multi_list.setVisible(show_y and multi_y)
        if show_y and multi_y:
            self.chart_y_label.setVisible(True)

        self.chart_group_label.setVisible(show_group)
        self.chart_group_combo.setVisible(show_group)

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self._chart_color = color.name()
            self.color_swatch.setStyleSheet(f"background-color: {self._chart_color}; border: 1px solid {BORDER}; border-radius: 4px;")

    def reset_color(self):
        self._chart_color = None
        self.color_swatch.setStyleSheet(f"background-color: transparent; border: 1px solid {BORDER}; border-radius: 4px;")

    def _parse_float(self, line_edit: QLineEdit) -> Optional[float]:
        text = line_edit.text().strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None

    def generate_chart(self):
        if not self.project_id or not self._selected_dataset:
            QMessageBox.information(self, "No Dataset", "Import and select a dataset first.")
            return

        chart_key = self.chart_combo.currentData()
        x_column = self.chart_x_combo.currentText()
        if not x_column:
            QMessageBox.warning(self, "Input Error", "This dataset has no columns to select.")
            return

        params = {'x_column': x_column}

        if self.chart_y_multi_list.isVisible():
            y_columns = [item.text() for item in self.chart_y_multi_list.selectedItems()]
            if not y_columns:
                QMessageBox.warning(self, "Input Error", "Select at least 1 Y column (ctrl/cmd-click to multi-select).")
                return
            params['y_columns'] = y_columns
        elif self.chart_y_combo.isVisible() and self.chart_y_combo.currentText():
            params['y_column'] = self.chart_y_combo.currentText()

        if self.chart_group_combo.isVisible() and self.chart_group_combo.currentText() not in ('', '(none)'):
            params['group_column'] = self.chart_group_combo.currentText()
        if self.chart_title.text().strip():
            params['title'] = self.chart_title.text().strip()

        row_range = self._row_range()
        if row_range:
            params['row_range'] = row_range

        x_min, x_max = self._parse_float(self.x_min_input), self._parse_float(self.x_max_input)
        if x_min is not None and x_max is not None:
            params['xlim'] = [x_min, x_max]
        y_min, y_max = self._parse_float(self.y_min_input), self._parse_float(self.y_max_input)
        if y_min is not None and y_max is not None:
            params['ylim'] = [y_min, y_max]

        x_tick = self._parse_float(self.x_tick_input)
        if x_tick:
            params['x_tick_interval'] = x_tick
        y_tick = self._parse_float(self.y_tick_input)
        if y_tick:
            params['y_tick_interval'] = y_tick
        rotation = self._parse_float(self.tick_rotation_input)
        if rotation is not None:
            params['tick_rotation'] = rotation

        if self._chart_color:
            params['color'] = self._chart_color

        self.chart_image_label.setText("Generating chart…")
        self.chart_image_label.setPixmap(QPixmap())

        worker = APIWorker(
            f"{self.api_base_url}/api/v1/projects/{self.project_id}/datasets/{self._selected_dataset['id']}/chart",
            method="POST", data={"chart_type": chart_key, "params": params}
        )
        self._workers.append(worker)
        worker.result_ready.connect(self.show_chart)
        worker.error_occurred.connect(lambda e: self.chart_image_label.setText(f"Error: {e}"))
        worker.start()

    def show_chart(self, result: Dict[str, Any]):
        chart = result.get('chart', {})
        image_b64 = chart.get('image_base64')
        if not image_b64:
            self.chart_image_label.setText("No chart image returned.")
            return

        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(image_b64))
        self.chart_image_label.setText("")
        self.chart_image_label.setPixmap(pixmap)


# ============================================================================
# Journal guidelines lookup (curated reference, paired with the Journals CRUD list)
# ============================================================================

class JournalGuidelinesCard(QWidget):
    """Look up curated submission guidelines for a journal by name"""

    def __init__(self, api_base_url: str):
        super().__init__()
        self.api_base_url = api_base_url
        self._workers = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 24)
        layout.setSpacing(16)

        card, card_layout = make_card(
            "Journal Submission Guidelines",
            "Look up a curated summary of common formatting/structure requirements. "
            "Always confirm current details on the journal's own author guidelines page before submitting.",
            accent="sand"
        )

        row = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Nature, PLOS ONE, JAMA, IEEE...")
        row.addWidget(self.name_input)
        lookup_btn = primary_button("Look Up", "sand")
        lookup_btn.clicked.connect(self.lookup)
        row.addWidget(lookup_btn)
        card_layout.addLayout(row)

        self.result_display = QTextBrowser()
        self.result_display.setMinimumHeight(150)
        self.result_display.setHtml(f"<div style='color:{TEXT_MUTED};'>Enter a journal name above.</div>")
        card_layout.addWidget(self.result_display)

        layout.addWidget(card)

    def lookup(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Enter a journal name first")
            return

        self.result_display.setHtml(f"<div style='color:{TEXT_MUTED};'>Looking up&hellip;</div>")
        worker = APIWorker(f"{self.api_base_url}/api/v1/journal-guidelines?name={name}")
        self._workers.append(worker)
        worker.result_ready.connect(self.show_result)
        worker.error_occurred.connect(lambda e: self.result_display.setHtml(error_html(e)))
        worker.start()

    def show_result(self, result: Dict[str, Any]):
        g = result.get('guidelines', {})
        html = f"""
            <div style='font-weight:700; font-size:14px;'>{g.get('name', 'Unknown')}</div>
            <div style='margin-top:8px;'><b>Citation style:</b> {g.get('citation_style', 'N/A')}</div>
            <div style='margin-top:4px;'><b>Word limit:</b> {g.get('word_limit', 'N/A')}</div>
            <div style='margin-top:4px;'><b>Structure:</b> {g.get('structure', 'N/A')}</div>
            <div style='margin-top:8px; color:{TEXT_MUTED};'>{g.get('notes', '')}</div>
        """
        homepage = g.get('homepage')
        if homepage:
            html += f"<div style='margin-top:8px;'><a href='{homepage}' style='color:{BLUE};'>Official author guidelines &rarr;</a></div>"
        self.result_display.setOpenExternalLinks(True)
        self.result_display.setHtml(html)


class JournalsPageTab(QWidget):
    """Journals & Submissions CRUD list, paired with a guidelines lookup below it"""

    def __init__(self, api_base_url: str):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.crud_tab = CrudListTab(
            api_base_url, 'journals', "Journals & Submissions",
            "Track target journals and submission status.", "sand",
            fields=[
                {'key': 'name', 'label': 'Journal Name', 'kind': 'line'},
                {'key': 'status', 'label': 'Status', 'kind': 'combo',
                 'options': ['target', 'submitted', 'under_review', 'revisions_requested', 'accepted', 'rejected']},
                {'key': 'notes', 'label': 'Notes', 'kind': 'multiline'},
            ],
            renderer=lambda j: f"{j.get('name', '')}\n[{j.get('status', '')}]",
            tools=PAGE_TOOLS['journals'], tools_title="Journal Verification Tools"
        )
        layout.addWidget(self.crud_tab)

        self.guidelines_card = JournalGuidelinesCard(api_base_url)
        layout.addWidget(self.guidelines_card)

    def set_project(self, project_id: str):
        self.crud_tab.set_project(project_id)

    def refresh(self):
        self.crud_tab.refresh()


# ============================================================================
# Overview page (project-scoped)
# ============================================================================

class OverviewTab(QWidget):
    """Project summary: metadata + methodology progress snapshot"""

    def __init__(self, api_base_url: str):
        super().__init__()
        self.api_base_url = api_base_url
        self.project = None
        self._workers = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(16)

        info_card, info_layout = make_card("Project Overview", accent="rose")
        self.info_display = QTextBrowser()
        self.info_display.setMinimumHeight(260)
        info_layout.addWidget(self.info_display)
        layout.addWidget(info_card)

        progress_card, progress_layout = make_card("Methodology Progress", accent="sage")
        self.progress_display = QTextBrowser()
        self.progress_display.setMinimumHeight(120)
        progress_layout.addWidget(self.progress_display)
        layout.addWidget(progress_card, stretch=1)

    def set_project(self, project: Dict):
        self.project = project

        html = f"""
            <div style='font-family:Georgia, serif; font-size:18px; font-weight:700;'>{project.get('title', 'Untitled')}</div>
            <div style='color:{TEXT_MUTED}; margin-top:4px;'>{project.get('research_area', '')}</div>
            <table style='margin-top:14px;' cellpadding='4'>
                <tr><td style='color:{TEXT_MUTED};'>Institution</td><td>{project.get('institution') or '&mdash;'}</td></tr>
                <tr><td style='color:{TEXT_MUTED};'>Collaborators</td><td>{', '.join(project.get('collaborators', [])) or '&mdash;'}</td></tr>
                <tr><td style='color:{TEXT_MUTED};'>Funding</td><td>{project.get('funding') or '&mdash;'}</td></tr>
                <tr><td style='color:{TEXT_MUTED};'>Target journals</td><td>{', '.join(project.get('target_journals', [])) or '&mdash;'}</td></tr>
                <tr><td style='color:{TEXT_MUTED};'>Citation style</td><td>{project.get('citation_style') or '&mdash;'}</td></tr>
                <tr><td style='color:{TEXT_MUTED};'>Language</td><td>{project.get('language') or '&mdash;'}</td></tr>
                <tr><td style='color:{TEXT_MUTED};'>Timeline</td><td>{project.get('timeline') or '&mdash;'}</td></tr>
                <tr><td style='color:{TEXT_MUTED};'>Privacy</td><td>{project.get('privacy') or '&mdash;'}</td></tr>
                <tr><td style='color:{TEXT_MUTED};'>Status</td><td>{project.get('status') or '&mdash;'}</td></tr>
            </table>
        """
        self.info_display.setHtml(html)

        self.progress_display.setHtml(f"<div style='color:{TEXT_MUTED};'>Loading&hellip;</div>")
        worker = APIWorker(f"{self.api_base_url}/api/v1/projects/{project['id']}/methodology")
        self._workers.append(worker)
        worker.result_ready.connect(self._show_progress)
        worker.start()

    def _show_progress(self, result: Dict[str, Any]):
        methodology = result.get('methodology', {})
        total = methodology.get('total_steps', 0)
        completed = methodology.get('completed_count', 0)
        pct = completed / total if total else 0

        html = f"""
            <div style='font-weight:600;'>{methodology.get('research_type_name', '')}</div>
            <div style='margin-top:8px;'>{metric_bar_html('Steps completed', pct, SAGE)}</div>
            <div style='margin-top:6px; color:{TEXT_MUTED}; font-size:12px;'>{completed} of {total} steps completed</div>
        """
        self.progress_display.setHtml(html)


# ============================================================================
# Documentation page
# ============================================================================

class DocumentationTab(QWidget):
    """Guides and reference material"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(16)

        docs_card, docs_layout = make_card("Documentation & Resources", accent="rose")

        docs = [
            ("Quick Start Guide", "Create a project, pick a research type, and start tracking your work"),
            ("Research Types Guide", "Theoretical, Experimental, Exploratory, Pilot, Literature Review, Clinical"),
            ("Literature Search", "Europe PMC, CrossRef, arXiv, ERIC, Semantic Scholar - plus Scopus/ScienceDirect/Web of Science with your own API key"),
            ("Similarity Metrics", "How overall similarity, topic overlap, and shared terminology are computed"),
        ]

        for doc_title, desc in docs:
            btn = QPushButton(f"  {doc_title}\n    {desc}")
            btn.setObjectName("linkButton")
            btn.setIcon(icon("link.svg"))
            btn.setIconSize(QSize(16, 16))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            docs_layout.addWidget(btn)

        layout.addWidget(docs_card)

        about_card, about_layout = make_card("About Cortex", accent="rose")
        about_text = QLabel(
            "Cortex is a general-purpose AI-assisted research workspace, not limited to any single field.\n\n"
            "Version: 2.0.0\n\n"
            "Features:\n"
            "• Organize research into projects, each with its own research type\n"
            "• 6 general research types: Theoretical, Experimental, Exploratory, Pilot, Literature Review, Clinical\n"
            "• Validate research ideas against real literature (Europe PMC, CrossRef, arXiv, ERIC, Semantic Scholar,\n"
            "  plus Scopus/ScienceDirect/Web of Science if you configure an API key)\n"
            "• Paper Library with match-score tracking, one-click access to each paper, and annotations\n"
            "• Track methodology steps, tasks, hypotheses, manuscript drafts, and journal submissions\n"
            "• Transparent similarity metrics: topic overlap + shared terminology\n"
            "• Note: JSTOR, EBSCO, ProQuest, and Google Scholar have no public API and must be added manually"
        )
        about_text.setStyleSheet(f"color: {TEXT_MUTED};")
        about_text.setWordWrap(True)
        about_layout.addWidget(about_text)
        layout.addWidget(about_card)

        layout.addStretch()


# ============================================================================
# Projects home screen
# ============================================================================

class ProjectsHomeScreen(QWidget):
    """Landing screen: browse existing projects or create a new one"""

    project_opened = pyqtSignal(dict)

    def __init__(self, api_base_url: str):
        super().__init__()
        self.api_base_url = api_base_url
        self._projects = []
        self._workers = []
        self.init_ui()
        self.refresh()

    def init_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        content = QWidget()
        outer_layout.addWidget(scrollable(content))

        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        header_row = QHBoxLayout()
        logo_label = QLabel()
        logo_label.setPixmap(icon("logo.svg").pixmap(32, 32))
        header_row.addWidget(logo_label)

        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title = QLabel("CORTEX")
        title.setObjectName("sidebarBrand")
        subtitle = QLabel("Your Research Projects")
        subtitle.setObjectName("pageSubtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_row.addLayout(title_box)
        header_row.addStretch()

        new_btn = primary_button("New Project", "rose", icon_name="send.svg")
        new_btn.clicked.connect(lambda: self.create_card.setVisible(True))
        header_row.addWidget(new_btn)
        layout.addLayout(header_row)

        list_card, list_layout = make_card(
            "Existing Projects", "Double-click a project to open its workspace.", accent="blue"
        )
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(220)
        self.list_widget.itemDoubleClicked.connect(self.open_selected)
        list_layout.addWidget(self.list_widget)

        open_row = QHBoxLayout()
        open_btn = primary_button("Open Project", "blue", icon_name="send.svg")
        open_btn.clicked.connect(self.open_selected)
        open_row.addWidget(open_btn)
        open_row.addStretch()
        list_layout.addLayout(open_row)
        layout.addWidget(list_card)

        self.create_card, create_layout = make_card(
            "New Project",
            "Every project starts in a standardized workspace with a research type, "
            "and gets the matching methodology checklist automatically.",
            accent="sage"
        )
        self.create_card.setVisible(False)

        self.inputs = {}

        def add_field(key, label, kind='line', options=None, placeholder=''):
            lbl = QLabel(label)
            lbl.setObjectName("fieldLabel")
            create_layout.addWidget(lbl)
            if kind == 'combo':
                w = QComboBox()
                w.addItems(options)
            else:
                w = QLineEdit()
                w.setPlaceholderText(placeholder)
            self.inputs[key] = w
            create_layout.addWidget(w)

        add_field('title', 'Project Title *', placeholder='e.g. Sleep and Memory Consolidation Study')
        add_field('research_area', 'Research Area', placeholder='e.g. Cognitive Neuroscience, Labor Economics, Materials Science')
        add_field('research_type', 'Research Type *', kind='combo', options=[name for _, name in RESEARCH_TYPE_CHOICES])
        add_field('keywords', 'Keywords (comma-separated)', placeholder='e.g. memory, sleep, hippocampus')
        add_field('institution', 'Institution', placeholder='')
        add_field('collaborators', 'Collaborators (comma-separated)', placeholder='')
        add_field('funding', 'Funding', placeholder='e.g. NSF Grant #12345')
        add_field('target_journals', 'Target Journals (comma-separated)', placeholder='')
        add_field('citation_style', 'Citation Style', kind='combo', options=['APA', 'MLA', 'Chicago', 'Vancouver', 'IEEE', 'Harvard'])
        add_field('language', 'Language', placeholder='English')
        add_field('timeline', 'Timeline', placeholder='e.g. 2026-2027')
        add_field('privacy', 'Privacy', kind='combo', options=['private', 'team', 'public'])
        add_field('status', 'Status', kind='combo', options=['active', 'on_hold', 'completed', 'archived'])

        create_row = QHBoxLayout()
        create_btn = primary_button("Create Project", "sage", icon_name="send.svg")
        create_btn.clicked.connect(self.create_project)
        create_row.addWidget(create_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("linkButton")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(lambda: self.create_card.setVisible(False))
        create_row.addWidget(cancel_btn)
        create_row.addStretch()
        create_layout.addLayout(create_row)

        layout.addWidget(self.create_card)

    def refresh(self):
        worker = APIWorker(f"{self.api_base_url}/api/v1/projects")
        self._workers.append(worker)
        worker.result_ready.connect(self._populate)
        worker.start()

    def _populate(self, result: Dict[str, Any]):
        self._projects = result.get('projects', [])
        self.list_widget.clear()
        for project in self._projects:
            type_name = dict(RESEARCH_TYPE_CHOICES).get(project.get('research_type'), project.get('research_type'))
            text = f"{project.get('title')}  —  {type_name}  •  {project.get('status', '')}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, project)
            self.list_widget.addItem(item)

    def open_selected(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QMessageBox.information(self, "No Selection", "Select a project first.")
            return
        project = self.list_widget.item(row).data(Qt.ItemDataRole.UserRole)
        self.project_opened.emit(project)

    def create_project(self):
        title = self.inputs['title'].text().strip()
        if not title:
            QMessageBox.warning(self, "Input Error", "Please enter a project title")
            return

        type_name = self.inputs['research_type'].currentText()
        type_key = next((k for k, n in RESEARCH_TYPE_CHOICES if n == type_name), 'experimental')

        def split_list(key):
            return [s.strip() for s in self.inputs[key].text().split(',') if s.strip()]

        payload = {
            'title': title,
            'research_area': self.inputs['research_area'].text().strip(),
            'research_type': type_key,
            'keywords': split_list('keywords'),
            'institution': self.inputs['institution'].text().strip(),
            'collaborators': split_list('collaborators'),
            'funding': self.inputs['funding'].text().strip(),
            'target_journals': split_list('target_journals'),
            'citation_style': self.inputs['citation_style'].currentText(),
            'language': self.inputs['language'].text().strip() or 'English',
            'timeline': self.inputs['timeline'].text().strip(),
            'privacy': self.inputs['privacy'].currentText(),
            'status': self.inputs['status'].currentText(),
        }

        worker = APIWorker(f"{self.api_base_url}/api/v1/projects", method="POST", data=payload)
        self._workers.append(worker)
        worker.result_ready.connect(self._on_created)
        worker.error_occurred.connect(lambda e: QMessageBox.critical(self, "Error", e))
        worker.start()

    def _on_created(self, result: Dict[str, Any]):
        self.create_card.setVisible(False)
        self.refresh()
        project = result.get('project')
        if project:
            self.project_opened.emit(project)


# ============================================================================
# Workspace screen (sidebar + topbar + project-scoped pages)
# ============================================================================

class WorkspaceScreen(QWidget):
    """Sidebar-driven workspace for a single open project"""

    back_requested = pyqtSignal()

    NAV_ITEMS = [
        ("home.svg", "Overview", "Project summary and progress", "rose"),
        ("compass.svg", "Methodology", "Track your research steps", "sage"),
        ("lightbulb.svg", "Literature", "Search and validate against real literature", "blue"),
        ("folder.svg", "Paper Library", "Papers saved to this project", "sand"),
        ("question.svg", "Hypotheses", "Track proposed hypotheses", "rose"),
        ("checklist.svg", "Tasks", "Project tasks and milestones", "sage"),
        ("chart.svg", "Data & Analysis", "Import data, run stats, and make charts", "blue"),
        ("document_pen.svg", "Manuscript", "Draft your manuscript sections", "blue"),
        ("newspaper.svg", "Journals", "Target journals and submissions", "sand"),
        ("book.svg", "Documentation", "Guides and reference material", "rose"),
    ]

    def __init__(self, api_base_url: str):
        super().__init__()
        self.api_base_url = api_base_url
        self.project = None
        self.init_ui()

    def init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.overview_tab = OverviewTab(self.api_base_url)
        self.methodology_tab = ProjectMethodologyTab(self.api_base_url)
        self.literature_tab = IdeaValidationTab(self.api_base_url)
        self.papers_tab = PaperLibraryTab(self.api_base_url)
        self.hypotheses_tab = CrudListTab(
            self.api_base_url, 'hypotheses', "Hypotheses",
            "Track candidate hypotheses for this project.", "rose",
            fields=[
                {'key': 'text', 'label': 'Hypothesis', 'kind': 'multiline'},
                {'key': 'status', 'label': 'Status', 'kind': 'combo', 'options': ['proposed', 'supported', 'rejected', 'inconclusive']},
            ],
            renderer=lambda h: f"{h.get('text', '')}\n[{h.get('status', '')}]",
            tools=PAGE_TOOLS['hypotheses'], tools_title="Idea Generation Tools"
        )
        self.tasks_tab = CrudListTab(
            self.api_base_url, 'tasks', "Tasks & Milestones",
            "Track tasks for this project.", "sage",
            fields=[
                {'key': 'title', 'label': 'Task', 'kind': 'line'},
                {'key': 'status', 'label': 'Status', 'kind': 'combo', 'options': ['todo', 'in_progress', 'done']},
                {'key': 'due_date', 'label': 'Due Date', 'kind': 'line', 'placeholder': 'YYYY-MM-DD'},
            ],
            renderer=lambda t: f"{t.get('title', '')}\n[{t.get('status', '')}] due {t.get('due_date') or '—'}",
            tools=PAGE_TOOLS['tasks'], tools_title="Project Management Tools"
        )
        self.data_tab = DataAnalysisTab(self.api_base_url)
        self.manuscript_tab = ManuscriptTab(self.api_base_url)
        self.journals_tab = JournalsPageTab(self.api_base_url)
        self.documentation_tab = DocumentationTab()

        self.pages = QStackedWidget()
        for page in [
            self.overview_tab, self.methodology_tab, self.literature_tab, self.papers_tab,
            self.hypotheses_tab, self.tasks_tab, self.data_tab, self.manuscript_tab, self.journals_tab, self.documentation_tab
        ]:
            self.pages.addWidget(scrollable(page))

        content_layout.addWidget(self._build_topbar())
        content_layout.addWidget(self.pages, stretch=1)
        root.addWidget(content, stretch=1)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 18, 14, 18)
        layout.setSpacing(4)

        back_btn = QPushButton("  All Projects")
        back_btn.setObjectName("backButton")
        back_btn.setIcon(icon("arrow_left.svg"))
        back_btn.setIconSize(QSize(13, 13))
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.back_requested.emit)
        layout.addWidget(back_btn)
        layout.addSpacing(12)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_buttons = []

        for i, (icon_name, label, _tip, accent) in enumerate(self.NAV_ITEMS):
            btn = QPushButton(f"  {label}".replace('&', '&&'))
            btn.setObjectName("navButton")
            btn.setProperty("accent", accent)
            btn.setIcon(icon(icon_name))
            btn.setIconSize(QSize(16, 16))
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(38)
            btn.clicked.connect(lambda _checked, idx=i: self._navigate(idx))
            self.nav_group.addButton(btn, i)
            self.nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()
        return sidebar

    def _build_topbar(self) -> QFrame:
        topbar = QFrame()
        topbar.setObjectName("topBar")
        topbar.setFixedHeight(64)

        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(24, 10, 24, 10)

        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        self.page_title = QLabel(self.NAV_ITEMS[0][1])
        self.page_title.setObjectName("pageTitle")
        self.page_subtitle = QLabel(self.NAV_ITEMS[0][2])
        self.page_subtitle.setObjectName("pageSubtitle")
        title_box.addWidget(self.page_title)
        title_box.addWidget(self.page_subtitle)
        layout.addLayout(title_box)
        layout.addStretch()

        self.status_pill = QLabel()
        layout.addWidget(self.status_pill)
        self._refresh_server_status()

        return topbar

    def _navigate(self, index: int):
        self.pages.setCurrentIndex(index)
        self.page_title.setText(self.NAV_ITEMS[index][1])
        self.page_subtitle.setText(self.NAV_ITEMS[index][2])
        self._refresh_page(index)

    def _refresh_page(self, index: int):
        """Re-fetch data for pages whose content may have changed elsewhere in
        the session (e.g. papers saved from Literature while Paper Library was
        last shown). Manuscript and Literature are intentionally excluded so
        in-progress typing/search state isn't clobbered by a background refresh."""
        if index == 0 and self.project:
            self.overview_tab.set_project(self.project)
        elif index == 1:
            self.methodology_tab.refresh()
        elif index == 3:
            self.papers_tab.refresh()
        elif index == 4:
            self.hypotheses_tab.refresh()
        elif index == 5:
            self.tasks_tab.refresh()
        elif index == 6:
            self.data_tab.refresh()
        elif index == 7:
            self.journals_tab.refresh()

    def _refresh_server_status(self):
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=2)
            online = response.status_code == 200
        except Exception:
            online = False

        if online:
            self.status_pill.setText("&#9679;  Server Online")
            self.status_pill.setStyleSheet(
                f"background-color: {SAGE_TINT}; color: #4c6444; border-radius: 12px; padding: 5px 12px; font-size: 11px; font-weight: 600;"
            )
        else:
            self.status_pill.setText("&#9679;  Server Offline")
            self.status_pill.setStyleSheet(
                f"background-color: {ROSE_TINT}; color: #8a4c3a; border-radius: 12px; padding: 5px 12px; font-size: 11px; font-weight: 600;"
            )
        self.status_pill.setTextFormat(Qt.TextFormat.RichText)

    def open_project(self, project: Dict):
        self.project = project
        project_id = project['id']

        self.overview_tab.set_project(project)
        self.methodology_tab.set_project(project_id)
        self.literature_tab.set_project(project_id)
        self.papers_tab.set_project(project_id)
        self.hypotheses_tab.set_project(project_id)
        self.tasks_tab.set_project(project_id)
        self.data_tab.set_project(project_id)
        self.manuscript_tab.set_project(project_id)
        self.journals_tab.set_project(project_id)

        self.nav_buttons[0].setChecked(True)
        self._navigate(0)
        self._refresh_server_status()


# ============================================================================
# Main window
# ============================================================================

class CortexMainWindow(QMainWindow):
    """Main application window: swaps between the projects home and an open workspace"""

    def __init__(self, api_base_url: str = "http://localhost:5050"):
        super().__init__()
        self.api_base_url = api_base_url

        self.setWindowTitle("Cortex - AI-Assisted Research Workspace")
        self.setGeometry(100, 100, 1120, 780)
        self.setMinimumSize(920, 620)

        self.root_stack = QStackedWidget()
        self.setCentralWidget(self.root_stack)

        self.projects_screen = ProjectsHomeScreen(api_base_url)
        self.workspace_screen = WorkspaceScreen(api_base_url)

        self.projects_screen.project_opened.connect(self.open_project)
        self.workspace_screen.back_requested.connect(self.show_projects)

        self.root_stack.addWidget(self.projects_screen)
        self.root_stack.addWidget(self.workspace_screen)

        self.statusBar().showMessage("Ready")

    def open_project(self, project: Dict):
        self.workspace_screen.open_project(project)
        self.root_stack.setCurrentIndex(1)

    def show_projects(self):
        self.projects_screen.refresh()
        self.root_stack.setCurrentIndex(0)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(STYLESHEET)

    window = CortexMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
