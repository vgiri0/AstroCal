#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) Open Astro Technologies, USA.
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/PyJHora

# This file is part of the "PyJHora" Python library
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Basic GUI tests for the PyJHora widgets.

This module used to start a Qt application and block waiting for user
interaction.  When running in headless or CI environments such behaviour
causes the test suite to hang.  The tests below create the application in
``offscreen`` mode, instantiate the widget and immediately close everything so
that the suite finishes promptly.
"""

import os
import sys
import pytest
from PyQt6.QtWidgets import QApplication


@pytest.fixture
def qapp():
    """Create a QApplication for tests and ensure it is closed afterwards."""

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication(sys.argv)
    yield app
    # Close all remaining windows and quit the application
    for widget in list(app.topLevelWidgets()):
        widget.close()
    app.quit()


def test_chart_tabbed_creation(qapp):
    """Simply instantiate ``ChartTabbed`` and show/hide it."""

    from jhora.ui.horo_chart_tabs import ChartTabbed

    widget = ChartTabbed()
    widget.show()
    qapp.processEvents()
    assert widget.isVisible()
    widget.close()
