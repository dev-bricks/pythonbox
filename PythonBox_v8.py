#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Python Code Architect (Baukasten v8)
FEATURES v5:
- Suchen & Ersetzen (Ctrl+F / Ctrl+H)
- Integriertes Output-Panel
- Tab-System für mehrere Dateien
- Undo/Redo Buttons
- Statusbar mit Zeilen/Spalten-Anzeige
- Zuletzt geöffnete Dateien

FEATURES v6:
- Auto-Completion für Python Keywords und Builtins
- Code Folding (Klassen/Funktionen einklappen)
- Einstellungs-Dialog (Schriftgröße, Tab-Größe, Theme)
- Gehe zu Zeile (Ctrl+G)
- Bracket Matching (Klammer-Hervorhebung)

FEATURES v7:
- Minimap (Code-Vorschau rechts)
- Code Folding (Klassen/Funktionen einklappen mit +/- Buttons)
- Linter-Integration (Pylint/Flake8 Fehleranzeige)
- Git-Integration (Status, Diff, Modified-Anzeige)
- Fehler-Markierungen im Editor (rote Wellenlinien)

NEUE FEATURES v8:
- VS Code Integration (In VS Code öffnen/debuggen)
- PDB Debugger im Output-Panel (interaktiv)
- Breakpoint-Verwaltung (visuell im Editor)
- Debug-Toolbar mit Step-Controls
- PyCharm Integration (optional)
"""

import sys
import os
import shutil
import json
import ast
import subprocess
import re
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple

# GUI Imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSplitter, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QInputDialog, QPlainTextEdit, QFrame, QComboBox,
    QDialog, QFormLayout, QDialogButtonBox, QTextEdit, QMenu, QAction,
    QFileDialog, QProgressBar, QCheckBox, QStyle, QSystemTrayIcon,
    QTabWidget, QTabBar, QLineEdit, QShortcut, QToolBar, QStatusBar,
    QDockWidget, QGroupBox, QRadioButton, QCompleter, QSpinBox,
    QScrollBar, QSlider, QSizePolicy, QListWidget, QListWidgetItem,
    QToolTip
)
from PyQt5.QtCore import (
    Qt, QSize, QRect, QRegExp, QUrl, QMimeData, QProcess, 
    QTimer, pyqtSignal, QSettings, QStringListModel, QPoint
)
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QTextFormat, QSyntaxHighlighter, 
    QTextCharFormat, QPalette, QIcon, QKeySequence, QTextCursor,
    QTextDocument, QFontMetrics, QPen, QBrush
)

# ============================================================================
# MODERN UI THEME
# ============================================================================

def set_dark_theme(app):
    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_color = QColor(40, 40, 40)
    
    dark_palette.setColor(QPalette.Window, dark_color)
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.AlternateBase, dark_color)
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    
    app.setPalette(dark_palette)
    app.setStyleSheet("""
        QTreeWidget { background-color: #252525; border: 1px solid #444; color: #ddd; }
        QHeaderView::section { background-color: #353535; border: 1px solid #444; }
        QPlainTextEdit { background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas, monospace; }
        QPushButton { 
            background-color: #3a3a3a; border: 1px solid #555; 
            padding: 6px 12px; border-radius: 4px; color: white;
        }
        QPushButton:hover { background-color: #4a4a4a; border-color: #2a82da; }
        QPushButton:pressed { background-color: #2a82da; }
        QPushButton:disabled { background-color: #2a2a2a; color: #666; }
        QSplitter::handle { background-color: #444; width: 2px; }
        QMenuBar { background-color: #353535; color: white; }
        QMenuBar::item:selected { background-color: #2a82da; }
        QMenu { background-color: #353535; color: white; border: 1px solid #555; }
        QMenu::item:selected { background-color: #2a82da; }
        QTabWidget::pane { border: 1px solid #444; background: #1e1e1e; }
        QTabBar::tab { 
            background: #353535; color: #aaa; padding: 8px 16px; 
            border: 1px solid #444; border-bottom: none; margin-right: 2px;
        }
        QTabBar::tab:selected { background: #1e1e1e; color: white; border-bottom: 1px solid #1e1e1e; }
        QTabBar::tab:hover { background: #4a4a4a; }
        QLineEdit { 
            background: #2a2a2a; border: 1px solid #555; color: white; 
            padding: 4px 8px; border-radius: 3px;
        }
        QLineEdit:focus { border-color: #2a82da; }
        QToolBar { background: #353535; border: none; spacing: 3px; padding: 3px; }
        QToolBar QToolButton { background: transparent; border: none; padding: 4px; }
        QToolBar QToolButton:hover { background: #4a4a4a; border-radius: 3px; }
        QDockWidget { color: white; }
        QDockWidget::title { background: #353535; padding: 6px; }
    """)

# ============================================================================
# EDITOR KOMPONENTEN
# ============================================================================

class LineNumberArea(QWidget):
    """Widget für Zeilennummern-Anzeige und Breakpoint-Verwaltung.

    Zeigt Zeilennummern links vom Code-Editor an und ermöglicht das Setzen
    von Breakpoints durch Klick auf die Zeilennummer.
    """
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

    def mousePressEvent(self, event):
        """Weiterleitung an Editor für Breakpoint-Toggle (NEU v8)"""
        self.codeEditor.lineNumberAreaMousePress(event)


class CodeEditor(QPlainTextEdit):
    """Erweiterter Code-Editor mit umfangreichen Entwicklungs-Features.

    Features:
    - Zeilennummern-Anzeige mit Breakpoint-Support
    - Syntax-Highlighting für Python
    - Auto-Completion (Keywords, Builtins)
    - Bracket Matching (Klammer-Hervorhebung)
    - Code Folding (Klassen/Funktionen einklappbar)
    - Linter-Integration (Pylint/Flake8 Fehleranzeige)
    - Git-Integration (Modified/Added Lines Anzeige)
    - Minimap (Code-Vorschau)
    - Suchen & Ersetzen mit Highlighting

    Signals:
        cursorPositionInfo(int, int): Sendet Cursor-Position (Zeile, Spalte)
        modificationChanged(bool): Sendet Änderungsstatus des Dokuments
    """

    cursorPositionInfo = pyqtSignal(int, int)  # Zeile, Spalte
    modificationChanged = pyqtSignal(bool)
    
    # Klammer-Paare für Matching
    BRACKETS = {'(': ')', '[': ']', '{': '}', ')': '(', ']': '[', '}': '{'}
    OPEN_BRACKETS = '([{'
    CLOSE_BRACKETS = ')]}'
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Search highlighting - MUSS vor highlightCurrentLine() initialisiert werden!
        self.search_selections = []
        self.bracket_selections = []
        self.error_selections = []  # NEU v7: Linter-Fehler
        
        # Settings
        self.autocomplete_enabled = True
        self.bracket_matching_enabled = True
        self.show_line_numbers = True
        self.show_folding = True  # NEU v7
        
        # Linter Errors (NEU v7)
        self.linter_errors: List[Dict] = []
        self.git_modified_lines: set = set()
        self.git_added_lines: set = set()
        
        # Breakpoints (NEU v8)
        self.breakpoints: set = set()  # Set von Zeilennummern
        self.current_debug_line: int = -1  # Aktuelle Debug-Zeile
        
        self.lineNumberArea = LineNumberArea(self)
        
        # Folding Area (NEU v7)
        self.foldingArea = FoldingArea(self)
        
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.cursorPositionChanged.connect(self.emitCursorPosition)
        self.cursorPositionChanged.connect(self.matchBrackets)
        self.document().modificationChanged.connect(self.modificationChanged.emit)
        
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
        
        font = QFont("Consolas", 10) 
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setTabStopWidth(self.fontMetrics().width(' ') * 4)
        
        # Auto-Completion Setup
        self.completer = None
        self.setup_completer()

    def setup_completer(self):
        """Initialisiert den Auto-Completer"""
        words = sorted(set(PYTHON_KEYWORDS + PYTHON_BUILTINS + list(PYTHON_SNIPPETS.keys())))
        
        self.completer = QCompleter(words, self)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.activated.connect(self.insert_completion)
        
        # Popup Style
        popup = self.completer.popup()
        popup.setStyleSheet("""
            QListView {
                background-color: #2d2d2d;
                color: #ddd;
                border: 1px solid #555;
                selection-background-color: #2a82da;
            }
        """)

    def insert_completion(self, completion: str):
        """Fügt die Completion ein"""
        tc = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        
        # Prüfe ob es ein Snippet ist
        if completion in PYTHON_SNIPPETS:
            tc.movePosition(QTextCursor.StartOfWord, QTextCursor.KeepAnchor)
            tc.removeSelectedText()
            tc.insertText(PYTHON_SNIPPETS[completion])
        else:
            tc.insertText(completion[-extra:])
        
        self.setTextCursor(tc)

    def text_under_cursor(self) -> str:
        """Gibt das Wort unter dem Cursor zurück"""
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def keyPressEvent(self, event):
        """Überschriebenes Key Event für Auto-Completion und Auto-Indent"""
        # Completer aktiv?
        if self.completer and self.completer.popup().isVisible():
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, 
                              Qt.Key_Tab, Qt.Key_Backtab):
                event.ignore()
                return
        
        # Auto-Indent bei Enter
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            cursor = self.textCursor()
            line = cursor.block().text()
            indent = len(line) - len(line.lstrip())
            
            # Extra Indent nach :
            if line.rstrip().endswith(':'):
                indent += 4
            
            super().keyPressEvent(event)
            cursor = self.textCursor()
            cursor.insertText(' ' * indent)
            return
        
        # Auto-Close Brackets
        bracket_pairs = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'"}
        if event.text() in bracket_pairs:
            cursor = self.textCursor()
            super().keyPressEvent(event)
            cursor = self.textCursor()
            cursor.insertText(bracket_pairs[event.text()])
            cursor.movePosition(QTextCursor.Left)
            self.setTextCursor(cursor)
            return
        
        super().keyPressEvent(event)
        
        # Auto-Completion Trigger
        if self.autocomplete_enabled and self.completer:
            prefix = self.text_under_cursor()
            
            if len(prefix) < 2:
                self.completer.popup().hide()
                return
            
            if prefix != self.completer.completionPrefix():
                self.completer.setCompletionPrefix(prefix)
                self.completer.popup().setCurrentIndex(
                    self.completer.completionModel().index(0, 0)
                )
            
            cr = self.cursorRect()
            cr.setWidth(self.completer.popup().sizeHintForColumn(0) + 
                       self.completer.popup().verticalScrollBar().sizeHint().width())
            self.completer.complete(cr)

    def matchBrackets(self):
        """Hebt passende Klammern hervor"""
        self.bracket_selections = []
        
        if not self.bracket_matching_enabled:
            self.highlightCurrentLine()
            return
        
        cursor = self.textCursor()
        text = self.toPlainText()
        pos = cursor.position()
        
        if pos >= len(text):
            self.highlightCurrentLine()
            return
        
        char_at_pos = text[pos] if pos < len(text) else ''
        char_before = text[pos - 1] if pos > 0 else ''
        
        bracket_char = None
        bracket_pos = None
        
        if char_at_pos in self.BRACKETS:
            bracket_char = char_at_pos
            bracket_pos = pos
        elif char_before in self.BRACKETS:
            bracket_char = char_before
            bracket_pos = pos - 1
        
        if bracket_char and bracket_pos is not None:
            match_pos = self.find_matching_bracket(text, bracket_pos, bracket_char)
            
            if match_pos is not None:
                # Hervorhebungs-Format
                fmt = QTextCharFormat()
                fmt.setBackground(QColor(80, 80, 0))
                fmt.setForeground(QColor(255, 255, 0))
                
                # Erste Klammer
                sel1 = QTextEdit.ExtraSelection()
                sel1.format = fmt
                cur1 = self.textCursor()
                cur1.setPosition(bracket_pos)
                cur1.setPosition(bracket_pos + 1, QTextCursor.KeepAnchor)
                sel1.cursor = cur1
                self.bracket_selections.append(sel1)
                
                # Zweite Klammer
                sel2 = QTextEdit.ExtraSelection()
                sel2.format = fmt
                cur2 = self.textCursor()
                cur2.setPosition(match_pos)
                cur2.setPosition(match_pos + 1, QTextCursor.KeepAnchor)
                sel2.cursor = cur2
                self.bracket_selections.append(sel2)
        
        self.highlightCurrentLine()

    def find_matching_bracket(self, text: str, pos: int, bracket: str) -> int:
        """Findet die passende Klammer"""
        if bracket in self.OPEN_BRACKETS:
            # Suche vorwärts
            target = self.BRACKETS[bracket]
            direction = 1
            start = pos + 1
            end = len(text)
        else:
            # Suche rückwärts
            target = self.BRACKETS[bracket]
            direction = -1
            start = pos - 1
            end = -1
        
        count = 1
        i = start
        
        while i != end:
            char = text[i]
            if char == bracket:
                count += 1
            elif char == target:
                count -= 1
                if count == 0:
                    return i
            i += direction
        
        return None

    def emitCursorPosition(self):
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursorPositionInfo.emit(line, col)

    def lineNumberAreaWidth(self):
        digits = 1
        max_val = max(1, self.blockCount())
        while max_val >= 10:
            max_val //= 10
            digits += 1
        width = 20 + self.fontMetrics().width('9') * digits
        # Platz für Git-Markierung
        width += 4
        return width

    def foldingAreaWidth(self):
        return 14 if self.show_folding else 0

    def updateLineNumberAreaWidth(self, _):
        total_margin = self.lineNumberAreaWidth() + self.foldingAreaWidth()
        self.setViewportMargins(total_margin, 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
            self.foldingArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
            self.foldingArea.update(0, rect.y(), self.foldingArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        line_width = self.lineNumberAreaWidth()
        fold_width = self.foldingAreaWidth()
        
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), line_width, cr.height()))
        self.foldingArea.setGeometry(QRect(cr.left() + line_width, cr.top(), fold_width, cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor(35, 35, 35)) 
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line_num = blockNumber + 1
                number = str(line_num)
                
                # Breakpoint-Markierung (NEU v8) - roter Kreis
                if line_num in self.breakpoints:
                    painter.setBrush(QColor(200, 50, 50))
                    painter.setPen(Qt.NoPen)
                    circle_size = min(12, self.fontMetrics().height() - 2)
                    painter.drawEllipse(2, top + 2, circle_size, circle_size)
                
                # Aktuelle Debug-Zeile (NEU v8) - gelber Pfeil
                if line_num == self.current_debug_line:
                    painter.setBrush(QColor(255, 255, 0))
                    painter.setPen(Qt.NoPen)
                    # Pfeil zeichnen
                    arrow_y = top + self.fontMetrics().height() // 2
                    painter.drawPolygon([
                        QPoint(4, arrow_y - 4),
                        QPoint(12, arrow_y),
                        QPoint(4, arrow_y + 4)
                    ])
                
                # Git-Markierung (NEU v7)
                if line_num in self.git_added_lines:
                    painter.fillRect(14, top, 3, self.fontMetrics().height(), QColor(0, 180, 0))
                elif line_num in self.git_modified_lines:
                    painter.fillRect(14, top, 3, self.fontMetrics().height(), QColor(200, 150, 0))
                
                # Linter-Fehler-Markierung (NEU v7)
                has_error = any(e['line'] == line_num and e['severity'] == 'error' for e in self.linter_errors)
                has_warning = any(e['line'] == line_num and e['severity'] == 'warning' for e in self.linter_errors)
                
                if has_error:
                    painter.setPen(QColor(255, 80, 80))
                elif has_warning:
                    painter.setPen(QColor(255, 200, 80))
                else:
                    painter.setPen(QColor(100, 100, 100))
                
                painter.drawText(18, top, self.lineNumberArea.width() - 22, 
                               self.fontMetrics().height(), Qt.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def lineNumberAreaMousePress(self, event):
        """Klick auf Zeilennummer-Bereich zum Setzen von Breakpoints (NEU v8)"""
        if event.button() == Qt.LeftButton:
            # Finde angeklickte Zeile
            block = self.firstVisibleBlock()
            top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
            
            while block.isValid():
                block_height = int(self.blockBoundingRect(block).height())
                if top <= event.y() < top + block_height:
                    line = block.blockNumber() + 1
                    self.toggle_breakpoint(line)
                    break
                top += block_height
                block = block.next()

    def toggle_breakpoint(self, line: int) -> bool:
        """Setzt oder entfernt Breakpoint, gibt neuen Status zurück (NEU v8)"""
        if line in self.breakpoints:
            self.breakpoints.remove(line)
            status = False
        else:
            self.breakpoints.add(line)
            status = True
        self.lineNumberArea.update()
        return status

    def set_debug_line(self, line: int):
        """Setzt aktuelle Debug-Zeile (NEU v8)"""
        self.current_debug_line = line
        self.lineNumberArea.update()
        
        # Zeile zentrieren
        if line > 0:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line - 1)
            self.setTextCursor(cursor)
            self.centerCursor()

    def clear_debug_state(self):
        """Löscht Debug-Zustand (NEU v8)"""
        self.current_debug_line = -1
        self.lineNumberArea.update()

    def set_linter_errors(self, errors: List[Dict]):
        """Setzt Linter-Fehler und aktualisiert Markierungen (NEU v7)"""
        self.linter_errors = errors
        self.error_selections = []
        
        for error in errors:
            line = error.get('line', 1) - 1
            block = self.document().findBlockByNumber(line)
            if not block.isValid():
                continue
            
            selection = QTextEdit.ExtraSelection()
            
            # Fehler = rot unterstrichen, Warnung = gelb
            if error.get('severity') == 'error':
                selection.format.setUnderlineColor(QColor(255, 80, 80))
            else:
                selection.format.setUnderlineColor(QColor(255, 200, 80))
            
            selection.format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
            
            cursor = QTextCursor(block)
            cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
            selection.cursor = cursor
            
            self.error_selections.append(selection)
        
        self.lineNumberArea.update()
        self.highlightCurrentLine()

    def set_git_status(self, added: set, modified: set):
        """Setzt Git-Status für Zeilen (NEU v7)"""
        self.git_added_lines = added
        self.git_modified_lines = modified
        self.lineNumberArea.update()

    def highlightCurrentLine(self):
        extraSelections = list(self.search_selections) + list(self.bracket_selections) + list(self.error_selections)
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(45, 45, 45))
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.insert(0, selection)
        self.setExtraSelections(extraSelections)

    def highlightSearchResults(self, pattern: str, case_sensitive: bool = False):
        """Hebt alle Suchergebnisse hervor"""
        self.search_selections = []
        if not pattern:
            self.highlightCurrentLine()
            return 0
        
        flags = QTextDocument.FindFlags()
        if case_sensitive:
            flags |= QTextDocument.FindCaseSensitively
        
        cursor = QTextCursor(self.document())
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor(100, 100, 0))
        highlight_format.setForeground(QColor(255, 255, 255))
        
        count = 0
        while True:
            cursor = self.document().find(pattern, cursor, flags)
            if cursor.isNull():
                break
            selection = QTextEdit.ExtraSelection()
            selection.format = highlight_format
            selection.cursor = cursor
            self.search_selections.append(selection)
            count += 1
        
        self.highlightCurrentLine()
        return count

    def clearSearchHighlight(self):
        self.search_selections = []
        self.highlightCurrentLine()


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax-Highlighter für Python-Code.

    Hebt folgende Elemente farblich hervor:
    - Keywords (and, if, def, class, etc.) - Blau
    - Decorators (@decorator) - Lila
    - Strings ("text", 'text') - Orange
    - Kommentare (# comment) - Grün
    - Funktions-/Klassendefinitionen - Gelb
    - Zahlen - Hellgrün
    """
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []
        
        # Keywords (Blau)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(86, 156, 214))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'finally', 'for', 'from',
            'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal',
            'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with',
            'yield', 'True', 'False', 'None', 'self'
        ]
        for word in keywords:
            self.highlighting_rules.append((QRegExp(r'\b' + word + r'\b'), keyword_format))
        
        # Decorators (Lila)
        dec_format = QTextCharFormat()
        dec_format.setForeground(QColor(189, 147, 249))
        self.highlighting_rules.append((QRegExp(r'@[^\n]+'), dec_format))

        # Strings (Orange)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(206, 145, 120))
        self.highlighting_rules.append((QRegExp(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.highlighting_rules.append((QRegExp(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))
        
        # Comments (Grün)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(106, 153, 85))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((QRegExp(r'#[^\n]*'), comment_format))
        
        # Function/Class Definitions (Gelb)
        func_format = QTextCharFormat()
        func_format.setForeground(QColor(220, 220, 170))
        self.highlighting_rules.append((QRegExp(r'\bdef\s+(\w+)'), func_format))
        self.highlighting_rules.append((QRegExp(r'\bclass\s+(\w+)'), func_format))
        
        # Numbers (Hellgrün)
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(181, 206, 168))
        self.highlighting_rules.append((QRegExp(r'\b[0-9]+\.?[0-9]*\b'), number_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)


# ============================================================================
# MINIMAP (NEU v7!)
# ============================================================================

class Minimap(QPlainTextEdit):
    """Minimap für Code-Vorschau und schnelle Navigation.

    Zeigt eine miniaturisierte Version des gesamten Code-Dokuments an und
    ermöglicht schnelles Springen zu beliebigen Code-Stellen durch Klick.
    Hebt den aktuell sichtbaren Bereich im Haupteditor hervor.

    Args:
        editor: Referenz zum Haupt-CodeEditor
        parent: Optional parent widget
    """

    def __init__(self, editor: 'CodeEditor', parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setReadOnly(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.setCursor(Qt.PointingHandCursor)
        
        # Sehr kleine Schrift für Minimap
        font = QFont("Consolas", 1)
        self.setFont(font)
        
        # Styling
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1a1a1a;
                border: none;
                border-left: 1px solid #333;
            }
        """)
        
        self.setFixedWidth(80)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        
        # Viewport-Rechteck
        self.viewport_rect = QRect()
        
        # Verbindungen
        self.editor.textChanged.connect(self.update_content)
        self.editor.verticalScrollBar().valueChanged.connect(self.update_viewport)
        
        self.update_content()

    def update_content(self):
        """Aktualisiert den Minimap-Inhalt"""
        self.setPlainText(self.editor.toPlainText())
        self.update_viewport()

    def update_viewport(self):
        """Aktualisiert die Viewport-Anzeige"""
        editor_scrollbar = self.editor.verticalScrollBar()
        
        if editor_scrollbar.maximum() == 0:
            # Keine Scrollbar nötig
            self.viewport_rect = QRect(0, 0, self.width(), self.height())
        else:
            # Berechne sichtbaren Bereich
            ratio = editor_scrollbar.value() / max(1, editor_scrollbar.maximum())
            visible_ratio = self.editor.viewport().height() / max(1, self.editor.document().size().height())
            
            y = int(ratio * self.height())
            h = int(visible_ratio * self.height())
            h = max(20, min(h, self.height()))
            
            self.viewport_rect = QRect(0, y, self.width(), h)
        
        self.viewport().update()

    def paintEvent(self, event):
        super().paintEvent(event)
        
        # Zeichne Viewport-Rechteck
        painter = QPainter(self.viewport())
        painter.setOpacity(0.3)
        painter.fillRect(self.viewport_rect, QColor(100, 100, 200))
        painter.setOpacity(1.0)
        painter.setPen(QPen(QColor(100, 100, 200), 1))
        painter.drawRect(self.viewport_rect)

    def mousePressEvent(self, event):
        """Springt zur geklickten Position"""
        if event.button() == Qt.LeftButton:
            self._scroll_to_position(event.pos().y())

    def mouseMoveEvent(self, event):
        """Scrollt beim Ziehen"""
        if event.buttons() & Qt.LeftButton:
            self._scroll_to_position(event.pos().y())

    def _scroll_to_position(self, y: int):
        """Scrollt den Editor zur Y-Position"""
        ratio = y / max(1, self.height())
        scrollbar = self.editor.verticalScrollBar()
        scrollbar.setValue(int(ratio * scrollbar.maximum()))


# ============================================================================
# FOLDING AREA (NEU v7!)
# ============================================================================

class FoldingArea(QWidget):
    """Bereich für Code-Folding Buttons (+/-).

    Ermöglicht das Ein- und Ausklappen von Code-Blöcken wie Funktionen,
    Klassen, if/for/while-Statements. Zeigt +/- Buttons für alle faltbaren
    Blöcke an. Erkennt faltbare Blöcke automatisch anhand der Einrückung
    und ':' am Zeilenende.

    Args:
        editor: Referenz zum Haupt-CodeEditor
    """

    def __init__(self, editor: 'CodeEditor'):
        super().__init__(editor)
        self.editor = editor
        self.folded_blocks = set()  # Set von gefalteten Block-Nummern
        self.foldable_blocks = {}   # {block_number: end_block_number}
        
        self.setFixedWidth(14)
        self.setCursor(Qt.PointingHandCursor)
        
        # Verbindungen
        self.editor.blockCountChanged.connect(self.update_foldable_blocks)
        self.editor.textChanged.connect(self.update_foldable_blocks)

    def update_foldable_blocks(self):
        """Ermittelt faltbare Blöcke (def, class, if, for, etc.)"""
        self.foldable_blocks = {}
        text = self.editor.toPlainText()
        lines = text.split('\n')
        
        stack = []  # (start_line, indent)
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
            
            indent = len(line) - len(line.lstrip())
            
            # Schließe vorherige Blöcke wenn Einrückung zurückgeht
            while stack and indent <= stack[-1][1]:
                start_line, start_indent = stack.pop()
                if i > start_line + 1:  # Mindestens 2 Zeilen
                    self.foldable_blocks[start_line] = i - 1
            
            # Neuen Block starten bei :
            if stripped.endswith(':') and not stripped.startswith('#'):
                stack.append((i, indent))
        
        # Verbleibende Blöcke schließen
        for start_line, _ in stack:
            if len(lines) > start_line + 1:
                self.foldable_blocks[start_line] = len(lines) - 1
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(35, 35, 35))
        
        block = self.editor.firstVisibleBlock()
        top = int(self.editor.blockBoundingGeometry(block).translated(
            self.editor.contentOffset()).top())
        bottom = top + int(self.editor.blockBoundingRect(block).height())
        
        while block.isValid() and top <= event.rect().bottom():
            block_number = block.blockNumber()
            
            if block_number in self.foldable_blocks:
                # Zeichne +/- Symbol
                is_folded = block_number in self.folded_blocks
                symbol = "+" if is_folded else "−"
                
                painter.setPen(QColor(150, 150, 150))
                painter.drawText(0, top, self.width(), 
                               self.editor.fontMetrics().height(),
                               Qt.AlignCenter, symbol)
            
            block = block.next()
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())

    def mousePressEvent(self, event):
        """Toggle Folding beim Klick"""
        if event.button() != Qt.LeftButton:
            return
        
        # Finde geklickten Block
        block = self.editor.firstVisibleBlock()
        top = int(self.editor.blockBoundingGeometry(block).translated(
            self.editor.contentOffset()).top())
        
        while block.isValid():
            block_height = int(self.editor.blockBoundingRect(block).height())
            if top <= event.y() < top + block_height:
                block_number = block.blockNumber()
                if block_number in self.foldable_blocks:
                    self.toggle_fold(block_number)
                break
            top += block_height
            block = block.next()

    def toggle_fold(self, block_number: int):
        """Faltet/Entfaltet einen Block"""
        if block_number not in self.foldable_blocks:
            return
        
        end_block = self.foldable_blocks[block_number]
        
        if block_number in self.folded_blocks:
            # Entfalten
            self.folded_blocks.remove(block_number)
            self._set_blocks_visible(block_number + 1, end_block, True)
        else:
            # Falten
            self.folded_blocks.add(block_number)
            self._set_blocks_visible(block_number + 1, end_block, False)
        
        self.update()

    def _set_blocks_visible(self, start: int, end: int, visible: bool):
        """Setzt die Sichtbarkeit von Blöcken"""
        block = self.editor.document().findBlockByNumber(start)
        while block.isValid() and block.blockNumber() <= end:
            block.setVisible(visible)
            block = block.next()
        self.editor.viewport().update()


# ============================================================================
# LINTER INTEGRATION (NEU v7!)
# ============================================================================

class LinterRunner:
    """Führt Code-Linter (Pylint/Flake8) aus und sammelt Ergebnisse.

    Prüft Python-Code auf Fehler, Warnungen und Stil-Verstöße. Nutzt
    Flake8 wenn verfügbar (schneller), sonst Pylint. Falls kein Linter
    installiert ist, wird AST-basierte Syntax-Prüfung verwendet.

    Attributes:
        errors: Liste von gefundenen Fehlern
        warnings: Liste von gefundenen Warnungen
        has_pylint: Ob Pylint verfügbar ist
        has_flake8: Ob Flake8 verfügbar ist
    """

    def __init__(self):
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
        self._check_available_linters()

    def _check_available_linters(self):
        """Prüft welche Linter verfügbar sind"""
        self.has_pylint = shutil.which("pylint") is not None
        self.has_flake8 = shutil.which("flake8") is not None

    def run_linter(self, code: str, file_path: Optional[str] = None) -> List[Dict]:
        """Führt Linter aus und gibt Ergebnisse zurück"""
        self.errors = []
        self.warnings = []
        
        # Temporäre Datei für Linting
        tmp_path = Path.home() / ".python_baukasten" / "temp_lint.py"
        tmp_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path.write_text(code, encoding='utf-8')
        
        results = []
        
        # Versuche Flake8 (schneller)
        if self.has_flake8:
            results.extend(self._run_flake8(str(tmp_path)))
        # Fallback auf Pylint
        elif self.has_pylint:
            results.extend(self._run_pylint(str(tmp_path)))
        # Kein Linter verfügbar - nutze AST für Syntax-Fehler
        else:
            results.extend(self._run_ast_check(code))
        
        return results

    def _run_flake8(self, file_path: str) -> List[Dict]:
        """Führt Flake8 aus"""
        results = []
        try:
            proc = subprocess.run(
                ["flake8", "--format=%(row)d:%(col)d:%(code)s:%(text)s", file_path],
                capture_output=True, text=True, timeout=10
            )
            
            for line in proc.stdout.strip().split('\n'):
                if ':' in line:
                    parts = line.split(':', 3)
                    if len(parts) >= 4:
                        results.append({
                            'line': int(parts[0]),
                            'column': int(parts[1]),
                            'code': parts[2],
                            'message': parts[3],
                            'severity': 'error' if parts[2].startswith('E') else 'warning'
                        })
        except Exception:
            pass
        
        return results

    def _run_pylint(self, file_path: str) -> List[Dict]:
        """Führt Pylint aus"""
        results = []
        try:
            proc = subprocess.run(
                ["pylint", "--output-format=text", "--msg-template={line}:{column}:{msg_id}:{msg}", 
                 file_path],
                capture_output=True, text=True, timeout=30
            )
            
            for line in proc.stdout.strip().split('\n'):
                if ':' in line and not line.startswith('*'):
                    parts = line.split(':', 3)
                    if len(parts) >= 4:
                        results.append({
                            'line': int(parts[0]),
                            'column': int(parts[1]),
                            'code': parts[2],
                            'message': parts[3],
                            'severity': 'error' if parts[2].startswith('E') else 'warning'
                        })
        except Exception:
            pass
        
        return results

    def _run_ast_check(self, code: str) -> List[Dict]:
        """Prüft nur Syntax-Fehler mit AST"""
        results = []
        try:
            ast.parse(code)
        except SyntaxError as e:
            results.append({
                'line': e.lineno or 1,
                'column': e.offset or 0,
                'code': 'E999',
                'message': str(e.msg),
                'severity': 'error'
            })
        return results


# ============================================================================
# GIT INTEGRATION (NEU v7!)
# ============================================================================

class GitIntegration:
    """Git-Integration für Status-Anzeige und Diff-Unterstützung.

    Ermöglicht das Anzeigen von Git-Status (Modified, Added, etc.) und
    Diff-Ansicht für Dateien. Prüft automatisch ob Git verfügbar ist und
    findet das Repository-Root. Zeigt Status-Symbole im Editor an:
    - ● Modified (geändert)
    - + Added (neu hinzugefügt)
    - − Deleted (gelöscht)
    - ? Untracked (nicht versioniert)
    - → Renamed (umbenannt)

    Attributes:
        has_git: Ob Git installiert und verfügbar ist
    """

    def __init__(self):
        self.has_git = shutil.which("git") is not None

    def get_repo_root(self, file_path: str) -> Optional[str]:
        """Findet das Git-Repository Root"""
        if not self.has_git:
            return None
        
        try:
            result = subprocess.run(
                ["git", "-C", str(Path(file_path).parent), "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def get_file_status(self, file_path: str) -> str:
        """Gibt den Git-Status einer Datei zurück"""
        if not self.has_git or not file_path:
            return ""
        
        repo_root = self.get_repo_root(file_path)
        if not repo_root:
            return ""
        
        try:
            result = subprocess.run(
                ["git", "-C", repo_root, "status", "--porcelain", file_path],
                capture_output=True, text=True, timeout=5
            )
            status = result.stdout.strip()
            if status:
                code = status[:2].strip()
                status_map = {
                    'M': '● Modified',
                    'A': '+ Added',
                    'D': '− Deleted',
                    '??': '? Untracked',
                    'R': '→ Renamed',
                    'C': '⊕ Copied',
                    'U': '⚡ Conflict'
                }
                return status_map.get(code, code)
            return "✓ Unchanged"
        except Exception:
            return ""

    def get_diff(self, file_path: str) -> str:
        """Gibt den Git-Diff für eine Datei zurück"""
        if not self.has_git or not file_path:
            return ""
        
        repo_root = self.get_repo_root(file_path)
        if not repo_root:
            return ""
        
        try:
            result = subprocess.run(
                ["git", "-C", repo_root, "diff", file_path],
                capture_output=True, text=True, timeout=10
            )
            return result.stdout
        except Exception:
            return ""

    def get_modified_lines(self, file_path: str) -> Tuple[set, set, set]:
        """Gibt Sets von hinzugefügten, geänderten und gelöschten Zeilen zurück"""
        added = set()
        modified = set()
        deleted = set()
        
        diff = self.get_diff(file_path)
        if not diff:
            return added, modified, deleted
        
        current_line = 0
        for line in diff.split('\n'):
            if line.startswith('@@'):
                # Parse @@ -start,count +start,count @@
                match = re.search(r'\+(\d+)', line)
                if match:
                    current_line = int(match.group(1)) - 1
            elif line.startswith('+') and not line.startswith('+++'):
                current_line += 1
                added.add(current_line)
            elif line.startswith('-') and not line.startswith('---'):
                deleted.add(current_line)
            else:
                current_line += 1
        
        return added, modified, deleted


# ============================================================================
# EXTERNAL IDE INTEGRATION (NEU v8!)
# ============================================================================

class ExternalIDEIntegration:
    """Integration mit externen IDEs (VS Code, PyCharm).

    Ermöglicht das Öffnen von Dateien in externen IDEs und das Starten
    von Debug-Sessions. Sucht automatisch nach installierten IDEs auf dem
    System (prüft PATH und Standard-Installationspfade).

    Features:
    - Öffnen von Dateien in VS Code an bestimmter Zeile
    - Debug-Session in VS Code starten
    - Öffnen von Dateien in PyCharm
    - Automatische Erkennung von IDE-Installationen

    Attributes:
        vscode_path: Pfad zur VS Code Installation (None wenn nicht gefunden)
        pycharm_path: Pfad zur PyCharm Installation (None wenn nicht gefunden)
    """

    def __init__(self):
        self.vscode_path = self._find_vscode()
        self.pycharm_path = self._find_pycharm()

    def _find_vscode(self) -> Optional[str]:
        """Sucht VS Code Installation"""
        # Prüfe ob 'code' im PATH ist
        if shutil.which("code"):
            return "code"
        
        # Windows-spezifische Pfade
        possible_paths = [
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Microsoft VS Code/Code.exe",
            Path(os.environ.get("PROGRAMFILES", "")) / "Microsoft VS Code/Code.exe",
            Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft VS Code/Code.exe",
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        return None

    def _find_pycharm(self) -> Optional[str]:
        """Sucht PyCharm Installation"""
        if shutil.which("pycharm"):
            return "pycharm"
        
        # Windows-spezifische Pfade
        jetbrains_base = Path(os.environ.get("LOCALAPPDATA", "")) / "JetBrains/Toolbox/apps"
        if jetbrains_base.exists():
            for pycharm_dir in jetbrains_base.glob("PyCharm*/**/pycharm64.exe"):
                return str(pycharm_dir)
        
        return None

    def has_vscode(self) -> bool:
        return self.vscode_path is not None

    def has_pycharm(self) -> bool:
        return self.pycharm_path is not None

    def open_in_vscode(self, file_path: str, line: int = 1):
        """Öffnet Datei in VS Code an bestimmter Zeile"""
        if not self.vscode_path:
            return False, "VS Code nicht gefunden"
        
        try:
            subprocess.Popen([self.vscode_path, "--goto", f"{file_path}:{line}"])
            return True, "Geöffnet in VS Code"
        except Exception as e:
            return False, str(e)

    def debug_in_vscode(self, file_path: str):
        """Startet Debugging in VS Code"""
        if not self.vscode_path:
            return False, "VS Code nicht gefunden"
        
        try:
            # Öffne Datei und starte Debug (F5)
            subprocess.Popen([self.vscode_path, file_path])
            return True, "VS Code geöffnet - drücke F5 zum Debuggen"
        except Exception as e:
            return False, str(e)

    def open_in_pycharm(self, file_path: str, line: int = 1):
        """Öffnet Datei in PyCharm an bestimmter Zeile"""
        if not self.pycharm_path:
            return False, "PyCharm nicht gefunden"
        
        try:
            subprocess.Popen([self.pycharm_path, "--line", str(line), file_path])
            return True, "Geöffnet in PyCharm"
        except Exception as e:
            return False, str(e)


# ============================================================================
# BREAKPOINT MANAGER (NEU v8!)
# ============================================================================

class BreakpointManager:
    """Verwaltet Breakpoints für pdb-Debugging.

    Zentraler Manager für das Setzen, Entfernen und Abfragen von Breakpoints
    in Python-Dateien. Speichert Breakpoints pro Datei als Set von Zeilennummern.

    Features:
    - Toggle-Funktionalität (Klick setzt/entfernt Breakpoint)
    - Mehrere Breakpoints pro Datei möglich
    - Generierung von pdb-Befehlen (b <zeile>) für Debug-Sessions
    - Unterstützung für mehrere Dateien gleichzeitig

    Attributes:
        breakpoints: Dict mit Datei-Pfaden als Keys und Sets von Zeilennummern als Values

    Example:
        manager = BreakpointManager()
        manager.toggle_breakpoint('/path/to/file.py', 42)  # Setzt Breakpoint
        manager.toggle_breakpoint('/path/to/file.py', 42)  # Entfernt Breakpoint
    """

    def __init__(self):
        self.breakpoints: Dict[str, set] = {}  # {file_path: {line1, line2, ...}}

    def toggle_breakpoint(self, file_path: str, line: int) -> bool:
        """Setzt oder entfernt Breakpoint, gibt neuen Status zurück"""
        if file_path not in self.breakpoints:
            self.breakpoints[file_path] = set()
        
        if line in self.breakpoints[file_path]:
            self.breakpoints[file_path].remove(line)
            return False
        else:
            self.breakpoints[file_path].add(line)
            return True

    def has_breakpoint(self, file_path: str, line: int) -> bool:
        return file_path in self.breakpoints and line in self.breakpoints[file_path]

    def get_breakpoints(self, file_path: str) -> set:
        return self.breakpoints.get(file_path, set())

    def clear_all(self, file_path: str = None):
        if file_path:
            self.breakpoints[file_path] = set()
        else:
            self.breakpoints = {}

    def generate_pdb_commands(self, file_path: str) -> List[str]:
        """Generiert pdb-Befehle zum Setzen aller Breakpoints"""
        commands = []
        for line in sorted(self.get_breakpoints(file_path)):
            commands.append(f"b {line}")
        return commands


# ============================================================================
# DEBUG OUTPUT PANEL (NEU v8!)
# ============================================================================

class DebugOutputPanel(QWidget):
    """Erweitertes Output-Panel mit integriertem pdb-Debugger.

    Kombiniert Konsolen-Output mit interaktiver pdb-Steuerung. Ermöglicht
    das Ausführen von Python-Scripts sowohl im Normal- als auch im Debug-Modus.

    Features:
    - Debug-Toolbar mit Step-Controls (Continue, Step, Step Into, Step Out)
    - Interaktive Eingabezeile für pdb-Befehle
    - Command-History mit Pfeiltasten-Navigation
    - Farbcodierter Output (grün auf schwarz, Terminal-Style)
    - Automatische Erkennung von pdb-Prompts

    Signals:
        debugStateChanged(bool): Wird emittiert wenn Debugging startet/stoppt
            (True = debugging aktiv, False = inaktiv)

    Attributes:
        process: QProcess-Instanz für den laufenden Python-Prozess
        is_debugging: Boolean, ob aktuell eine Debug-Session aktiv ist
        command_history: Liste der eingegebenen pdb-Befehle
    """

    debugStateChanged = pyqtSignal(bool)  # True = debugging aktiv
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None
        self.is_debugging = False
        self.command_history = []
        self.history_index = 0
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Debug Toolbar
        self.debug_toolbar = QHBoxLayout()
        
        self.btn_continue = QPushButton("▶️ Continue (c)")
        self.btn_continue.clicked.connect(lambda: self.send_command("c"))
        self.btn_continue.setEnabled(False)
        self.debug_toolbar.addWidget(self.btn_continue)
        
        self.btn_step = QPushButton("⏭️ Step (n)")
        self.btn_step.clicked.connect(lambda: self.send_command("n"))
        self.btn_step.setEnabled(False)
        self.debug_toolbar.addWidget(self.btn_step)
        
        self.btn_step_into = QPushButton("⬇️ Step Into (s)")
        self.btn_step_into.clicked.connect(lambda: self.send_command("s"))
        self.btn_step_into.setEnabled(False)
        self.debug_toolbar.addWidget(self.btn_step_into)
        
        self.btn_step_out = QPushButton("⬆️ Step Out (r)")
        self.btn_step_out.clicked.connect(lambda: self.send_command("r"))
        self.btn_step_out.setEnabled(False)
        self.debug_toolbar.addWidget(self.btn_step_out)
        
        self.debug_toolbar.addStretch()
        
        self.btn_stop = QPushButton("⏹️ Stop")
        self.btn_stop.clicked.connect(self.stop_process)
        self.btn_stop.setEnabled(False)
        self.debug_toolbar.addWidget(self.btn_stop)
        
        layout.addLayout(self.debug_toolbar)
        
        # Output-Bereich
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 9))
        self.output.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                border: none;
            }
        """)
        layout.addWidget(self.output)
        
        # Eingabezeile für pdb-Befehle
        input_layout = QHBoxLayout()
        
        self.lbl_prompt = QLabel("(Pdb)")
        self.lbl_prompt.setStyleSheet("color: #00ff00; font-weight: bold;")
        self.lbl_prompt.setVisible(False)
        input_layout.addWidget(self.lbl_prompt)
        
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("pdb-Befehl eingeben (n=next, s=step, c=continue, p var=print, q=quit)")
        self.input_line.setFont(QFont("Consolas", 9))
        self.input_line.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: #00ff00;
                border: 1px solid #444;
                padding: 4px;
            }
        """)
        self.input_line.returnPressed.connect(self.on_input_entered)
        self.input_line.installEventFilter(self)
        input_layout.addWidget(self.input_line)
        
        layout.addLayout(input_layout)

    def eventFilter(self, obj, event):
        """Behandelt Pfeiltasten für Command-History"""
        if obj == self.input_line and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Up:
                self.navigate_history(-1)
                return True
            elif event.key() == Qt.Key_Down:
                self.navigate_history(1)
                return True
        return super().eventFilter(obj, event)

    def navigate_history(self, direction: int):
        """Navigiert durch Befehlshistorie"""
        if not self.command_history:
            return
        
        self.history_index = max(0, min(len(self.command_history) - 1, 
                                        self.history_index + direction))
        self.input_line.setText(self.command_history[self.history_index])

    def run_with_pdb(self, file_path: str, breakpoints: List[str] = None):
        """Startet Script mit pdb-Debugger"""
        self.stop_process()
        self.output.clear()
        
        self.is_debugging = True
        self.set_debug_buttons_enabled(True)
        self.lbl_prompt.setVisible(True)
        self.debugStateChanged.emit(True)
        
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.finished.connect(self.on_process_finished)
        
        self.output.appendPlainText(f"🐛 Starte Debugger für: {file_path}\n")
        self.output.appendPlainText("─" * 50)
        self.output.appendPlainText("Befehle: n(ext), s(tep), c(ontinue), r(eturn), p <var>, l(ist), q(uit)")
        self.output.appendPlainText("─" * 50 + "\n")
        
        self.process.start("python", ["-m", "pdb", file_path])
        
        # Breakpoints setzen nach Start
        if breakpoints:
            QTimer.singleShot(500, lambda: self.set_initial_breakpoints(breakpoints))

    def set_initial_breakpoints(self, breakpoints: List[str]):
        """Setzt initiale Breakpoints nach pdb-Start"""
        for bp_cmd in breakpoints:
            self.send_command(bp_cmd)
        # Nach Breakpoints: Continue um zum ersten zu laufen
        if breakpoints:
            QTimer.singleShot(200, lambda: self.send_command("c"))

    def run_normal(self, file_path: str):
        """Startet Script normal (ohne Debugger)"""
        self.stop_process()
        self.output.clear()
        
        self.is_debugging = False
        self.set_debug_buttons_enabled(False)
        self.lbl_prompt.setVisible(False)
        self.debugStateChanged.emit(False)
        
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.finished.connect(self.on_process_finished)
        
        self.output.appendPlainText(f"▶️ Ausführen: {file_path}\n")
        self.output.appendPlainText("─" * 50 + "\n")
        
        self.process.start("python", ["-u", file_path])
        self.btn_stop.setEnabled(True)

    def send_command(self, cmd: str):
        """Sendet Befehl an pdb"""
        if self.process and self.process.state() == QProcess.Running:
            self.output.appendPlainText(f"(Pdb) {cmd}")
            self.process.write((cmd + "\n").encode())
            
            if cmd.strip() and cmd not in self.command_history[-1:]:
                self.command_history.append(cmd)
            self.history_index = len(self.command_history)

    def on_input_entered(self):
        """Verarbeitet Eingabe"""
        cmd = self.input_line.text().strip()
        if cmd:
            self.send_command(cmd)
            self.input_line.clear()

    def read_output(self):
        """Liest Ausgabe vom Prozess"""
        if self.process:
            data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
            self.output.appendPlainText(data.rstrip())
            
            # Auto-scroll
            scrollbar = self.output.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def on_process_finished(self, exit_code, exit_status):
        """Wird aufgerufen wenn Prozess beendet"""
        self.output.appendPlainText(f"\n{'─' * 50}")
        self.output.appendPlainText(f"✅ Prozess beendet (Exit-Code: {exit_code})")
        
        self.is_debugging = False
        self.set_debug_buttons_enabled(False)
        self.lbl_prompt.setVisible(False)
        self.btn_stop.setEnabled(False)
        self.debugStateChanged.emit(False)

    def set_debug_buttons_enabled(self, enabled: bool):
        """Aktiviert/Deaktiviert Debug-Buttons"""
        self.btn_continue.setEnabled(enabled)
        self.btn_step.setEnabled(enabled)
        self.btn_step_into.setEnabled(enabled)
        self.btn_step_out.setEnabled(enabled)
        self.btn_stop.setEnabled(enabled)

    def stop_process(self):
        """Stoppt laufenden Prozess"""
        if self.process and self.process.state() == QProcess.Running:
            self.process.kill()
            self.process.waitForFinished(1000)


# ============================================================================
# PYTHON KEYWORDS & BUILTINS FÜR AUTO-COMPLETION (NEU v6!)
# ============================================================================

PYTHON_KEYWORDS = [
    'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
    'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
    'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
    'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
    'while', 'with', 'yield'
]

PYTHON_BUILTINS = [
    'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes',
    'callable', 'chr', 'classmethod', 'compile', 'complex', 'delattr',
    'dict', 'dir', 'divmod', 'enumerate', 'eval', 'exec', 'filter',
    'float', 'format', 'frozenset', 'getattr', 'globals', 'hasattr',
    'hash', 'help', 'hex', 'id', 'input', 'int', 'isinstance', 'issubclass',
    'iter', 'len', 'list', 'locals', 'map', 'max', 'memoryview', 'min',
    'next', 'object', 'oct', 'open', 'ord', 'pow', 'print', 'property',
    'range', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
    'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type',
    'vars', 'zip', '__import__', '__name__', '__doc__', '__file__',
    'Exception', 'BaseException', 'ValueError', 'TypeError', 'KeyError',
    'IndexError', 'AttributeError', 'ImportError', 'RuntimeError',
    'StopIteration', 'GeneratorExit', 'FileNotFoundError', 'OSError',
    'self', 'cls'
]

PYTHON_SNIPPETS = {
    'def': 'def function_name(args):\n    pass',
    'class': 'class ClassName:\n    def __init__(self):\n        pass',
    'if': 'if condition:\n    pass',
    'for': 'for item in iterable:\n    pass',
    'while': 'while condition:\n    pass',
    'try': 'try:\n    pass\nexcept Exception as e:\n    pass',
    'with': 'with open(file) as f:\n    pass',
    'lambda': 'lambda x: x',
    'list_comp': '[x for x in iterable]',
    'dict_comp': '{k: v for k, v in iterable}',
    '__init__': 'def __init__(self):\n    pass',
    '__str__': 'def __str__(self):\n    return ""',
    '__repr__': 'def __repr__(self):\n    return f"{self.__class__.__name__}()"',
    'main': 'if __name__ == "__main__":\n    main()',
    'docstring': '"""Description.\n\nArgs:\n    arg: Description.\n\nReturns:\n    Description.\n"""',
}


# ============================================================================
# GEHE ZU ZEILE DIALOG (NEU v6!)
# ============================================================================

class GotoLineDialog(QDialog):
    """Dialog zum Springen zu einer bestimmten Zeile"""
    
    def __init__(self, parent=None, max_line: int = 1):
        super().__init__(parent)
        self.setWindowTitle("Gehe zu Zeile")
        self.setFixedSize(250, 100)
        
        layout = QVBoxLayout(self)
        
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel(f"Zeile (1-{max_line}):"))
        
        self.line_spin = QSpinBox()
        self.line_spin.setRange(1, max_line)
        self.line_spin.setValue(1)
        h_layout.addWidget(self.line_spin)
        
        layout.addLayout(h_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.line_spin.setFocus()
        self.line_spin.selectAll()

    def get_line(self) -> int:
        return self.line_spin.value()


# ============================================================================
# EINSTELLUNGS-DIALOG (NEU v6!)
# ============================================================================

class SettingsDialog(QDialog):
    """Dialog für Editor-Einstellungen"""
    
    def __init__(self, parent=None, settings: QSettings = None):
        super().__init__(parent)
        self.settings = settings or QSettings("PythonArchitect", "v6")
        self.setWindowTitle("Einstellungen")
        self.setMinimumSize(400, 350)
        
        layout = QVBoxLayout(self)
        
        # --- Editor Gruppe ---
        editor_group = QGroupBox("Editor")
        editor_layout = QFormLayout(editor_group)
        
        # Schriftgröße
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(self.settings.value("font_size", 10, type=int))
        editor_layout.addRow("Schriftgröße:", self.font_size_spin)
        
        # Tab-Größe
        self.tab_size_spin = QSpinBox()
        self.tab_size_spin.setRange(2, 8)
        self.tab_size_spin.setValue(self.settings.value("tab_size", 4, type=int))
        editor_layout.addRow("Tab-Größe:", self.tab_size_spin)
        
        # Zeilenumbruch
        self.word_wrap_check = QCheckBox("Aktiviert")
        self.word_wrap_check.setChecked(self.settings.value("word_wrap", False, type=bool))
        editor_layout.addRow("Zeilenumbruch:", self.word_wrap_check)
        
        # Auto-Completion
        self.autocomplete_check = QCheckBox("Aktiviert")
        self.autocomplete_check.setChecked(self.settings.value("autocomplete", True, type=bool))
        editor_layout.addRow("Auto-Completion:", self.autocomplete_check)
        
        # Bracket Matching
        self.bracket_check = QCheckBox("Aktiviert")
        self.bracket_check.setChecked(self.settings.value("bracket_matching", True, type=bool))
        editor_layout.addRow("Klammer-Matching:", self.bracket_check)
        
        layout.addWidget(editor_group)
        
        # --- Darstellung Gruppe ---
        display_group = QGroupBox("Darstellung")
        display_layout = QFormLayout(display_group)
        
        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark (Standard)", "Light", "Monokai", "Dracula"])
        current_theme = self.settings.value("theme", "Dark (Standard)")
        self.theme_combo.setCurrentText(current_theme)
        display_layout.addRow("Theme:", self.theme_combo)
        
        # Minimap
        self.minimap_check = QCheckBox("Aktiviert")
        self.minimap_check.setChecked(self.settings.value("minimap", False, type=bool))
        display_layout.addRow("Minimap:", self.minimap_check)
        
        # Zeilennummern
        self.line_numbers_check = QCheckBox("Aktiviert")
        self.line_numbers_check.setChecked(self.settings.value("line_numbers", True, type=bool))
        display_layout.addRow("Zeilennummern:", self.line_numbers_check)
        
        layout.addWidget(display_group)
        
        # --- Buttons ---
        layout.addStretch()
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        layout.addWidget(buttons)

    def apply_settings(self):
        self.settings.setValue("font_size", self.font_size_spin.value())
        self.settings.setValue("tab_size", self.tab_size_spin.value())
        self.settings.setValue("word_wrap", self.word_wrap_check.isChecked())
        self.settings.setValue("autocomplete", self.autocomplete_check.isChecked())
        self.settings.setValue("bracket_matching", self.bracket_check.isChecked())
        self.settings.setValue("theme", self.theme_combo.currentText())
        self.settings.setValue("minimap", self.minimap_check.isChecked())
        self.settings.setValue("line_numbers", self.line_numbers_check.isChecked())

    def accept(self):
        self.apply_settings()
        super().accept()

    def get_settings(self) -> dict:
        return {
            "font_size": self.font_size_spin.value(),
            "tab_size": self.tab_size_spin.value(),
            "word_wrap": self.word_wrap_check.isChecked(),
            "autocomplete": self.autocomplete_check.isChecked(),
            "bracket_matching": self.bracket_check.isChecked(),
            "theme": self.theme_combo.currentText(),
            "minimap": self.minimap_check.isChecked(),
            "line_numbers": self.line_numbers_check.isChecked(),
        }


# ============================================================================
# SUCHEN & ERSETZEN DIALOG (NEU!)
# ============================================================================

class SearchReplaceBar(QFrame):
    """Eingebettete Such- und Ersetzen-Leiste"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor: Optional[CodeEditor] = None
        self.current_match = 0
        self.total_matches = 0
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("QFrame { background: #2d2d2d; border: 1px solid #555; padding: 5px; }")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Suchen-Zeile
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("🔍"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Suchen... (Ctrl+F)")
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.returnPressed.connect(self.find_next)
        search_row.addWidget(self.search_input, 1)
        
        self.match_label = QLabel("0/0")
        self.match_label.setMinimumWidth(60)
        search_row.addWidget(self.match_label)
        
        self.btn_prev = QPushButton("◀")
        self.btn_prev.setFixedWidth(30)
        self.btn_prev.clicked.connect(self.find_prev)
        search_row.addWidget(self.btn_prev)
        
        self.btn_next = QPushButton("▶")
        self.btn_next.setFixedWidth(30)
        self.btn_next.clicked.connect(self.find_next)
        search_row.addWidget(self.btn_next)
        
        self.case_check = QCheckBox("Aa")
        self.case_check.setToolTip("Groß-/Kleinschreibung beachten")
        self.case_check.stateChanged.connect(self.on_search_changed)
        search_row.addWidget(self.case_check)
        
        btn_close = QPushButton("✕")
        btn_close.setFixedWidth(30)
        btn_close.clicked.connect(self.hide)
        search_row.addWidget(btn_close)
        
        layout.addLayout(search_row)
        
        # Ersetzen-Zeile
        self.replace_row = QWidget()
        replace_layout = QHBoxLayout(self.replace_row)
        replace_layout.setContentsMargins(0, 0, 0, 0)
        
        replace_layout.addWidget(QLabel("↔️"))
        
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Ersetzen durch...")
        replace_layout.addWidget(self.replace_input, 1)
        
        self.btn_replace = QPushButton("Ersetzen")
        self.btn_replace.clicked.connect(self.replace_current)
        replace_layout.addWidget(self.btn_replace)
        
        self.btn_replace_all = QPushButton("Alle")
        self.btn_replace_all.clicked.connect(self.replace_all)
        replace_layout.addWidget(self.btn_replace_all)
        
        layout.addWidget(self.replace_row)
        self.replace_row.hide()
        
        self.hide()

    def set_editor(self, editor: CodeEditor):
        self.editor = editor

    def show_search(self):
        self.replace_row.hide()
        self.show()
        self.search_input.setFocus()
        self.search_input.selectAll()

    def show_replace(self):
        self.replace_row.show()
        self.show()
        self.search_input.setFocus()
        self.search_input.selectAll()

    def on_search_changed(self):
        if not self.editor:
            return
        pattern = self.search_input.text()
        case_sensitive = self.case_check.isChecked()
        self.total_matches = self.editor.highlightSearchResults(pattern, case_sensitive)
        self.current_match = 0
        self.update_match_label()
        
        if self.total_matches > 0:
            self.find_next()

    def update_match_label(self):
        if self.total_matches > 0:
            self.match_label.setText(f"{self.current_match}/{self.total_matches}")
        else:
            self.match_label.setText("0/0")

    def find_next(self):
        if not self.editor or not self.search_input.text():
            return
        
        flags = QTextDocument.FindFlags()
        if self.case_check.isChecked():
            flags |= QTextDocument.FindCaseSensitively
        
        cursor = self.editor.textCursor()
        found = self.editor.document().find(self.search_input.text(), cursor, flags)
        
        if found.isNull():
            # Wrap around
            cursor.movePosition(QTextCursor.Start)
            found = self.editor.document().find(self.search_input.text(), cursor, flags)
        
        if not found.isNull():
            self.editor.setTextCursor(found)
            self.current_match = min(self.current_match + 1, self.total_matches)
            if self.current_match == 0:
                self.current_match = 1
            self.update_match_label()


    def find_prev(self):
        if not self.editor or not self.search_input.text():
            return
        
        flags = QTextDocument.FindBackward
        if self.case_check.isChecked():
            flags |= QTextDocument.FindCaseSensitively
        
        cursor = self.editor.textCursor()
        cursor.setPosition(cursor.selectionStart())
        found = self.editor.document().find(self.search_input.text(), cursor, flags)
        
        if found.isNull():
            cursor.movePosition(QTextCursor.End)
            found = self.editor.document().find(self.search_input.text(), cursor, flags)
        
        if not found.isNull():
            self.editor.setTextCursor(found)
            self.current_match = max(self.current_match - 1, 1)
            self.update_match_label()

    def replace_current(self):
        if not self.editor:
            return
        cursor = self.editor.textCursor()
        if cursor.hasSelection() and cursor.selectedText().lower() == self.search_input.text().lower():
            cursor.insertText(self.replace_input.text())
            self.on_search_changed()
        self.find_next()

    def replace_all(self):
        if not self.editor or not self.search_input.text():
            return
        
        text = self.editor.toPlainText()
        search_text = self.search_input.text()
        replace_text = self.replace_input.text()
        
        if self.case_check.isChecked():
            new_text = text.replace(search_text, replace_text)
        else:
            new_text = re.sub(re.escape(search_text), replace_text, text, flags=re.IGNORECASE)
        
        if new_text != text:
            cursor = self.editor.textCursor()
            cursor.beginEditBlock()
            self.editor.setPlainText(new_text)
            cursor.endEditBlock()
            self.on_search_changed()

    def hideEvent(self, event):
        if self.editor:
            self.editor.clearSearchHighlight()
        super().hideEvent(event)


# ============================================================================
# OUTPUT PANEL (NEU!)
# ============================================================================

class OutputPanel(QWidget):
    """Integriertes Output-Panel für Skript-Ausgaben"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.process: Optional[QProcess] = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("📟 Ausgabe"))
        toolbar.addStretch()
        
        self.btn_stop = QPushButton("⏹ Stop")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_process)
        toolbar.addWidget(self.btn_stop)
        
        btn_clear = QPushButton("🗑 Leeren")
        btn_clear.clicked.connect(self.clear_output)
        toolbar.addWidget(btn_clear)
        
        layout.addLayout(toolbar)
        
        # Output Text
        self.output_text = QPlainTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 9))
        self.output_text.setStyleSheet("""
            QPlainTextEdit { 
                background-color: #1a1a1a; 
                color: #00ff00; 
                border: 1px solid #333;
            }
        """)
        layout.addWidget(self.output_text)

    def run_script(self, script_path: str):
        """Führt ein Python-Skript aus und zeigt Output"""
        if self.process and self.process.state() == QProcess.Running:
            QMessageBox.warning(self, "Läuft", "Ein Prozess läuft bereits.")
            return
        
        self.clear_output()
        self.append_output(f"▶ Starte: {script_path}\n{'='*50}\n")
        
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.finished.connect(self.process_finished)
        self.process.errorOccurred.connect(self.process_error)
        
        self.process.start(sys.executable, [script_path])
        self.btn_stop.setEnabled(True)

    def run_code(self, code: str):
        """Führt Python-Code direkt aus"""
        # Temporäre Datei erstellen
        tmp_path = Path.home() / ".python_baukasten" / "temp_run.py"
        tmp_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path.write_text(code, encoding='utf-8')
        self.run_script(str(tmp_path))

    def read_output(self):
        if self.process:
            data = self.process.readAllStandardOutput()
            text = bytes(data).decode('utf-8', errors='replace')
            self.append_output(text)

    def append_output(self, text: str):
        self.output_text.moveCursor(QTextCursor.End)
        self.output_text.insertPlainText(text)
        self.output_text.moveCursor(QTextCursor.End)

    def process_finished(self, exit_code, exit_status):
        self.append_output(f"\n{'='*50}\n✓ Beendet (Code: {exit_code})\n")
        self.btn_stop.setEnabled(False)

    def process_error(self, error):
        self.append_output(f"\n⚠ Fehler: {error}\n")
        self.btn_stop.setEnabled(False)

    def stop_process(self):
        if self.process:
            self.process.kill()
            self.append_output("\n⏹ Prozess abgebrochen.\n")

    def clear_output(self):
        self.output_text.clear()


# ============================================================================
# TAB-SYSTEM (NEU!)
# ============================================================================

class EditorTab:
    """Datenklasse für einen Editor-Tab"""
    def __init__(self, editor: CodeEditor, highlighter: PythonSyntaxHighlighter, 
                 file_path: Optional[str] = None):
        self.editor = editor
        self.highlighter = highlighter
        self.file_path = file_path
        self.is_modified = False


class MultiTabEditor(QWidget):
    """Tab-basierter Editor für mehrere Dateien"""
    
    currentEditorChanged = pyqtSignal(CodeEditor)
    fileModified = pyqtSignal(str, bool)  # filename, is_modified
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tabs: Dict[int, EditorTab] = {}
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Plus-Button für neuen Tab
        self.tab_widget.setCornerWidget(self._create_new_tab_button(), Qt.TopRightCorner)
        
        layout.addWidget(self.tab_widget)
        
        # Ersten Tab erstellen
        self.new_tab()

    def _create_new_tab_button(self) -> QPushButton:
        btn = QPushButton("+")
        btn.setFixedSize(24, 24)
        btn.setToolTip("Neuer Tab (Ctrl+N)")
        btn.clicked.connect(self.new_tab)
        return btn

    def new_tab(self, file_path: Optional[str] = None, content: str = "") -> int:
        """Erstellt einen neuen Editor-Tab"""
        editor = CodeEditor()
        highlighter = PythonSyntaxHighlighter(editor.document())
        
        if content:
            editor.setPlainText(content)
        
        # Tab-Name
        if file_path:
            name = Path(file_path).name
        else:
            # Zähle unbenannte Tabs
            unnamed_count = sum(1 for t in self.tabs.values() if not t.file_path)
            name = f"Unbenannt-{unnamed_count + 1}"
        
        index = self.tab_widget.addTab(editor, name)
        
        tab_data = EditorTab(editor, highlighter, file_path)
        self.tabs[index] = tab_data
        
        # Verbinde Modifikations-Signal
        editor.document().modificationChanged.connect(
            lambda modified, idx=index: self._on_modification_changed(idx, modified)
        )
        
        self.tab_widget.setCurrentIndex(index)
        return index

    def _on_modification_changed(self, index: int, modified: bool):
        """Aktualisiert Tab-Titel bei Änderungen"""
        if index not in self.tabs:
            return
        
        tab = self.tabs[index]
        tab.is_modified = modified
        
        name = Path(tab.file_path).name if tab.file_path else f"Unbenannt"
        if modified:
            name = f"● {name}"
        
        self.tab_widget.setTabText(index, name)
        self.fileModified.emit(name, modified)

    def close_tab(self, index: int):
        """Schließt einen Tab (mit Speicher-Dialog)"""
        if index not in self.tabs:
            return
        
        tab = self.tabs[index]
        
        if tab.is_modified:
            name = Path(tab.file_path).name if tab.file_path else "Unbenannt"
            result = QMessageBox.question(
                self, "Speichern?",
                f"'{name}' wurde geändert. Speichern?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if result == QMessageBox.Cancel:
                return
            elif result == QMessageBox.Save:
                if not self.save_tab(index):
                    return
        
        self.tab_widget.removeTab(index)
        del self.tabs[index]
        
        # Tabs neu indizieren
        new_tabs = {}
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            for old_idx, tab in list(self.tabs.items()):
                if tab.editor == widget:
                    new_tabs[i] = tab
                    break
        self.tabs = new_tabs
        
        # Mindestens ein Tab muss existieren
        if self.tab_widget.count() == 0:
            self.new_tab()

    def save_tab(self, index: int) -> bool:
        """Speichert den Tab"""
        if index not in self.tabs:
            return False
        
        tab = self.tabs[index]
        
        if not tab.file_path:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Speichern unter", "", "Python (*.py);;Alle Dateien (*)"
            )
            if not file_path:
                return False
            tab.file_path = file_path
        
        try:
            Path(tab.file_path).write_text(tab.editor.toPlainText(), encoding='utf-8')
            tab.editor.document().setModified(False)
            self.tab_widget.setTabText(index, Path(tab.file_path).name)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Speichern fehlgeschlagen: {e}")
            return False

    def open_file(self, file_path: str) -> int:
        """Öffnet eine Datei in einem neuen Tab"""
        # Prüfe ob Datei bereits geöffnet
        for idx, tab in self.tabs.items():
            if tab.file_path == file_path:
                self.tab_widget.setCurrentIndex(idx)
                return idx
        
        try:
            content = Path(file_path).read_text(encoding='utf-8')
            return self.new_tab(file_path, content)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Öffnen fehlgeschlagen: {e}")
            return -1

    def current_editor(self) -> Optional[CodeEditor]:
        """Gibt den aktuellen Editor zurück"""
        index = self.tab_widget.currentIndex()
        if index in self.tabs:
            return self.tabs[index].editor
        return None

    def current_tab(self) -> Optional[EditorTab]:
        """Gibt den aktuellen Tab zurück"""
        index = self.tab_widget.currentIndex()
        return self.tabs.get(index)

    def on_tab_changed(self, index: int):
        if index in self.tabs:
            self.currentEditorChanged.emit(self.tabs[index].editor)


# ============================================================================
# LOGIC: IMPORT OPTIMIZER
# ============================================================================

class ImportOptimizer:
    @staticmethod
    def organize_imports(code):
        """Sortiert und dedupliziert Imports"""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return None, f"Syntax Fehler: {e}"

        imports = []
        from_imports = []
        other_lines = code.splitlines()
        import_linenos = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    asname = f" as {alias.asname}" if alias.asname else ""
                    imports.append(f"import {name}{asname}")
                import_linenos.update(range(node.lineno - 1, node.end_lineno))
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ""
                names = []
                for alias in node.names:
                    name = alias.name
                    asname = f" as {alias.asname}" if alias.asname else ""
                    names.append(f"{name}{asname}")
                from_imports.append(f"from {module} import {', '.join(names)}")
                import_linenos.update(range(node.lineno - 1, node.end_lineno))

        imports = sorted(list(set(imports)))
        from_imports = sorted(list(set(from_imports)))

        new_body = [line for i, line in enumerate(other_lines) if i not in import_linenos]

        header = imports + from_imports
        if header and new_body:
            final_code = "\n".join(header) + "\n\n" + "\n".join(new_body)
        elif header:
            final_code = "\n".join(header)
        else:
            final_code = "\n".join(new_body)

        final_code = re.sub(r'\n{3,}', '\n\n', final_code)
        return final_code, "Imports optimiert."


# ============================================================================
# LIBRARY MANAGER
# ============================================================================

class LibraryManager:
    def __init__(self):
        self.root = Path.home() / ".python_baukasten" / "library"
        self.lock_file = self.root / "locks.json"
        self._ensure_defaults()
        self.locked_items = self._load_locks()

    def _ensure_defaults(self):
        self.root.mkdir(parents=True, exist_ok=True)
        if not (self.root / "Beispiele").exists():
            d = self.root / "Beispiele"
            d.mkdir()
            (d / "HelloWorld.py").write_text('print("Hallo Welt")', encoding='utf-8')

    def _load_locks(self):
        if self.lock_file.exists():
            try:
                with open(self.lock_file, 'r') as f:
                    return set(json.load(f))
            except (OSError, json.JSONDecodeError):
                return set()
        return set()

    def _save_locks(self):
        with open(self.lock_file, 'w') as f:
            json.dump(list(self.locked_items), f)

    def is_locked(self, topic, name):
        return f"{topic}/{name}" in self.locked_items

    def toggle_lock(self, topic, name):
        key = f"{topic}/{name}"
        if key in self.locked_items:
            self.locked_items.remove(key)
        else:
            self.locked_items.add(key)
        self._save_locks()

    def get_topics(self):
        if not self.root.exists(): return []
        return sorted([d.name for d in self.root.iterdir() if d.is_dir()])

    def get_items(self, topic):
        path = self.root / topic
        if not path.exists(): return []
        return sorted([f.stem for f in path.glob("*.py")])

    def get_content(self, topic, name):
        path = self.root / topic / f"{name}.py"
        if path.exists(): return path.read_text(encoding='utf-8')
        return ""

    def save_snippet(self, topic, name, content):
        if self.is_locked(topic, name):
            return False, "Eintrag ist gesperrt."
        try:
            topic_dir = self.root / topic
            topic_dir.mkdir(exist_ok=True)
            (topic_dir / f"{name}.py").write_text(content, encoding='utf-8')
            return True, "Gespeichert."
        except Exception as e:
            return False, str(e)

    def delete_item(self, topic, name):
        if self.is_locked(topic, name):
            return False
        path = self.root / topic / f"{name}.py"
        if path.exists():
            os.remove(path)
            key = f"{topic}/{name}"
            if key in self.locked_items:
                self.locked_items.remove(key)
                self._save_locks()
            return True
        return False


# ============================================================================
# DIALOGS
# ============================================================================

class SnippetDialog(QDialog):
    def __init__(self, parent, topics, topic="", name="", content=""):
        super().__init__(parent)
        self.setWindowTitle("Snippet Eintrag")
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.topic_combo = QComboBox()
        self.topic_combo.setEditable(True)
        self.topic_combo.addItems(topics)
        if topic: self.topic_combo.setCurrentText(topic)
        
        self.name_edit = QLineEdit()
        self.name_edit.setText(name)
        
        form.addRow("Kategorie:", self.topic_combo)
        form.addRow("Name:", self.name_edit)
        layout.addLayout(form)
        
        layout.addWidget(QLabel("Code:"))
        self.code_edit = CodeEditor()
        self.code_edit.setPlainText(content)
        self.highlighter = PythonSyntaxHighlighter(self.code_edit.document())
        layout.addWidget(self.code_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return (
            self.topic_combo.currentText().strip(),
            self.name_edit.text().strip(),
            self.code_edit.toPlainText()
        )


# ============================================================================
# MAIN APPLICATION (ERWEITERT!)
# ============================================================================

class PythonArchitect(QMainWindow):
    # Window-Konstanten
    DEFAULT_WINDOW_WIDTH = 1500
    DEFAULT_WINDOW_HEIGHT = 950

    def __init__(self):
        super().__init__()
        self.lib_manager = LibraryManager()
        self.settings = QSettings("PythonArchitect", "v8")
        self.recent_files: List[str] = self._load_recent_files()
        
        # NEU v7: Linter und Git
        self.linter = LinterRunner()
        self.git = GitIntegration()
        self.lint_timer = QTimer()
        self.lint_timer.timeout.connect(self.run_linter_delayed)
        self.lint_timer.setSingleShot(True)
        
        # NEU v8: External IDE + Breakpoints
        self.ide_integration = ExternalIDEIntegration()
        self.breakpoint_manager = BreakpointManager()
        
        self.setup_ui()
        self.setup_shortcuts()
        self.load_library_tree()
        self.scan_external_tools()
        self._restore_window_state()
        self._apply_settings_to_editors()

    def setup_ui(self):
        self.setWindowTitle("Python Code Architect v8.0")
        self.resize(self.DEFAULT_WINDOW_WIDTH, self.DEFAULT_WINDOW_HEIGHT)
        
        # --- MENÜ ---
        menubar = self.menuBar()
        
        # Datei-Menü
        file_menu = menubar.addMenu("Datei")
        file_menu.addAction("Neu", self.new_file, QKeySequence.New)
        file_menu.addAction("Öffnen...", self.open_file, QKeySequence.Open)
        file_menu.addSeparator()
        file_menu.addAction("Speichern", self.save_file, QKeySequence.Save)
        file_menu.addAction("Speichern unter...", self.save_file_as, QKeySequence("Ctrl+Shift+S"))
        file_menu.addSeparator()
        
        # Zuletzt geöffnete Dateien
        self.recent_menu = file_menu.addMenu("📂 Zuletzt geöffnet")
        self._update_recent_menu()
        
        file_menu.addSeparator()
        file_menu.addAction("Beenden", self.close, QKeySequence.Quit)
        
        # Bearbeiten-Menü
        edit_menu = menubar.addMenu("Bearbeiten")
        edit_menu.addAction("Rückgängig", self.undo_action, QKeySequence.Undo)
        edit_menu.addAction("Wiederholen", self.redo_action, QKeySequence.Redo)
        edit_menu.addSeparator()
        edit_menu.addAction("Ausschneiden", self.cut_action, QKeySequence.Cut)
        edit_menu.addAction("Kopieren", self.copy_action, QKeySequence.Copy)
        edit_menu.addAction("Einfügen", self.paste_action, QKeySequence.Paste)
        edit_menu.addSeparator()
        edit_menu.addAction("🔍 Suchen...", self.show_search, QKeySequence.Find)
        edit_menu.addAction("↔️ Ersetzen...", self.show_replace, QKeySequence.Replace)
        edit_menu.addAction("📍 Gehe zu Zeile...", self.goto_line, QKeySequence("Ctrl+G"))
        edit_menu.addSeparator()
        edit_menu.addAction("⚙️ Einstellungen...", self.show_settings)
        
        # Tools-Menü
        tools_menu = menubar.addMenu("Werkzeuge")
        tools_menu.addAction("🧹 Imports aufräumen", self.optimize_imports_action)
        tools_menu.addAction("🔍 Einrückung prüfen", self.check_indentation)
        tools_menu.addAction("🔧 Encoding Fix (UTF-8)", self.fix_encoding)
        tools_menu.addSeparator()
        self.ext_tools_menu = tools_menu.addMenu("🚀 Externe Tools")
        self.ext_tools_menu.addAction("Tools Ordner öffnen...", self.open_tools_folder)
        self.ext_tools_menu.addSeparator()
        
        # Debug-Menü (NEU v8!)
        debug_menu = menubar.addMenu("Debug")
        debug_menu.addAction("🐛 Mit Debugger starten", self.run_with_debugger, QKeySequence("F6"))
        debug_menu.addAction("▶️ Normal ausführen", self.run_script, QKeySequence("F5"))
        debug_menu.addSeparator()
        debug_menu.addAction("🔴 Breakpoint setzen/entfernen", self.toggle_breakpoint_action, QKeySequence("F9"))
        debug_menu.addAction("🗑️ Alle Breakpoints löschen", self.clear_all_breakpoints)
        debug_menu.addSeparator()
        
        # VS Code / PyCharm Integration
        self.vscode_menu = debug_menu.addMenu("🔷 VS Code")
        self.vscode_menu.addAction("In VS Code öffnen", self.open_in_vscode)
        self.vscode_menu.addAction("In VS Code debuggen", self.debug_in_vscode)
        self.vscode_menu.setEnabled(self.ide_integration.has_vscode())
        
        self.pycharm_menu = debug_menu.addMenu("🟢 PyCharm")
        self.pycharm_menu.addAction("In PyCharm öffnen", self.open_in_pycharm)
        self.pycharm_menu.setEnabled(self.ide_integration.has_pycharm())
        
        # Build-Menü
        compile_menu = menubar.addMenu("Build")
        compile_menu.addAction("▶️ Ausführen", self.run_script, QKeySequence("F5"))
        compile_menu.addAction("▶️ Ausführen (extern)", self.run_script_external, QKeySequence("Ctrl+F5"))
        compile_menu.addSeparator()
        compile_menu.addAction("📦 EXE erstellen", self.build_exe)

        # Ansicht-Menü (NEU v7!)
        view_menu = menubar.addMenu("Ansicht")
        self.minimap_action = view_menu.addAction("🗺️ Minimap")
        self.minimap_action.setCheckable(True)
        self.minimap_action.setChecked(self.settings.value("show_minimap", False, type=bool))
        self.minimap_action.triggered.connect(self.toggle_minimap)
        
        self.linter_action = view_menu.addAction("⚠️ Linter-Panel")
        self.linter_action.setCheckable(True)
        self.linter_action.setChecked(False)
        self.linter_action.triggered.connect(self.toggle_linter_panel)
        
        view_menu.addSeparator()
        view_menu.addAction("🔄 Linter ausführen", self.run_linter_now, QKeySequence("Ctrl+L"))
        view_menu.addAction("📊 Git Status", self.show_git_status)

        # --- TOOLBAR ---
        toolbar = QToolBar("Hauptwerkzeugleiste")
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)
        
        toolbar.addAction("📄", self.new_file).setToolTip("Neue Datei (Ctrl+N)")
        toolbar.addAction("📂", self.open_file).setToolTip("Öffnen (Ctrl+O)")
        toolbar.addAction("💾", self.save_file).setToolTip("Speichern (Ctrl+S)")
        toolbar.addSeparator()
        toolbar.addAction("↩️", self.undo_action).setToolTip("Rückgängig (Ctrl+Z)")
        toolbar.addAction("↪️", self.redo_action).setToolTip("Wiederholen (Ctrl+Y)")
        toolbar.addSeparator()
        toolbar.addAction("🔍", self.show_search).setToolTip("Suchen (Ctrl+F)")
        toolbar.addSeparator()
        toolbar.addAction("▶️", self.run_script).setToolTip("Ausführen (F5)")
        toolbar.addAction("🐛", self.run_with_debugger).setToolTip("Mit Debugger (F6)")
        toolbar.addAction("🔴", self.toggle_breakpoint_action).setToolTip("Breakpoint (F9)")
        toolbar.addSeparator()
        toolbar.addAction("⚠️", self.run_linter_now).setToolTip("Linter (Ctrl+L)")
        toolbar.addSeparator()
        
        # VS Code Button (nur wenn verfügbar)
        if self.ide_integration.has_vscode():
            toolbar.addAction("🔷", self.open_in_vscode).setToolTip("In VS Code öffnen")

        # --- CENTRAL WIDGET ---
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # --- LEFT: LIBRARY ---
        left_widget = QWidget()
        l_layout = QVBoxLayout(left_widget)
        l_layout.setContentsMargins(0,0,0,0)
        
        lbl_lib = QLabel("📚 Bibliothek")
        lbl_lib.setFont(QFont("Segoe UI", 11, QFont.Bold))
        l_layout.addWidget(lbl_lib)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.dragEnterEvent = self.tree_drag_enter
        self.tree.dropEvent = self.tree_drop
        self.tree.itemClicked.connect(self.on_tree_select)
        self.tree.itemDoubleClicked.connect(self.on_tree_double_click)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_tree_context)
        l_layout.addWidget(self.tree)
        
        splitter.addWidget(left_widget)
        
        # --- CENTER: TAB EDITOR + SEARCH BAR ---
        center_widget = QWidget()
        c_layout = QVBoxLayout(center_widget)
        c_layout.setContentsMargins(0,0,0,0)
        c_layout.setSpacing(0)
        
        # Such-Leiste
        self.search_bar = SearchReplaceBar()
        c_layout.addWidget(self.search_bar)
        
        # Editor + Minimap Container (NEU v7)
        editor_container = QWidget()
        editor_h_layout = QHBoxLayout(editor_container)
        editor_h_layout.setContentsMargins(0, 0, 0, 0)
        editor_h_layout.setSpacing(0)
        
        # Multi-Tab Editor
        self.tab_editor = MultiTabEditor()
        self.tab_editor.currentEditorChanged.connect(self.on_editor_changed)
        editor_h_layout.addWidget(self.tab_editor)
        
        # Minimap (NEU v7)
        self.minimap = None  # Wird bei Bedarf erstellt
        self.minimap_container = QWidget()
        self.minimap_container.setFixedWidth(80)
        self.minimap_container.setVisible(self.settings.value("show_minimap", False, type=bool))
        editor_h_layout.addWidget(self.minimap_container)
        
        c_layout.addWidget(editor_container)
        
        # Verbinde Search-Bar mit aktuellem Editor
        self.on_editor_changed(self.tab_editor.current_editor())
        
        splitter.addWidget(center_widget)
        
        # --- RIGHT: PREVIEW ---
        right_widget = QWidget()
        r_layout = QVBoxLayout(right_widget)
        r_layout.setContentsMargins(0,0,0,0)
        
        h_prev = QHBoxLayout()
        self.lbl_preview = QLabel("Vorschau")
        self.btn_insert = QPushButton("⬇️ Einfügen")
        self.btn_insert.setEnabled(False)
        self.btn_insert.clicked.connect(self.insert_snippet)
        h_prev.addWidget(self.lbl_preview)
        h_prev.addStretch()
        h_prev.addWidget(self.btn_insert)
        r_layout.addLayout(h_prev)
        
        self.preview_editor = CodeEditor()
        self.preview_editor.setReadOnly(True)
        self.preview_highlighter = PythonSyntaxHighlighter(self.preview_editor.document())
        r_layout.addWidget(self.preview_editor)
        
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 1)
        
        layout.addWidget(splitter)

        # --- DEBUG OUTPUT PANEL (DOCK) (ERWEITERT v8!) ---
        self.output_dock = QDockWidget("Ausgabe / Debugger", self)
        self.debug_output = DebugOutputPanel()
        self.debug_output.debugStateChanged.connect(self.on_debug_state_changed)
        self.output_dock.setWidget(self.debug_output)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.output_dock)
        self.output_dock.hide()

        # --- LINTER PANEL (DOCK) (NEU v7!) ---
        self.linter_dock = QDockWidget("Linter Probleme", self)
        self.linter_list = QListWidget()
        self.linter_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                color: #ddd;
                border: none;
            }
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:hover {
                background-color: #2a2a2a;
            }
            QListWidget::item:selected {
                background-color: #2a82da;
            }
        """)
        self.linter_list.itemDoubleClicked.connect(self.goto_linter_error)
        self.linter_dock.setWidget(self.linter_list)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.linter_dock)
        self.linter_dock.hide()

        # --- MINIMAP (NEU v7!) ---
        self.minimap = None  # Wird bei Bedarf erstellt

        # --- STATUS BAR ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # --- GIT STATUS LABEL (NEU v7!) ---
        self.git_label = QLabel("")
        self.status_bar.addWidget(self.git_label)
        
        self.pos_label = QLabel("Zeile: 1 | Spalte: 1")
        self.status_bar.addPermanentWidget(self.pos_label)
        
        # Linter-Status
        self.linter_status = QLabel("")
        self.status_bar.addPermanentWidget(self.linter_status)


    def setup_shortcuts(self):
        """Richtet Tastenkürzel ein"""
        # Escape schließt Suchleiste
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.search_bar.hide)

    def on_editor_changed(self, editor: CodeEditor):
        """Wird aufgerufen wenn der aktive Editor wechselt"""
        if editor:
            self.search_bar.set_editor(editor)
            editor.cursorPositionInfo.connect(self.update_cursor_position)
            
            # NEU v7: Git-Status aktualisieren (nur wenn git_label existiert)
            if hasattr(self, 'git_label'):
                tab = self.tab_editor.current_tab()
                if tab and tab.file_path:
                    status = self.git.get_file_status(tab.file_path)
                    self.git_label.setText(f"Git: {status}" if status else "")
                    
                    # Git-Zeilen-Markierungen
                    added, modified, deleted = self.git.get_modified_lines(tab.file_path)
                    editor.set_git_status(added, modified)
                else:
                    self.git_label.setText("")
            
            # Minimap aktualisieren
            if hasattr(self, 'minimap_action'):
                self._update_minimap(editor)

    def update_cursor_position(self, line: int, col: int):
        self.pos_label.setText(f"Zeile: {line} | Spalte: {col}")

    # --- RECENT FILES ---
    
    def _load_recent_files(self) -> List[str]:
        files = self.settings.value("recent_files", [])
        return files if isinstance(files, list) else []

    def _save_recent_files(self):
        self.settings.setValue("recent_files", self.recent_files[:10])

    def _add_recent_file(self, path: str):
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        self.recent_files = self.recent_files[:10]
        self._save_recent_files()
        self._update_recent_menu()

    def _update_recent_menu(self):
        self.recent_menu.clear()
        for path in self.recent_files:
            if Path(path).exists():
                action = self.recent_menu.addAction(Path(path).name)
                action.setToolTip(path)
                action.triggered.connect(lambda checked, p=path: self.open_recent_file(p))
        
        if not self.recent_files:
            action = self.recent_menu.addAction("(Keine)")
            action.setEnabled(False)

    def open_recent_file(self, path: str):
        if Path(path).exists():
            self.tab_editor.open_file(path)
            self._add_recent_file(path)

    def _restore_window_state(self):
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    # --- EDIT ACTIONS ---
    
    def undo_action(self):
        editor = self.tab_editor.current_editor()
        if editor:
            editor.undo()

    def redo_action(self):
        editor = self.tab_editor.current_editor()
        if editor:
            editor.redo()

    def cut_action(self):
        editor = self.tab_editor.current_editor()
        if editor:
            editor.cut()

    def copy_action(self):
        editor = self.tab_editor.current_editor()
        if editor:
            editor.copy()

    def paste_action(self):
        editor = self.tab_editor.current_editor()
        if editor:
            editor.paste()

    def show_search(self):
        self.search_bar.show_search()

    def show_replace(self):
        self.search_bar.show_replace()

    def goto_line(self):
        """Öffnet den Gehe-zu-Zeile Dialog"""
        editor = self.tab_editor.current_editor()
        if not editor:
            return
        
        max_line = editor.blockCount()
        dlg = GotoLineDialog(self, max_line)
        
        # Aktuelle Zeile vorausfüllen
        cursor = editor.textCursor()
        dlg.line_spin.setValue(cursor.blockNumber() + 1)
        
        if dlg.exec_() == QDialog.Accepted:
            line = dlg.get_line()
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line - 1)
            editor.setTextCursor(cursor)
            editor.centerCursor()
            editor.setFocus()

    def show_settings(self):
        """Öffnet den Einstellungs-Dialog"""
        dlg = SettingsDialog(self, self.settings)
        if dlg.exec_() == QDialog.Accepted:
            self._apply_settings_to_editors()
            self.status_bar.showMessage("Einstellungen gespeichert", 3000)

    def _apply_settings_to_editors(self):
        """Wendet Einstellungen auf alle Editoren an"""
        font_size = self.settings.value("font_size", 10, type=int)
        tab_size = self.settings.value("tab_size", 4, type=int)
        word_wrap = self.settings.value("word_wrap", False, type=bool)
        autocomplete = self.settings.value("autocomplete", True, type=bool)
        bracket_matching = self.settings.value("bracket_matching", True, type=bool)
        
        # Alle Editoren aktualisieren
        for tab in self.tab_editor.tabs.values():
            editor = tab.editor
            
            # Schriftgröße
            font = editor.font()
            font.setPointSize(font_size)
            editor.setFont(font)
            
            # Tab-Größe
            editor.setTabStopWidth(editor.fontMetrics().width(' ') * tab_size)
            
            # Zeilenumbruch
            if word_wrap:
                editor.setLineWrapMode(QPlainTextEdit.WidgetWidth)
            else:
                editor.setLineWrapMode(QPlainTextEdit.NoWrap)
            
            # Auto-Completion
            editor.autocomplete_enabled = autocomplete
            
            # Bracket Matching
            editor.bracket_matching_enabled = bracket_matching
        
        # Preview Editor auch
        font = self.preview_editor.font()
        font.setPointSize(font_size)
        self.preview_editor.setFont(font)

    # --- NEU v7: MINIMAP, LINTER, GIT ---

    def toggle_minimap(self, checked: bool):
        """Minimap ein-/ausschalten"""
        self.settings.setValue("show_minimap", checked)
        self.minimap_container.setVisible(checked)
        if checked:
            editor = self.tab_editor.current_editor()
            if editor:
                self._update_minimap(editor)
        self.status_bar.showMessage(f"Minimap {'aktiviert' if checked else 'deaktiviert'}", 2000)

    def _update_minimap(self, editor: CodeEditor):
        """Aktualisiert/Erstellt Minimap für Editor"""
        if not self.minimap_action.isChecked():
            return
        
        # Alte Minimap entfernen
        if self.minimap:
            self.minimap.deleteLater()
        
        # Neue Minimap erstellen
        layout = self.minimap_container.layout()
        if not layout:
            layout = QVBoxLayout(self.minimap_container)
            layout.setContentsMargins(0, 0, 0, 0)
        
        self.minimap = Minimap(editor, self.minimap_container)
        layout.addWidget(self.minimap)

    def toggle_linter_panel(self, checked: bool):
        """Linter-Panel ein-/ausblenden"""
        if checked:
            self.linter_dock.show()
        else:
            self.linter_dock.hide()

    def run_linter_now(self):
        """Führt Linter sofort aus"""
        editor = self.tab_editor.current_editor()
        if not editor:
            return
        
        code = editor.toPlainText()
        tab = self.tab_editor.current_tab()
        file_path = tab.file_path if tab else None
        
        self.status_bar.showMessage("Linter wird ausgeführt...", 0)
        QApplication.processEvents()
        
        errors = self.linter.run_linter(code, file_path)
        
        # Ergebnisse anzeigen
        self.linter_list.clear()
        error_count = 0
        warning_count = 0
        
        for error in errors:
            severity = error.get('severity', 'error')
            line = error.get('line', 1)
            col = error.get('column', 0)
            code_str = error.get('code', '')
            msg = error.get('message', '')
            
            icon = "❌" if severity == 'error' else "⚠️"
            item_text = f"{icon} Zeile {line}:{col} [{code_str}] {msg}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, error)
            
            if severity == 'error':
                item.setForeground(QColor(255, 100, 100))
                error_count += 1
            else:
                item.setForeground(QColor(255, 200, 100))
                warning_count += 1
            
            self.linter_list.addItem(item)
        
        # Editor markieren
        editor.set_linter_errors(errors)
        
        # Status
        if errors:
            self.linter_status.setText(f"❌ {error_count} | ⚠️ {warning_count}")
            self.linter_dock.show()
            self.linter_action.setChecked(True)
        else:
            self.linter_status.setText("✓ Keine Probleme")
        
        self.status_bar.showMessage(f"Linter: {error_count} Fehler, {warning_count} Warnungen", 3000)

    def run_linter_delayed(self):
        """Verzögerter Linter-Aufruf (nach Tipp-Pause)"""
        self.run_linter_now()

    def schedule_linter(self):
        """Plant Linter-Ausführung nach Verzögerung"""
        self.lint_timer.stop()
        self.lint_timer.start(1500)  # 1.5 Sekunden nach letztem Tastendruck

    def goto_linter_error(self, item: QListWidgetItem):
        """Springt zur Fehlerstelle"""
        error = item.data(Qt.UserRole)
        if not error:
            return
        
        line = error.get('line', 1)
        col = error.get('column', 0)
        
        editor = self.tab_editor.current_editor()
        if editor:
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line - 1)
            cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, col)
            editor.setTextCursor(cursor)
            editor.centerCursor()
            editor.setFocus()

    def show_git_status(self):
        """Zeigt Git-Status Dialog"""
        tab = self.tab_editor.current_tab()
        if not tab or not tab.file_path:
            QMessageBox.information(self, "Git Status", "Datei muss erst gespeichert werden.")
            return
        
        status = self.git.get_file_status(tab.file_path)
        diff = self.git.get_diff(tab.file_path)
        
        if not status:
            QMessageBox.information(self, "Git Status", "Keine Git-Repository gefunden.")
            return
        
        dlg = QDialog(self)
        dlg.setWindowTitle("Git Status")
        dlg.resize(600, 400)
        
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel(f"Status: {status}"))
        layout.addWidget(QLabel(f"Datei: {tab.file_path}"))
        
        if diff:
            layout.addWidget(QLabel("Diff:"))
            diff_edit = QPlainTextEdit()
            diff_edit.setReadOnly(True)
            diff_edit.setPlainText(diff)
            diff_edit.setFont(QFont("Consolas", 9))
            diff_edit.setStyleSheet("background-color: #1e1e1e; color: #ddd;")
            layout.addWidget(diff_edit)
        else:
            layout.addWidget(QLabel("Keine Änderungen."))
        
        btn = QPushButton("Schließen")
        btn.clicked.connect(dlg.close)
        layout.addWidget(btn)
        
        dlg.exec_()

    def update_git_status(self):
        """Aktualisiert Git-Status für aktuellen Editor"""
        tab = self.tab_editor.current_tab()
        editor = self.tab_editor.current_editor()
        
        if not tab or not tab.file_path or not editor:
            self.git_label.setText("")
            return
        
        status = self.git.get_file_status(tab.file_path)
        if status:
            self.git_label.setText(f"Git: {status}")
            
            # Zeilen-Markierungen
            added, modified, deleted = self.git.get_modified_lines(tab.file_path)
            editor.set_git_status(added, modified)

    # --- DEBUG FUNKTIONEN (NEU v8!) ---

    def run_script(self):
        """Führt aktuelles Script normal aus"""
        tab = self.tab_editor.current_tab()
        if not tab or not tab.file_path:
            QMessageBox.warning(self, "Fehler", "Bitte speichere die Datei zuerst.")
            return
        
        # Speichern vor Ausführung
        self.save_file()
        
        self.output_dock.show()
        self.debug_output.run_normal(tab.file_path)

    def run_with_debugger(self):
        """Startet Script mit pdb-Debugger (NEU v8!)"""
        tab = self.tab_editor.current_tab()
        editor = self.tab_editor.current_editor()
        
        if not tab or not tab.file_path:
            QMessageBox.warning(self, "Fehler", "Bitte speichere die Datei zuerst.")
            return
        
        # Speichern vor Ausführung
        self.save_file()
        
        # Breakpoints sammeln
        bp_commands = []
        if editor:
            for line in sorted(editor.breakpoints):
                bp_commands.append(f"b {line}")
        
        self.output_dock.show()
        self.debug_output.run_with_pdb(tab.file_path, bp_commands)

    def toggle_breakpoint_action(self):
        """Setzt/Entfernt Breakpoint an aktueller Cursor-Position (NEU v8!)"""
        editor = self.tab_editor.current_editor()
        if not editor:
            return
        
        cursor = editor.textCursor()
        line = cursor.blockNumber() + 1
        
        is_set = editor.toggle_breakpoint(line)
        
        if is_set:
            self.status_bar.showMessage(f"🔴 Breakpoint gesetzt an Zeile {line}", 2000)
        else:
            self.status_bar.showMessage(f"Breakpoint entfernt von Zeile {line}", 2000)

    def clear_all_breakpoints(self):
        """Entfernt alle Breakpoints (NEU v8!)"""
        editor = self.tab_editor.current_editor()
        if editor:
            editor.breakpoints.clear()
            editor.lineNumberArea.update()
            self.status_bar.showMessage("Alle Breakpoints entfernt", 2000)

    def on_debug_state_changed(self, is_debugging: bool):
        """Wird aufgerufen wenn Debug-Status sich ändert (NEU v8!)"""
        editor = self.tab_editor.current_editor()
        if editor and not is_debugging:
            editor.clear_debug_state()

    def open_in_vscode(self):
        """Öffnet aktuelle Datei in VS Code (NEU v8!)"""
        tab = self.tab_editor.current_tab()
        editor = self.tab_editor.current_editor()
        
        if not tab or not tab.file_path:
            QMessageBox.warning(self, "Fehler", "Bitte speichere die Datei zuerst.")
            return
        
        # Aktuelle Zeile ermitteln
        line = 1
        if editor:
            line = editor.textCursor().blockNumber() + 1
        
        success, msg = self.ide_integration.open_in_vscode(tab.file_path, line)
        
        if success:
            self.status_bar.showMessage(f"🔷 {msg}", 3000)
        else:
            QMessageBox.warning(self, "VS Code", f"Fehler: {msg}")

    def debug_in_vscode(self):
        """Startet Debugging in VS Code (NEU v8!)"""
        tab = self.tab_editor.current_tab()
        
        if not tab or not tab.file_path:
            QMessageBox.warning(self, "Fehler", "Bitte speichere die Datei zuerst.")
            return
        
        # Speichern vor Debugging
        self.save_file()
        
        success, msg = self.ide_integration.debug_in_vscode(tab.file_path)
        
        if success:
            self.status_bar.showMessage(f"🔷 {msg}", 3000)
        else:
            QMessageBox.warning(self, "VS Code", f"Fehler: {msg}")

    def open_in_pycharm(self):
        """Öffnet aktuelle Datei in PyCharm (NEU v8!)"""
        tab = self.tab_editor.current_tab()
        editor = self.tab_editor.current_editor()
        
        if not tab or not tab.file_path:
            QMessageBox.warning(self, "Fehler", "Bitte speichere die Datei zuerst.")
            return
        
        line = 1
        if editor:
            line = editor.textCursor().blockNumber() + 1
        
        success, msg = self.ide_integration.open_in_pycharm(tab.file_path, line)
        
        if success:
            self.status_bar.showMessage(f"🟢 {msg}", 3000)
        else:
            QMessageBox.warning(self, "PyCharm", f"Fehler: {msg}")

    # --- FILE OPERATIONS ---

    def new_file(self):
        self.tab_editor.new_tab()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Skript öffnen", "", 
            "Python (*.py);;Text (*.txt);;Alle Dateien (*)"
        )
        if path:
            self.tab_editor.open_file(path)
            self._add_recent_file(path)

    def save_file(self):
        index = self.tab_editor.tab_widget.currentIndex()
        if self.tab_editor.save_tab(index):
            tab = self.tab_editor.current_tab()
            if tab and tab.file_path:
                self._add_recent_file(tab.file_path)
                self.status_bar.showMessage(f"Gespeichert: {tab.file_path}", 3000)

    def save_file_as(self):
        tab = self.tab_editor.current_tab()
        if tab:
            tab.file_path = None  # Force "Save As" dialog
            index = self.tab_editor.tab_widget.currentIndex()
            self.tab_editor.save_tab(index)

    # --- LIBRARY TREE ---

    def load_library_tree(self):
        self.tree.clear()
        topics = self.lib_manager.get_topics()
        
        for topic in topics:
            item = QTreeWidgetItem(self.tree)
            item.setText(0, topic)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setExpanded(True)
            item.setIcon(0, self.style().standardIcon(QStyle.SP_DirIcon))
            
            snippets = self.lib_manager.get_items(topic)
            for snippet in snippets:
                child = QTreeWidgetItem(item)
                is_locked = self.lib_manager.is_locked(topic, snippet)
                prefix = "🔒 " if is_locked else ""
                child.setText(0, f"{prefix}{snippet}")
                child.setData(0, Qt.UserRole, {"topic": topic, "name": snippet, "locked": is_locked})
                child.setIcon(0, self.style().standardIcon(QStyle.SP_FileIcon))

    def on_tree_select(self, item, col):
        data = item.data(0, Qt.UserRole)
        if data:
            content = self.lib_manager.get_content(data['topic'], data['name'])
            self.lbl_preview.setText(f"Vorschau: {data['name']}")
            self.preview_editor.setPlainText(content)
            self.btn_insert.setEnabled(True)
        else:
            self.btn_insert.setEnabled(False)

    def on_tree_double_click(self, item, col):
        """Doppelklick fügt Snippet direkt ein"""
        data = item.data(0, Qt.UserRole)
        if data:
            self.insert_snippet()

    def open_tree_context(self, position):
        item = self.tree.itemAt(position)
        menu = QMenu()
        
        menu.addAction("➕ Neuer Eintrag...", self.new_library_item)
        
        if item and item.data(0, Qt.UserRole):
            data = item.data(0, Qt.UserRole)
            is_locked = data['locked']
            
            menu.addSeparator()
            menu.addAction("✏️ Bearbeiten", lambda: self.edit_library_item(item))
            
            lock_text = "🔓 Entsperren" if is_locked else "🔒 Sperren"
            menu.addAction(lock_text, lambda: self.toggle_lock_item(item))
            
            if not is_locked:
                menu.addAction("🗑️ Löschen", lambda: self.delete_library_item(item))
            else:
                act = menu.addAction("🗑️ Löschen (Gesperrt)")
                act.setEnabled(False)
        
        menu.exec_(self.tree.viewport().mapToGlobal(position))


    # --- LIBRARY ACTIONS ---

    def new_library_item(self):
        topics = self.lib_manager.get_topics()
        dlg = SnippetDialog(self, topics)
        if dlg.exec_() == QDialog.Accepted:
            t, n, c = dlg.get_data()
            if t and n:
                success, msg = self.lib_manager.save_snippet(t, n, c)
                if success:
                    self.load_library_tree()
                else:
                    QMessageBox.warning(self, "Fehler", msg)

    def edit_library_item(self, item):
        data = item.data(0, Qt.UserRole)
        content = self.lib_manager.get_content(data['topic'], data['name'])
        topics = self.lib_manager.get_topics()
        
        dlg = SnippetDialog(self, topics, data['topic'], data['name'], content)
        if dlg.exec_() == QDialog.Accepted:
            t, n, c = dlg.get_data()
            if t != data['topic'] or n != data['name']:
                if data['locked']:
                    QMessageBox.warning(self, "Gesperrt", "Namen ändern bei gesperrten Items nicht erlaubt.")
                    return
                self.lib_manager.delete_item(data['topic'], data['name'])
            
            self.lib_manager.save_snippet(t, n, c)
            self.load_library_tree()

    def delete_library_item(self, item):
        data = item.data(0, Qt.UserRole)
        if QMessageBox.question(self, "Löschen", f"{data['name']} wirklich löschen?") == QMessageBox.Yes:
            if self.lib_manager.delete_item(data['topic'], data['name']):
                self.load_library_tree()

    def toggle_lock_item(self, item):
        data = item.data(0, Qt.UserRole)
        self.lib_manager.toggle_lock(data['topic'], data['name'])
        self.load_library_tree()

    # --- DRAG & DROP ---
    
    def tree_drag_enter(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def tree_drop(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = Path(url.toLocalFile())
                if path.is_file() and path.suffix == '.py':
                    content = path.read_text(encoding='utf-8')
                    self.lib_manager.save_snippet("Importiert", path.stem, content)
            self.load_library_tree()
        elif event.mimeData().hasText():
            text = event.mimeData().text()
            self.lib_manager.save_snippet("Importiert", "Neues_Snippet", text)
            self.load_library_tree()

    # --- ASSEMBLY ACTIONS ---

    def insert_snippet(self):
        editor = self.tab_editor.current_editor()
        if not editor:
            return
        
        text = self.preview_editor.toPlainText()
        cursor = editor.textCursor()
        
        if editor.toPlainText().strip():
            cursor.movePosition(QTextCursor.End)
            cursor.insertText("\n\n")
        
        cursor.insertText(text)
        editor.setTextCursor(cursor)
        editor.setFocus()

    def optimize_imports_action(self):
        editor = self.tab_editor.current_editor()
        if not editor:
            return
        
        code = editor.toPlainText()
        new_code, msg = ImportOptimizer.organize_imports(code)
        if new_code:
            editor.setPlainText(new_code)
            self.status_bar.showMessage(msg, 3000)
        else:
            QMessageBox.warning(self, "Fehler", msg)

    def check_indentation(self):
        editor = self.tab_editor.current_editor()
        if not editor:
            return
        
        code = editor.toPlainText().splitlines()
        errors = []
        for i, line in enumerate(code):
            stripped = line.strip()
            if stripped.endswith(":") and not stripped.startswith("#"):
                if i + 1 < len(code):
                    next_line = code[i+1]
                    if next_line.strip() and not (len(next_line) - len(next_line.lstrip()) > len(line) - len(line.lstrip())):
                        errors.append(f"Zeile {i+1}: Block erwartet, aber Einrückung fehlt.")
            if "\t" in line:
                errors.append(f"Zeile {i+1}: Tabs gefunden (PEP8 empfiehlt Leerzeichen).")
        
        if errors:
            QMessageBox.warning(self, "Indentation Check", "\n".join(errors[:10]))
        else:
            QMessageBox.information(self, "OK", "Keine offensichtlichen Einrückungsfehler gefunden.")

    def fix_encoding(self):
        QMessageBox.information(self, "Info", "Text ist bereits interner Unicode. Speichern erzwingt UTF-8.")

    # --- BUILD & RUN ---

    def run_script(self):
        """Führt das aktuelle Skript im integrierten Output-Panel aus"""
        editor = self.tab_editor.current_editor()
        if not editor:
            return
        
        code = editor.toPlainText()
        if not code.strip():
            return
        
        self.output_dock.show()
        self.output_panel.run_code(code)

    def run_script_external(self):
        """Führt das aktuelle Skript in externem Terminal aus"""
        editor = self.tab_editor.current_editor()
        if not editor:
            return
        
        code = editor.toPlainText()
        if not code.strip():
            return
        
        tmp_path = Path.home() / ".python_baukasten" / "temp_run.py"
        tmp_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path.write_text(code, encoding='utf-8')
        
        if sys.platform == "win32":
            subprocess.Popen(f'start cmd /k python "{tmp_path}"', shell=True)
        else:
            subprocess.Popen(['x-terminal-emulator', '-e', f'python3 "{tmp_path}"'])

    def build_exe(self):
        if not shutil.which("pyinstaller"):
            QMessageBox.critical(self, "Fehler", "PyInstaller nicht gefunden.\nBitte `pip install pyinstaller` ausführen.")
            return
        
        tab = self.tab_editor.current_tab()
        if not tab or not tab.file_path:
            QMessageBox.warning(self, "Achtung", "Bitte Datei erst speichern.")
            return

        dist_dir = Path(tab.file_path).parent / "dist"
        cmd = ["pyinstaller", "--onefile", "--noconfirm", "--distpath", str(dist_dir), tab.file_path]
        
        self.status_bar.showMessage("Erstelle EXE...", 0)
        try:
            subprocess.run(cmd, check=True)
            QMessageBox.information(self, "Fertig", f"EXE erstellt in:\n{dist_dir}")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Build Fehler", str(e))
        finally:
            self.status_bar.clearMessage()

    # --- EXTERNAL TOOLS ---
    
    def open_tools_folder(self):
        tools_dir = Path.home() / ".python_baukasten" / "tools"
        tools_dir.mkdir(parents=True, exist_ok=True)
        if sys.platform == 'win32':
            os.startfile(tools_dir)
        else:
            subprocess.Popen(['xdg-open', str(tools_dir)])

    def scan_external_tools(self):
        tools_dir = Path.home() / ".python_baukasten" / "tools"
        tools_dir.mkdir(parents=True, exist_ok=True)
        
        actions = self.ext_tools_menu.actions()
        for action in actions[2:]: 
            self.ext_tools_menu.removeAction(action)
            
        py_files = sorted(list(tools_dir.glob("*.py")))
        
        if not py_files:
            dummy = self.ext_tools_menu.addAction("(Keine Tools gefunden)")
            dummy.setEnabled(False)
            return

        for tool in py_files:
            name = tool.stem.replace("_", " ").title()
            self.ext_tools_menu.addAction(f"🛠️ {name}", lambda t=tool: self.run_external_tool(t))

    def run_external_tool(self, path):
        if sys.platform == "win32":
            subprocess.Popen(f'start cmd /k python "{path}"', shell=True)
        else:
            subprocess.Popen(['python3', str(path)])


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    app = QApplication(sys.argv)
    set_dark_theme(app)
    
    window = PythonArchitect()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
