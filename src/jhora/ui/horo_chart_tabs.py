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
"""PyQt6 based UI for displaying horoscope charts."""

import os
import re
import sys

sys.path.append("../")

from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontMetrics
from PyQt6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QAbstractScrollArea,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QLayout,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QStyledItemDelegate,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)
from _datetime import datetime, timedelta, timezone
import img2pdf
from PIL import Image
import numpy as np
from jhora import const, utils
from jhora.panchanga import drik, pancha_paksha, vratha
from jhora.horoscope import main
from jhora.horoscope.prediction import general
from jhora.horoscope.match import compatibility
from jhora.horoscope.chart import ashtakavarga
from jhora.horoscope.chart import yoga, raja_yoga, dosha, charts, strength, arudhas
from jhora.horoscope.chart import house
from jhora.ui import varga_chart_dialog,options_dialog, mixed_chart_dialog, dhasa_bhukthi_options_dialog,vratha_finder, \
                     conjunction_dialog, pancha_pakshi_sastra_widget
from jhora.ui.options_dialog import OptionDialog
from jhora.ui.panchangam import PanchangaInfoDialog
from jhora.horoscope.dhasa.graha import vimsottari
from jhora.ui.chart_styles import EastIndianChart, WesternChart, SouthIndianChart, NorthIndianChart, SudarsanaChakraChart
from jhora.ui.label_grid import LabelGrid
from jhora.horoscope.dhasa import sudharsana_chakra
from jhora.ui.chakra import KotaChakra, KaalaChakra, Sarvatobadra, Shoola, SuryaKalanala, Tripataki,ChandraKalanala, \
                            SapthaShalaka, PanchaShalaka, SapthaNaadi
_available_ayanamsa_modes = [k for k in list(const.available_ayanamsa_modes.keys()) if k not in ['SENTHIL','SIDM_USER','SUNDAR_SS']]
_KEY_COLOR = 'brown'; _VALUE_COLOR = 'blue'; _HEADER_COLOR='green'
_KEY_LENGTH=50; _VALUE_LENGTH=50; _HEADER_LENGTH=100
_HEADER_FORMAT_ = '<b><span style="color:'+_HEADER_COLOR+';">{:.'+str(_HEADER_LENGTH)+'}</span></b><br>'
_KEY_VALUE_FORMAT_ = '<span style="color:'+_KEY_COLOR+';">{:.'+str(_KEY_LENGTH)+'}</span><span style="color:'+\
        _VALUE_COLOR+';">{:.'+str(_VALUE_LENGTH)+'}</span><br>'
_images_path = const._IMAGES_PATH
_IMAGES_PER_PDF_PAGE = 2
_INPUT_DATA_FILE = const._INPUT_DATA_FILE
_SHOW_GOURI_PANCHANG_OR_SHUBHA_HORA = 0  # 0=Gowri Panchang 1=Shubha Hora
_world_city_csv_file = const._world_city_csv_file
_planet_symbols = const._planet_symbols
_zodiac_symbols = const._zodiac_symbols

# ---------------------------------------------------------------------------
# UI Constants
# ---------------------------------------------------------------------------
_main_window_width = 1000#750 #725
_main_window_height = 725#630 #580 #
_comp_table_font_size = 8
_comp_results_per_list_item = 3
_yoga_text_font_size = 10#8.5
_dosha_text_font_size = 10#9
_prediction_text_font_size = 5
_raja_yogas_per_list_item = 1 # Do not change this from 1 yet
_yogas_per_list_item = 3
_yoga_chart_option = None # None => Get yogas/raja yogas for all Chart; 1,2,3,=>Get yogas for specified varga
_doshas_per_list_item = 1
_predictions_per_list_item = 1
_compatability_list_width = 175#145
_yoga_list_box_width = 125
_dosha_list_box_width = 150#125
_prediction_list_box_width = 150
_shodhaya_table_font_size = 9#6.3
_drishti_table_font_size = 8#6.3
_saham_table_font_size = 8#6.3
_chart_info_label_font_size = 6#7# # if uranus/neptune/pluto included
south_chart_title_font_size = 12; north_chart_title_font_size=12; east_chart_title_font_size=12
west_chart_title_font_size = 10; sudarsana_chakra_chart_title_font_size = 8
_main_ui_label_button_font_size = 10#8
#_main_ui_comp_label_font_size = 7
_info_label1_height = 200
_info_label1_width = 100
_info_label1_font_size = 4.87#8
_info_label2_height = _info_label1_height; _info_label3_height = _info_label1_height
_info_label2_width = 100
_info_label2_font_size = 4.87#8
_info_label3_font_size = 4.87#8
_row3_widget_width = 75
_chart_info_label_width = 230#350
_ashtaka_chart_size_factor = 0.475
_footer_label_font_height = 8
_footer_label_height = 30
_chart_size_factor = 1.35
_bhava_chart_size_factor = 1.25
_chart_label_font_size = 12
_margin_between_chart_and_info = 1
_arudha_lagnas_included_in_chart = const._arudha_lagnas_included_in_chart
_chart_names = ['raasi_str','hora_str','drekkanam_str','chaturthamsa_str','panchamsa_str',
              'shashthamsa_str','saptamsam_str','ashtamsa_str','navamsam_str','dhasamsam_str','rudramsa_str',
              'dhwadamsam_str','shodamsa_str','vimsamsa_str','chaturvimsamsa_str','nakshatramsa_str','thrisamsam_str',
              'khavedamsa_str','akshavedamsa_str','sashtiamsam_str','nava_navamsa_str','ashtotharamsa_str',
              'dwadas_dwadasamsa_str','custom_varga_kundali_str','mixed_varga_kundali_str']
_custom_chart_index = len(const.division_chart_factors) ; _mixed_chart_index = _custom_chart_index+1
_custom_varga_index = const.DEFAULT_CUSTOM_VARGA_FACTOR
_mixed_chart_index_1 = 8; _mixed_chart_method_1 = 1
_mixed_chart_index_2 = 11; _mixed_chart_method_2 = 1
_bala_names = ['amsa_ruler_str','sphuta_str','drishti_str','bhava_graha_arudha_str','vimsopaka_bala_str','vaiseshikamsa_bala_str',
               'harsha_pancha_dwadhasa_vargeeya_bala_str','shad_bala_str','bhava_bala_str']
""" dhasa dictionary {"dhasa":[tab_count,table_font_size,tables_per_tab,rows_per_table,cols_per_table] """
_graha_dhasa_dict = {'vimsottari':[3,10,3,9,1,0,[],[]],'yoga_vimsottari':[3,10,3,9,1,0,[],[]],'rasi_bhukthi_vimsottari':[3,10,3,12,1,0,[],[]],
                     'ashtottari':[3,10,3,8,1,0,[],[]],'tithi_ashtottari':[3,10,3,8,1,0,[],[]],'yogini':[4,8,4,8,1,0,[],[]],
                     'tithi_yogini':[4,8,4,8,1,0,[],[]],'shodasottari':[2,8,4,8,1,0,[],[]],'dwadasottari':[2,8,4,8,1,0,[],[]],
                     'dwisatpathi':[4,8,4,8,1,0,[],[]],'panchottari':[2,8,4,7,1,0,[],[]],'satabdika':[2,8,4,7,1,0,[],[]],
                     'chaturaaseeti_sama':[2,8,4,7,1,0,[],[]],'karana_chaturaaseeti_sama':[2,8,4,7,1,0,[],[]],
                     'shashtisama':[2,8,4,8,1,0,[],[]],'shattrimsa_sama':[6,7,4,8,1,0,[],[]],'naisargika':[2,8,4,6,1,0,[],[]],
                     'tara':[3,10,3,9,1,0,[],[]],'karaka':[4,7.5,4,8,1,0,[],[]],'buddhi_gathi':[5,7,4,9,1,0,[],[]],
                     'kaala':[6,8,3,18,1,0,[],[]],'aayu':[2,8,4,8,1,0,[],[]],'saptharishi_nakshathra':[3,8,3,11,1,0,[],[]]}
_graha_dhasa_names = list(_graha_dhasa_dict.keys())
_graha_dhasa_tab_count = sum(v[0] for k,v in _graha_dhasa_dict.items())
_rasi_dhasa_dict = {'narayana':[4,7,3,12,1,0,[],[]],'kendraadhi_rasi':[4,7,3,12,1,0,[],[]],'sudasa':[4,7,3,12,1,0,[],[]],'drig':[3,8,4,12,1,0,[],[]],
                'nirayana':[4,7,3,12,1,0,[],[]], 'shoola':[4,7,3,12,1,0,[],[]],'kendraadhi_karaka':[4,7,3,12,1,0,[],[]],
                'chara':[4,7,3,12,1,0,[],[]],'lagnamsaka':[4,7,3,12,1,0,[],[]],'padhanadhamsa':[4,7,3,12,1,0,[],[]],
                'mandooka':[4,7,3,12,1,0,[],[]],'sthira':[4,7,3,12,1,0,[],[]],'tara_lagna':[4,7,3,12,1,0,[],[]],
                'brahma':[4,7,3,12,1,0,[],[]],'varnada':[4,7,3,12,1,0,[],[]],'yogardha':[4,7,3,12,1,0,[],[]],
                'navamsa':[3,7.5,4,12,1,0,[],[]],'paryaaya':[3,7.5,4,12,1,0,[],[]],'trikona':[3,7.5,4,12,1,0,[],[]],
                'kalachakra':[3,8,3,9,1,0,[],[]],'chakra':[3,7.5,4,12,1,0,[],[]],'sandhya_panchaka':[3,7.5,4,12,1,0,[],[]]}
_varnada_method_options = ['1=>BV Raman','2=>Sharma/Santhanam','3=Sanjay Rath','4=Sitaram Jha']
### 'paryaaya':[1,10,2,12,1,0,[],[]],'trikona':[1,10,2,12,1,0,[],[]],
_rasi_dhasa_names = list(_rasi_dhasa_dict.keys())
_rasi_dhasa_tab_count = sum(v[0] for k,v in _rasi_dhasa_dict.items())
_annual_dhasa_dict ={'patyayini':[2,7.5,4,8,1,0,[],[]],'varsha_vimsottari':[3,9,3,9,1,0,[],[]],'varsha_narayana':[5,7.5,4,12,1,0,[],[]],}
_annual_dhasa_names = list(_annual_dhasa_dict.keys())
_annual_dhasa_tab_count = sum(v[0] for k,v in _annual_dhasa_dict.items())
_DB_LABEL_MAX = 4
""" NOTE: !!!! THIS UI ASSUMES COMPATIBILITY IS THE LAST TAB !!!! """
_other_names = ['ashtaka_varga_str','argala_str','shodhaya_pinda_str','yoga_str','dosha_str',
                'prediction_str','compatibility_str']
_tab_names = ['panchangam_str'] + ['bhaava_str'] + ['pancha_pakshi_sastra_str']+['raasi_str'] + _bala_names + _graha_dhasa_names + _rasi_dhasa_names + \
            _annual_dhasa_names + _other_names
_pancha_pakshi_sastra_font_size = 7.5
_tabcount_before_chart_tab = 3
_chart_tab_end = 1 +_tabcount_before_chart_tab

_kpinfo_tab_start = _chart_tab_end
_kpinfo_tab_count = 1
_kpinfo_tab_end = _kpinfo_tab_start + _kpinfo_tab_count-1
_kpinfo_label_font_size = 6

_chakra_tab_start = _kpinfo_tab_end + 1
_chakra_tab_count = 1
_chakra_tab_end = _chakra_tab_start+_chakra_tab_count-1
_chakra_label_font_size = 6
_available_chakras = ['kota','kaala','sarvatobadra','surya_kalanala','chandra_kalanala','shoola','tripataki',
                      'saptha_shalaka','pancha_shalaka','saptha_nadi']
_EXCLUDE_SAPTHA_NADI_CHARA = True
if _EXCLUDE_SAPTHA_NADI_CHARA: _available_chakras.remove('saptha_nadi')

_amsa_ruler_tab_start = _chakra_tab_end + 1
_amsa_ruler_tab_count = 1
_amsa_ruler_tab_end = _amsa_ruler_tab_start + _amsa_ruler_tab_count - 1
_amsa_ruler_table_font_size = 10
_amsa_include_upagraha = True; _amsa_include_special_lagna=True;_amsa_include_sphuta=True

_sphuta_tab_start = _amsa_ruler_tab_end + 1
_sphuta_tab_count = 1#6#1
_sphuta_tab_end = _sphuta_tab_start + _sphuta_tab_count - 1
_sphuta_table_font_size= 9#7

_saham_tab_start = _sphuta_tab_end + 1
_saham_tab_count = 1
_saham_tab_end = _saham_tab_start + _saham_tab_count - 1

_drishti_tab_start = _saham_tab_end + 1
_drishti_tab_count = 1
_drishti_tab_end = _drishti_tab_start + _drishti_tab_count - 1

_graha_arudha_tab_start = _drishti_tab_end + 1#_drishti_tab_start+1
_graha_arudha_tab_count = 1#6
_graha_arudha_tab_end = _graha_arudha_tab_start + _graha_arudha_tab_count - 1
_arudha_table_font_size= 9#8
_bhava_arudha_list = const._bhava_arudha_list
_vimsopaka_bala_tab_start = _graha_arudha_tab_end + 1 
_vimsopaka_bala_tab_count = 1
_vimsopaka_bala_tab_end = _vimsopaka_bala_tab_start + _vimsopaka_bala_tab_count - 1
_vimsopaka_bala_table_font_size = 8#6

_vaiseshikamsa_bala_tab_start = _vimsopaka_bala_tab_end + 1 
_vaiseshikamsa_bala_tab_count = 1
_vaiseshikamsa_bala_tab_end = _vaiseshikamsa_bala_tab_start + _vaiseshikamsa_bala_tab_count - 1
_vaiseshikamsa_bala_table_font_size = 8#6

_other_bala_tab_start = _vaiseshikamsa_bala_tab_end + 1 
_other_bala_tab_count = 1
_other_bala_tab_end = _other_bala_tab_start + _other_bala_tab_count - 1
_other_bala_table_font_size = 12#8

_shad_bala_tab_start = _other_bala_tab_end + 1 
_shad_bala_tab_count = 1
_shad_bala_tab_end = _shad_bala_tab_start + _shad_bala_tab_count - 1
_shad_bala_table_font_size = 12

_bhava_bala_tab_start = _shad_bala_tab_end + 1 
_bhava_bala_tab_count = 1
_bhava_bala_tab_end = _bhava_bala_tab_start + _bhava_bala_tab_count - 1
_bhava_bala_table_font_size = 12
_ashtaka_varga_tab_start = _bhava_bala_tab_end+1#_dhasa_bhukthi_tab_index  + 1
""" 8 BAV/PAV-Raasi for each planet and Asc. One SAV-D1/SAV-D9. 8 BAV/PAV-D9 for each planet"""
_ashtaka_varga_tab_count = 1 # len(_chart_names)# len(_tab_names[_tabcount_before_chart_tab:_chart_tab_end])#_vimsottari_dhasa_tab_start]) #+1 # +1 for shodhaya tables
_ashtaka_varga_tab_end = _ashtaka_varga_tab_start + _ashtaka_varga_tab_count - 1
ashtaka_chart_title_font_size = 8

_argala_tab_start = _ashtaka_varga_tab_end + 1
_argala_tab_count = 1
_argala_tab_end = _argala_tab_start + _argala_tab_count - 1
_argala_table_font_size = 10#6.5

_shodhaya_tab_start  = _argala_tab_end + 1
_shodhaya_tab_count = 1#2 # one for Raasi and another for Navamsam
_shodhaya_dict = {0:'raasi_str',7:'navamsam_str'} #2 and 7 are horoscope chart counters
_shodhaya_tab_end = _shodhaya_tab_start + _shodhaya_tab_count - 1
_dhasa_bhukthi_tab_index = _shodhaya_tab_end + 1

_yoga_tab_start = _dhasa_bhukthi_tab_index + 1
_yoga_tab_count = 1
_yoga_tab_end = _yoga_tab_start + _yoga_tab_count - 1

_dosha_tab_start = _yoga_tab_end + 1
_dosha_tab_count = 1
_dosha_tab_end = _dosha_tab_start + _dosha_tab_count - 1

_prediction_tab_start = _dosha_tab_end + 1 
_compatibility_tab_start = _prediction_tab_start + 1 
_tab_count = len(_tab_names)

available_chart_types = {
    'south_indian': SouthIndianChart,
    'north_indian': NorthIndianChart,
    'east_indian': EastIndianChart,
    'western': WesternChart,
    'sudarsana_chakra': SudarsanaChakraChart,
}
available_languages = const.available_languages

# ---------------------------------------------------------------------------
# Delegate classes
# ---------------------------------------------------------------------------
class AlignDelegate(QStyledItemDelegate):
    """Center-aligns text within table cells."""

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignmentFlag.AlignHCenter
class GrowingTextEdit(QTextEdit):
    """Text edit that grows vertically to fit its contents."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.document().contentsChanged.connect(self.sizeChange)

        self.heightMin = 0
        self.heightMax = 65000

    def sizeChange(self) -> None:
        doc_height = int(self.document().size().height())
        if self.heightMin <= doc_height <= self.heightMax:
            self.setMinimumHeight(doc_height)


# ---------------------------------------------------------------------------
# Main application widget
# ---------------------------------------------------------------------------
class ChartTabbed(QWidget):
    """Main widget that hosts all horoscope related tabs."""

    def __init__(
        self,
        chart_type: str = "south_indian",
        show_marriage_compatibility: bool = True,
        calculation_type: str = "drik",
        language: str = "English",
        date_of_birth: str | None = None,
        time_of_birth: str | None = None,
        place_of_birth: tuple | None = None,
        gender: int = 0,
        use_world_city_database: bool = const.check_database_for_world_cities,
        use_internet_for_location_check: bool = const.use_internet_for_location_check,
    ) -> None:
        """Initialize the tabbed horoscope widget."""

        super().__init__()
        self._initialize_state(
            chart_type,
            show_marriage_compatibility,
            calculation_type,
            language,
            place_of_birth,
            use_world_city_database,
            use_internet_for_location_check,
        )

        self._build_ui()
        self._populate_defaults(date_of_birth, time_of_birth, gender)

    # ------------------------------------------------------------------
    # Initialization helpers
    # ------------------------------------------------------------------
    def _initialize_state(
        self,
        chart_type: str,
        show_marriage_compatibility: bool,
        calculation_type: str,
        language: str,
        place_of_birth,
        use_world_city_database: bool,
        use_internet_for_location_check: bool,
    ) -> None:
        """Set up instance variables and global settings."""

        self._horo = None
        self.use_world_city_database = use_world_city_database
        self.use_internet_for_location_check = use_internet_for_location_check
        self._chart_type = (
            chart_type if chart_type.lower() in const.available_chart_types else "south_indian"
        )
        self._language = language
        utils.set_language(available_languages[language])
        utils.use_database_for_world_cities(use_world_city_database)
        self.resources = utils.resource_strings
        self._place_name = place_of_birth
        self._bhava_chart_type = chart_type
        self._calculation_type = calculation_type
        self._show_compatibility = show_marriage_compatibility

        self._conjunction_dialog_accepted = False
        self._conj_planet1 = ""
        self._conj_planet2 = ""
        self._raasi = ""
        self._lunar_month_type = ""
        self._separation_angle_list: list = []
        self._separation_angle_index = 0

    def _build_ui(self) -> None:
        """Construct all UI widgets."""

        self._init_main_window()
        self._v_layout = QVBoxLayout()
        self._create_row1_ui()
        self._create_row_2_and_3_ui()
        if self._show_compatibility:
            self._create_comp_ui()
        self._init_tab_widget_ui()

    def _populate_defaults(self, date_of_birth: str | None, time_of_birth: str | None, gender: int) -> None:
        """Populate initial values and compute julian day."""

        current_date_str, current_time_str = datetime.now().strftime("%Y,%m,%d;%H:%M:%S").split(";")
        if date_of_birth is None:
            self.date_of_birth(current_date_str)
        if time_of_birth is None:
            self.time_of_birth(current_time_str)

        if not self._validate_ui() and self.use_internet_for_location_check:
            loc = utils.get_place_from_user_ip_address()
            if len(loc) == 4:
                self.place(loc[0], loc[1], loc[2], loc[3])

        if gender is None or gender not in [0, 1, 2, 3]:
            self.gender(0)
        else:
            self.gender(gender)

        year, month, day = self._dob_text.text().split(",")
        dob = (int(year), int(month), int(day))
        tob = tuple(int(x) for x in self._tob_text.text().split(":"))
        self._birth_julian_day = utils.julian_day_number(dob, tob)

    def _hide_2nd_row_widgets(self,show=True):
            self._dob_label.setVisible(show)
            self._dob_text.setVisible(show)
            self._tob_label.setVisible(show)
            self._tob_text.setVisible(show)
            self._years_label.setVisible(show);self._months_label.setVisible(show);self._60hrs_label.setVisible(show)
            self._years_combo.setVisible(show); self._months_combo.setVisible(show); self._60hrs_combo.setVisible(show)
            self._chart_type_combo.setVisible(show)
            self._ayanamsa_combo.setVisible(show)
    def _process_tab_changed(self):
        _current_tab_index = self.tabWidget.currentIndex()
        self._show_hide_marriage_checkboxes(False)
        if _current_tab_index == _compatibility_tab_start :
            self._show_hide_marriage_checkboxes(True)
        elif _current_tab_index > _bhava_bala_tab_end:
            self._hide_2nd_row_widgets(False)
        else:
            self._hide_2nd_row_widgets(True)
            self._show_hide_marriage_checkboxes(False)
    def _init_tab_widget_ui(self):
        self._western_chart = False
        if 'west' in self._chart_type.lower():
            self._western_chart = True
            self.tabNames = _tab_names[:_chart_tab_end]
        elif self._show_compatibility:
            self.tabNames = _tab_names
        else:
            self.tabNames = _tab_names[:-1]
        self.tabWidget = QTabWidget()
        self.tabWidget.currentChanged.connect(self._process_tab_changed)
        self._v_layout.addWidget(self.tabWidget)
        self.tabCount = len(self.tabNames)
        self.horo_tabs = []
        self._kundali_charts = [] ; self._bhava_chart = None
        self._ashtaka_charts = []
        self._drishti_table1 = None
        self._drishti_table2 = None
        self._saham_table1 = None
        self._saham_table2 = None
        self._argala_table1 = None
        self._argala_table2 = None
        self._shad_bala_table = []
        self._bhava_bala_table = []
        self._shodhaya_table1 = []
        self._shodhaya_table_label1=[]
        self._shodhaya_table2 = []
        self._shodhaya_table_label2=[]
        self._chart_info_label1 = QLabel('');self._chart_info_label2 = QLabel('')
        self.match_tables = [[ QTableWidget(13,4) for _ in range(2)] for _ in range(10)]
        self.vimsottari_db_tables =  []
        self._matching_star_list = QListWidget()
        self._yoga_list = QListWidget()
        self._yoga_text = QTextEdit()
        self._yoga_text.setReadOnly(True)# setDisabled(True)
        self._dosha_list = QListWidget()
        self._dosha_text = QTextEdit()
        self._dosha_text.setReadOnly(True)# setDisabled(True)
        self._prediction_list = QListWidget()
        self._prediction_text = QTextEdit()#GrowingTextEdit()
        self._prediction_text.setReadOnly(True)# setDisabled(True)
        t = 0
        self._init_panchanga_tab_widgets(t)
        t+=1
        self._init_bhaava_tab_widgets(t)
        t+=1
        self._init_pps_tab_widgets(t)
        t+=1
        self._init_chart_tab_widgets(t)
        t += 1 #len(_chart_names)
        if not self._western_chart or 'west' not in self._chart_type.lower():
            self._init_kpinfo_tab_widgets(t)
            t+= _kpinfo_tab_count
            self._init_chakra_tab_widgets(t)
            t+= _chakra_tab_count
            self._init_amsa_ruler_tab_widgets(t)
            t += _amsa_ruler_tab_count
            self._init_sphuta_tab_widgets(t)
            t += _sphuta_tab_count
            self._init_saham_tab_widgets(t)
            t += _saham_tab_count
            self._init_drishti_tab_widgets(t)
            t += _drishti_tab_count
            self._init_graha_arudha_tab_widgets(t)
            t += _graha_arudha_tab_count
            self._init_vimsopaka_bala_tab_widgets(t)
            t += _vimsopaka_bala_tab_count
            self._init_vaiseshikamsa_bala_tab_widgets(t)
            t += _vaiseshikamsa_bala_tab_count
            self._init_other_bala_tab_widgets(t)
            t += _other_bala_tab_count
            self._init_shad_bala_tab_widgets(t)
            t += _shad_bala_tab_count
            self._init_bhava_bala_tab_widgets(t)
            t += _bhava_bala_tab_count
            self._init_ashtaka_tab_widgets(t)
            t += 1
            self._init_argala_tab_widgets(t)
            t += _argala_tab_count
            self._init_shodhaya_tab_widgets(t)
            t += _shodhaya_tab_count
            self._init_dhasa_tab_widgets_new(t)
            t += 1
            self._init_yoga_tab_widgets(t)
            t += _yoga_tab_count
            self._init_dosha_tab_widgets(t)
            t += _dosha_tab_count
            self._init_prediction_tab_widgets(t); t += 1
            if self._show_compatibility and t==_compatibility_tab_start:
                self._init_compatibility_tab_widgets(t)
                t += 1
        self.tabCount = self.tabWidget.count()
        self._add_footer_to_chart()
        self.setLayout(self._v_layout)        
        self._show_hide_marriage_checkboxes(False)
    def _init_pps_tab_widgets(self, tab_index):
        v_layout = QVBoxLayout()
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],'')
        self._pps_tree = pancha_pakshi_sastra_widget.PanchaPakshiSastraWidget(synch_with_local_clock=True)
        v_layout.addWidget(self._pps_tree)
        self.horo_tabs[tab_index].setLayout(v_layout)
    def _init_prediction_tab_widgets(self, tab_index):
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],'')
        h_layout = QHBoxLayout()
        self._prediction_list =QListWidget()
        self._prediction_list.currentRowChanged.connect(self._update_prediction_table)
        self._prediction_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._prediction_list.setMaximumWidth(_prediction_list_box_width)
        h_layout.addWidget(self._prediction_list)
        self._prediction_text = QTextEdit()#GrowingTextEdit()
        self._prediction_text.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self._prediction_text.setStyleSheet('font-size:'+str(_prediction_text_font_size)+'pt')
        h_layout.addWidget(self._prediction_text)
        self.horo_tabs[_prediction_tab_start].setLayout(h_layout)
    def _init_dosha_tab_widgets(self, tab_index):
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],'')
        h_layout = QHBoxLayout()
        self._dosha_list =QListWidget()
        self._dosha_list.currentRowChanged.connect(self._update_dosha_table)
        self._dosha_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._dosha_list.setMaximumWidth(_dosha_list_box_width)
        h_layout.addWidget(self._dosha_list)
        self._dosha_text = QTextEdit()
        self._dosha_text.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self._dosha_text.setStyleSheet('font-size:'+str(_dosha_text_font_size)+'pt')
        h_layout.addWidget(self._dosha_text)
        self.horo_tabs[_dosha_tab_start].setLayout(h_layout)
    def _init_yoga_tab_widgets(self, tab_index):
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],'')
        h_layout = QHBoxLayout()
        self._yoga_list =QListWidget()
        self._yoga_list.currentRowChanged.connect(self._update_yoga_table)
        self._yoga_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._yoga_list.setMaximumWidth(_yoga_list_box_width)
        h_layout.addWidget(self._yoga_list)
        self._yoga_text = QTextEdit()
        self._yoga_text.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self._yoga_text.setStyleSheet('font-size:'+str(_yoga_text_font_size)+'pt')
        h_layout.addWidget(self._yoga_text)
        self.horo_tabs[_yoga_tab_start].setLayout(h_layout)
    def _init_compatibility_tab_widgets(self,tab_index):
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],'')
        h_layout = QHBoxLayout()
        self._matching_star_list = QListWidget()
        self._matching_star_list.currentRowChanged.connect(self._update_compatibility_table)
        self._matching_star_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._matching_star_list.setMaximumWidth(_compatability_list_width)
        h_layout.addWidget(self._matching_star_list)
        self._comp_results_table = []
        for c in range(_comp_results_per_list_item):
            self._comp_results_table.append(QTableWidget(13,4))
            self._comp_results_table[c].setStyleSheet('font-size:'+str(_comp_table_font_size)+'pt')
            self._comp_results_table[c].verticalHeader().hide()
            self._comp_results_table[c].setHorizontalHeaderItem(0,QTableWidgetItem('Porutham/Koota'))
            self._comp_results_table[c].setHorizontalHeaderItem(1,QTableWidgetItem('Score'))
            self._comp_results_table[c].setHorizontalHeaderItem(2,QTableWidgetItem('Max Score'))
            self._comp_results_table[c].setHorizontalHeaderItem(3,QTableWidgetItem('%'))
            self._comp_results_table[c].setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self._comp_results_table[c].setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
            h_layout.addWidget(self._comp_results_table[c])
        self._matching_star_list.setMaximumHeight(self._comp_results_table[0].height())
        self.horo_tabs[_compatibility_tab_start].setLayout(h_layout) 
    def _init_amsa_ruler_tab_widgets(self, tab_index):
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],self.tabNames[tab_index])
        v_layout = QVBoxLayout()
        self._amsa_chart_combo = QComboBox()
        self._amsa_vargas = list(const.amsa_rulers.keys())
        _amsa_ruler_list = [_chart_names[const.division_chart_factors.index(ak)] for ak in self._amsa_vargas[:-1]] + \
                            ['naadiamsha_str']
        self._amsa_chart_combo.addItems(_amsa_ruler_list); self._current_amsa_chart_index = 12
        self._amsa_chart_combo.setCurrentIndex(self._current_amsa_chart_index)
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(self._amsa_chart_combo)        
        self._amsa_chart_option_button = QPushButton('Select Chart Options')
        self._amsa_chart_option_button.clicked.connect(self._show_amsa_chart_options)
        self._amsa_chart_option_button.setEnabled(True)
        h_layout1.addWidget(self._amsa_chart_option_button)
        self._amsa_option_info_label = QLabel('')
        self._amsa_option_info_label.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._amsa_option_info_label.setEnabled(True)
        h_layout1.addWidget(self._amsa_option_info_label)
        v_layout.addLayout(h_layout1)
        planet_count = len(drik.planet_list) + 1
        upagraha_count = len(const._solar_upagraha_list) + len(const._other_upagraha_list)
        special_lagna_count = len(const._special_lagna_list)
        sphuta_count = len(const.sphuta_list)
        self._amsa_ruler_table1 = QTableWidget(planet_count,2)
        self._amsa_ruler_table1.setStyleSheet('font-size:'+str(_amsa_ruler_table_font_size)+'pt')
        self._amsa_ruler_table1.horizontalHeader().setVisible(False); self._amsa_ruler_table1.verticalHeader().setVisible(False)
        self._amsa_ruler_table1.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        delegate = AlignDelegate(self._amsa_ruler_table1)
        self._amsa_ruler_table1.setItemDelegate(delegate)
        self._amsa_ruler_table1.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._amsa_ruler_table1.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self._amsa_ruler_table1)
        if _amsa_include_special_lagna: 
            self._amsa_ruler_table2 = QTableWidget(special_lagna_count,2)
            self._amsa_ruler_table2.setStyleSheet('font-size:'+str(_amsa_ruler_table_font_size)+'pt')
            self._amsa_ruler_table2.horizontalHeader().setVisible(False); self._amsa_ruler_table2.verticalHeader().setVisible(False)
            self._amsa_ruler_table2.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
            delegate = AlignDelegate(self._amsa_ruler_table2)
            self._amsa_ruler_table2.setItemDelegate(delegate)
            self._amsa_ruler_table2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self._amsa_ruler_table2.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            h_layout.addWidget(self._amsa_ruler_table2)
        if _amsa_include_upagraha:
            self._amsa_ruler_table3 = QTableWidget(upagraha_count,2)
            self._amsa_ruler_table3.setStyleSheet('font-size:'+str(_amsa_ruler_table_font_size)+'pt')
            self._amsa_ruler_table3.horizontalHeader().setVisible(False); self._amsa_ruler_table3.verticalHeader().setVisible(False)
            self._amsa_ruler_table3.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
            delegate = AlignDelegate(self._amsa_ruler_table3)
            self._amsa_ruler_table3.setItemDelegate(delegate)
            self._amsa_ruler_table3.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self._amsa_ruler_table3.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            h_layout.addWidget(self._amsa_ruler_table3)
        if _amsa_include_sphuta:
            self._amsa_ruler_table4 = QTableWidget(sphuta_count,2)
            self._amsa_ruler_table4.setStyleSheet('font-size:'+str(_amsa_ruler_table_font_size)+'pt')
            self._amsa_ruler_table4.horizontalHeader().setVisible(False); self._amsa_ruler_table4.verticalHeader().setVisible(False)
            self._amsa_ruler_table4.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
            delegate = AlignDelegate(self._amsa_ruler_table4)
            self._amsa_ruler_table4.setItemDelegate(delegate)
            self._amsa_ruler_table4.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self._amsa_ruler_table4.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            h_layout.addWidget(self._amsa_ruler_table4)
        v_layout.addLayout(h_layout)
        self._amsa_chart_combo.currentIndexChanged.connect(self._amsa_chart_selection_changed)
        self.tabWidget.setTabText(tab_index,'amsa_ruler_str')
        self.horo_tabs[_amsa_ruler_tab_start].setLayout(v_layout) 
        self._amsa_method_index=1
        self._amsa_varga_dict = {k:v for k,v in varga_chart_dialog.get_varga_option_dict().items() if k in self._amsa_vargas}
        self._amsa_varga_dict[150] = self._amsa_varga_dict[60]
    def _show_amsa_chart_options(self):
        self._current_amsa_chart_index = self._amsa_chart_combo.currentIndex()
        self._amsa_option_info_label.setText(self._amsa_chart_options_str)
        varga_index = list(self._amsa_varga_dict.keys())[self._current_amsa_chart_index]
        self._amsa_method_index = self._amsa_varga_dict[varga_index][1]
        if self._current_amsa_chart_index == len(self._amsa_vargas)-1:
            self._amsa_chart_options_str = self.resources['dn_custom_option'+str(self._amsa_method_index)+'_str']
        else:
            self._amsa_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._amsa_method_index)+'_str']
        dlg = varga_chart_dialog.VargaChartOptionsDialog(varga_factor=varga_index,
                                chart_method=self._amsa_method_index,
                                    base_rasi=self._amsa_varga_dict[varga_index][2],
                                    count_from_end_of_sign=self._amsa_varga_dict[varga_index][3])
        if dlg.exec()==1:
            self._amsa_method_index = dlg._method_index    
            if dlg._varga_factor != None: varga_index = dlg._varga_factor 
            self._amsa_varga_dict[varga_index] = (self._amsa_varga_dict[varga_index][0],self._amsa_method_index,
                                                  dlg._base_rasi_index,dlg._count_from_end_of_sign)
            self._update_amsa_ruler_tab_information(self._current_amsa_chart_index,self._amsa_method_index,
                                        divisional_chart_factor=dlg._varga_factor,
                                    base_rasi=self._amsa_varga_dict[varga_index][2],
                                    count_from_end_of_sign=self._amsa_varga_dict[varga_index][3])
        self._amsa_chart_options_str = dlg._option_string
        self._amsa_option_info_label.setText(self._amsa_chart_options_str)
    def _amsa_chart_selection_changed(self):
        self._current_amsa_chart_index = self._amsa_chart_combo.currentIndex()
        varga_index = list(self._amsa_varga_dict.keys())[self._current_amsa_chart_index]
        self._amsa_method_index = self._amsa_varga_dict[varga_index][1]
        if self._current_amsa_chart_index == len(self._amsa_vargas)-1:
            self._amsa_chart_options_str = self.resources['dn_custom_option'+str(self._amsa_method_index)+'_str']
        else:
            self._amsa_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._amsa_method_index)+'_str']
        self._amsa_chart_option_button.setText(self._amsa_chart_combo.currentText()+' '+self.resources['options_str'])
        self._amsa_option_info_label.setText(self._amsa_chart_options_str)
        self._amsa_option_info_label.adjustSize()
        self._update_amsa_ruler_tab_information(self._current_amsa_chart_index,self._amsa_method_index)
        
    def _init_sphuta_tab_widgets(self,tab_index):
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],self.tabNames[tab_index])
        v_layout = QVBoxLayout()
        h_layout1 = QHBoxLayout()
        self._sphuta_chart_combo = QComboBox()
        self._sphuta_chart_combo.addItems(_chart_names)
        self._sphuta_chart_combo.SizeAdjustPolicy.AdjustToContents
        self._sphuta_chart_combo.currentIndexChanged.connect(self._sphuta_chart_selection_changed)
        h_layout1.addWidget(self._sphuta_chart_combo)        
        self._sphuta_chart_option_button = QPushButton('Select Chart Options')
        #self._sphuta_chart_option_button.setFlat(True)
        #self._sphuta_chart_option_button.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._sphuta_chart_option_button.clicked.connect(self._show_sphuta_chart_options)
        self._sphuta_chart_option_button.setEnabled(False)
        h_layout1.addWidget(self._sphuta_chart_option_button)
        self._sphuta_option_info_label = QLabel('')
        self._sphuta_option_info_label.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._sphuta_option_info_label.setEnabled(False)
        #self._sphuta_option_info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        h_layout1.addWidget(self._sphuta_option_info_label)
        self._varnada_option_button = QPushButton('Varnada Options')
        self._varnada_option_button.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._varnada_option_button.clicked.connect(self._show_varnada_options)
        h_layout1.addWidget(self._varnada_option_button)
        self._varnada_option_info_label = QLabel('')
        self._varnada_option_info_label.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        #self._varnada_option_info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        h_layout1.addWidget(self._varnada_option_info_label)
        v_layout.addLayout(h_layout1)
        h_layout1 = QHBoxLayout()
        self._sphuta_table = QTableWidget(len(const.sphuta_list),2)
        self._sphuta_table.setStyleSheet('font-size:'+str(_sphuta_table_font_size)+'pt')
        self._sphuta_table.verticalHeader().setVisible(False)
        self._sphuta_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        h_layout1.addWidget(self._sphuta_table)
        self._varnada_table = QTableWidget(12,2)
        self._varnada_table.setStyleSheet('font-size:'+str(_sphuta_table_font_size)+'pt')
        self._varnada_table.verticalHeader().setVisible(False)
        self._varnada_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        h_layout1.addWidget(self._varnada_table)
        v_layout.addLayout(h_layout1)
        self.horo_tabs[_sphuta_tab_start].setLayout(v_layout) 
        self._current_sphuta_chart_index = 0
        self._sphuta_method_index=1
        self._varnada_method_index = 1
        self._sphuta_varga_dict = varga_chart_dialog.get_varga_option_dict()
        self._varnada_varga_dict ={dcf:1 for dcf in [1]+list(self._sphuta_varga_dict.keys())}
        self._sphuta_custom_varga = _custom_varga_index
        self._sphuta_mixed_dict_1 = self._sphuta_varga_dict
        self._sphuta_mixed_dict_2 = self._sphuta_varga_dict
        self._sphuta_custom_varga = _custom_varga_index
        self._sphuta_mixed_chart_index_1 = _mixed_chart_index_1; self._sphuta_mixed_chart_index_2 = _mixed_chart_index_2
        self._sphuta_mixed_method_index_1 = _mixed_chart_method_1; self._sphuta_mixed_method_index_2 = _mixed_chart_method_2
    def _show_varnada_options(self):
        if self._current_sphuta_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_sphuta_chart_index]
        else:
            varga_index = self._sphuta_custom_varga
        self._varnada_method_index = self._varnada_varga_dict[varga_index]
        self._varnada_option_info_label.setText(_varnada_method_options[self._varnada_method_index-1])
        dlg = options_dialog.OptionDialog(title='Varnada Options',option_label='Select Varnatha Lagna options from',
                     options_list=_varnada_method_options,default_options=self._varnada_method_index-1,
                     multi_selection=False)
        if dlg.exec()==1:
            self._varnada_method_index = dlg._option_index
            self._varnada_varga_dict[varga_index] = dlg._option_index
            if self._current_sphuta_chart_index==_mixed_chart_index:
                self._update_sphuta_tab_information(chart_index=self._current_sphuta_chart_index,
                        varnada_method_index=self._varnada_method_index,
                        chart_index_1=self._sphuta_mixed_chart_index_1,chart_method_1=self._sphuta_mixed_method_index_1,
                        chart_index_2=self._sphuta_mixed_chart_index_2,chart_method_2=self._sphuta_mixed_method_index_2)
            else:
                self._update_sphuta_tab_information(chart_index=self._current_sphuta_chart_index,method_index=self._sphuta_method_index,
                                        varnada_method_index=self._varnada_method_index,divisional_chart_factor=varga_index,
                                        base_rasi=self._sphuta_varga_dict[varga_index][2],
                                        count_from_end_of_sign=self._sphuta_varga_dict[varga_index][3])
        self._varnada_method_index = self._varnada_varga_dict[varga_index]
        self._varnada_option_info_label.setText(_varnada_method_options[self._varnada_method_index-1])
    def _show_sphuta_chart_options(self):
        self._current_sphuta_chart_index = self._sphuta_chart_combo.currentIndex()
        self._sphuta_option_info_label.setText(self._sphuta_chart_options_str)
        if self._current_sphuta_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_sphuta_chart_index]
            self._sphuta_method_index = self._sphuta_varga_dict[varga_index][1]
            self._sphuta_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._sphuta_method_index)+'_str']
        elif self._current_sphuta_chart_index== _custom_chart_index:
            varga_index = self._sphuta_custom_varga
            self._sphuta_method_index = self._sphuta_varga_dict[varga_index][1]
            self._sphuta_chart_options_str = self.resources['dn_custom_option'+str(self._sphuta_method_index)+'_str']
        elif self._current_sphuta_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._sphuta_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._sphuta_mixed_chart_index_2]
            self._sphuta_mixed_method_index_1 = self._sphuta_mixed_dict_1[v1][1]
            self._sphuta_mixed_method_index_2 = self._sphuta_mixed_dict_2[v2][1]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._sphuta_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._sphuta_mixed_method_index_2)+'_str']
            self._sphuta_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
        if self._current_sphuta_chart_index<=_custom_chart_index:
            dlg = varga_chart_dialog.VargaChartOptionsDialog(chart_index=self._current_sphuta_chart_index,
                                    chart_method=self._sphuta_method_index,varga_factor=varga_index,
                                        base_rasi=self._sphuta_varga_dict[varga_index][2],
                                        count_from_end_of_sign=self._sphuta_varga_dict[varga_index][3])
            if dlg.exec()==1:
                self._sphuta_method_index = dlg._method_index
                if dlg._varga_factor != None: varga_index = dlg._varga_factor
                if self._current_sphuta_chart_index==_custom_chart_index: self._sphuta_custom_varga = varga_index
                self._sphuta_varga_dict[varga_index] = \
                    (self._sphuta_varga_dict[varga_index][0],dlg._method_index,
                        dlg._base_rasi_index,dlg._count_from_end_of_sign)
                self._update_sphuta_tab_information(chart_index=self._current_sphuta_chart_index,
                            method_index=self._sphuta_method_index,varnada_method_index=self._varnada_method_index,
                            divisional_chart_factor=varga_index,base_rasi=self._sphuta_varga_dict[varga_index][2],
                            count_from_end_of_sign=self._sphuta_varga_dict[varga_index][3])
            self._sphuta_chart_options_str = dlg._option_string
            self._sphuta_option_info_label.setText(self._sphuta_chart_options_str)
        elif self._current_sphuta_chart_index==_mixed_chart_index:
            v1 = const.division_chart_factors[self._sphuta_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._sphuta_mixed_chart_index_2]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._sphuta_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._sphuta_mixed_method_index_2)+'_str']
            self._sphuta_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._sphuta_option_info_label.setText(self._sphuta_chart_options_str)
            dlg = mixed_chart_dialog.MixedChartOptionsDialog(chart_index_1=self._sphuta_mixed_chart_index_1,chart_index_2=self._sphuta_mixed_chart_index_2,
                                                 chart_method_1=self._sphuta_mixed_method_index_1,chart_method_2=self._sphuta_mixed_method_index_2)
            if dlg.exec()==1:
                self._sphuta_mixed_chart_index_1 = dlg._chart_index_1;self._sphuta_mixed_chart_index_2 = dlg._chart_index_2
                self._sphuta_mixed_method_index_1 = dlg._method_index_1;self._sphuta_mixed_method_index_2 = dlg._method_index_2
                v1 = dlg._varga_factor_1; v2 = dlg._varga_factor_2
                v1s = self.resources['d'+str(v1)+'_option'+str(self._sphuta_mixed_method_index_1)+'_str']
                v2s = self.resources['d'+str(v2)+'_option'+str(self._sphuta_mixed_method_index_2)+'_str']
                self._sphuta_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
                self._sphuta_option_info_label.setText(self._sphuta_chart_options_str)
                mds = 'D'+str(v1)+'xD'+ str(v2)+' '
                self._sphuta_chart_option_button.setText(mds+self.resources['options_str'])
                self._update_sphuta_tab_information(chart_index=self._current_sphuta_chart_index,
                                                varnada_method_index=self._varnada_method_index,
                                                chart_index_1=dlg._chart_index_1,chart_method_1=dlg._method_index_1,
                                                chart_index_2=dlg._chart_index_2,chart_method_2=dlg._method_index_2)
    def _sphuta_chart_selection_changed(self):
        self._current_sphuta_chart_index = self._sphuta_chart_combo.currentIndex()
        if self._current_sphuta_chart_index==0:
            varga_index = 1
            self._sphuta_method_index = 1
            self._sphuta_chart_options_str = ''
        elif self._current_sphuta_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_sphuta_chart_index]
            self._sphuta_method_index = self._sphuta_varga_dict[varga_index][1]
            self._sphuta_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._sphuta_method_index)+'_str']
        elif self._current_sphuta_chart_index == _custom_chart_index:
            varga_index = self._sphuta_custom_varga
            self._sphuta_method_index = self._sphuta_varga_dict[varga_index][1]
            self._sphuta_chart_options_str = self.resources['dn_custom_option'+str(self._sphuta_method_index)+'_str']
        elif self._current_sphuta_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._sphuta_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._sphuta_mixed_chart_index_2]
            mds = 'D'+str(v1)+'('+str(self._sphuta_mixed_method_index_1)+')xD'+ \
                    str(v2)+'('+str(self._sphuta_mixed_method_index_2)+')'+' '
            v1s = self.resources['d'+str(v1)+'_option'+str(self._sphuta_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._sphuta_mixed_method_index_2)+'_str']
            self._sphuta_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._sphuta_option_info_label.setText(self._sphuta_chart_options_str)
        self._sphuta_option_info_label.setText(self._sphuta_chart_options_str)
        self._sphuta_option_info_label.adjustSize()
        if self._current_sphuta_chart_index==0:
            self._sphuta_chart_option_button.setEnabled(False);self._sphuta_chart_option_button.setVisible(False)
            self._sphuta_option_info_label.setEnabled(False);self._sphuta_option_info_label.setVisible(False)
        else:
            self._sphuta_chart_option_button.setEnabled(True);self._sphuta_chart_option_button.setVisible(True)
            self._sphuta_option_info_label.setEnabled(True);self._sphuta_option_info_label.setVisible(True)
        if self._current_sphuta_chart_index==_mixed_chart_index:
            mds = 'D'+str(v1)+'xD'+ str(v2)+' '
            self._sphuta_chart_option_button.setText(mds+self.resources['options_str'])
            self._update_sphuta_tab_information(chart_index=self._current_sphuta_chart_index,
                        varnada_method_index=self._varnada_method_index,
                        chart_index_1=self._sphuta_mixed_chart_index_1,chart_method_1=self._sphuta_mixed_method_index_1,
                        chart_index_2=self._sphuta_mixed_chart_index_2,chart_method_2=self._sphuta_mixed_method_index_2)
        else:
            self._sphuta_chart_option_button.setText(self._sphuta_chart_combo.currentText()+' '+self.resources['options_str'])
            if self._current_sphuta_chart_index==_custom_chart_index:
                self._sphuta_chart_option_button.setText('D'+str(varga_index)+' '+self.resources['options_str'])
            self._update_sphuta_tab_information(chart_index=self._current_sphuta_chart_index,method_index=self._sphuta_method_index,
                                    varnada_method_index=self._varnada_method_index,divisional_chart_factor=varga_index,
                                    base_rasi=self._sphuta_varga_dict[varga_index][2],
                                    count_from_end_of_sign=self._sphuta_varga_dict[varga_index][3])
    def _init_graha_arudha_tab_widgets(self,tab_index):
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],self.tabNames[tab_index])
        v_layout = QVBoxLayout()
        h_layout1 = QHBoxLayout()
        self._arudha_chart_combo = QComboBox()
        self._arudha_chart_combo.addItems(_chart_names)
        self._arudha_chart_combo.SizeAdjustPolicy.AdjustToContents
        self._arudha_chart_combo.currentIndexChanged.connect(self._graha_arudha_chart_selection_changed)
        h_layout1.addWidget(self._arudha_chart_combo)        
        self._arudha_chart_option_button = QPushButton('Select Chart Options')
        #self._arudha_chart_option_button.setFlat(True)
        #self._arudha_chart_option_button.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._arudha_chart_option_button.clicked.connect(self._show_arudha_chart_options)
        self._arudha_chart_option_button.setEnabled(False)
        h_layout1.addWidget(self._arudha_chart_option_button)
        self._arudha_option_info_label = QLabel('')
        self._arudha_option_info_label.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._arudha_option_info_label.setEnabled(False)
        self._arudha_option_info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        h_layout1.addWidget(self._arudha_option_info_label)
        v_layout.addLayout(h_layout1)
        h_layout1 = QHBoxLayout()
        self._bhava_arudha_label1 = QLabel('')
        h_layout1.addWidget(self._bhava_arudha_label1)
        self._bhava_arudha_combo = QComboBox()
        self._bhava_arudha_combo.addItems(_bhava_arudha_list)
        self._bhava_arudha_combo.currentIndexChanged.connect(self._graha_arudha_chart_selection_changed)
        h_layout1.addWidget(self._bhava_arudha_combo)
        self._bhava_arudha_label2 = QLabel('')
        h_layout1.addWidget(self._bhava_arudha_label2)
        v_layout.addLayout(h_layout1)
        h_layout1 = QHBoxLayout()
        self._graha_arudha_table = QTableWidget(10,2)
        self._graha_arudha_table.setStyleSheet('font-size:'+str(_arudha_table_font_size)+'pt')
        self._graha_arudha_table.horizontalHeader().setVisible(False); self._graha_arudha_table.verticalHeader().setVisible(False)
        h_layout1.addWidget(self._graha_arudha_table)
        self._bhava_arudha_table = QTableWidget(12,2)
        self._bhava_arudha_table.setStyleSheet('font-size:'+str(_arudha_table_font_size)+'pt')
        self._bhava_arudha_table.horizontalHeader().setVisible(False); self._bhava_arudha_table.verticalHeader().setVisible(False)
        h_layout1.addWidget(self._bhava_arudha_table)
        v_layout.addLayout(h_layout1)
        self.horo_tabs[_graha_arudha_tab_start].setLayout(v_layout) 
        self._arudha_method_index=1
        self._arudha_varga_dict = varga_chart_dialog.get_varga_option_dict()
        self._arudha_mixed_dict_1 = self._arudha_varga_dict
        self._arudha_mixed_dict_2 = self._arudha_varga_dict
        self._arudha_custom_varga = _custom_varga_index
        self._arudha_mixed_chart_index_1 = _mixed_chart_index_1; self._arudha_mixed_chart_index_2 = _mixed_chart_index_2
        self._arudha_mixed_method_index_1 = _mixed_chart_method_1; self._arudha_mixed_method_index_2 = _mixed_chart_method_2
    def _show_arudha_chart_options(self):
        self._current_arudha_chart_index = self._arudha_chart_combo.currentIndex()
        self._arudha_option_info_label.setText(self._arudha_chart_options_str)
        if self._current_arudha_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_arudha_chart_index]
            self._arudha_method_index = self._arudha_varga_dict[varga_index][1]
            self._arudha_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._arudha_method_index)+'_str']
        elif self._current_arudha_chart_index== _custom_chart_index:
            varga_index = self._arudha_custom_varga
            self._arudha_method_index = self._arudha_varga_dict[varga_index][1]
            self._arudha_chart_options_str = self.resources['dn_custom_option'+str(self._arudha_method_index)+'_str']
        elif self._current_arudha_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._arudha_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._arudha_mixed_chart_index_2]
            self._arudha_mixed_method_index_1 = self._arudha_mixed_dict_1[v1][1]
            self._arudha_mixed_method_index_2 = self._arudha_mixed_dict_2[v2][1]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._arudha_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._arudha_mixed_method_index_2)+'_str']
            self._arudha_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
        if self._current_arudha_chart_index<=_custom_chart_index:
            dlg = varga_chart_dialog.VargaChartOptionsDialog(chart_index=self._current_arudha_chart_index,
                                    chart_method=self._arudha_method_index,varga_factor=varga_index,
                                        base_rasi=self._arudha_varga_dict[self._arudha_custom_varga][2],
                                        count_from_end_of_sign=self._arudha_varga_dict[self._arudha_custom_varga][3])
            if dlg.exec()==1:
                self._arudha_method_index = dlg._method_index
                if dlg._varga_factor != None: varga_index = dlg._varga_factor         
                if self._current_arudha_chart_index==_custom_chart_index: self._arudha_custom_varga = varga_index
                self._arudha_varga_dict[varga_index] = \
                    (self._arudha_varga_dict[varga_index][0],dlg._method_index,
                        dlg._base_rasi_index,dlg._count_from_end_of_sign)
                self._update_graha_arudha_tab_information(self._current_arudha_chart_index,self._arudha_method_index,
                                        divisional_chart_factor=varga_index,
                                        base_rasi=self._arudha_varga_dict[varga_index][2],
                                        count_from_end_of_sign=self._arudha_varga_dict[varga_index][3])
            self._arudha_chart_options_str = dlg._option_string
            self._arudha_option_info_label.setText(self._arudha_chart_options_str)
        elif self._current_arudha_chart_index==_mixed_chart_index:
            v1 = const.division_chart_factors[self._arudha_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._arudha_mixed_chart_index_2]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._arudha_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._arudha_mixed_method_index_2)+'_str']
            self._arudha_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._arudha_option_info_label.setText(self._arudha_chart_options_str)
            dlg = mixed_chart_dialog.MixedChartOptionsDialog(chart_index_1=self._arudha_mixed_chart_index_1,chart_index_2=self._arudha_mixed_chart_index_2,
                                                 chart_method_1=self._arudha_mixed_method_index_1,chart_method_2=self._arudha_mixed_method_index_2)
            if dlg.exec()==1:
                self._arudha_mixed_chart_index_1 = dlg._chart_index_1;self._arudha_mixed_chart_index_2 = dlg._chart_index_2
                self._arudha_mixed_method_index_1 = dlg._method_index_1;self._arudha_mixed_method_index_2 = dlg._method_index_2
                v1 = dlg._varga_factor_1; v2 = dlg._varga_factor_2
                v1s = self.resources['d'+str(v1)+'_option'+str(self._arudha_mixed_method_index_1)+'_str']
                v2s = self.resources['d'+str(v2)+'_option'+str(self._arudha_mixed_method_index_2)+'_str']
                self._arudha_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
                self._arudha_option_info_label.setText(self._arudha_chart_options_str)
                mds = 'D'+str(v1)+'xD'+ str(v2)+' '
                self._arudha_chart_option_button.setText(mds+self.resources['options_str'])
                self._update_graha_arudha_tab_information(chart_index=self._current_arudha_chart_index,
                                                   chart_index_1=dlg._chart_index_1,chart_method_1=dlg._method_index_1,
                                                   chart_index_2=dlg._chart_index_2,chart_method_2=dlg._method_index_2)
    def _graha_arudha_chart_selection_changed(self):
        self._current_arudha_chart_index = self._arudha_chart_combo.currentIndex()
        if self._current_arudha_chart_index==0:
            varga_index = 1
            self._arudha_method_index = 1
            self._arudha_chart_options_str = ''
        elif self._current_arudha_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_arudha_chart_index]
            self._arudha_method_index = self._arudha_varga_dict[varga_index][1]
            self._arudha_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._arudha_method_index)+'_str']
        elif self._current_arudha_chart_index == _custom_chart_index:
            varga_index = self._arudha_custom_varga
            self._arudha_method_index = self._arudha_varga_dict[varga_index][1]
            self._arudha_chart_options_str = self.resources['dn_custom_option'+str(self._arudha_method_index)+'_str']
        elif self._current_arudha_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._arudha_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._arudha_mixed_chart_index_2]
            mds = 'D'+str(v1)+'('+str(self._arudha_mixed_method_index_1)+')xD'+ \
                    str(v2)+'('+str(self._arudha_mixed_method_index_2)+')'+' '
            v1s = self.resources['d'+str(v1)+'_option'+str(self._arudha_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._arudha_mixed_method_index_2)+'_str']
            self._arudha_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._arudha_option_info_label.setText(self._arudha_chart_options_str)
        self._arudha_option_info_label.setText(self._arudha_chart_options_str)
        self._arudha_option_info_label.adjustSize()
        if self._current_arudha_chart_index==0:
            self._arudha_chart_option_button.setEnabled(False);self._arudha_chart_option_button.setVisible(False)
            self._arudha_option_info_label.setEnabled(False);self._arudha_option_info_label.setVisible(False)
        else:
            self._arudha_chart_option_button.setEnabled(True);self._arudha_chart_option_button.setVisible(True)
            self._arudha_option_info_label.setEnabled(True);self._arudha_option_info_label.setVisible(True)
        if self._current_arudha_chart_index==_mixed_chart_index:
            mds = 'D'+str(v1)+'xD'+ str(v2)+' '
            self._arudha_chart_option_button.setText(mds+self.resources['options_str'])
            self._update_graha_arudha_tab_information(chart_index=self._current_arudha_chart_index,
                                chart_index_1=self._arudha_mixed_chart_index_1,chart_method_1=self._arudha_mixed_method_index_1,
                                chart_index_2=self._arudha_mixed_chart_index_2,chart_method_2=self._arudha_mixed_method_index_2)
        else:
            self._arudha_chart_option_button.setText(self._arudha_chart_combo.currentText()+' '+self.resources['options_str'])
            if self._current_arudha_chart_index==_custom_chart_index:
                self._arudha_chart_option_button.setText('D'+str(varga_index)+' '+self.resources['options_str'])
            self._update_graha_arudha_tab_information(self._current_arudha_chart_index,self._arudha_method_index,
                                    divisional_chart_factor=varga_index,
                                    base_rasi=self._arudha_varga_dict[varga_index][2],
                                    count_from_end_of_sign=self._arudha_varga_dict[varga_index][3])
    def _init_vimsopaka_bala_tab_widgets(self,tab_index):
        self._vimsopaka_bala_rows_per_table = 9
        self._vimsopaka_bala_cols_per_table = 1
        self._vimsopaka_bala_tables_per_tab = 4
        self.vimsopaka_bala_db_tables = self._init_dhasa_tab_widgets(tab_index, self._vimsopaka_bala_tables_per_tab, self._vimsopaka_bala_rows_per_table, 
                                            self._vimsopaka_bala_cols_per_table, _vimsopaka_bala_tab_start, _vimsopaka_bala_tab_count, 
                                            'vimsopaka_bala_str', _vimsopaka_bala_table_font_size)
        return
    def _init_vaiseshikamsa_bala_tab_widgets(self,tab_index):
        self._vaiseshikamsa_bala_rows_per_table = 9
        self._vaiseshikamsa_bala_cols_per_table = 1
        self._vaiseshikamsa_bala_tables_per_tab = 4
        self.vaiseshikamsa_bala_db_tables = self._init_dhasa_tab_widgets(tab_index, self._vaiseshikamsa_bala_tables_per_tab, self._vaiseshikamsa_bala_rows_per_table, 
                                            self._vaiseshikamsa_bala_cols_per_table, _vaiseshikamsa_bala_tab_start, _vaiseshikamsa_bala_tab_count, 
                                            'vaiseshikamsa_bala_str', _vaiseshikamsa_bala_table_font_size)
        return
    def _init_other_bala_tab_widgets(self,tab_index):
        self._other_bala_rows_per_table = 7
        self._other_bala_cols_per_table = 1
        self._other_bala_tables_per_tab = 3
        self.other_bala_db_tables = self._init_dhasa_tab_widgets(tab_index, self._other_bala_tables_per_tab, self._other_bala_rows_per_table, 
                                            self._other_bala_cols_per_table, _other_bala_tab_start, _other_bala_tab_count, 
                                            'harsha_pancha_dwadhasa_vargeeya_bala_str', _other_bala_table_font_size)
        return
    def _init_dhasa_tab_widgets_new(self,tab_index):
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],'dhasa_bhukthi_str')
        self.tabCount += 1
        self._db_labels = []
        v_layout = QVBoxLayout()
        h_layout1 = QHBoxLayout()
        self._dhasa_type_combo = QComboBox()
        self._dhasa_type_combo.activated.connect(self._dhasa_type_selection_changed)
        h_layout1.addWidget(self._dhasa_type_combo)
        self._dhasa_combo = QComboBox()
        self._dhasa_combo.activated.connect(self._dhasa_type_selection_changed)
        self._current_dhasa_index = 0
        self._dhasa_varga_combo = QComboBox()
        self._dhasa_varga_combo.activated.connect(self._dhasa_type_selection_changed)
        h_layout1.addWidget(self._dhasa_combo)
        h_layout1.addWidget(self._dhasa_varga_combo)
        self._dhasa_varga_combo.setVisible(False)
        self._dhasa_options_button = QPushButton('Select Dhasa Options')
        self._dhasa_options_button.setFlat(False)
        self._dhasa_options_button.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._dhasa_options_button.clicked.connect(self._show_dhasa_options)
        self._dhasa_bhukthi_options_str = ['' for _ in range(len(_graha_dhasa_dict))]
        self._dhasa_options_button.setVisible(True)
        self._dhasa_options_list = const.dhasa_default_options
        h_layout1.addWidget(self._dhasa_options_button)
        v_layout.addLayout(h_layout1)
        self._dhasa_option_info_label = QLabel('')
        v_layout.addWidget(self._dhasa_option_info_label)
        self._dhasa_option_info_label.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._dhasa_type_selection_changed()
        h_layout2 = QHBoxLayout()
        for t in range(_DB_LABEL_MAX):
            self._db_labels.append(QLabel('', alignment=Qt.AlignmentFlag.AlignTop))
            h_layout2.addWidget(self._db_labels[t])
        v_layout.addLayout(h_layout2)
        self.horo_tabs[tab_index].setLayout(v_layout)
        self.tabWidget.setTabText(tab_index,'dhasa_bhukthi_str')
    def _dhasa_type_selection_changed(self):
        self._current_dhasa_type_index = self._dhasa_type_combo.currentIndex()
        self._current_dhasa_index = self._dhasa_combo.currentIndex()
        self._current_dhasa_varga_index = self._dhasa_varga_combo.currentIndex()
        self._dhasa_option_info_label.setText(self._dhasa_bhukthi_options_str[self._current_dhasa_index]) #RESET option status
        if self.resources != None:
            self._dhasa_combo.clear()
            if self._dhasa_type_combo.currentIndex()==0:
                self._dhasa_options_button.setVisible(True); self._dhasa_varga_combo.setVisible(False)
                _dhasa_list = [self.resources[d+'_str'] for d in list(_graha_dhasa_dict.keys())]
                self._dhasa_combo.addItems(_dhasa_list)
                self._dhasa_combo.setCurrentIndex(self._current_dhasa_index) if (self._current_dhasa_index>=0 and self._current_dhasa_index < len(_graha_dhasa_dict)) else 0
                self._dhasa_options_button.setText(self._dhasa_combo.currentText()+' '+self.resources['options_str']) 
            elif self._dhasa_type_combo.currentIndex()==1:
                self._dhasa_options_button.setVisible(False); self._dhasa_varga_combo.setVisible(True)
                _dhasa_list = [self.resources[d+'_str'] for d in list(_rasi_dhasa_dict.keys())]
                self._dhasa_combo.addItems(_dhasa_list)
                self._dhasa_combo.setCurrentIndex(self._current_dhasa_index) if (self._current_dhasa_index>=0 and self._current_dhasa_index < len(_rasi_dhasa_dict)) else 0 
            else:
                self._dhasa_options_button.setVisible(False); self._dhasa_varga_combo.setVisible(True)
                _dhasa_list = [self.resources[d+'_str'] for d in list(_annual_dhasa_dict.keys())]
                self._dhasa_combo.addItems(_dhasa_list)
                self._dhasa_combo.setCurrentIndex(self._current_dhasa_index) if (self._current_dhasa_index>=0 and self._current_dhasa_index < len(_annual_dhasa_dict)) else 0 
            self._dhasa_type_combo.setCurrentIndex(self._current_dhasa_type_index)
            self._dhasa_varga_combo.setCurrentIndex(self._current_dhasa_varga_index)
        else:
            self._dhasa_type_combo.setCurrentIndex(0)
            self._dhasa_combo.setCurrentIndex(0)
            self._dhasa_varga_combo.setCurrentIndex(0)
        self._update_dhasa_bhukthi_tab_information()
    def _init_dhasa_tab_widgets(self,tab_index,tables_per_tab,rows_per_table,cols_per_table,
                                tab_start,tab_count,tab_str,table_font_size):
        """ Add more tabs for narayna dhasa  """
        for t in range(tab_count):
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index+t],'')
        self.tabCount += tab_count
        _db_tables = [[ QTableWidget(rows_per_table,cols_per_table) for _ in range(tables_per_tab)] for _ in range(tab_count)]
        for db_tab in range(tab_count):
            grid_layout = QGridLayout()
            for col in range(tables_per_tab):
                delegate = AlignDelegate(_db_tables[db_tab][col])
                _db_tables[db_tab][col].setItemDelegate(delegate)
                _db_tables[db_tab][col].setStyleSheet('font-size:'+str(table_font_size)+'pt')
                _db_tables[db_tab][col].setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                _db_tables[db_tab][col].setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                grid_layout.addWidget(_db_tables[db_tab][col],1,col)
            self.horo_tabs[tab_start+db_tab].setLayout(grid_layout)
            _tabname = tab_str+str(db_tab+1) if tab_count>1 else tab_str
            self.tabWidget.setTabText(tab_start+db_tab,_tabname)
        return _db_tables
    def _init_panchanga_tab_widgets(self,tab_index):
        self.panchanga_info_dialog = PanchangaInfoDialog(language=self._language,
                                                         info_label1_font_size=_info_label1_font_size,
                                                         info_label2_font_size=_info_label2_font_size,
                                                         info_label3_font_size=_info_label3_font_size,
                                                         info_label_height=_info_label1_height)
        self.horo_tabs.append(self.panchanga_info_dialog)
        self.tabWidget.addTab(self.horo_tabs[tab_index],self.tabNames[tab_index])
        return
    def _init_bhaava_tab_widgets(self,tab_index):
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],self.tabNames[tab_index])
        h_layout = QHBoxLayout()
        self._bhava_chart_type = 'south_indian' if 'west' in self._chart_type.lower() else self._chart_type
        self._western_chart = True if 'west' in self._chart_type.lower() else False
        self._bhava_chart= available_chart_types[self._bhava_chart_type](chart_size_factor=_bhava_chart_size_factor, 
                                                                   label_font_size=_chart_label_font_size)
        self._bhava_table_rows=13 ; self._bhava_table_columns=5
        self._bhava_table = LabelGrid(rows=self._bhava_table_rows,columns=self._bhava_table_columns,label_font_size=10,
                                      fit_to_contents=False)
        h_layout.addWidget(self._bhava_chart)
        v_layout = QVBoxLayout()
        self._bhava_method_combo = QComboBox()
        self._bhava_method_combo.addItems(const.available_house_systems.values())
        self._bhava_method_combo.setCurrentIndex(0)
        _bhava_value_index = self._bhava_method_combo.currentIndex()
        self._bhaava_madhya_method = list(const.available_house_systems.keys())[_bhava_value_index] 
        self._bhava_method_combo.currentIndexChanged.connect(self._bhava_method_changed)
        v_layout.addWidget(self._bhava_method_combo)
        v_layout.addWidget(self._bhava_table)
        h_layout.addLayout(v_layout)
        h_layout.setSpacing(_margin_between_chart_and_info)
        #h_layout.setContentsMargins(0,0,0,0)
        self.horo_tabs[tab_index].setLayout(h_layout)
        self._bhava_chart.update()
    def _init_chakra_tab_widgets(self, tab_index):
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],'Chakra')
        v_layout = QVBoxLayout()
        #"""
        h_layout1 = QHBoxLayout()
        self._chakra_chart_combo = QComboBox()
        self._chakra_chart_combo.addItems(_chart_names)
        self._chakra_chart_combo.SizeAdjustPolicy.AdjustToContents
        self._chakra_chart_combo.currentIndexChanged.connect(self._chakra_chart_selection_changed)
        h_layout1.addWidget(self._chakra_chart_combo)
        self._chakra_chart_option_button = QPushButton('Select Chart Options')
        #self._chakra_chart_option_button.setFlat(True)
        #self._chakra_chart_option_button.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._chakra_chart_option_button.clicked.connect(self._show_chakra_chart_options)
        self._chakra_chart_option_button.setEnabled(False)
        h_layout1.addWidget(self._chakra_chart_option_button)
        self._chakra_option_info_label = QLabel('')
        self._chakra_option_info_label.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._chakra_option_info_label.setEnabled(False)
        self._chakra_option_info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        h_layout1.addWidget(self._chakra_option_info_label)
        v_layout.addLayout(h_layout1)
        #"""
        h_layout1 = QHBoxLayout()
        self._chakra_options_group = QButtonGroup()
        for c in range(len(_available_chakras)):
            btn = QRadioButton(_available_chakras[c])
            self._chakra_options_group.addButton(btn,c)
            h_layout1.addWidget(btn)
        self._chakra_options_group.button(0).setChecked(True)
        self._chakra_options_group.buttonClicked.connect(self._chakra_chart_selection_changed)
        v_layout.addLayout(h_layout1)
        self._chakra_info_label = QLabel('')
        v_layout.addWidget(self._chakra_info_label)
        self._chakra_widget = QStackedWidget(); self._chakra_widget.addWidget(QWidget())
        v_layout.addWidget(self._chakra_widget)
        self.horo_tabs[_chakra_tab_start].setLayout(v_layout)
        self._current_chakra_chart_index = 0
        self._chakra_method_index = 1
        self._chakra_varga_dict = varga_chart_dialog.get_varga_option_dict()
        self._chakra_mixed_dict_1 = self._chakra_varga_dict
        self._chakra_mixed_dict_2 = self._chakra_varga_dict
        self._chakra_custom_varga = _custom_varga_index
        self._chakra_mixed_chart_index_1 = _mixed_chart_index_1; self._chakra_mixed_chart_index_2 = _mixed_chart_index_2
        self._chakra_mixed_method_index_1 = _mixed_chart_method_1; self._chakra_mixed_method_index_2 = _mixed_chart_method_2
    def _show_chakra_chart_options(self):
        self._current_chakra_chart_index = self._chakra_chart_combo.currentIndex()
        self._chakra_option_info_label.setText(self._chakra_chart_options_str)
        if self._current_chakra_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_chakra_chart_index]
            self._chakra_method_index = self._chakra_varga_dict[varga_index][1]
            self._chakra_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._chakra_method_index)+'_str']
        elif self._current_chakra_chart_index== _custom_chart_index:
            varga_index = self._chakra_custom_varga
            self._chakra_method_index = self._chakra_varga_dict[varga_index][1]
            self._chakra_chart_options_str = self.resources['dn_custom_option'+str(self._chakra_method_index)+'_str']
        elif self._current_chakra_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._chakra_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._chakra_mixed_chart_index_2]
            self._chakra_mixed_method_index_1 = self._chakra_mixed_dict_1[v1][1]
            self._chakra_mixed_method_index_2 = self._chakra_mixed_dict_2[v2][1]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._chakra_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._chakra_mixed_method_index_2)+'_str']
            self._chakra_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
        if self._current_chakra_chart_index<=_custom_chart_index:
            dlg = varga_chart_dialog.VargaChartOptionsDialog(chart_index=self._current_chakra_chart_index,
                                    chart_method=self._chakra_method_index,varga_factor=varga_index,
                                        base_rasi=self._chakra_varga_dict[self._chakra_custom_varga][2],
                                        count_from_end_of_sign=self._chakra_varga_dict[self._chakra_custom_varga][3])
            if dlg.exec()==1:
                self._chakra_method_index = dlg._method_index
                if dlg._varga_factor != None: varga_index = dlg._varga_factor         
                if self._current_chakra_chart_index==_custom_chart_index: self._chakra_custom_varga = varga_index
                self._chakra_varga_dict[varga_index] = \
                    (self._chakra_varga_dict[varga_index][0],dlg._method_index,
                        dlg._base_rasi_index,dlg._count_from_end_of_sign)
                self._update_chakra_tab_information(chart_index=self._current_chakra_chart_index,
                                        chart_method=self._chakra_method_index,divisional_chart_factor=varga_index,
                                        base_rasi=self._chakra_varga_dict[varga_index][2],
                                        count_from_end_of_sign=self._chakra_varga_dict[varga_index][3])
            self._chakra_chart_options_str = dlg._option_string
            self._chakra_option_info_label.setText(self._chakra_chart_options_str)
        elif self._current_chakra_chart_index==_mixed_chart_index:
            v1 = const.division_chart_factors[self._chakra_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._chakra_mixed_chart_index_2]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._chakra_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._chakra_mixed_method_index_2)+'_str']
            self._chakra_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._chakra_option_info_label.setText(self._chakra_chart_options_str)
            dlg = mixed_chart_dialog.MixedChartOptionsDialog(chart_index_1=self._chakra_mixed_chart_index_1,chart_index_2=self._chakra_mixed_chart_index_2,
                                                 chart_method_1=self._chakra_mixed_method_index_1,chart_method_2=self._chakra_mixed_method_index_2)
            if dlg.exec()==1:
                self._chakra_mixed_chart_index_1 = dlg._chart_index_1;self._chakra_mixed_chart_index_2 = dlg._chart_index_2
                self._chakra_mixed_method_index_1 = dlg._method_index_1;self._chakra_mixed_method_index_2 = dlg._method_index_2
                v1 = dlg._varga_factor_1; v2 = dlg._varga_factor_2
                v1s = self.resources['d'+str(v1)+'_option'+str(self._chakra_mixed_method_index_1)+'_str']
                v2s = self.resources['d'+str(v2)+'_option'+str(self._chakra_mixed_method_index_2)+'_str']
                self._chakra_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
                self._chakra_option_info_label.setText(self._chakra_chart_options_str)
                mds = 'D'+str(v1)+'xD'+ str(v2)+' '
                self._chakra_chart_option_button.setText(mds+self.resources['options_str'])
                self._update_chakra_tab_information(chart_index=self._current_chakra_chart_index,
                                                   chart_index_1=dlg._chart_index_1,chart_method_1=dlg._method_index_1,
                                                   chart_index_2=dlg._chart_index_2,chart_method_2=dlg._method_index_2)
    def _chakra_chart_selection_changed(self):
        
        self._current_chakra_chart_index = self._chakra_chart_combo.currentIndex()
        if self._current_chakra_chart_index==0:
            varga_index = 1
            self._chakra_method_index = 1
            self._chakra_chart_options_str = ''
        elif self._current_chakra_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_chakra_chart_index]
            self._chakra_method_index = self._chakra_varga_dict[varga_index][1]
            self._chakra_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._chakra_method_index)+'_str']
        elif self._current_chakra_chart_index == _custom_chart_index:
            varga_index = self._chakra_custom_varga
            self._chakra_method_index = self._chakra_varga_dict[varga_index][1]
            self._chakra_chart_options_str = self.resources['dn_custom_option'+str(self._chakra_method_index)+'_str']
        elif self._current_chakra_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._chakra_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._chakra_mixed_chart_index_2]
            mds = 'D'+str(v1)+'('+str(self._chakra_mixed_method_index_1)+')xD'+ \
                    str(v2)+'('+str(self._chakra_mixed_method_index_2)+')'+' '
            v1s = self.resources['d'+str(v1)+'_option'+str(self._chakra_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._chakra_mixed_method_index_2)+'_str']
            self._chakra_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._chakra_option_info_label.setText(self._chakra_chart_options_str)
            
        self._chakra_option_info_label.setText(self._chakra_chart_options_str)
        self._chakra_option_info_label.adjustSize()
        if self._current_chakra_chart_index==0:
            self._chakra_chart_option_button.setEnabled(False);self._chakra_chart_option_button.setVisible(False)
            self._chakra_option_info_label.setEnabled(False);self._chakra_option_info_label.setVisible(False)
        else:
            self._chakra_chart_option_button.setEnabled(True);self._chakra_chart_option_button.setVisible(True)
            self._chakra_option_info_label.setEnabled(True);self._chakra_option_info_label.setVisible(True)
        if self._current_chakra_chart_index==_mixed_chart_index:
            mds = 'D'+str(v1)+'xD'+ str(v2)+' '
            self._chakra_chart_option_button.setText(mds+self.resources['options_str'])
            self._update_chakra_tab_information(chart_index=self._current_chakra_chart_index,
                                chart_index_1=self._chakra_mixed_chart_index_1,chart_method_1=self._chakra_mixed_method_index_1,
                                chart_index_2=self._chakra_mixed_chart_index_2,chart_method_2=self._chakra_mixed_method_index_2)
        else:
            self._chakra_chart_option_button.setText(self._chakra_chart_combo.currentText()+' '+self.resources['options_str'])
            if self._current_chakra_chart_index==_custom_chart_index:
                self._chakra_chart_option_button.setText('D'+str(varga_index)+' '+self.resources['options_str'])
            self._update_chakra_tab_information(chart_index=self._current_chakra_chart_index,chart_method=self._chakra_method_index,
                                    divisional_chart_factor=varga_index,
                                    base_rasi=self._chakra_varga_dict[varga_index][2],
                                    count_from_end_of_sign=self._chakra_varga_dict[varga_index][3])
    def _init_kpinfo_tab_widgets(self,tab_index):
        v_layout = QVBoxLayout()
        h_layout1 = QHBoxLayout()
        self._kpinfo_chart_combo = QComboBox()
        self._kpinfo_chart_combo.addItems(_chart_names)
        self._kpinfo_chart_combo.SizeAdjustPolicy.AdjustToContents
        self._kpinfo_chart_combo.currentIndexChanged.connect(self._kpinfo_chart_selection_changed)
        h_layout1.addWidget(self._kpinfo_chart_combo)
        self._kpinfo_chart_option_button = QPushButton('Select Chart Options')
        #self._kpinfo_chart_option_button.setFlat(True)
        #self._kpinfo_chart_option_button.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._kpinfo_chart_option_button.clicked.connect(self._show_kpinfo_chart_options)
        self._kpinfo_chart_option_button.setEnabled(False)
        h_layout1.addWidget(self._kpinfo_chart_option_button)
        self._kpinfo_option_info_label = QLabel('')
        self._kpinfo_option_info_label.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._kpinfo_option_info_label.setEnabled(False)
        self._kpinfo_option_info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        h_layout1.addWidget(self._kpinfo_option_info_label)
        v_layout.addLayout(h_layout1)        
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],self.tabNames[tab_index])
        self._kpinfo_table = QTableWidget(25,7)
        self._kpinfo_table.setStyleSheet('font-size:'+str(_kpinfo_label_font_size)+'pt')
        self._kpinfo_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._kpinfo_table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        v_layout.addWidget(self._kpinfo_table)
        self._current_kpinfo_chart_index = 0
        self._kpinfo_method_index = 1
        self._kpinfo_varga_dict = varga_chart_dialog.get_varga_option_dict()
        self._kpinfo_mixed_dict_1 = self._kpinfo_varga_dict
        self._kpinfo_mixed_dict_2 = self._kpinfo_varga_dict
        self._kpinfo_custom_varga = _custom_varga_index
        self._kpinfo_mixed_chart_index_1 = _mixed_chart_index_1; self._kpinfo_mixed_chart_index_2 = _mixed_chart_index_2
        self._kpinfo_mixed_method_index_1 = _mixed_chart_method_1; self._kpinfo_mixed_method_index_2 = _mixed_chart_method_2
        self.horo_tabs[tab_index].setLayout(v_layout)
    def _show_kpinfo_chart_options(self):
        self._current_kpinfo_chart_index = self._kpinfo_chart_combo.currentIndex()
        self._kpinfo_option_info_label.setText(self._kpinfo_chart_options_str)
        if self._current_kpinfo_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_kpinfo_chart_index]
            self._kpinfo_method_index = self._kpinfo_varga_dict[varga_index][1]
            self._kpinfo_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._kpinfo_method_index)+'_str']
        elif self._current_kpinfo_chart_index== _custom_chart_index:
            varga_index = self._kpinfo_custom_varga
            self._kpinfo_method_index = self._kpinfo_varga_dict[varga_index][1]
            self._kpinfo_chart_options_str = self.resources['dn_custom_option'+str(self._kpinfo_method_index)+'_str']
        elif self._current_kpinfo_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._kpinfo_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._kpinfo_mixed_chart_index_2]
            self._kpinfo_mixed_method_index_1 = self._kpinfo_mixed_dict_1[v1][1]
            self._kpinfo_mixed_method_index_2 = self._kpinfo_mixed_dict_2[v2][1]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._kpinfo_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._kpinfo_mixed_method_index_2)+'_str']
            self._kpinfo_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
        if self._current_kpinfo_chart_index<=_custom_chart_index:
            dlg = varga_chart_dialog.VargaChartOptionsDialog(chart_index=self._current_kpinfo_chart_index,
                                    chart_method=self._kpinfo_method_index,varga_factor=varga_index,
                                        base_rasi=self._kpinfo_varga_dict[self._kpinfo_custom_varga][2],
                                        count_from_end_of_sign=self._kpinfo_varga_dict[self._kpinfo_custom_varga][3])
            if dlg.exec()==1:
                self._kpinfo_method_index = dlg._method_index
                if dlg._varga_factor != None: varga_index = dlg._varga_factor         
                if self._current_kpinfo_chart_index==_custom_chart_index: self._kpinfo_custom_varga = varga_index
                self._kpinfo_varga_dict[varga_index] = \
                    (self._kpinfo_varga_dict[varga_index][0],dlg._method_index,
                        dlg._base_rasi_index,dlg._count_from_end_of_sign)
                self._update_kpinfo_information(chart_index=self._current_kpinfo_chart_index,
                                        chart_method=self._kpinfo_method_index,divisional_chart_factor=varga_index,
                                        base_rasi=self._kpinfo_varga_dict[varga_index][2],
                                        count_from_end_of_sign=self._kpinfo_varga_dict[varga_index][3])
            self._kpinfo_chart_options_str = dlg._option_string
            self._kpinfo_option_info_label.setText(self._kpinfo_chart_options_str)
        elif self._current_kpinfo_chart_index==_mixed_chart_index:
            v1 = const.division_chart_factors[self._kpinfo_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._kpinfo_mixed_chart_index_2]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._kpinfo_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._kpinfo_mixed_method_index_2)+'_str']
            self._kpinfo_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._kpinfo_option_info_label.setText(self._kpinfo_chart_options_str)
            dlg = mixed_chart_dialog.MixedChartOptionsDialog(chart_index_1=self._kpinfo_mixed_chart_index_1,chart_index_2=self._kpinfo_mixed_chart_index_2,
                                                 chart_method_1=self._kpinfo_mixed_method_index_1,chart_method_2=self._kpinfo_mixed_method_index_2)
            if dlg.exec()==1:
                self._kpinfo_mixed_chart_index_1 = dlg._chart_index_1;self._kpinfo_mixed_chart_index_2 = dlg._chart_index_2
                self._kpinfo_mixed_method_index_1 = dlg._method_index_1;self._kpinfo_mixed_method_index_2 = dlg._method_index_2
                v1 = dlg._varga_factor_1; v2 = dlg._varga_factor_2
                v1s = self.resources['d'+str(v1)+'_option'+str(self._kpinfo_mixed_method_index_1)+'_str']
                v2s = self.resources['d'+str(v2)+'_option'+str(self._kpinfo_mixed_method_index_2)+'_str']
                self._kpinfo_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
                self._kpinfo_option_info_label.setText(self._kpinfo_chart_options_str)
                mds = 'D'+str(v1)+'xD'+ str(v2)+' '
                self._kpinfo_chart_option_button.setText(mds+self.resources['options_str'])
                self._update_kpinfo_information(chart_index=self._current_kpinfo_chart_index,
                                                   chart_index_1=dlg._chart_index_1,chart_method_1=dlg._method_index_1,
                                                   chart_index_2=dlg._chart_index_2,chart_method_2=dlg._method_index_2)
    def _kpinfo_chart_selection_changed(self):
        self._current_kpinfo_chart_index = self._kpinfo_chart_combo.currentIndex()
        if self._current_kpinfo_chart_index==0:
            varga_index = 1
            self._kpinfo_method_index = 1
            self._kpinfo_chart_options_str = ''
        elif self._current_kpinfo_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_kpinfo_chart_index]
            self._kpinfo_method_index = self._kpinfo_varga_dict[varga_index][1]
            self._kpinfo_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._kpinfo_method_index)+'_str']
        elif self._current_kpinfo_chart_index == _custom_chart_index:
            varga_index = self._kpinfo_custom_varga
            self._kpinfo_method_index = self._kpinfo_varga_dict[varga_index][1]
            self._kpinfo_chart_options_str = self.resources['dn_custom_option'+str(self._kpinfo_method_index)+'_str']
        elif self._current_kpinfo_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._kpinfo_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._kpinfo_mixed_chart_index_2]
            mds = 'D'+str(v1)+'('+str(self._kpinfo_mixed_method_index_1)+')xD'+ \
                    str(v2)+'('+str(self._kpinfo_mixed_method_index_2)+')'+' '
            v1s = self.resources['d'+str(v1)+'_option'+str(self._kpinfo_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._kpinfo_mixed_method_index_2)+'_str']
            self._kpinfo_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._kpinfo_option_info_label.setText(self._kpinfo_chart_options_str)
            
        self._kpinfo_option_info_label.setText(self._kpinfo_chart_options_str)
        self._kpinfo_option_info_label.adjustSize()
        if self._current_kpinfo_chart_index==0:
            self._kpinfo_chart_option_button.setEnabled(False);self._kpinfo_chart_option_button.setVisible(False)
            self._kpinfo_option_info_label.setEnabled(False);self._kpinfo_option_info_label.setVisible(False)
        else:
            self._kpinfo_chart_option_button.setEnabled(True);self._kpinfo_chart_option_button.setVisible(True)
            self._kpinfo_option_info_label.setEnabled(True);self._kpinfo_option_info_label.setVisible(True)
        if self._current_kpinfo_chart_index==_mixed_chart_index:
            mds = 'D'+str(v1)+'xD'+ str(v2)+' '
            self._kpinfo_chart_option_button.setText(mds+self.resources['options_str'])
            self._update_kpinfo_information(chart_index=self._current_kpinfo_chart_index,
                                chart_index_1=self._kpinfo_mixed_chart_index_1,chart_method_1=self._kpinfo_mixed_method_index_1,
                                chart_index_2=self._kpinfo_mixed_chart_index_2,chart_method_2=self._kpinfo_mixed_method_index_2)
        else:
            self._kpinfo_chart_option_button.setText(self._kpinfo_chart_combo.currentText()+' '+self.resources['options_str'])
            if self._current_kpinfo_chart_index==_custom_chart_index:
                self._kpinfo_chart_option_button.setText('D'+str(varga_index)+' '+self.resources['options_str'])
            self._update_kpinfo_information(chart_index=self._current_kpinfo_chart_index,chart_method=self._kpinfo_method_index,
                                    divisional_chart_factor=varga_index,
                                    base_rasi=self._kpinfo_varga_dict[varga_index][2],
                                    count_from_end_of_sign=self._kpinfo_varga_dict[varga_index][3])
    def _init_chart_tab_widgets(self,tab_index):
        c = 0
        v_layout = QVBoxLayout()
        h_layout1 = QHBoxLayout()
        self._kundali_chart_combo = QComboBox()
        self._kundali_chart_combo.addItems(_chart_names)
        self._kundali_chart_combo.SizeAdjustPolicy.AdjustToContents
        self._kundali_chart_combo.currentIndexChanged.connect(self._kundali_chart_selection_changed)
        h_layout1.addWidget(self._kundali_chart_combo)
        self._kundali_chart_option_button = QPushButton('Select Chart Options')
        #self._kundali_chart_option_button.setFlat(True)
        #self._kundali_chart_option_button.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._kundali_chart_option_button.clicked.connect(self._show_kundali_chart_options)
        self._kundali_chart_option_button.setEnabled(False)
        h_layout1.addWidget(self._kundali_chart_option_button)
        self._kundali_option_info_label = QLabel('')
        self._kundali_option_info_label.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._kundali_option_info_label.setEnabled(False)
        self._kundali_option_info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        h_layout1.addWidget(self._kundali_option_info_label)
        v_layout.addLayout(h_layout1)        
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index+c],self.tabNames[tab_index+c])
        h_layout = QHBoxLayout()
        self._kundali_charts.append(available_chart_types[self._chart_type](chart_size_factor=_chart_size_factor, label_font_size=_chart_label_font_size))
        h_layout.addWidget(self._kundali_charts[tab_index+c-_tabcount_before_chart_tab])
        self._chart_info_label1.setText('Chart Information')
        h_layout.addWidget(self._chart_info_label1)
        self._chart_info_label1.setStyleSheet('font-size:'+str(_chart_info_label_font_size)+'pt')
        self._chart_info_label2.setText('Chart Information')
        h_layout.addWidget(self._chart_info_label2)
        self._chart_info_label2.setStyleSheet('font-size:'+str(_chart_info_label_font_size)+'pt')
        h_layout.setSpacing(_margin_between_chart_and_info)
        h_layout.setContentsMargins(0,0,0,0)
        self._kundali_charts[tab_index+c-_tabcount_before_chart_tab].update()
        v_layout.addLayout(h_layout)
        self.horo_tabs[tab_index+c].setLayout(v_layout)
        self._current_kundali_chart_index = 0
        self._kundali_method_index = 1
        self._kundali_varga_dict = varga_chart_dialog.get_varga_option_dict()
        self._kundali_mixed_dict_1 = self._kundali_varga_dict
        self._kundali_mixed_dict_2 = self._kundali_varga_dict
        self._kundali_custom_varga = _custom_varga_index
        self._kundali_mixed_chart_index_1 = _mixed_chart_index_1; self._kundali_mixed_chart_index_2 = _mixed_chart_index_2
        self._kundali_mixed_method_index_1 = _mixed_chart_method_1; self._kundali_mixed_method_index_2 = _mixed_chart_method_2
    def _show_kundali_chart_options(self):
        self._current_kundali_chart_index = self._kundali_chart_combo.currentIndex()
        self._kundali_option_info_label.setText(self._kundali_chart_options_str)
        if self._current_kundali_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_kundali_chart_index]
            self._kundali_method_index = self._kundali_varga_dict[varga_index][1]
            self._kundali_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._kundali_method_index)+'_str']
        elif self._current_kundali_chart_index== _custom_chart_index:
            varga_index = self._kundali_custom_varga
            self._kundali_method_index = self._kundali_varga_dict[varga_index][1]
            self._kundali_chart_options_str = self.resources['dn_custom_option'+str(self._kundali_method_index)+'_str']
        elif self._current_kundali_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._kundali_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._kundali_mixed_chart_index_2]
            self._kundali_mixed_method_index_1 = self._kundali_mixed_dict_1[v1][1]
            self._kundali_mixed_method_index_2 = self._kundali_mixed_dict_2[v2][1]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._kundali_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._kundali_mixed_method_index_2)+'_str']
            self._kundali_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
        if self._current_kundali_chart_index<=_custom_chart_index:
            dlg = varga_chart_dialog.VargaChartOptionsDialog(chart_index=self._current_kundali_chart_index,
                                    chart_method=self._kundali_method_index,varga_factor=varga_index,
                                        base_rasi=self._kundali_varga_dict[self._kundali_custom_varga][2],
                                        count_from_end_of_sign=self._kundali_varga_dict[self._kundali_custom_varga][3])
            if dlg.exec()==1:
                self._kundali_method_index = dlg._method_index
                if dlg._varga_factor != None: varga_index = dlg._varga_factor         
                if self._current_kundali_chart_index==_custom_chart_index: self._kundali_custom_varga = varga_index
                self._kundali_varga_dict[varga_index] = \
                    (self._kundali_varga_dict[varga_index][0],dlg._method_index,
                        dlg._base_rasi_index,dlg._count_from_end_of_sign)
                self._update_tab_chart_information(chart_index=self._current_kundali_chart_index,
                                        chart_method=self._kundali_method_index,divisional_chart_factor=varga_index,
                                        base_rasi=self._kundali_varga_dict[varga_index][2],
                                        count_from_end_of_sign=self._kundali_varga_dict[varga_index][3])
            self._kundali_chart_options_str = dlg._option_string
            self._kundali_option_info_label.setText(self._kundali_chart_options_str)
            self._kundali_chart_option_button.setText(self._kundali_chart_combo.currentText()+' '+self.resources['options_str'])
            if self._current_kundali_chart_index==_custom_chart_index:
                self._kundali_chart_option_button.setText('D'+str(varga_index)+' '+self.resources['options_str'])
        elif self._current_kundali_chart_index==_mixed_chart_index:
            v1 = const.division_chart_factors[self._kundali_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._kundali_mixed_chart_index_2]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._kundali_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._kundali_mixed_method_index_2)+'_str']
            self._kundali_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._kundali_option_info_label.setText(self._kundali_chart_options_str)
            dlg = mixed_chart_dialog.MixedChartOptionsDialog(chart_index_1=self._kundali_mixed_chart_index_1,chart_index_2=self._kundali_mixed_chart_index_2,
                                                 chart_method_1=self._kundali_mixed_method_index_1,chart_method_2=self._kundali_mixed_method_index_2)
            if dlg.exec()==1:
                self._kundali_mixed_chart_index_1 = dlg._chart_index_1;self._kundali_mixed_chart_index_2 = dlg._chart_index_2
                self._kundali_mixed_method_index_1 = dlg._method_index_1;self._kundali_mixed_method_index_2 = dlg._method_index_2
                v1 = dlg._varga_factor_1; v2 = dlg._varga_factor_2
                v1s = self.resources['d'+str(v1)+'_option'+str(self._kundali_mixed_method_index_1)+'_str']
                v2s = self.resources['d'+str(v2)+'_option'+str(self._kundali_mixed_method_index_2)+'_str']
                self._kundali_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
                self._kundali_option_info_label.setText(self._kundali_chart_options_str)
                mds = 'D'+str(v1)+'xD'+ str(v2)+' '
                self._kundali_chart_option_button.setText(mds+self.resources['options_str'])
                self._update_tab_chart_information(chart_index=self._current_kundali_chart_index,
                                                   chart_index_1=dlg._chart_index_1,chart_method_1=dlg._method_index_1,
                                                   chart_index_2=dlg._chart_index_2,chart_method_2=dlg._method_index_2)
    def _kundali_chart_selection_changed(self):
        self._current_kundali_chart_index = self._kundali_chart_combo.currentIndex()
        if self._current_kundali_chart_index==0:
            varga_index = 1
            self._kundali_method_index = 1
            self._kundali_chart_options_str = ''
        elif self._current_kundali_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_kundali_chart_index]
            self._kundali_method_index = self._kundali_varga_dict[varga_index][1]
            self._kundali_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._kundali_method_index)+'_str']
        elif self._current_kundali_chart_index == _custom_chart_index:
            varga_index = self._kundali_custom_varga
            self._kundali_method_index = self._kundali_varga_dict[varga_index][1]
            self._kundali_chart_options_str = self.resources['dn_custom_option'+str(self._kundali_method_index)+'_str']
        elif self._current_kundali_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._kundali_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._kundali_mixed_chart_index_2]
            mds = 'D'+str(v1)+'('+str(self._kundali_mixed_method_index_1)+')xD'+ \
                    str(v2)+'('+str(self._kundali_mixed_method_index_2)+')'+' '
            v1s = self.resources['d'+str(v1)+'_option'+str(self._kundali_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._kundali_mixed_method_index_2)+'_str']
            self._kundali_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._kundali_option_info_label.setText(self._kundali_chart_options_str)
            
        self._kundali_option_info_label.setText(self._kundali_chart_options_str)
        self._kundali_option_info_label.adjustSize()
        if self._current_kundali_chart_index==0:
            self._kundali_chart_option_button.setEnabled(False);self._kundali_chart_option_button.setVisible(False)
            self._kundali_option_info_label.setEnabled(False);self._kundali_option_info_label.setVisible(False)
        else:
            self._kundali_chart_option_button.setEnabled(True);self._kundali_chart_option_button.setVisible(True)
            self._kundali_option_info_label.setEnabled(True);self._kundali_option_info_label.setVisible(True)
        if self._current_kundali_chart_index==_mixed_chart_index:
            mds = 'D'+str(v1)+'xD'+ str(v2)+' '
            self._kundali_chart_option_button.setText(mds+self.resources['options_str'])
            self._update_tab_chart_information(chart_index=self._current_kundali_chart_index,
                                chart_index_1=self._kundali_mixed_chart_index_1,chart_method_1=self._kundali_mixed_method_index_1,
                                chart_index_2=self._kundali_mixed_chart_index_2,chart_method_2=self._kundali_mixed_method_index_2)
        else:
            self._kundali_chart_option_button.setText(self._kundali_chart_combo.currentText()+' '+self.resources['options_str'])
            if self._current_kundali_chart_index==_custom_chart_index:
                self._kundali_chart_option_button.setText('D'+str(varga_index)+' '+self.resources['options_str'])
            self._update_tab_chart_information(chart_index=self._current_kundali_chart_index,chart_method=self._kundali_method_index,
                                    divisional_chart_factor=varga_index,
                                    base_rasi=self._kundali_varga_dict[varga_index][2],
                                    count_from_end_of_sign=self._kundali_varga_dict[varga_index][3])
    def _init_saham_tab_widgets(self,tab_index):
        v_layout = QVBoxLayout()
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],'')
        self._saham_table1 = QTableWidget(18,2); self._saham_table1.verticalHeader().setVisible(False)
        self._saham_table2 = QTableWidget(18,2); self._saham_table2.verticalHeader().setVisible(False)
        h_layout1 = QHBoxLayout()
        self._saham_chart_combo = QComboBox()
        self._saham_chart_combo.addItems(_chart_names)
        self._saham_chart_combo.SizeAdjustPolicy.AdjustToContents
        self._saham_chart_combo.currentIndexChanged.connect(self._saham_chart_selection_changed)
        h_layout1.addWidget(self._saham_chart_combo)
        self._saham_chart_option_button = QPushButton('Select Chart Options')
        #self._saham_chart_option_button.setFlat(True)
        #self._saham_chart_option_button.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._saham_chart_option_button.clicked.connect(self._show_saham_chart_options)
        self._saham_chart_option_button.setEnabled(False)
        h_layout1.addWidget(self._saham_chart_option_button)
        self._saham_option_info_label = QLabel('')
        self._saham_option_info_label.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._saham_option_info_label.setEnabled(False)
        self._saham_option_info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        h_layout1.addWidget(self._saham_option_info_label)
        v_layout.addLayout(h_layout1)        
        h_layout = QHBoxLayout()
        delegate = AlignDelegate(self._saham_table1)
        self._saham_table1.setItemDelegate(delegate)
        delegate = AlignDelegate(self._saham_table2)
        self._saham_table2.setItemDelegate(delegate)
        h_layout.addWidget(self._saham_table1)
        h_layout.addWidget(self._saham_table2)
        self._saham_table1.setStyleSheet('font-size:'+str(_saham_table_font_size)+'pt')
        self._saham_table2.setStyleSheet('font-size:'+str(_saham_table_font_size)+'pt')
        for table in [self._saham_table1, self._saham_table2]:
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
            table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            row_count = table.rowCount()
            col_count = table.columnCount()
            for row in range(row_count):
                for col in range(col_count):
                    table.setItem(row,col,QTableWidgetItem(''))
            table.update()
        v_layout.addLayout(h_layout)
        self.horo_tabs[tab_index].setLayout(v_layout)            
        self._current_saham_chart_index = 0
        self._saham_method_index = 1
        self._saham_varga_dict = varga_chart_dialog.get_varga_option_dict()
        self._saham_mixed_dict_1 = self._saham_varga_dict
        self._saham_mixed_dict_2 = self._saham_varga_dict
        self._saham_custom_varga = _custom_varga_index
        self._saham_mixed_chart_index_1 = _mixed_chart_index_1; self._saham_mixed_chart_index_2 = _mixed_chart_index_2
        self._saham_mixed_method_index_1 = _mixed_chart_method_1; self._saham_mixed_method_index_2 = _mixed_chart_method_2
    def _show_saham_chart_options(self):
        self._current_saham_chart_index = self._saham_chart_combo.currentIndex()
        self._saham_option_info_label.setText(self._saham_chart_options_str)
        if self._current_saham_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_saham_chart_index]
            self._saham_method_index = self._saham_varga_dict[varga_index][1]
            self._saham_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._saham_method_index)+'_str']
        elif self._current_saham_chart_index== _custom_chart_index:
            varga_index = self._saham_custom_varga
            self._saham_method_index = self._saham_varga_dict[varga_index][1]
            self._saham_chart_options_str = self.resources['dn_custom_option'+str(self._saham_method_index)+'_str']
        elif self._current_saham_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._saham_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._saham_mixed_chart_index_2]
            self._saham_mixed_method_index_1 = self._saham_mixed_dict_1[v1][1]
            self._saham_mixed_method_index_2 = self._saham_mixed_dict_2[v2][1]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._saham_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._saham_mixed_method_index_2)+'_str']
            self._saham_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
        if self._current_saham_chart_index<=_custom_chart_index:
            dlg = varga_chart_dialog.VargaChartOptionsDialog(chart_index=self._current_saham_chart_index,
                                    chart_method=self._saham_method_index,varga_factor=varga_index,
                                        base_rasi=self._saham_varga_dict[varga_index][2],
                                        count_from_end_of_sign=self._saham_varga_dict[varga_index][3])
            if dlg.exec()==1:
                self._saham_method_index = dlg._method_index
                if dlg._varga_factor != None: varga_index = dlg._varga_factor         
                if self._current_saham_chart_index==_custom_chart_index: self._saham_custom_varga = varga_index
                self._saham_varga_dict[varga_index] = \
                    (self._saham_varga_dict[varga_index][0],dlg._method_index,
                        dlg._base_rasi_index,dlg._count_from_end_of_sign)
                self._update_saham_table_information(self._current_saham_chart_index,self._saham_method_index,
                                        divisional_chart_factor=varga_index,
                                        base_rasi=self._saham_varga_dict[varga_index][2],
                                        count_from_end_of_sign=self._saham_varga_dict[varga_index][3])
            self._saham_chart_options_str = dlg._option_string
            self._saham_option_info_label.setText(self._saham_chart_options_str)
        elif self._current_saham_chart_index==_mixed_chart_index:
            v1 = const.division_chart_factors[self._saham_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._saham_mixed_chart_index_2]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._saham_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._saham_mixed_method_index_2)+'_str']
            self._saham_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._saham_option_info_label.setText(self._saham_chart_options_str)
            dlg = mixed_chart_dialog.MixedChartOptionsDialog(chart_index_1=self._saham_mixed_chart_index_1,chart_index_2=self._saham_mixed_chart_index_2,
                                                 chart_method_1=self._saham_mixed_method_index_1,chart_method_2=self._saham_mixed_method_index_2)
            if dlg.exec()==1:
                self._saham_mixed_chart_index_1 = dlg._chart_index_1;self._saham_mixed_chart_index_2 = dlg._chart_index_2
                self._saham_mixed_method_index_1 = dlg._method_index_1;self._saham_mixed_method_index_2 = dlg._method_index_2
                v1 = dlg._varga_factor_1; v2 = dlg._varga_factor_2
                v1s = self.resources['d'+str(v1)+'_option'+str(self._saham_mixed_method_index_1)+'_str']
                v2s = self.resources['d'+str(v2)+'_option'+str(self._saham_mixed_method_index_2)+'_str']
                self._saham_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
                self._saham_option_info_label.setText(self._saham_chart_options_str)
                mds = 'D'+str(v1)+'xD'+ str(v2)+' '
                self._saham_chart_option_button.setText(mds+self.resources['options_str'])
                self._update_saham_table_information(chart_index=self._current_saham_chart_index,
                                                   chart_index_1=dlg._chart_index_1,chart_method_1=dlg._method_index_1,
                                                   chart_index_2=dlg._chart_index_2,chart_method_2=dlg._method_index_2)
    def _saham_chart_selection_changed(self):
        self._current_saham_chart_index = self._saham_chart_combo.currentIndex()
        if self._current_saham_chart_index==0:
            varga_index = 1
            self._saham_method_index = 1
            self._saham_chart_options_str = ''
        elif self._current_saham_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_saham_chart_index]
            self._saham_method_index = self._saham_varga_dict[varga_index][1]
            self._saham_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._saham_method_index)+'_str']
        elif self._current_saham_chart_index == _custom_chart_index:
            varga_index = self._saham_custom_varga
            self._saham_method_index = self._saham_varga_dict[varga_index][1]
            self._saham_chart_options_str = self.resources['dn_custom_option'+str(self._saham_method_index)+'_str']
        elif self._current_saham_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._saham_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._saham_mixed_chart_index_2]
            mds = 'D'+str(v1)+'('+str(self._saham_mixed_method_index_1)+')xD'+ \
                    str(v2)+'('+str(self._saham_mixed_method_index_2)+')'+' '
            v1s = self.resources['d'+str(v1)+'_option'+str(self._saham_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._saham_mixed_method_index_2)+'_str']
            self._saham_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._saham_option_info_label.setText(self._saham_chart_options_str)
        self._saham_option_info_label.setText(self._saham_chart_options_str)
        self._saham_option_info_label.adjustSize()
        if self._current_saham_chart_index==0:
            self._saham_chart_option_button.setEnabled(False);self._saham_chart_option_button.setVisible(False)
            self._saham_option_info_label.setEnabled(False);self._saham_option_info_label.setVisible(False)
        else:
            self._saham_chart_option_button.setEnabled(True);self._saham_chart_option_button.setVisible(True)
            self._saham_option_info_label.setEnabled(True);self._saham_option_info_label.setVisible(True)
        if self._current_saham_chart_index==_mixed_chart_index:
            mds = 'D'+str(v1)+'xD'+ str(v2)+' '
            self._saham_chart_option_button.setText(mds+self.resources['options_str'])
            self._update_saham_table_information(chart_index=self._current_saham_chart_index,
                                chart_index_1=self._saham_mixed_chart_index_1,chart_method_1=self._saham_mixed_method_index_1,
                                chart_index_2=self._saham_mixed_chart_index_2,chart_method_2=self._saham_mixed_method_index_2)
        else:
            self._saham_chart_option_button.setText(self._saham_chart_combo.currentText()+' '+self.resources['options_str'])
            if self._current_saham_chart_index==_custom_chart_index:
                self._saham_chart_option_button.setText('D'+str(varga_index)+' '+self.resources['options_str'])
            self._update_saham_table_information(self._current_saham_chart_index,self._saham_method_index,
                                    divisional_chart_factor=varga_index,
                                    base_rasi=self._saham_varga_dict[varga_index][2],
                                    count_from_end_of_sign=self._saham_varga_dict[varga_index][3])
    def _init_drishti_tab_widgets(self,tab_index):
        v_layout = QVBoxLayout()
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],'')
        self._drishti_table1 = QTableWidget(7,3) 
        self._drishti_table2 = QTableWidget(9,3) 
        h_layout1 = QHBoxLayout()
        self._drishti_chart_combo = QComboBox()
        self._drishti_chart_combo.addItems(_chart_names)
        self._drishti_chart_combo.SizeAdjustPolicy.AdjustToContents
        self._drishti_chart_combo.currentIndexChanged.connect(self._drishti_chart_selection_changed)
        h_layout1.addWidget(self._drishti_chart_combo)
        self._drishti_chart_option_button = QPushButton('Select Chart Options')
        #self._drishti_chart_option_button.setFlat(True)
        #self._drishti_chart_option_button.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._drishti_chart_option_button.clicked.connect(self._show_drishti_chart_options)
        self._drishti_chart_option_button.setEnabled(False)
        h_layout1.addWidget(self._drishti_chart_option_button)
        self._drishti_option_info_label = QLabel('')
        self._drishti_option_info_label.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._drishti_option_info_label.setEnabled(False)
        self._drishti_option_info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        h_layout1.addWidget(self._drishti_option_info_label)
        v_layout.addLayout(h_layout1)        
        h_layout = QHBoxLayout()
        delegate = AlignDelegate(self._drishti_table1)
        self._drishti_table1.setItemDelegate(delegate)
        delegate = AlignDelegate(self._drishti_table2)
        self._drishti_table2.setItemDelegate(delegate)
        h_layout.addWidget(self._drishti_table1)
        h_layout.addWidget(self._drishti_table2)
        self._drishti_table2.setStyleSheet('font-size:'+str(_drishti_table_font_size)+'pt')
        for table in [self._drishti_table1, self._drishti_table2]:
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
            table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            row_count = table.rowCount()
            col_count = table.columnCount()
            for row in range(row_count):
                for col in range(col_count):
                    table.setItem(row,col,QTableWidgetItem(''))
            table.update()
        v_layout.addLayout(h_layout)
        self.horo_tabs[tab_index].setLayout(v_layout)            
        self._current_drishti_chart_index = 0
        self._drishti_method_index = 1
        self._drishti_varga_dict = varga_chart_dialog.get_varga_option_dict()
        self._drishti_mixed_dict_1 = self._drishti_varga_dict
        self._drishti_mixed_dict_2 = self._drishti_varga_dict
        self._drishti_custom_varga = _custom_varga_index
        self._drishti_mixed_chart_index_1 = _mixed_chart_index_1; self._drishti_mixed_chart_index_2 = _mixed_chart_index_2
        self._drishti_mixed_method_index_1 = _mixed_chart_method_1; self._drishti_mixed_method_index_2 = _mixed_chart_method_2
    def _show_drishti_chart_options(self):
        self._current_drishti_chart_index = self._drishti_chart_combo.currentIndex()
        self._drishti_option_info_label.setText(self._drishti_chart_options_str)
        if self._current_drishti_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_drishti_chart_index]
            self._drishti_method_index = self._drishti_varga_dict[varga_index][1]
            self._drishti_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._drishti_method_index)+'_str']
        elif self._current_drishti_chart_index== _custom_chart_index:
            varga_index = self._drishti_custom_varga
            self._drishti_method_index = self._drishti_varga_dict[varga_index][1]
            self._drishti_chart_options_str = self.resources['dn_custom_option'+str(self._drishti_method_index)+'_str']
        elif self._current_drishti_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._drishti_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._drishti_mixed_chart_index_2]
            self._drishti_mixed_method_index_1 = self._drishti_mixed_dict_1[v1][1]
            self._drishti_mixed_method_index_2 = self._drishti_mixed_dict_2[v2][1]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._drishti_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._drishti_mixed_method_index_2)+'_str']
            self._drishti_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
        if self._current_drishti_chart_index<=_custom_chart_index:
            dlg = varga_chart_dialog.VargaChartOptionsDialog(chart_index=self._current_drishti_chart_index,
                                    chart_method=self._drishti_method_index,varga_factor=varga_index,
                                        base_rasi=self._drishti_varga_dict[varga_index][2],
                                        count_from_end_of_sign=self._drishti_varga_dict[varga_index][3])
            if dlg.exec()==1:
                self._drishti_method_index = dlg._method_index
                if dlg._varga_factor != None: varga_index = dlg._varga_factor         
                if self._current_drishti_chart_index==_custom_chart_index: self._drishti_custom_varga = varga_index
                self._drishti_varga_dict[varga_index] = \
                    (self._drishti_varga_dict[varga_index][0],dlg._method_index,
                        dlg._base_rasi_index,dlg._count_from_end_of_sign)
                self._update_drishti_table_information(self._current_drishti_chart_index,self._drishti_method_index,
                                        divisional_chart_factor=varga_index,
                                        base_rasi=self._drishti_varga_dict[varga_index][2],
                                        count_from_end_of_sign=self._drishti_varga_dict[varga_index][3])
            self._drishti_chart_options_str = dlg._option_string
            self._drishti_option_info_label.setText(self._drishti_chart_options_str)
        elif self._current_drishti_chart_index==_mixed_chart_index:
            v1 = const.division_chart_factors[self._drishti_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._drishti_mixed_chart_index_2]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._drishti_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._drishti_mixed_method_index_2)+'_str']
            self._drishti_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._drishti_option_info_label.setText(self._drishti_chart_options_str)
            dlg = mixed_chart_dialog.MixedChartOptionsDialog(chart_index_1=self._drishti_mixed_chart_index_1,chart_index_2=self._drishti_mixed_chart_index_2,
                                                 chart_method_1=self._drishti_mixed_method_index_1,chart_method_2=self._drishti_mixed_method_index_2)
            if dlg.exec()==1:
                self._drishti_mixed_chart_index_1 = dlg._chart_index_1;self._drishti_mixed_chart_index_2 = dlg._chart_index_2
                self._drishti_mixed_method_index_1 = dlg._method_index_1;self._drishti_mixed_method_index_2 = dlg._method_index_2
                v1 = dlg._varga_factor_1; v2 = dlg._varga_factor_2
                v1s = self.resources['d'+str(v1)+'_option'+str(self._drishti_mixed_method_index_1)+'_str']
                v2s = self.resources['d'+str(v2)+'_option'+str(self._drishti_mixed_method_index_2)+'_str']
                self._drishti_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
                self._drishti_option_info_label.setText(self._drishti_chart_options_str)
                mds = 'D'+str(v1)+'xD'+ str(v2)+' '
                self._drishti_chart_option_button.setText(mds+self.resources['options_str'])
                self._update_drishti_table_information(chart_index=self._current_drishti_chart_index,
                                                   chart_index_1=dlg._chart_index_1,chart_method_1=dlg._method_index_1,
                                                   chart_index_2=dlg._chart_index_2,chart_method_2=dlg._method_index_2)
    def _drishti_chart_selection_changed(self):
        self._current_drishti_chart_index = self._drishti_chart_combo.currentIndex()
        if self._current_drishti_chart_index==0:
            varga_index = 1
            self._drishti_method_index = 1
            self._drishti_chart_options_str = ''
        elif self._current_drishti_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_drishti_chart_index]
            self._drishti_method_index = self._drishti_varga_dict[varga_index][1]
            self._drishti_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._drishti_method_index)+'_str']
        elif self._current_drishti_chart_index == _custom_chart_index:
            varga_index = self._drishti_custom_varga
            self._drishti_method_index = self._drishti_varga_dict[varga_index][1]
            self._drishti_chart_options_str = self.resources['dn_custom_option'+str(self._drishti_method_index)+'_str']
        elif self._current_drishti_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._drishti_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._drishti_mixed_chart_index_2]
            mds = 'D'+str(v1)+'('+str(self._drishti_mixed_method_index_1)+')xD'+ \
                    str(v2)+'('+str(self._drishti_mixed_method_index_2)+')'+' '
            v1s = self.resources['d'+str(v1)+'_option'+str(self._drishti_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._drishti_mixed_method_index_2)+'_str']
            self._drishti_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._drishti_option_info_label.setText(self._drishti_chart_options_str)
        self._drishti_option_info_label.setText(self._drishti_chart_options_str)
        self._drishti_option_info_label.adjustSize()
        if self._current_drishti_chart_index==0:
            self._drishti_chart_option_button.setEnabled(False);self._drishti_chart_option_button.setVisible(False)
            self._drishti_option_info_label.setEnabled(False);self._drishti_option_info_label.setVisible(False)
        else:
            self._drishti_chart_option_button.setEnabled(True);self._drishti_chart_option_button.setVisible(True)
            self._drishti_option_info_label.setEnabled(True);self._drishti_option_info_label.setVisible(True)
        if self._current_drishti_chart_index==_mixed_chart_index:
            mds = 'D'+str(v1)+'xD'+ str(v2)+' '
            self._drishti_chart_option_button.setText(mds+self.resources['options_str'])
            self._update_drishti_table_information(chart_index=self._current_drishti_chart_index,
                                chart_index_1=self._drishti_mixed_chart_index_1,chart_method_1=self._drishti_mixed_method_index_1,
                                chart_index_2=self._drishti_mixed_chart_index_2,chart_method_2=self._drishti_mixed_method_index_2)
        else:
            self._drishti_chart_option_button.setText(self._drishti_chart_combo.currentText()+' '+self.resources['options_str'])
            if self._current_drishti_chart_index==_custom_chart_index:
                self._drishti_chart_option_button.setText('D'+str(varga_index)+' '+self.resources['options_str'])
            self._update_drishti_table_information(self._current_drishti_chart_index,self._drishti_method_index,
                                    divisional_chart_factor=varga_index,
                                    base_rasi=self._drishti_varga_dict[varga_index][2],
                                    count_from_end_of_sign=self._drishti_varga_dict[varga_index][3])
    def _init_shad_bala_tab_widgets(self, tab_index):
        for t in range(_shad_bala_tab_count):
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index+t],'')
        self._shad_bala_table = [ QTableWidget(9,7) for _ in range(_shad_bala_tab_count)] 
        for t in range(_shad_bala_tab_count):
            h_layout = QHBoxLayout()
            delegate = AlignDelegate(self._shad_bala_table[t])
            self._shad_bala_table[t].setItemDelegate(delegate)
            h_layout.addWidget(self._shad_bala_table[t])
            for table in [self._shad_bala_table[t]]:
                table.setStyleSheet('font-size:'+str(_shad_bala_table_font_size)+'pt')
                table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
                table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                row_count = table.rowCount()
                col_count = table.columnCount()
                for row in range(row_count):
                    for col in range(col_count):
                        table.setItem(row,col,QTableWidgetItem(''))
                table.update()
            self.horo_tabs[tab_index+t].setLayout(h_layout)            
    def _init_bhava_bala_tab_widgets(self, tab_index):
        for t in range(_bhava_bala_tab_count):
            self.horo_tabs.append(QWidget())
            self.tabWidget.addTab(self.horo_tabs[tab_index+t],'')
        self._bhava_bala_table = [ QTableWidget(12,3) for _ in range(_bhava_bala_tab_count)] 
        for t in range(_bhava_bala_tab_count):
            h_layout = QHBoxLayout()
            delegate = AlignDelegate(self._bhava_bala_table[t])
            self._bhava_bala_table[t].setItemDelegate(delegate)
            h_layout.addWidget(self._bhava_bala_table[t])
            for table in [self._bhava_bala_table[t]]:
                table.setStyleSheet('font-size:'+str(_bhava_bala_table_font_size)+'pt')
                table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
                table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                row_count = table.rowCount()
                col_count = table.columnCount()
                for row in range(row_count):
                    for col in range(col_count):
                        table.setItem(row,col,QTableWidgetItem(''))
                table.update()
            self.horo_tabs[tab_index+t].setLayout(h_layout)  
    def _init_argala_tab_widgets(self,tab_index):
        v_layout = QVBoxLayout()
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],'')
        self._argala_table1 = QTableWidget(12,4) 
        self._argala_table2 = QTableWidget(12,4) 
        h_layout1 = QHBoxLayout()
        self._argala_chart_combo = QComboBox()
        self._argala_chart_combo.addItems(_chart_names)
        self._argala_chart_combo.SizeAdjustPolicy.AdjustToContents
        self._argala_chart_combo.currentIndexChanged.connect(self._argala_chart_selection_changed)
        h_layout1.addWidget(self._argala_chart_combo)
        self._argala_chart_option_button = QPushButton('Select Chart Options')
        #self._argala_chart_option_button.setFlat(True)
        #self._argala_chart_option_button.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._argala_chart_option_button.clicked.connect(self._show_argala_chart_options)
        self._argala_chart_option_button.setEnabled(False)
        h_layout1.addWidget(self._argala_chart_option_button)
        self._argala_option_info_label = QLabel('')
        self._argala_option_info_label.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._argala_option_info_label.setEnabled(False)
        self._argala_option_info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        h_layout1.addWidget(self._argala_option_info_label)
        v_layout.addLayout(h_layout1)        
        h_layout = QHBoxLayout()
        delegate = AlignDelegate(self._argala_table1)
        self._argala_table1.setItemDelegate(delegate)
        delegate = AlignDelegate(self._argala_table2)
        self._argala_table2.setItemDelegate(delegate)
        h_layout.addWidget(self._argala_table1)
        h_layout.addWidget(self._argala_table2)
        for table in [self._argala_table1, self._argala_table2]:
            table.setStyleSheet('font-size:'+str(_argala_table_font_size)+'pt')
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
            table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            row_count = table.rowCount()
            col_count = table.columnCount()
            for row in range(row_count):
                for col in range(col_count):
                    table.setItem(row,col,QTableWidgetItem(''))
            table.update()
        v_layout.addLayout(h_layout)
        self.horo_tabs[tab_index].setLayout(v_layout)            
        self._current_argala_chart_index = 0
        self._argala_method_index = 1
        self._argala_varga_dict = varga_chart_dialog.get_varga_option_dict()
        self._argala_mixed_dict_1 = self._argala_varga_dict
        self._argala_mixed_dict_2 = self._argala_varga_dict
        self._argala_custom_varga = _custom_varga_index
        self._argala_mixed_chart_index_1 = _mixed_chart_index_1; self._argala_mixed_chart_index_2 = _mixed_chart_index_2
        self._argala_mixed_method_index_1 = _mixed_chart_method_1; self._argala_mixed_method_index_2 = _mixed_chart_method_2
    def _show_argala_chart_options(self):
        self._current_argala_chart_index = self._argala_chart_combo.currentIndex()
        self._argala_option_info_label.setText(self._argala_chart_options_str)
        if self._current_argala_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_argala_chart_index]
            self._argala_method_index = self._argala_varga_dict[varga_index][1]
            self._argala_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._argala_method_index)+'_str']
        elif self._current_argala_chart_index== _custom_chart_index:
            varga_index = self._argala_custom_varga
            self._argala_method_index = self._argala_varga_dict[varga_index][1]
            self._argala_chart_options_str = self.resources['dn_custom_option'+str(self._argala_method_index)+'_str']
        elif self._current_argala_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._argala_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._argala_mixed_chart_index_2]
            self._argala_mixed_method_index_1 = self._argala_mixed_dict_1[v1][1]
            self._argala_mixed_method_index_2 = self._argala_mixed_dict_2[v2][1]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._argala_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._argala_mixed_method_index_2)+'_str']
            self._argala_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
        if self._current_argala_chart_index<=_custom_chart_index:
            dlg = varga_chart_dialog.VargaChartOptionsDialog(chart_index=self._current_argala_chart_index,
                                    chart_method=self._argala_method_index,varga_factor=varga_index,
                                        base_rasi=self._argala_varga_dict[varga_index][2],
                                        count_from_end_of_sign=self._argala_varga_dict[varga_index][3])
            if dlg.exec()==1:
                self._argala_method_index = dlg._method_index
                if dlg._varga_factor != None: varga_index = dlg._varga_factor         
                if self._current_argala_chart_index==_custom_chart_index: self._argala_custom_varga = varga_index
                self._argala_varga_dict[varga_index] = \
                    (self._argala_varga_dict[varga_index][0],dlg._method_index,
                        dlg._base_rasi_index,dlg._count_from_end_of_sign)
                self._update_argala_table_information(self._current_argala_chart_index,self._argala_method_index,
                                        divisional_chart_factor=varga_index,
                                        base_rasi=self._argala_varga_dict[varga_index][2],
                                        count_from_end_of_sign=self._argala_varga_dict[varga_index][3])
            self._argala_chart_options_str = dlg._option_string
            self._drishti_option_info_label.setText(self._drishti_chart_options_str)
        elif self._current_argala_chart_index==_mixed_chart_index:
            v1 = const.division_chart_factors[self._argala_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._argala_mixed_chart_index_2]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._argala_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._argala_mixed_method_index_2)+'_str']
            self._argala_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._argala_option_info_label.setText(self._argala_chart_options_str)
            dlg = mixed_chart_dialog.MixedChartOptionsDialog(chart_index_1=self._argala_mixed_chart_index_1,chart_index_2=self._argala_mixed_chart_index_2,
                                                 chart_method_1=self._argala_mixed_method_index_1,chart_method_2=self._argala_mixed_method_index_2)
            if dlg.exec()==1:
                self._argala_mixed_chart_index_1 = dlg._chart_index_1;self._argala_mixed_chart_index_2 = dlg._chart_index_2
                self._argala_mixed_method_index_1 = dlg._method_index_1;self._argala_mixed_method_index_2 = dlg._method_index_2
                v1 = dlg._varga_factor_1; v2 = dlg._varga_factor_2
                v1s = self.resources['d'+str(v1)+'_option'+str(self._argala_mixed_method_index_1)+'_str']
                v2s = self.resources['d'+str(v2)+'_option'+str(self._argala_mixed_method_index_2)+'_str']
                self._argala_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
                self._argala_option_info_label.setText(self._argala_chart_options_str)
                mds = 'D'+str(v1)+'xD'+ str(v2)+' '
                self._argala_chart_option_button.setText(mds+self.resources['options_str'])
                self._update_argala_table_information(chart_index=self._current_argala_chart_index,
                                                   chart_index_1=dlg._chart_index_1,chart_method_1=dlg._method_index_1,
                                                   chart_index_2=dlg._chart_index_2,chart_method_2=dlg._method_index_2)
    def _argala_chart_selection_changed(self):
        self._current_argala_chart_index = self._argala_chart_combo.currentIndex()
        if self._current_argala_chart_index==0:
            varga_index = 1
            self._argala_method_index = 1
            self._argala_chart_options_str = ''
        elif self._current_argala_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_argala_chart_index]
            self._argala_method_index = self._argala_varga_dict[varga_index][1]
            self._argala_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._argala_method_index)+'_str']
        elif self._current_argala_chart_index == _custom_chart_index:
            varga_index = self._argala_custom_varga
            self._argala_method_index = self._argala_varga_dict[varga_index][1]
            self._argala_chart_options_str = self.resources['dn_custom_option'+str(self._argala_method_index)+'_str']
        elif self._current_argala_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._argala_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._argala_mixed_chart_index_2]
            mds = 'D'+str(v1)+'('+str(self._argala_mixed_method_index_1)+')xD'+ \
                    str(v2)+'('+str(self._argala_mixed_method_index_2)+')'+' '
            v1s = self.resources['d'+str(v1)+'_option'+str(self._argala_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._argala_mixed_method_index_2)+'_str']
            self._argala_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._argala_option_info_label.setText(self._argala_chart_options_str)
        self._argala_option_info_label.setText(self._argala_chart_options_str)
        self._argala_option_info_label.adjustSize()
        if self._current_argala_chart_index==0:
            self._argala_chart_option_button.setEnabled(False);self._argala_chart_option_button.setVisible(False)
            self._argala_option_info_label.setEnabled(False);self._argala_option_info_label.setVisible(False)
        else:
            self._argala_chart_option_button.setEnabled(True);self._argala_chart_option_button.setVisible(True)
            self._argala_option_info_label.setEnabled(True);self._argala_option_info_label.setVisible(True)
        if self._current_argala_chart_index==_mixed_chart_index:
            mds = 'D'+str(v1)+'xD'+ str(v2)+' '
            self._argala_chart_option_button.setText(mds+self.resources['options_str'])
            self._update_argala_table_information(chart_index=self._current_argala_chart_index,
                                chart_index_1=self._argala_mixed_chart_index_1,chart_method_1=self._argala_mixed_method_index_1,
                                chart_index_2=self._argala_mixed_chart_index_2,chart_method_2=self._argala_mixed_method_index_2)
        else:
            self._argala_chart_option_button.setText(self._argala_chart_combo.currentText()+' '+self.resources['options_str'])
            if self._current_argala_chart_index==_custom_chart_index:
                self._argala_chart_option_button.setText('D'+str(varga_index)+' '+self.resources['options_str'])
            self._update_argala_table_information(self._current_argala_chart_index,self._argala_method_index,
                                    divisional_chart_factor=varga_index,
                                    base_rasi=self._argala_varga_dict[varga_index][2],
                                    count_from_end_of_sign=self._argala_varga_dict[varga_index][3])
    def _init_shodhaya_tab_widgets(self,tab_index):
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],'')
        v_layout = QVBoxLayout()
        h_layout1 = QHBoxLayout()
        self._shodhaya_chart_combo = QComboBox()
        self._shodhaya_chart_combo.addItems(_chart_names)
        self._shodhaya_chart_combo.SizeAdjustPolicy.AdjustToContents
        self._shodhaya_chart_combo.currentIndexChanged.connect(self._shodhaya_chart_selection_changed)
        h_layout1.addWidget(self._shodhaya_chart_combo)
        self._shodhaya_chart_option_button = QPushButton('Select Chart Options')
        #self._shodhaya_chart_option_button.setFlat(True)
        #self._shodhaya_chart_option_button.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._shodhaya_chart_option_button.clicked.connect(self._show_shodhaya_chart_options)
        self._shodhaya_chart_option_button.setEnabled(False)
        h_layout1.addWidget(self._shodhaya_chart_option_button)
        self._shodhaya_option_info_label = QLabel('')
        self._shodhaya_option_info_label.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._shodhaya_option_info_label.setEnabled(False)
        self._shodhaya_option_info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        h_layout1.addWidget(self._shodhaya_option_info_label)
        v_layout.addLayout(h_layout1)        
        self._shodhaya_table1 = QTableWidget(9,12) 
        self._shodhaya_table_label1 = QLabel() 
        self._shodhaya_table2 = QTableWidget(3,7) 
        self._shodhaya_table_label2 = QLabel() 
        """ create tables in shodhaya tab """
        self._shodhaya_table_label1.setText('Ashtaka Varga (After reduction)')
        delegate = AlignDelegate(self._shodhaya_table1)
        self._shodhaya_table1.setItemDelegate(delegate)
        self._shodhaya_table_label2.setText('Ashtaka Varga (Shodhaya Pinda)')
        delegate = AlignDelegate(self._shodhaya_table2)
        self._shodhaya_table2.setItemDelegate(delegate)
        v_layout.addWidget(self._shodhaya_table_label1)
        v_layout.addWidget(self._shodhaya_table1)
        v_layout.addWidget(self._shodhaya_table_label2)
        v_layout.addWidget(self._shodhaya_table2)
        for table in [self._shodhaya_table1, self._shodhaya_table2]:
            table.setStyleSheet('font-size:'+str(_shodhaya_table_font_size)+'pt')
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
            table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            row_count = table.rowCount()
            col_count = table.columnCount()
            for row in range(row_count):
                for col in range(col_count):
                    table.setItem(row,col,QTableWidgetItem(str(0)))                
        self.horo_tabs[tab_index].setLayout(v_layout) 
        self._current_shodhaya_chart_index = 0
        self._shodhaya_method_index = 1
        self._shodhaya_varga_dict = varga_chart_dialog.get_varga_option_dict()
        self._shodhaya_mixed_dict_1 = self._shodhaya_varga_dict
        self._shodhaya_mixed_dict_2 = self._shodhaya_varga_dict
        self._shodhaya_custom_varga = _custom_varga_index
        self._shodhaya_mixed_chart_index_1 = _mixed_chart_index_1; self._shodhaya_mixed_chart_index_2 = _mixed_chart_index_2
        self._shodhaya_mixed_method_index_1 = _mixed_chart_method_1; self._shodhaya_mixed_method_index_2 = _mixed_chart_method_2
    def _show_shodhaya_chart_options(self):
        self._current_shodhaya_chart_index = self._shodhaya_chart_combo.currentIndex()
        self._shodhaya_option_info_label.setText(self._shodhaya_chart_options_str)
        if self._current_shodhaya_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_shodhaya_chart_index]
            self._shodhaya_method_index = self._shodhaya_varga_dict[varga_index][1]
            self._shodhaya_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._shodhaya_method_index)+'_str']
        elif self._current_shodhaya_chart_index== _custom_chart_index:
            varga_index = self._shodhaya_custom_varga
            self._shodhaya_method_index = self._shodhaya_varga_dict[varga_index][1]
            self._shodhaya_chart_options_str = self.resources['dn_custom_option'+str(self._shodhaya_method_index)+'_str']
        elif self._current_shodhaya_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._shodhaya_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._shodhaya_mixed_chart_index_2]
            self._shodhaya_mixed_method_index_1 = self._shodhaya_mixed_dict_1[v1][1]
            self._shodhaya_mixed_method_index_2 = self._shodhaya_mixed_dict_2[v2][1]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._shodhaya_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._shodhaya_mixed_method_index_2)+'_str']
            self._shodhaya_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
        if self._current_shodhaya_chart_index<=_custom_chart_index:
            dlg = varga_chart_dialog.VargaChartOptionsDialog(chart_index=self._current_shodhaya_chart_index,
                                    chart_method=self._shodhaya_method_index,varga_factor=varga_index,
                                        base_rasi=self._shodhaya_varga_dict[varga_index][2],
                                        count_from_end_of_sign=self._shodhaya_varga_dict[varga_index][3])
            if dlg.exec()==1:
                self._shodhaya_method_index = dlg._method_index
                if dlg._varga_factor != None: varga_index = dlg._varga_factor         
                if self._current_shodhaya_chart_index==_custom_chart_index: self._shodhaya_custom_varga = varga_index
                self._shodhaya_varga_dict[varga_index] = \
                    (self._shodhaya_varga_dict[varga_index][0],dlg._method_index,
                        dlg._base_rasi_index,dlg._count_from_end_of_sign)
                self._update_shodhaya_table_information(self._current_shodhaya_chart_index,self._shodhaya_method_index,
                                        divisional_chart_factor=varga_index,
                                        base_rasi=self._shodhaya_varga_dict[varga_index][2],
                                        count_from_end_of_sign=self._shodhaya_varga_dict[varga_index][3])
            self._shodhaya_chart_options_str = dlg._option_string
            self._shodhaya_option_info_label.setText(self._shodhaya_chart_options_str)
        elif self._current_shodhaya_chart_index==_mixed_chart_index:
            v1 = const.division_chart_factors[self._shodhaya_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._shodhaya_mixed_chart_index_2]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._shodhaya_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._shodhaya_mixed_method_index_2)+'_str']
            self._shodhaya_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._shodhaya_option_info_label.setText(self._shodhaya_chart_options_str)
            dlg = mixed_chart_dialog.MixedChartOptionsDialog(chart_index_1=self._shodhaya_mixed_chart_index_1,chart_index_2=self._shodhaya_mixed_chart_index_2,
                                                 chart_method_1=self._shodhaya_mixed_method_index_1,chart_method_2=self._shodhaya_mixed_method_index_2)
            if dlg.exec()==1:
                self._shodhaya_mixed_chart_index_1 = dlg._chart_index_1;self._shodhaya_mixed_chart_index_2 = dlg._chart_index_2
                self._shodhaya_mixed_method_index_1 = dlg._method_index_1;self._shodhaya_mixed_method_index_2 = dlg._method_index_2
                v1 = dlg._varga_factor_1; v2 = dlg._varga_factor_2
                v1s = self.resources['d'+str(v1)+'_option'+str(self._shodhaya_mixed_method_index_1)+'_str']
                v2s = self.resources['d'+str(v2)+'_option'+str(self._shodhaya_mixed_method_index_2)+'_str']
                self._shodhaya_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
                self._shodhaya_option_info_label.setText(self._shodhaya_chart_options_str)
                mds = 'D'+str(v1)+'xD'+ str(v2)+' '
                self._shodhaya_chart_option_button.setText(mds+self.resources['options_str'])
                self._update_shodhaya_table_information(chart_index=self._current_shodhaya_chart_index,
                                                   chart_index_1=dlg._chart_index_1,chart_method_1=dlg._method_index_1,
                                                   chart_index_2=dlg._chart_index_2,chart_method_2=dlg._method_index_2)
    def _shodhaya_chart_selection_changed(self):
        self._current_shodhaya_chart_index = self._shodhaya_chart_combo.currentIndex()
        if self._current_shodhaya_chart_index==0:
            varga_index = 1
            self._shodhaya_method_index = 1
            self._shodhaya_chart_options_str = ''
        elif self._current_shodhaya_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_shodhaya_chart_index]
            self._shodhaya_method_index = self._shodhaya_varga_dict[varga_index][1]
            self._shodhaya_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._shodhaya_method_index)+'_str']
        elif self._current_shodhaya_chart_index == _custom_chart_index:
            varga_index = self._shodhaya_custom_varga
            self._shodhaya_method_index = self._shodhaya_varga_dict[varga_index][1]
            self._shodhaya_chart_options_str = self.resources['dn_custom_option'+str(self._shodhaya_method_index)+'_str']
        elif self._current_shodhaya_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._shodhaya_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._shodhaya_mixed_chart_index_2]
            mds = 'D'+str(v1)+'('+str(self._shodhaya_mixed_method_index_1)+')xD'+ \
                    str(v2)+'('+str(self._shodhaya_mixed_method_index_2)+')'+' '
            v1s = self.resources['d'+str(v1)+'_option'+str(self._shodhaya_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._shodhaya_mixed_method_index_2)+'_str']
            self._shodhaya_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._shodhaya_option_info_label.setText(self._shodhaya_chart_options_str)
        self._shodhaya_option_info_label.setText(self._shodhaya_chart_options_str)
        self._shodhaya_option_info_label.adjustSize()
        if self._current_shodhaya_chart_index==0:
            self._shodhaya_chart_option_button.setEnabled(False);self._shodhaya_chart_option_button.setVisible(False)
            self._shodhaya_option_info_label.setEnabled(False);self._shodhaya_option_info_label.setVisible(False)
        else:
            self._shodhaya_chart_option_button.setEnabled(True);self._shodhaya_chart_option_button.setVisible(True)
            self._shodhaya_option_info_label.setEnabled(True);self._shodhaya_option_info_label.setVisible(True)
        if self._current_shodhaya_chart_index==_mixed_chart_index:
            mds = 'D'+str(v1)+'xD'+ str(v2)+' '
            self._shodhaya_chart_option_button.setText(mds+self.resources['options_str'])
            self._update_shodhaya_table_information(chart_index=self._current_shodhaya_chart_index,
                                chart_index_1=self._shodhaya_mixed_chart_index_1,chart_method_1=self._shodhaya_mixed_method_index_1,
                                chart_index_2=self._shodhaya_mixed_chart_index_2,chart_method_2=self._shodhaya_mixed_method_index_2)
        else:
            self._shodhaya_chart_option_button.setText(self._shodhaya_chart_combo.currentText()+' '+self.resources['options_str'])
            if self._current_shodhaya_chart_index==_custom_chart_index:
                self._shodhaya_chart_option_button.setText('D'+str(varga_index)+' '+self.resources['options_str'])
            self._update_shodhaya_table_information(self._current_shodhaya_chart_index,self._shodhaya_method_index,
                                    divisional_chart_factor=varga_index,
                                    base_rasi=self._shodhaya_varga_dict[varga_index][2],
                                    count_from_end_of_sign=self._shodhaya_varga_dict[varga_index][3])
    def _init_ashtaka_tab_widgets(self, tab_index):
        c = 0
        v_layout = QVBoxLayout()
        h_layout1 = QHBoxLayout()
        self._ashtaka_chart_combo = QComboBox()
        self._ashtaka_chart_combo.addItems(_chart_names)
        self._ashtaka_chart_combo.SizeAdjustPolicy.AdjustToContents
        self._ashtaka_chart_combo.currentIndexChanged.connect(self._ashtaka_chart_selection_changed)
        h_layout1.addWidget(self._ashtaka_chart_combo)
        self._ashtaka_chart_option_button = QPushButton('Select Chart Options')
        #self._ashtaka_chart_option_button.setFlat(True)
        #self._ashtaka_chart_option_button.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._ashtaka_chart_option_button.clicked.connect(self._show_ashtaka_chart_options)
        self._ashtaka_chart_option_button.setEnabled(False)
        h_layout1.addWidget(self._ashtaka_chart_option_button)
        self._ashtaka_option_info_label = QLabel('')
        self._ashtaka_option_info_label.setStyleSheet("border: 2px solid black;font-size:12px; font-weight:bold;")
        self._ashtaka_option_info_label.setEnabled(False)
        self._ashtaka_option_info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        h_layout1.addWidget(self._ashtaka_option_info_label)
        v_layout.addLayout(h_layout1)        
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],'')
        """ create 9x9 chart grid. 1st one SAV and others are 8 planet BAV """
        self._ashtaka_grid_layout = QGridLayout()
        """ Sudarsana Chakra Chart does not Asktaka Varga Chart - So Force North Indian """
        __chart_type = available_chart_types[self._chart_type]
        if 'sudar' in self._chart_type.lower():
            __chart_type = available_chart_types['north_indian']
        self._ashtaka_charts =[(__chart_type(chart_size_factor=_ashtaka_chart_size_factor)) for i in range(9)]
        ac = 0
        for i in range(3):
            for j in range(3):
                self._ashtaka_grid_layout.addWidget(self._ashtaka_charts[ac],i,j)
                ac+=1
        self._ashtaka_grid_layout.setSpacing(0)
        v_layout.addLayout(self._ashtaka_grid_layout)
        self.horo_tabs[tab_index].setLayout(v_layout)        
        self._current_ashtaka_chart_index = 0
        self._ashtaka_method_index = 1
        self._ashtaka_varga_dict = varga_chart_dialog.get_varga_option_dict()
        self._ashtaka_mixed_dict_1 = self._ashtaka_varga_dict
        self._ashtaka_mixed_dict_2 = self._ashtaka_varga_dict
        self._ashtaka_custom_varga = _custom_varga_index
        self._ashtaka_mixed_chart_index_1 = _mixed_chart_index_1; self._ashtaka_mixed_chart_index_2 = _mixed_chart_index_2
        self._ashtaka_mixed_method_index_1 = _mixed_chart_method_1; self._ashtaka_mixed_method_index_2 = _mixed_chart_method_2
    def _show_ashtaka_chart_options(self):
        self._current_ashtaka_chart_index = self._ashtaka_chart_combo.currentIndex()
        self._ashtaka_option_info_label.setText(self._ashtaka_chart_options_str)
        if self._current_ashtaka_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_ashtaka_chart_index]
            self._ashtaka_method_index = self._ashtaka_varga_dict[varga_index][1]
            self._ashtaka_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._ashtaka_method_index)+'_str']
        elif self._current_ashtaka_chart_index== _custom_chart_index:
            varga_index = self._ashtaka_custom_varga
            self._ashtaka_method_index = self._ashtaka_varga_dict[varga_index][1]
            self._ashtaka_chart_options_str = self.resources['dn_custom_option'+str(self._ashtaka_method_index)+'_str']
        elif self._current_ashtaka_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._ashtaka_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._ashtaka_mixed_chart_index_2]
            self._ashtaka_mixed_method_index_1 = self._ashtaka_mixed_dict_1[v1][1]
            self._ashtaka_mixed_method_index_2 = self._ashtaka_mixed_dict_2[v2][1]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._ashtaka_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._ashtaka_mixed_method_index_2)+'_str']
            self._ashtaka_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
        if self._current_ashtaka_chart_index<=_custom_chart_index:
            dlg = varga_chart_dialog.VargaChartOptionsDialog(chart_index=self._current_ashtaka_chart_index,
                                    chart_method=self._ashtaka_method_index,varga_factor=varga_index,
                                        base_rasi=self._ashtaka_varga_dict[varga_index][2],
                                        count_from_end_of_sign=self._ashtaka_varga_dict[varga_index][3])
            if dlg.exec()==1:
                self._ashtaka_method_index = dlg._method_index
                if dlg._varga_factor != None: varga_index = dlg._varga_factor         
                if self._current_ashtaka_chart_index==_custom_chart_index: self._ashtaka_custom_varga = varga_index
                self._ashtaka_varga_dict[varga_index] = \
                    (self._ashtaka_varga_dict[varga_index][0],dlg._method_index,
                        dlg._base_rasi_index,dlg._count_from_end_of_sign)
                self._update_ashtaka_varga_tab_information(self._current_ashtaka_chart_index,self._ashtaka_method_index,
                                        divisional_chart_factor=varga_index,
                                        base_rasi=self._ashtaka_varga_dict[varga_index][2],
                                        count_from_end_of_sign=self._ashtaka_varga_dict[varga_index][3])
            self._ashtaka_chart_options_str = dlg._option_string
            self._ashtaka_option_info_label.setText(self._ashtaka_chart_options_str)
        elif self._current_ashtaka_chart_index==_mixed_chart_index:
            v1 = const.division_chart_factors[self._ashtaka_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._ashtaka_mixed_chart_index_2]
            v1s = self.resources['d'+str(v1)+'_option'+str(self._ashtaka_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._ashtaka_mixed_method_index_2)+'_str']
            self._ashtaka_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._ashtaka_option_info_label.setText(self._ashtaka_chart_options_str)
            dlg = mixed_chart_dialog.MixedChartOptionsDialog(chart_index_1=self._ashtaka_mixed_chart_index_1,chart_index_2=self._ashtaka_mixed_chart_index_2,
                                                 chart_method_1=self._ashtaka_mixed_method_index_1,chart_method_2=self._ashtaka_mixed_method_index_2)
            if dlg.exec()==1:
                self._ashtaka_mixed_chart_index_1 = dlg._chart_index_1;self._ashtaka_mixed_chart_index_2 = dlg._chart_index_2
                self._ashtaka_mixed_method_index_1 = dlg._method_index_1;self._ashtaka_mixed_method_index_2 = dlg._method_index_2
                v1 = dlg._varga_factor_1; v2 = dlg._varga_factor_2
                v1s = self.resources['d'+str(v1)+'_option'+str(self._ashtaka_mixed_method_index_1)+'_str']
                v2s = self.resources['d'+str(v2)+'_option'+str(self._ashtaka_mixed_method_index_2)+'_str']
                self._ashtaka_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
                self._ashtaka_option_info_label.setText(self._ashtaka_chart_options_str)
                mds = 'D'+str(v1)+'xD'+ str(v2)+' '
                self._ashtaka_chart_option_button.setText(mds+self.resources['options_str'])
                self._update_ashtaka_varga_tab_information(chart_index=self._current_kundali_chart_index,
                                                   chart_index_1=dlg._chart_index_1,chart_method_1=dlg._method_index_1,
                                                   chart_index_2=dlg._chart_index_2,chart_method_2=dlg._method_index_2)
    def _ashtaka_chart_selection_changed(self):
        self._current_ashtaka_chart_index = self._ashtaka_chart_combo.currentIndex()
        if self._current_ashtaka_chart_index==0:
            varga_index = 1
            self._ashtaka_method_index = 1
            self._ashtaka_chart_options_str = ''
        elif self._current_ashtaka_chart_index < _custom_chart_index:
            varga_index = const.division_chart_factors[self._current_ashtaka_chart_index]
            self._ashtaka_method_index = self._ashtaka_varga_dict[varga_index][1]
            self._ashtaka_chart_options_str = self.resources['d'+str(varga_index)+'_option'+str(self._ashtaka_method_index)+'_str']
        elif self._current_ashtaka_chart_index == _custom_chart_index:
            varga_index = self._ashtaka_custom_varga
            self._ashtaka_method_index = self._ashtaka_varga_dict[varga_index][1]
            self._ashtaka_chart_options_str = self.resources['dn_custom_option'+str(self._ashtaka_method_index)+'_str']
        elif self._current_ashtaka_chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[self._ashtaka_mixed_chart_index_1]
            v2 = const.division_chart_factors[self._ashtaka_mixed_chart_index_2]
            mds = 'D'+str(v1)+'('+str(self._ashtaka_mixed_method_index_1)+')xD'+ \
                    str(v2)+'('+str(self._ashtaka_mixed_method_index_2)+')'+' '
            v1s = self.resources['d'+str(v1)+'_option'+str(self._ashtaka_mixed_method_index_1)+'_str']
            v2s = self.resources['d'+str(v2)+'_option'+str(self._ashtaka_mixed_method_index_2)+'_str']
            self._ashtaka_chart_options_str = 'D'+str(v1)+':'+v1s+'<br>'+'D'+str(v2)+':'+v2s
            self._ashtaka_option_info_label.setText(self._ashtaka_chart_options_str)
        self._ashtaka_option_info_label.setText(self._ashtaka_chart_options_str)
        self._ashtaka_option_info_label.adjustSize()
        if self._current_ashtaka_chart_index==0:
            self._ashtaka_chart_option_button.setEnabled(False);self._ashtaka_chart_option_button.setVisible(False)
            self._ashtaka_option_info_label.setEnabled(False);self._ashtaka_option_info_label.setVisible(False)
        else:
            self._ashtaka_chart_option_button.setEnabled(True);self._ashtaka_chart_option_button.setVisible(True)
            self._ashtaka_option_info_label.setEnabled(True);self._ashtaka_option_info_label.setVisible(True)
        if self._current_ashtaka_chart_index==_mixed_chart_index:
            mds = 'D'+str(v1)+'xD'+ str(v2)+' '
            self._ashtaka_chart_option_button.setText(mds+self.resources['options_str'])
            self._update_ashtaka_varga_tab_information(chart_index=self._current_ashtaka_chart_index,
                                chart_index_1=self._ashtaka_mixed_chart_index_1,chart_method_1=self._ashtaka_mixed_method_index_1,
                                chart_index_2=self._ashtaka_mixed_chart_index_2,chart_method_2=self._ashtaka_mixed_method_index_2)
        else:
            self._ashtaka_chart_option_button.setText(self._ashtaka_chart_combo.currentText()+' '+self.resources['options_str'])
            if self._current_ashtaka_chart_index==_custom_chart_index:
                self._ashtaka_chart_option_button.setText('D'+str(varga_index)+' '+self.resources['options_str'])
            self._update_ashtaka_varga_tab_information(self._current_ashtaka_chart_index,self._ashtaka_method_index,
                                    divisional_chart_factor=varga_index,
                                    base_rasi=self._ashtaka_varga_dict[varga_index][2],
                                    count_from_end_of_sign=self._ashtaka_varga_dict[varga_index][3])        
    def _init_main_window(self):
        self._footer_title = ''
        self.setWindowIcon(QtGui.QIcon(const._IMAGE_ICON_PATH))
        self._language = list(available_languages.keys())[0]#list(available_languages.keys())[0]
        ci = _index_containing_substring(available_chart_types.keys(),self._chart_type.lower())
        if ci >=0:
            self._chart_type = list(available_chart_types.keys())[ci]
            self._bhava_chart_type = 'south_indian' if 'west' in self._chart_type.lower() else self._chart_type
        self.setFixedSize(_main_window_width,_main_window_height)
        self.showMaximized()
        #self.setMinimumSize(_main_window_width,_main_window_height)        
    def _create_row1_ui(self):
        self._row1_h_layout = QHBoxLayout()
        self._name_label = QLabel("Name:")
        self._row1_h_layout.addWidget(self._name_label)
        self._name_text = QLineEdit("Today")
        self._name = self._name_text.text()
        self._name_text.setToolTip('Enter your name')
        self._row1_h_layout.addWidget(self._name_text)
        self._gender_combo = QComboBox()
        self._gender_combo.addItems(['Female','Male','Transgender','No preference'])
        self._gender_combo.setCurrentText('Female')
        self._gender_combo.currentIndexChanged.connect(self._gender_changed)
        #self._gender_index = self._gender_combo.currentIndex()
        self._row1_h_layout.addWidget(self._gender_combo)
        self._place_label = QLabel("Place:")
        self._row1_h_layout.addWidget(self._place_label)
        self._place_name = ''
        self._place_text = QLineEdit(self._place_name)
        completer = QCompleter(utils.world_cities_dict.keys())
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self._place_text.setCompleter(completer)
        self._place_text.textChanged.connect(self._resize_place_text_size)
        if self.use_internet_for_location_check: self._place_text.editingFinished.connect(lambda : self._get_location(self._place_text.text()))
        self._place_text.setToolTip('Enter place of birth, country name')
        self._row1_h_layout.addWidget(self._place_text)
        self._lat_label = QLabel("Latidude:")
        self._row1_h_layout.addWidget(self._lat_label)
        self._lat_text = QLineEdit('')
        self._latitude = 0.0
        self._lat_text.setToolTip('Enter Latitude preferably exact at place of birth: Format: +/- xx.xxx')
        self._row1_h_layout.addWidget(self._lat_text)
        self._long_label = QLabel("Longitude:")
        self._row1_h_layout.addWidget(self._long_label)
        self._long_text = QLineEdit('')
        self._longitude = 0.0
        self._long_text.setToolTip('Enter Longitude preferably exact at place of birth. Format +/- xx.xxx')
        self._row1_h_layout.addWidget(self._long_text)
        self._tz_label = QLabel("Time Zone:")
        self._row1_h_layout.addWidget(self._tz_label)
        self._tz_text = QLineEdit('')
        self._time_zone = 0.0
        self._tz_text.setToolTip('Enter Time offset from GMT e.g. -5.5 or 4.5')
        self._row1_h_layout.addWidget(self._tz_text)
        if not self._validate_ui() and self.use_internet_for_location_check:
            #""" Initialize with default place based on IP"""
            loc = utils.get_place_from_user_ip_address()
            if len(loc)==4:
                self.place(loc[0],loc[1],loc[2],loc[3])
        self._v_layout.addLayout(self._row1_h_layout)
    def _gender_changed(self):
        self._gender_index = self._gender_combo.currentIndex()
        self._show_compatibility = False
        if self._gender_index in [0,1]:
            self._show_compatibility = True
    def _create_row_3_ui(self):
        self._row3_h_layout = QHBoxLayout()
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(available_languages.keys())
        self._lang_combo.setCurrentText(self._language)
        self._lang_combo.setToolTip('Choose language for display')
        self._lang_combo.activated.connect(self._update_main_window_label_and_tooltips)
        self._row3_h_layout.addWidget(self._lang_combo)
        self._pravesha_combo = QComboBox()
        self._pravesha_combo.addItems(const._PRAVESHA_LIST)
        self._pravesha_combo.setCurrentIndex(0)
        self._pravesha_combo.setToolTip('Choose type of Pravesha (Janma, annual, tithi, present)')
        #self._pravesha_combo.currentIndexChanged.connect(self._enable_disable_annual_ui)
        self._pravesha_combo.activated.connect(self._enable_disable_annual_ui)
        self._row3_h_layout.addWidget(self._pravesha_combo)
        self._compute_button = QPushButton("Show Chart")
        self._compute_button.setFont(QtGui.QFont("Arial Bold",9))
        self._compute_button.clicked.connect(lambda: self.compute_horoscope(calculation_type=self._calculation_type))
        self._compute_button.setToolTip('Click to update the chart information based on selections made')
        self._row3_h_layout.addWidget(self._compute_button)
        self._save_image_button = QPushButton("Save as PDF")
        self._save_image_button.setFont(QtGui.QFont("Arial Bold",8))
        self._save_image_button.clicked.connect(lambda : self.save_as_pdf(pdf_file_name=None))
        self._save_image_button.setToolTip('Click to save horoscope as a PDF')
        self._row3_h_layout.addWidget(self._save_image_button)
        self._save_city_button = QPushButton("Save City")
        self._save_city_button.clicked.connect(self._save_city_to_database)
        self._save_city_button.setToolTip('Click to save the city information in csv database')
        self._row3_h_layout.addWidget(self._save_city_button)
    def _create_row_2_and_3_ui(self):
        v_layout = QVBoxLayout()
        self._row2_h_layout = QHBoxLayout()
        self._dob_label = QLabel("Date of Birth:")
        self._row2_h_layout.addWidget(self._dob_label)
        self._date_of_birth = ''
        self._dob_text = QLineEdit(self._date_of_birth)
        self._dob_text.setToolTip('Date of birth in the format YYYY,MM,DD\nFor BC enter negative years.\nAllowed Year Range: -13000 (BC) to 16800 (AD)')
        self._dob_label.setMaximumWidth(_row3_widget_width)
        self._dob_text.setMaximumWidth(_row3_widget_width)
        self._row2_h_layout.addWidget(self._dob_text)
        self._tob_label = QLabel("Time of Birth:")
        self._row2_h_layout.addWidget(self._tob_label)
        self._time_of_birth = ''
        self._tob_text = QLineEdit(self._time_of_birth)
        self._tob_text.setToolTip('Enter time of birth in the format HH:MM:SS if afternoon use 12+ hours')
        self._tob_label.setMaximumWidth(_row3_widget_width)
        self._tob_text.setMaximumWidth(_row3_widget_width)
        current_date_str,current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
        self.date_of_birth(current_date_str)
        self.time_of_birth(current_time_str)
        self._row2_h_layout.addWidget(self._tob_text)
        #"""
        self._years_label=QLabel('Years')
        self._row2_h_layout.addWidget(self._years_label)
        self._years_combo = QSpinBox()
        self._years_combo.setRange(1,100)
        self._years_combo.setSingleStep(1)
        self._years_combo.setValue(1)
        self._row2_h_layout.addWidget(self._years_combo)
        self._months_label=QLabel('Months')
        self._row2_h_layout.addWidget(self._months_label)
        self._months_combo = QSpinBox()
        self._months_combo.setRange(1,12)
        self._months_combo.setSingleStep(1)
        self._months_combo.setValue(1)
        self._row2_h_layout.addWidget(self._months_combo)
        self._60hrs_label=QLabel('60 Hrs')
        self._row2_h_layout.addWidget(self._60hrs_label)
        self._60hrs_combo = QSpinBox()
        self._60hrs_combo.setRange(1,12)
        self._60hrs_combo.setSingleStep(1)
        self._60hrs_combo.setValue(1)
        self._row2_h_layout.addWidget(self._60hrs_combo)
        #"""
        self._chart_type_combo = QComboBox()
        self._chart_type_combo.addItems(available_chart_types.keys())
        self._chart_type_combo.setToolTip('Choose birth chart style north, south or east indian')
        self._chart_type_combo.setCurrentText(self._chart_type)
        self._chart_type_combo.setMaximumWidth(_row3_widget_width)
        self._row2_h_layout.addWidget(self._chart_type_combo)
        self._ayanamsa_combo = QComboBox()
        self._ayanamsa_combo.addItems(_available_ayanamsa_modes)
        self._ayanamsa_mode = "LAHIRI"
        self._ayanamsa_combo.setCurrentText(self._ayanamsa_mode)
        self._ayanamsa_combo.activated.connect(self._ayanamsa_selection_changed)
        self._ayanamsa_combo.setToolTip('Choose Ayanamsa mode from the list')
        self._ayanamsa_value = None
        self._row2_h_layout.addWidget(self._ayanamsa_combo)
        v_layout.addLayout(self._row2_h_layout)
        self._create_row_3_ui()
        v_layout.addLayout(self._row3_h_layout)
        self._v_layout.addLayout(v_layout)
    def _create_comp_ui(self):
        self._comp_h_layout = QHBoxLayout()
        self._show_marriage_checkboxes = True # V2.6.1
        self._mahendra_porutham_checkbox = QCheckBox()
        self._mahendra_porutham_checkbox.setChecked(False)
        self._mahendra_porutham = self._mahendra_porutham_checkbox.isChecked()
        self._comp_h_layout.addWidget(self._mahendra_porutham_checkbox)
        self._vedha_porutham_checkbox = QCheckBox()
        self._vedha_porutham_checkbox.setChecked(False)
        self._vedha_porutham = self._vedha_porutham_checkbox.isChecked()
        self._comp_h_layout.addWidget(self._vedha_porutham_checkbox)
        self._rajju_porutham_checkbox = QCheckBox()
        self._rajju_porutham_checkbox.setChecked(False)
        self._rajju_porutham = self._rajju_porutham_checkbox.isChecked()
        self._comp_h_layout.addWidget(self._rajju_porutham_checkbox)
        self._sthree_dheerga_porutham_checkbox = QCheckBox()
        self._sthree_dheerga_porutham_checkbox.setChecked(False)
        self._sthree_dheerga_porutham = self._sthree_dheerga_porutham_checkbox.isChecked()
        self._comp_h_layout.addWidget(self._sthree_dheerga_porutham_checkbox)
        self._min_score_label = QLabel('')
        self._comp_h_layout.addWidget(self._min_score_label)
        self._min_score_combo = QDoubleSpinBox()
        if 'south' in self._chart_type.lower():
            self._min_score_combo.setValue(const.compatibility_minimum_score_south)
            self._min_score_combo.setRange(0.0,const.compatibility_maximum_score_south)
            self._min_score_combo.setSingleStep(1.0)
        else:
            self._min_score_combo.setValue(const.compatibility_minimum_score_north)
            self._min_score_combo.setRange(0.0,const.compatibility_maximum_score_north)
            self._min_score_combo.setSingleStep(0.5)
        self._comp_h_layout.addWidget(self._min_score_combo)
        self._v_layout.addLayout(self._comp_h_layout)
        self._comp_h_layout = QHBoxLayout()
        self._show_hide_marriage_checkboxes(True)
        self._v_layout.addLayout(self._comp_h_layout)
    def _show_dhasa_options(self):
        self._dhasa_option_info_label.setText(self._dhasa_bhukthi_options_str[self._current_dhasa_index])
        tab_str = self._dhasa_combo.currentText()
        if tab_str not in [self.resources['karaka_str'],self.resources['kaala_str']]:
            dlg = dhasa_bhukthi_options_dialog.DhasaBhukthiOptionDialog(self._current_dhasa_index, self._dhasa_options_list[self._current_dhasa_index])
            if dlg.exec()==1:
                self._dhasa_bhukthi_options_str[self._current_dhasa_index] = dlg._option_string
                self._dhasa_options_list[self._current_dhasa_index] = dlg._option_list
                self._dhasa_option_info_label.setText(self._dhasa_bhukthi_options_str[self._current_dhasa_index])
                self._update_dhasa_bhukthi_tab_information()
    def _show_vratha_finder_dialog(self):
        year,month,day = self._date_of_birth.split(","); dob = (int(year),int(month),int(day))
        #tob = tuple([int(x) for x in self._tob_text.text().split(':')])
        tob = tuple([int(x) for x in self._time_of_birth.split(':')])
        place = drik.Place(self._place_text.text(),float(self._lat_text.text()),float(self._long_text.text()),float(self._tz_text.text()))
        jd_at_dob = utils.julian_day_number(dob, tob)
        dlg = vratha_finder.VrathaFinderDialog(jd_at_dob,place)
        self._conjunction_dialog_accepted = False
        if dlg.exec()==1:
            self._conjunction_dialog_accepted = dlg._accept_clicked
            vrath_jd = dlg._selection_date_jd
            y,m,d,fh = utils.jd_to_gregorian(vrath_jd)
            self._date_of_birth = str(y)+','+str(m)+','+str(d)
            self._time_of_birth = ':'.join([str(x) for x in utils.to_dms(fh,as_string=False)])
        else:
            # Reset   pravesha_combo selection to 0
            self._pravesha_combo.setCurrentIndex(0)
            self.compute_horoscope(self._calculation_type)           
    def _show_conjunction_dialog(self,entry_type=0,chart_title=''):
        #year,month,day = self._dob_text.text().split(","); dob = (int(year),int(month),int(day))
        year,month,day = self._date_of_birth.split(","); dob = (int(year),int(month),int(day))
        #tob = tuple([int(x) for x in self._tob_text.text().split(':')])
        tob = tuple([int(x) for x in self._time_of_birth.split(':')])
        place = drik.Place(self._place_text.text(),float(self._lat_text.text()),float(self._long_text.text()),float(self._tz_text.text()))
        jd_at_dob = utils.julian_day_number(dob, tob)
        dlg = conjunction_dialog.ConjunctionDialog(jd_at_dob,place,entry_type=entry_type,chart_title=utils.resource_strings[chart_title])
        self._conjunction_dialog_accepted = False
        if dlg.exec()==1:
            self._conjunction_dialog_accepted = dlg._accept_clicked
            conj_jd = dlg._conjunction_date_jd
            y,m,d,fh = utils.jd_to_gregorian(conj_jd)
            self._date_of_birth = str(y)+','+str(m)+','+str(d)
            self._time_of_birth = ':'.join([str(x) for x in utils.to_dms(fh,as_string=False)])
            self._conj_planet1 = dlg._planet1
            if entry_type==0:
                self._conj_planet2 = dlg._planet2
                self._separation_angle_list = dlg._sep_angle_list
                self._separation_angle_index = dlg._separation_angle_index
            elif entry_type==1:
                self._conj_raasi = None if dlg._raasi==None else dlg._raasi-1
        else:
            # Reset   pravesha_combo selection to 0
            self._pravesha_combo.setCurrentIndex(0)
            self.compute_horoscope(self._calculation_type)           
    def _enable_disable_annual_ui(self):
        year,month,day = self._dob_text.text().split(",")
        birth_date = drik.Date(int(year),int(month),int(day))
        user_age = min(datetime.now().year - birth_date.year, const.annual_maximum_age) + 1
        dob = (int(year),int(month),int(day))
        tob = tuple([int(x) for x in self._tob_text.text().split(':')])
        self._birth_julian_day = utils.julian_day_number(dob, tob)
        place = drik.Place(self._place_text.text(),float(self._lat_text.text()),float(self._long_text.text()),float(self._tz_text.text()))
        self._years_combo.setValue(1); self._60hrs_combo.setValue(1); self._months_combo.setValue(1)
        self._years_combo.setEnabled(False); self._months_combo.setEnabled(False); self._60hrs_combo.setEnabled(False)
        if self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('birth_str'):
            self._years = 1; self._60hrs = 1; self._months = 1
            self._years_combo.setEnabled(False); self._months_combo.setEnabled(False); self._60hrs_combo.setEnabled(False)
            self._date_of_birth = self._dob_text.text()
            self._time_of_birth = self._tob_text.text()
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('annual_str'): 
            jd_at_dob = utils.julian_day_number(dob, tob)
            jd_years = drik.next_solar_date(jd_at_dob, place, user_age, self._months, self._60hrs)
            y,m,d,fh = utils.jd_to_gregorian(jd_years)
            self._date_of_birth = str(y)+','+str(m)+','+str(d)
            self._time_of_birth = ':'.join([str(x) for x in utils.to_dms(fh,as_string=False)])
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('tithi_pravesha_str'):
            tp = vratha.tithi_pravesha(birth_date, tob, place, user_age)
            tp_date = tp[0][0]; tp_time = tp[0][1]; tithi_time = tuple(utils.to_dms(tp_time,as_string=False))
            tp_date_new = drik.Date(tp_date[0],tp_date[1],tp_date[2])
            jd_years = utils.julian_day_number(tp_date_new, tithi_time)
            y,m,d,fh = utils.jd_to_gregorian(jd_years)
            self._date_of_birth = str(y)+','+str(m)+','+str(d)
            self._time_of_birth = ':'.join([str(x) for x in utils.to_dms(fh,as_string=False)])
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('present_str'):
            timezone_offset = self._time_zone
            tzinfo = timezone(timedelta(hours=timezone_offset))
            today = datetime.now(tzinfo)
            self._date_of_birth = today.strftime("%Y,%m,%d"); self._time_of_birth = today.strftime("%H:%M:%S")
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('planetary_conjunctions_str') \
                or self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('planet_transit_str') \
                or self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('vakra_gathi_change_str') \
                or self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('lunar_month_year_str'):
            pass
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('prenatal_time_str'):
            jd_at_dob = utils.julian_day_number(dob, tob)
            jd_prenatal = drik._nisheka_time(jd_at_dob, place)
            y,m,d,fh = utils.jd_to_gregorian(jd_prenatal)
            self._date_of_birth = str(y)+','+str(m)+','+str(d)
            self._time_of_birth = ':'.join([str(x) for x in utils.to_dms(fh,as_string=False)])            
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('vrathas_str'):
            timezone_offset = self._time_zone
            tzinfo = timezone(timedelta(hours=timezone_offset))
            today = datetime.now(tzinfo)
            self._date_of_birth = today.strftime("%Y,%m,%d"); self._time_of_birth = today.strftime("%H:%M:%S")
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('customized_str'): 
            jd_at_dob = utils.julian_day_number(dob, tob)
            jd_years = drik.next_solar_date(jd_at_dob, place, self._years, self._months, self._60hrs)
            y,m,d,fh = utils.jd_to_gregorian(jd_years)
            self._date_of_birth = str(y)+','+str(m)+','+str(d)
            self._time_of_birth = ':'.join([str(x) for x in utils.to_dms(fh,as_string=False)])
            self._years_combo.setEnabled(True); self._months_combo.setEnabled(True); self._60hrs_combo.setEnabled(True)
        else:
           # self._years_combo.setValue(1); self._60hrs_combo.setValue(1); self._months_combo.setValue(1)
            self._years_combo.setEnabled(True); self._months_combo.setEnabled(True); self._60hrs_combo.setEnabled(True)
            #self._date_of_birth = self._dob_text.text()
            #self._time_of_birth = self._tob_text.text()
    def _show_lunar_month_dialog(self):
        year,month,day = self._dob_text.text().split(",")
        dob = (int(year),int(month),int(day))
        tob = tuple([int(x) for x in self._tob_text.text().split(':')])
        jd = utils.julian_day_number(dob, tob)
        place = drik.Place(self._place_text.text(),float(self._lat_text.text()),float(self._long_text.text()),float(self._tz_text.text()))
        _title_list = ['amantha','purnimantha','solar']; _lmd_count = 3
        _title = '/'.join([self.resources[ol+'_str'] for ol in _title_list])+' '+self.resources['month_str']+'/'+self.resources['year_str']
        option_list = [[self.resources[ol+'_str']+' '+self.resources['month_str'] for ol in _title_list]+
                       [self.resources[ol+'_str']+' '+self.resources['year_str'] for ol in _title_list],
                       [self.resources[ol+'_str'] for ol in ['previous','next']]
                      ]
        lm_dlg = OptionDialog(title=_title,option_label=self.resources['select_one_of_options_from_str'],
                              options_list=option_list,multi_selection=None,default_options=1)
        self._lunar_month_type = ''
        if lm_dlg.exec()==1:
            _lunar_month_type,_direction = lm_dlg._option_index; _lunar_month_type -= 1
            if _direction == 1:
                direction_string = self.resources['previous_str']+' '
                if _lunar_month_type < _lmd_count:
                    (_lm_year,_lm_month,_lm_day),_lm_hours = drik.previous_lunar_month(jd, place, _lunar_month_type)
                else:
                    (_lm_year,_lm_month,_lm_day),_lm_hours = drik.previous_lunar_year(jd, place, _lunar_month_type-_lmd_count)
            else:
                direction_string = self.resources['next_str']+' '
                if _lunar_month_type < _lmd_count:
                    (_lm_year,_lm_month,_lm_day),_lm_hours = drik.next_lunar_month(jd, place, _lunar_month_type)
                else:
                    (_lm_year,_lm_month,_lm_day),_lm_hours = drik.next_lunar_year(jd, place, _lunar_month_type-_lmd_count)
            self._date_of_birth = str(_lm_year)+','+str(_lm_month)+','+str(_lm_day)
            self._time_of_birth = ':'.join([str(x) for x in utils.to_dms(_lm_hours,as_string=False)])
            if _lunar_month_type < 2: # < 3
                self._lunar_month_type = direction_string+' '+self.resources[_title_list[_lunar_month_type]+'_str']+' '+self.resources['month_str']
            else:
                self._lunar_month_type = direction_string+' '+self.resources[_title_list[_lunar_month_type-_lmd_count]+'_str']+' '+self.resources['year_str']
            #print('lunar year',self._lunar_month_type,self._date_of_birth,self._time_of_birth)
        else:
            self._pravesha_combo.setCurrentIndex(0)
            self.compute_horoscope(self._calculation_type)
    def _add_footer_to_chart(self):
        self._footer_label = QLabel('')
        self._footer_label.setTextFormat(Qt.TextFormat.RichText)
        self._footer_label.setText(self._footer_title)
        self._footer_label.setStyleSheet("border: 1px solid black;")
        self._footer_label.setFont(QtGui.QFont("Arial Bold",_footer_label_font_height))
        self._footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._footer_label.setFixedHeight(_footer_label_height)
        self._footer_label.setFixedWidth(self.width())
        self._footer_label.setWordWrap(True)
        self._footer_label.setOpenExternalLinks(True)
        self._v_layout.addWidget(self._footer_label)
    def _on_application_exit(self):
        def except_hook(cls, exception, traceback):
            sys.__excepthook__(cls, exception, traceback)
        sys.excepthook = except_hook
        QApplication.quit()
    def _ayanamsa_selection_changed(self):
        self._ayanamsa_mode = self._ayanamsa_combo.currentText().upper()
        drik.set_ayanamsa_mode(self._ayanamsa_mode)
        const._DEFAULT_AYANAMSA_MODE = self._ayanamsa_mode
    def ayanamsa_mode(self, ayanamsa_mode, ayanamsa=None):
        """
            Set Ayanamsa mode
            @param ayanamsa_mode - Default - Lahiri
            See 'drik.available_ayanamsa_modes' for the list of available models
        """
        if ayanamsa_mode.upper() in const.available_ayanamsa_modes.keys():
            self._ayanamsa_mode = ayanamsa_mode
            self._ayanamsa_value = ayanamsa
            self._ayanamsa_combo.setCurrentText(ayanamsa_mode)
            const._DEFAULT_AYANAMSA_MODE = self._ayanamsa_mode
    def place(self,place_name,latitude,longitude,timezone_hrs):
        """
            Set the place of birth
            @param - place_name - Specify with country code. e.g. Chennai, IN
            NOTE: Uses Nominatim to get the latitude and longitude
            An error message displayed if lat/long could not be found in which case enter lat/long manually.
            Also NOTE: calling latitude() or longitude() will replace the lat/long values added already
        """
        self._place_name = place_name
        self._latitude = latitude; self._longitude = longitude
        self._time_zone = timezone_hrs
        self._place_text.setText(self._place_name)
        self._lat_text.setText(str(self._latitude))
        self._long_text.setText(str(self._longitude))
        self._tz_text.setText(str(self._time_zone))
    def name(self,name):
        """
            Set name of the person whose horoscope is sought
            @param - Name of person
        """
        self._name = name
        self._name_text.setText(name)
    def gender(self,gender_index):
        """
            set gender of the person whose horoscope is sought
            @param gender_index: range 0..3 0=>Male, 1=>Female, 2=> Transgender 3=>No option 
        """
        if gender_index in [0,1,2,3]:
            self._gender_combo.setCurrentIndex(gender_index)
            self._gender = self._gender_combo.currentText()
        if gender_index >= 2:
            """ Disable compatibility ui if no male/femal selected """
            self._show_compatibility = False

    def chart_type(self,chart_type):
        """
            Set chart type of the horoscope
            @param - chart_type:
                options: 'south_indian'. 'north_indian', 'west_indian', 'western', 'sudarsana_chakra'
                Default: south_indian
        """
        ci = _index_containing_substring(available_chart_types.keys(),chart_type.lower())
        if ci >=0:
            self._chart_type = list(available_chart_types.keys())[ci]
            self._chart_type_combo.setCurrentText(chart_type.lower())
            self._bhava_chart_type = 'south_indian' if 'west' in self._chart_type.lower() else self._chart_type

    def latitude(self,latitude):
        """
            Sets the latitude manually
            @param - latitude
        """
        self._latitude = float(latitude)
        self._lat_text.setText(str(latitude))
    def longitude(self,longitude):
        """
            Sets the longitude manually
            @param - longitude
        """
        self._longitude = float(longitude)
        self._long_text.setText(str(longitude))
    def time_zone(self,time_zone):
        """
            Sets the time zone offset manually
            @param - time_zone - time zone offset
        """
        self._time_zone = float(time_zone)
        self._tz_text.setText(str(time_zone))
    def date_of_birth(self, date_of_birth):
        """
            Sets the Date of birth (Format:YYYY,MM,DD)
            @param - date_of_birth
        """
        self._date_of_birth = date_of_birth
        self._dob_text.setText(self._date_of_birth)
    def time_of_birth(self, time_of_birth):
        """
            Sets the time of birth (Format:HH:MM:SS)
            @param - time_of_birth
        """
        self._time_of_birth = time_of_birth
        self._tob_text.setText(self._time_of_birth)
    def language(self,language):
        """
            Sets the language for display
            @param - language
        """
        if language in available_languages.keys():
            self._language = language
            self._lang_combo.setCurrentText(language)
    def mahendra_porutham(self, bool_value:bool=True):
        """
            Set whether mahendra porutham/koota is required for compatibility
            @param bool_value True or False. default:True
                    True means - only those stars that match this porutham will be considered
                    False means - it will considers all stars whether matches or not
        """
        if self._show_compatibility:
            self._mahendra_porutham = bool_value
            self._mahendra_porutham_checkbox.setChecked(bool_value)
    def vedha_porutham(self, bool_value:bool=True):
        """
            Set whether vedha porutham/koota is required for compatibility
            @param bool_value True or False. default:True
                    True means - only those stars that match this porutham will be considered
                    False means - it will considers all stars whether matches or not
        """
        if self._show_compatibility:
            self._vedha_porutham = bool_value
            self._vedha_porutham_checkbox.setChecked(bool_value)
    def rajju_porutham(self, bool_value:bool=True):
        """
            Set whether rajju porutham/koota is required for compatibility
            @param bool_value True or False. default:True
                    True means - only those stars that match this porutham will be considered
                    False means - it will considers all stars whether matches or not
        """
        if self._show_compatibility:
            self._rajju_porutham = bool_value
            self._rajju_porutham_checkbox.setChecked(bool_value)
    def sthree_dheerga_porutham(self, bool_value:bool=True):
        """
            Set whether sthree dheerga porutham/koota is required for compatibility
            @param bool_value True or False. default:True
                    True means - only those stars that match this porutham will be considered
                    False means - it will considers all stars whether matches or not
        """
        if self._show_compatibility:
            self._sthree_dheerga_porutham = bool_value
            self._sthree_dheerga_porutham_checkbox.setChecked(bool_value)
    def minimum_compatibility_score(self,minm_comp_score:float=18.0):
        """
            Set minimum score required for marriage compatibility
            @param minm_comp_score: float in range(0.0,35.0,0.5) 
        """
        if 'south' in self._chart_type.lower():
            if self._show_compatibility and  minm_comp_score>0 and minm_comp_score <= const.compatibility_maximum_score_south:
                self._minimum_score = minm_comp_score
                self._min_score_combo.setValue(minm_comp_score)
        else:
            if self._show_compatibility and  minm_comp_score>0.0 and minm_comp_score <= const.compatibility_maximum_score_north:
                self._minimum_score = minm_comp_score
                self._min_score_combo.setValue(minm_comp_score)
    def _validate_ui(self):
        all_data_ok = self._place_text.text().strip() != '' and \
                        re.match(r"[\+|\-]?\d+\.\d+\s?", self._lat_text.text().strip(),re.IGNORECASE) and \
                        re.match(r"[\+|\-]?\d+\.\d+\s?", self._long_text.text().strip(),re.IGNORECASE) and \
                        re.match(r"[\+|\-]?\d{1,5}\,\d{1,2}\,\d{1,2}", self._dob_text.text().strip(),re.IGNORECASE) and \
                        re.match(r"\d{1,2}:\d{1,2}:\d{1,2}", self._tob_text.text().strip(),re.IGNORECASE)
        return all_data_ok
    def _update_main_window_label_and_tooltips(self):
        try:
            if self.resources:
                msgs = self.resources
                self._name_label.setText(msgs['name_str'])
                self._name_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._name_label.setToolTip(msgs['name_tooltip_str'])
                _gender_index = self._gender_combo.currentIndex()
                self._gender_combo.clear()
                self._gender_combo.addItems([msgs['gender_male_str'],msgs['gender_female_str'],msgs['gender_transgender_str'],msgs['gender_no_preference_str']])
                self._gender_combo.setCurrentIndex(_gender_index)
                self._place_label.setText(msgs['place_str'])
                self._place_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._place_label.setToolTip(msgs['place_tooltip_str'])
                self._lat_label.setText(msgs['latitude_str'])
                self._lat_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._lat_label.setToolTip(msgs['latitude_tooltip_str'])
                self._long_label.setText(msgs['longitude_str'])
                self._long_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._long_label.setToolTip(msgs['longitude_tooltip_str'])
                self._tz_label.setText(msgs['timezone_offset_str'])
                self._tz_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._tz_label.setToolTip(msgs['timezone_tooltip_str'])
                self._dob_label.setText(msgs['date_of_birth_str'])
                self._dob_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._dob_label.setToolTip(msgs['dob_tooltip_str'])
                self._tob_label.setText(msgs['time_of_birth_str'])
                self._tob_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._tob_label.setToolTip(msgs['tob_tooltip_str'])
                _pravesha_index = self._pravesha_combo.currentIndex()
                _years_prev = self._years; _months_prev = self._months; _60hrs_prev=self._60hrs
                self._pravesha_combo.clear()
                self._pravesha_combo.addItems([msgs[p] for p in const._PRAVESHA_LIST])
                self._pravesha_combo.setCurrentIndex(_pravesha_index)
                self._years = _years_prev; self._months = _months_prev; self._60hrs = _60hrs_prev
                self._years_label.setText(msgs['years_str'])
                self._months_label.setText(msgs['months_str'])
                self._60hrs_label.setText(msgs['60hrs_str'])
                _chart_type_index = self._chart_type_combo.currentIndex()
                self._chart_type_combo.clear()
                self._chart_type_combo.addItems([msgs[c+'_str'] for c in available_chart_types.keys()])
                self._chart_type_combo.setCurrentIndex(_chart_type_index)
                self._chart_type_combo.setMaximumWidth(300)
                _language_index = self._lang_combo.currentIndex()
                self._lang_combo.clear()
                #self._lang_combo.addItems([msgs[l.lower()+'_str'] for l in const.available_languages.keys()])
                self._lang_combo.addItems(const.available_languages.keys())
                self._lang_combo.setCurrentIndex(_language_index)
                _ar_keys = list(const.amsa_rulers.keys())
                _amsa_ruler_list = [msgs[_chart_names[const.division_chart_factors.index(ak)]] for ak in _ar_keys[:-1] ] + \
                                    [msgs['naadiamsha_str']+' (D-150)']
                self._current_amsa_chart_index = self._amsa_chart_combo.currentIndex()
                self._amsa_ruler_dcf = _ar_keys[self._current_amsa_chart_index] 
                self._amsa_chart_combo.clear()
                self._amsa_chart_combo.addItems(_amsa_ruler_list)
                self._amsa_chart_combo.setCurrentIndex(self._current_amsa_chart_index)
                self._ayanamsa_combo.setToolTip(msgs['ayanamsa_tooltip_str'])
                self._ayanamsa_combo.setMaximumWidth(300)
                self._lang_combo.setToolTip(msgs['language_tooltip_str'])
                self._compute_button.setText(msgs['show_chart_str'])
                self._compute_button.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._compute_button.setToolTip(msgs['compute_tooltip_str'])
                self._save_image_button.setText(msgs['save_pdf_str'])
                self._save_image_button.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._save_image_button.setToolTip(msgs['savepdf_tooltip_str'])
                self._save_city_button.setText(msgs['save_city_str'])
                self._save_city_button.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._save_city_button.setToolTip(msgs['savecity_tooltip_str'])
                self._mahendra_porutham_checkbox.setText(msgs['mahendra_match_str'])#.split()[0])
                self._mahendra_porutham_checkbox.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._mahendra_porutham_checkbox.setToolTip(msgs['mahendra_tooltip_str'])
                self._vedha_porutham_checkbox.setText(msgs['vedha_match_str'])#.split()[0])
                self._vedha_porutham_checkbox.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._vedha_porutham_checkbox.setToolTip(msgs['vedha_tooltip_str'])
                self._rajju_porutham_checkbox.setText(msgs['rajju_match_str'])#.split()[0])
                self._rajju_porutham_checkbox.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._rajju_porutham_checkbox.setToolTip(msgs['rajju_tooltip_str'])
                self._sthree_dheerga_porutham_checkbox.setText(msgs['sthree_dheerga_match_str'])#.split()[0])
                self._sthree_dheerga_porutham_checkbox.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._sthree_dheerga_porutham_checkbox.setToolTip(msgs['sthree_dheerga_tooltip_str'])
                self._min_score_label.setText(msgs['min_score_label_str'])
                self._min_score_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._min_score_label.setToolTip(msgs['min_score_tooltip_str'])
                self._footer_label.setText(msgs['window_footer_title'])
                self.setWindowTitle(msgs['window_title']+'-'+const._APP_VERSION)
                self._update_combos()
                self.update()
                print('UI Language change to',self._language,'completed')
        except:
            print('Some error happened during changing to',self._language,' language and displaying UI in that language.\n'+\
            'Please Check resources file:',const._DEFAULT_LANGUAGE_MSG_STR+available_languages[self._language]+'.txt')
            print(sys.exc_info())
    def _update_combos(self):
        self._current_kundali_chart_index = self._kundali_chart_combo.currentIndex() if self._kundali_chart_combo.currentIndex()>=0 else 0 
        self._kundali_chart_combo.clear()
        self._kundali_chart_combo.addItems([self.resources[cht] for cht in _chart_names])
        self._kundali_chart_combo.SizeAdjustPolicy.AdjustToContents
        self._kundali_chart_combo.adjustSize()
        self._kundali_chart_combo.setCurrentIndex(self._current_kundali_chart_index)
        self._kundali_chart_option_button.setText(self._kundali_chart_combo.currentText()+' '+self.resources['options_str'])
        if not self._western_chart:
            self._current_shodhaya_chart_index = self._shodhaya_chart_combo.currentIndex() if self._shodhaya_chart_combo.currentIndex()>=0 else 0 
            self._shodhaya_chart_combo.clear()
            self._shodhaya_chart_combo.addItems([self.resources[cht] for cht in _chart_names])
            self._shodhaya_chart_combo.SizeAdjustPolicy.AdjustToContents
            self._shodhaya_chart_combo.adjustSize()
            self._shodhaya_chart_combo.setCurrentIndex(self._current_shodhaya_chart_index)
            self._shodhaya_chart_option_button.setText(self._shodhaya_chart_combo.currentText()+' '+self.resources['options_str'])
            self._current_argala_chart_index = self._argala_chart_combo.currentIndex() if self._argala_chart_combo.currentIndex()>=0 else 0 
            self._argala_chart_combo.clear()
            self._argala_chart_combo.addItems([self.resources[cht] for cht in _chart_names])
            self._argala_chart_combo.SizeAdjustPolicy.AdjustToContents
            self._argala_chart_combo.adjustSize()
            self._argala_chart_combo.setCurrentIndex(self._current_argala_chart_index)
            self._argala_chart_option_button.setText(self._argala_chart_combo.currentText()+' '+self.resources['options_str'])
            self._current_saham_chart_index = self._saham_chart_combo.currentIndex() if self._saham_chart_combo.currentIndex()>=0 else 0 
            self._saham_chart_combo.clear()
            self._saham_chart_combo.addItems([self.resources[cht] for cht in _chart_names])
            self._saham_chart_combo.SizeAdjustPolicy.AdjustToContents
            self._saham_chart_combo.adjustSize()
            self._saham_chart_combo.setCurrentIndex(self._current_saham_chart_index)
            self._saham_chart_option_button.setText(self._saham_chart_combo.currentText()+' '+self.resources['options_str'])
            self._current_drishti_chart_index = self._drishti_chart_combo.currentIndex() if self._drishti_chart_combo.currentIndex()>=0 else 0 
            self._drishti_chart_combo.clear()
            self._drishti_chart_combo.addItems([self.resources[cht] for cht in _chart_names])
            self._drishti_chart_combo.SizeAdjustPolicy.AdjustToContents
            self._drishti_chart_combo.adjustSize()
            self._drishti_chart_combo.setCurrentIndex(self._current_drishti_chart_index)
            self._drishti_chart_option_button.setText(self._drishti_chart_combo.currentText()+' '+self.resources['options_str'])
            self._current_chakra_chart_index = self._chakra_chart_combo.currentIndex() if self._chakra_chart_combo.currentIndex()>=0 else 0 
            self._chakra_chart_combo.clear()
            self._chakra_chart_combo.addItems([self.resources[cht] for cht in _chart_names])
            self._chakra_chart_combo.SizeAdjustPolicy.AdjustToContents
            self._chakra_chart_combo.adjustSize()
            self._chakra_chart_combo.setCurrentIndex(self._current_chakra_chart_index)
            self._chakra_chart_option_button.setText(self._chakra_chart_combo.currentText()+' '+self.resources['options_str'])
            for c in range(len(_available_chakras)):
                self._chakra_options_group.button(c).setText(self.resources[_available_chakras[c]+'_str'])
            self._current_sphuta_chart_index = self._sphuta_chart_combo.currentIndex() if self._sphuta_chart_combo.currentIndex()>=0 else 0 
            self._sphuta_chart_combo.clear()
            self._sphuta_chart_combo.addItems([self.resources[cht] for cht in _chart_names])
            self._sphuta_chart_combo.SizeAdjustPolicy.AdjustToContents
            self._sphuta_chart_combo.adjustSize()
            self._sphuta_chart_combo.setCurrentIndex(self._current_sphuta_chart_index)
            self._current_kpinfo_chart_index = self._kpinfo_chart_combo.currentIndex() if self._kpinfo_chart_combo.currentIndex()>=0 else 0 
            self._kpinfo_chart_combo.clear()
            self._kpinfo_chart_combo.addItems([self.resources[cht] for cht in _chart_names])
            self._kpinfo_chart_combo.SizeAdjustPolicy.AdjustToContents
            self._kpinfo_chart_combo.adjustSize()
            self._kpinfo_chart_combo.setCurrentIndex(self._current_kpinfo_chart_index)
            self._arudha_chart_combo.clear()
            self._arudha_chart_combo.addItems([self.resources[cht] for cht in _chart_names])
            self._arudha_chart_combo.SizeAdjustPolicy.AdjustToContents
            self._arudha_chart_combo.adjustSize()
            self._arudha_chart_combo.setCurrentIndex(self._current_arudha_chart_index)
            _bhava_arudha_index = self._bhava_arudha_combo.currentIndex()
            self._bhava_arudha_combo.clear()
            self._bhava_arudha_combo.addItems([self.resources[r] for r in _bhava_arudha_list])
            self._bhava_arudha_combo.setCurrentIndex(_bhava_arudha_index)
            self._current_ashtaka_chart_index = self._ashtaka_chart_combo.currentIndex() if self._ashtaka_chart_combo.currentIndex()>=0 else 0
            self._ashtaka_chart_combo.clear()
            self._ashtaka_chart_combo.addItems([self.resources[cht] for cht in _chart_names])
            self._ashtaka_chart_combo.SizeAdjustPolicy.AdjustToContents
            self._ashtaka_chart_combo.adjustSize()
            self._ashtaka_chart_combo.setCurrentIndex(self._current_ashtaka_chart_index)
            self._current_dhasa_type_index = self._dhasa_type_combo.currentIndex() if self._dhasa_type_combo.currentIndex()>=0 else 0
            self._dhasa_type_combo.clear()
            self._dhasa_type_combo.addItems([d+' '+self.resources['dhasa_str'] for d in [self.resources['graha_str'],self.resources['raasi_str'],self.resources['annual_str']]])
            self._dhasa_type_combo.adjustSize()
            self._dhasa_type_combo.setCurrentIndex(self._current_dhasa_type_index)
            self._current_dhasa_index = self._dhasa_combo.currentIndex() if self._dhasa_combo.currentIndex()>=0 else 0
            self._dhasa_combo.clear()
            if self._dhasa_type_combo.currentIndex()==0:
                self._dhasa_combo.addItems([self.resources[d+'_str'] for d in _graha_dhasa_dict.keys()])
                self._dhasa_options_button.setVisible(True); self._dhasa_varga_combo.setVisible(False)
            elif self._dhasa_type_combo.currentIndex()==1:
                self._dhasa_options_button.setVisible(False); self._dhasa_varga_combo.setVisible(True)
                self._dhasa_combo.addItems([self.resources[d+'_str'] for d in _rasi_dhasa_dict.keys()])
            else:
                self._dhasa_options_button.setVisible(False); self._dhasa_varga_combo.setVisible(True)
                self._dhasa_combo.addItems([self.resources[d+'_str'] for d in _annual_dhasa_dict.keys()])
            self._dhasa_combo.setCurrentIndex(self._current_dhasa_index)
            self._current_dhasa_varga_index = self._dhasa_varga_combo.currentIndex() if self._dhasa_varga_combo.currentIndex()>=0 else 0
            self._dhasa_varga_combo.clear()
            self._dhasa_varga_combo.addItems([self.resources[cht] for cht in _chart_names])
            self._dhasa_varga_combo.adjustSize()
            self._dhasa_varga_combo.setCurrentIndex(self._current_dhasa_varga_index)
            self._dhasa_options_button.setText(self._dhasa_combo.currentText()+' '+self.resources['options_str'])
    def compute_horoscope(self, calculation_type='drik'):
        """
            Compute the horoscope based on details entered
            if details missing - error is displayed            
        """
        #start_time = datetime.now()
        if not self._validate_ui():
            print('values are not filled properly')
            return
        self._gender = self._gender_combo.currentText()
        self._place_name = self._place_text.text()
        self._latitude = float(self._lat_text.text())
        self._longitude = float(self._long_text.text())
        self._time_zone = float(self._tz_text.text())
        self._language = list(const.available_languages.keys())[self._lang_combo.currentIndex()]
        year,month,day = self._date_of_birth.split(",")
        birth_date = drik.Date(int(year),int(month),int(day))
        self._years = self._years_combo.value()
        self._months = self._months_combo.value()
        self._60hrs = self._60hrs_combo.value()
        if self._place_name.strip() == "":
            print("Please enter a place of birth")
            return
        self._ayanamsa_mode =  self._ayanamsa_combo.currentText()
        if self.use_internet_for_location_check and self._place_name.strip() == '' and abs(self._latitude) > 0.0 \
                and abs(self._longitude) > 0.0 and abs(self._time_zone) > 0.0: 
            [self._place_name,self._latitude,self._longitude,self._time_zone] = \
                utils.get_location_using_nominatim(self._place_name)
            self._lat_text.setText((self._latitude))
            self._long_text.setText((self._longitude))
            self._tz_text.setText((self._time_zone))
        self._enable_disable_annual_ui()
        if self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('planetary_conjunctions_str'):
            self._show_conjunction_dialog(entry_type=0,chart_title='planetary_conjunctions_str')
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('planet_transit_str'):
            self._show_conjunction_dialog(entry_type=1,chart_title='planet_transit_str')
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('vakra_gathi_change_str'):
            self._show_conjunction_dialog(entry_type=2,chart_title='vakra_gathi_change_str')
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('lunar_month_year_str'):
            self._show_lunar_month_dialog()
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('vrathas_str'):
            self._show_vratha_finder_dialog()
            year,month,day = self._date_of_birth.split(",")
            birth_date = drik.Date(int(year),int(month),int(day))
            if self._place_name.strip() != '' and abs(self._latitude) > 0.0 and abs(self._longitude) > 0.0 and abs(self._time_zone) > 0.0:
                self._horo= main.Horoscope(place_with_country_code=self._place_name,latitude=self._latitude,longitude=self._longitude,timezone_offset=self._time_zone,
                                           date_in=birth_date,birth_time=self._time_of_birth,ayanamsa_mode=self._ayanamsa_mode,
                                           ayanamsa_value=self._ayanamsa_value,calculation_type=calculation_type,
                                           years=self._years,months=self._months,sixty_hours=self._60hrs,
                                           pravesha_type=self._pravesha_combo.currentIndex(),language=available_languages[self._language])
            else:
                self._horo= main.Horoscope(place_with_country_code=self._place_name,date_in=birth_date,birth_time=self._time_of_birth,
                                           ayanamsa_mode=self._ayanamsa_mode,ayanamsa_value=self._ayanamsa_value,calculation_type=calculation_type,
                                           years=self._years,months=self._months,sixty_hours=self._60hrs,
                                           pravesha_type=self._pravesha_combo.currentIndex(),language=available_languages[self._language])
            self._calendar_info = self._horo.calendar_info
            self.resources = self._horo.cal_key_list
            info_str = ''
            format_str = _KEY_VALUE_FORMAT_
            self._fill_panchangam_info(info_str, format_str)
            self.tabWidget.setCurrentIndex(0) # Switch First / Panchanga Tab
            return """ For vrathas Show only Panchangam page updated and return """
        """ reset birth_date again based on self._date_of_birth and self._time_of_birth from pravesha functions """
        year,month,day = self._date_of_birth.split(",")
        birth_date = drik.Date(int(year),int(month),int(day))
        self._chart_type = list(available_chart_types)[self._chart_type_combo.currentIndex()]
        ' set the chart type and reset widgets'
        self._recreate_chart_tab_widgets()
        self._western_chart = False
        if 'west' in self._chart_type.lower():
            self._western_chart = True
            self.tabNames = _tab_names[:_chart_tab_end]
        if self._place_name.strip() != '' and abs(self._latitude) > 0.0 and abs(self._longitude) > 0.0 and abs(self._time_zone) > 0.0:
            self._horo= main.Horoscope(place_with_country_code=self._place_name,latitude=self._latitude,longitude=self._longitude,timezone_offset=self._time_zone,
                                       date_in=birth_date,birth_time=self._time_of_birth,ayanamsa_mode=self._ayanamsa_mode,
                                       ayanamsa_value=self._ayanamsa_value,calculation_type=calculation_type,
                                       years=self._years,months=self._months,sixty_hours=self._60hrs,
                                       pravesha_type=self._pravesha_combo.currentIndex(),bhava_madhya_method=self._bhaava_madhya_method,
                                       language=available_languages[self._language])
        else:
            self._horo= main.Horoscope(place_with_country_code=self._place_name,date_in=birth_date,birth_time=self._time_of_birth,
                                       ayanamsa_mode=self._ayanamsa_mode,ayanamsa_value=self._ayanamsa_value,calculation_type=calculation_type,
                                       years=self._years,months=self._months,sixty_hours=self._60hrs,
                                       pravesha_type=self._pravesha_combo.currentIndex(),bhava_madhya_method=self._bhaava_madhya_method,
                                       language=available_languages[self._language])
        self._calendar_info = self._horo.calendar_info
        self.resources = self._horo.cal_key_list
        self._kundali_info,self._kundali_chart,self._kundali_ascendant_house = \
            self._horo.get_horoscope_information_for_chart(self._current_kundali_chart_index, 
                                                           chart_method=self._kundali_method_index,
                                                           varnada_method=self._varnada_method_index,
                                                           base_rasi=self._kundali_varga_dict[self._kundali_custom_varga][2],
                                                           count_from_end_of_sign=self._kundali_varga_dict[self._kundali_custom_varga][3])
        if not self._western_chart:
            """ TODO: Should we change dob,tob to birth date/time here """
            dob = self._horo.Date
            tob = self._horo.birth_time
            dcf = const.division_chart_factors[self._current_dhasa_varga_index]
            #dob = self._dob_text.text().split(','); dob = drik.Date(dob[0],dob[1],dob[2])
            #tob = self._tob_text.text().split(':')
            place = self._horo.Place
            for tab_str,tab_values in _graha_dhasa_dict.items():
                option_str = ''#self._dhasa_bhukthi_options_str
                #if option_str.strip() != '': option_str = ','+option_str
                func_str = 'self._horo._get_'+tab_str+'_dhasa_bhukthi'
                arg_str = 'dob, tob, place'#,divisional_chart_factor='+str(dcf)
                eval_str = func_str+'('+arg_str+option_str+')'
                #print(self._dhasa_bhukthi_options_str,'compute_horoscope',eval_str)
                retval = eval(eval_str)
                tab_values[7] = retval
            r = 0
            for tab_str,tab_values in _rasi_dhasa_dict.items():
                retval = eval('self._horo._get_'+tab_str+'_dhasa(dob, tob, place,divisional_chart_factor='+str(dcf)+')')
                tab_values[7] = retval
            _db_info = self._horo._get_annual_dhasa_bhukthi(divisional_chart_factor=dcf)
            r = 0
            for tab_str,tab_values in _annual_dhasa_dict.items():
                tab_values[7] = _db_info[r]
                r+=1
            self._horo._get_arudha_padhas(dob, tob, place, divisional_chart_factor=1,
                                          years=self._years,months=self._months,sixty_hours=self._60hrs)
            self._vimsopaka_bala_info = self._horo._get_vimsopaka_bala(dob, tob, place)
            self._vaiseshikamsa_bala_info = self._horo._get_vaiseshikamsa_bala(dob, tob, place)
            self._other_bala_info = self._horo._get_other_bala(dob, tob, place)
            self._shad_bala_info = self._horo._get_shad_bala(dob, tob, place)
            self._bhava_bala_info = self._horo._get_bhava_bala(dob, tob, place)
        self._update_main_window_label_and_tooltips()
        self._update_chart_ui_with_info()
        self.resize(self.minimumSizeHint())
        self.tabWidget.setFocus()
        #end_time = datetime.now()
        #print('Elapsed time - compute_horoscope',end_time-start_time,'seconds')
    def _recreate_chart_tab_widgets(self):
        self._current_kundali_chart_index = self._kundali_chart_combo.currentIndex()
        self._v_layout.removeWidget(self.tabWidget)
        current_tab = self.tabWidget.currentIndex()
        self.tabWidget.deleteLater()
        self._footer_label.deleteLater()
        self.tabWidget = None
        self._init_tab_widget_ui()
        self.tabWidget.setCurrentIndex(current_tab)
        self._kundali_chart_combo.setCurrentIndex(self._current_kundali_chart_index)
    def _fill_panchangam_info(self, info_str,format_str):
        jd = self._horo.julian_day
        place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        bt=self._horo.birth_time
        tob = bt[0]+bt[1]/60.0+bt[2]/3600.0
        jd_years = drik.next_solar_date(jd, place)
        yb, mb, db, hfb = utils.jd_to_gregorian(jd)
        yy, my, dy, hfy = utils.jd_to_gregorian(jd_years)
        self._date_text_dob =  '%04d-%02d-%02d' %(yb,mb,db)
        self._time_text_dob = utils.to_dms(hfb,as_string=True)
        self._date_text_years =  '%04d-%02d-%02d' %(yy,my,dy)
        self._time_text_years = utils.to_dms(hfy,as_string=True)
        self._lat_chart_text = utils.to_dms(self._latitude,is_lat_long='lat')
        self._long_chart_text = utils.to_dms(self._longitude,is_lat_long='long')
        self._timezone_text = '(GMT '+str(self._tz_text.text())+')'
        self.panchanga_info_dialog.set_language(self._language)
        self.panchanga_info_dialog.update_panchangam_info(jd, place,ayanamsa_mode=self._ayanamsa_mode)
        return 
    def _convert_1d_chart_with_planet_names(self,chart_1d_list): #To be used for Sudarsana Chakra data as input
        result = []
        retrograde_planets = chart_1d_list[-1]
        for chart_1d in chart_1d_list[:-1]:
            res = []
            for z,pls in chart_1d:
                pl_str = ''
                tmp = pls.split('/')
                if len(tmp) == 1 and tmp[0] =='':
                    pl_str = ''
                    res.append((z,pl_str))
                    continue
                for p in tmp:
                    if p == const._ascendant_symbol:
                        pl_str += self.resources['ascendant_short_str']+'/'#' 'Lagnam'+'/'#const._ascendant_symbol+"/"
                    else:
                        ret_str = ''
                        if int(p) in retrograde_planets:
                            ret_str = const._retrogade_symbol
                        pl_str += utils.PLANET_SHORT_NAMES[int(p)]+ret_str+'/'# house.planet_list[int(p)]+'/'#const._planet_symbols[int(p)]+'/'
                pl_str = pl_str[:-1]
                res.append((z,pl_str))
            result.append(res)
        return result
    def _get_tab_chart_prefix(self):
        _chart_title_separator = ' '; tab_str=''
        if 'south' in self._chart_type.lower() or 'east' in self._chart_type.lower():
            _chart_title_separator = '\n'
        if int(self._months_combo.text()) > 1:
            tab_str = self.resources['monthly_str']+_chart_title_separator
        elif int(self._60hrs_combo.text()) > 1:
            tab_str = self.resources['60hourly_str']+_chart_title_separator
        elif self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('lunar_month_year_str'): 
            tab_str = self._lunar_month_type+_chart_title_separator
        elif self._conjunction_dialog_accepted:
            _pravesha_index = const._PRAVESHA_LIST[self._pravesha_combo.currentIndex()]
            pstr = self.resources[_pravesha_index]
            if self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('planetary_conjunctions_str'):
                pstr1 = self.resources['ascendant_str'] if self._conj_planet1=='L' else utils.PLANET_NAMES[self._conj_planet1]
                pstr2 = self.resources['ascendant_str'] if self._conj_planet2=='L' else utils.PLANET_NAMES[self._conj_planet2]
                pstr = pstr1+'/'+pstr2
                pstr += '-'+self._separation_angle_list[self._separation_angle_index]
            elif (self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('planet_transit_str')):
                pstr = self.resources['ascendant_str'] if self._conj_planet1=='L' else utils.PLANET_NAMES[self._conj_planet1]
                if self._conj_raasi is not None:
                    pstr = utils.RAASI_LIST[self._conj_raasi] + '-'+pstr
            elif (self._pravesha_combo.currentIndex()==const._PRAVESHA_LIST.index('vakra_gathi_change_str')):
                pstr = utils.PLANET_NAMES[self._conj_planet1]+'-'+self.resources['vakra_gathi_change_str']
            tab_str = pstr+_chart_title_separator
        elif int(self._years_combo.text()) > 1:
            tab_str = self.resources['annual_str']+_chart_title_separator
        else:
            _pravesha_index = const._PRAVESHA_LIST[self._pravesha_combo.currentIndex()]
            tab_str = self.resources[_pravesha_index]+_chart_title_separator
        tab_str = tab_str.replace('\n','-')
        return tab_str, _chart_title_separator
    def _get_menu_dicts(self,jd,place,chart_index=None,chart_method=None,divisional_chart_factor=None,
                                            base_rasi=None,count_from_end_of_sign=None,
                                    chart_index_1=None,chart_method_1=None,chart_index_2=None,chart_method_2=None):
        y,m,d,fh = utils.jd_to_gregorian(jd); dob = drik.Date(y,m,d); tob=(fh,0,0)
        tab_str,_chart_title_separator = self._get_tab_chart_prefix()
        format_str = '%-18s%-20s\n'
        t = chart_index
        if divisional_chart_factor==None:
            if chart_index < _custom_chart_index:
                dcf = const.division_chart_factors[chart_index]
            else:
                dcf = const.DEFAULT_CUSTOM_VARGA_FACTOR
        else:
            dcf = divisional_chart_factor
        if chart_index == _custom_chart_index:
            tab_name = tab_str + 'D'+str(dcf)
        elif chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[chart_index_1]; v2 = const.division_chart_factors[chart_index_2]
            dcf = v1*v2
            mds = ' D'+str(v1)+'('+str(chart_method_1)+')xD'+ str(v2)+'('+str(chart_method_2)+')'+' '
            tab_name = tab_str + mds
        else:
            tab_name = tab_str + self.resources[_chart_names[t]]
        if chart_index==_mixed_chart_index:
            planet_positions = charts.mixed_chart(jd, place, varga_factor_1=v1, chart_method_1=chart_method_1,
                                                  varga_factor_2=v2, chart_method_2=chart_method_2)
            _varnada_menu_dict = self._horo.get_varnada_lagna_for_mixed_chart(dob, tob, place,varga_factor_1=v1,
                                            chart_method_1=chart_method_1, varga_factor_2=v2,
                                            chart_method_2=chart_method_2, varnada_method=self._varnada_method_index)
            _karaka_menu_dict = self._horo.get_chara_karakas_for_mixed_chart(jd, place,varga_factor_1=v1,
                                            chart_method_1=chart_method_1, varga_factor_2=v2,
                                            chart_method_2=chart_method_2)
            _special_lagna_menu_dict = self._horo.get_special_lagnas_for_mixed_chart(jd, place,varga_factor_1=v1,
                                            chart_method_1=chart_method_1, varga_factor_2=v2,
                                            chart_method_2=chart_method_2)
            _special_planets_menu_dict = self._horo.get_special_planets_for_mixed_chart(jd, place,varga_factor_1=v1,
                                            chart_method_1=chart_method_1, varga_factor_2=v2,
                                            chart_method_2=chart_method_2)
            _sphuta_menu_dict = self._horo.get_sphutas_for_mixed_chart(jd, place, varga_factor_1=v1,
                                            chart_method_1=chart_method_1, varga_factor_2=v2,
                                            chart_method_2=chart_method_2)
            _yogi_info = self._horo.get_ava_saha_yoga_for_mixed_chart(jd, place, varga_factor_1=v1,
                                            chart_method_1=chart_method_1, varga_factor_2=v2,
                                            chart_method_2=chart_method_2)
        else:
            planet_positions = charts.divisional_chart(jd, place,divisional_chart_factor=dcf,
                                    chart_method=chart_method,base_rasi=base_rasi,
                                    count_from_end_of_sign=count_from_end_of_sign)
            _varnada_menu_dict = self._horo.get_varnada_lagna_for_chart(dob, tob, place, 
                                        divisional_chart_factor=dcf, chart_method=chart_method,
                                        varnada_method=1, base_rasi=base_rasi,
                                        count_from_end_of_sign=count_from_end_of_sign)
            _karaka_menu_dict = self._horo.get_chara_karakas_for_chart(jd, place, divisional_chart_factor=dcf,
                                            chart_method=chart_method, base_rasi=base_rasi,
                                            count_from_end_of_sign=count_from_end_of_sign)
            _special_lagna_menu_dict = self._horo.get_special_lagnas_for_chart(jd, place, divisional_chart_factor=dcf,
                                            chart_method=chart_method, base_rasi=base_rasi,
                                            count_from_end_of_sign=count_from_end_of_sign)
            _special_planets_menu_dict = self._horo.get_special_planets_for_chart(jd, place, divisional_chart_factor=dcf,
                                            chart_method=chart_method, base_rasi=base_rasi,
                                            count_from_end_of_sign=count_from_end_of_sign)
            _sphuta_menu_dict = self._horo.get_sphutas_for_chart(jd, place, divisional_chart_factor=dcf,
                                            chart_method=chart_method, base_rasi=base_rasi,
                                            count_from_end_of_sign=count_from_end_of_sign)
            _yogi_info = self._horo.get_ava_saha_yoga_info_for_chart(jd, place, divisional_chart_factor=dcf,
                                            chart_method=chart_method, base_rasi=base_rasi,
                                            count_from_end_of_sign=count_from_end_of_sign)
        vl_chart = ['' for _ in range(12)]
        _navamsa_drekkana_lord_menu_dict = {}; _ndl_22_widgets=None; _ndl_64_widgets=None
        if dcf == 3:
            _ndl_table = [['' for _ in range(3)] for _ in range(len(drik.planet_list)+2)]
            _colors = [['Green','Blue','Brown'] for _ in range(len(drik.planet_list)+2)]
            _drek_str = self.resources['drekkanam_str'].replace(' (D3)','')
            key = '22nd '+_drek_str
            _ndl_table[0][0] = self.resources['starts_at_str']
            _ndl_table[0][1] = self.resources['raasi_str']
            _ndl_table[0][2] = self.resources['lord_str']
            _22nd_drekkana = charts.get_22nd_drekkana(planet_positions)
            for p_i,(p,(v1,v2)) in enumerate(_22nd_drekkana.items()):
                pstr = self.resources['ascendant_str'] if p==const._ascendant_symbol else utils.PLANET_NAMES[p]
                _ndl_table[p_i+1][0] = pstr
                _ndl_table[p_i+1][1] = utils.RAASI_LIST[v1]
                _ndl_table[p_i+1][2] = utils.PLANET_NAMES[v2]
            _navamsa_drekkana_lord_menu_dict = {key:vl_chart}
            v_layout = QVBoxLayout()
            _widget = QWidget()
            _ndl_22_widget = LabelGrid(data=_ndl_table,has_header=True,set_labels_bold=False,colors=_colors)
            _method_str = self.resources['d' + str(dcf) + '_option' + str(chart_method) + '_str']
            lbl = QLabel(_method_str);lbl.setStyleSheet('font-weight:bold; color:black')
            v_layout.addWidget(_ndl_22_widget); v_layout.addWidget(lbl)
            _widget.setLayout(v_layout)
            _ndl_22_widgets = [_widget]
        elif dcf == 9:
            _ndl_table = [['' for _ in range(3)] for _ in range(len(drik.planet_list)+2)]
            _colors = [['Green','Blue','Brown'] for _ in range(len(drik.planet_list)+2)]
            _nava_str = self.resources['navamsam_str'].replace(' (D9)','')
            key = '64th '+_nava_str
            _ndl_table[0][0] = self.resources['starts_at_str']
            _ndl_table[0][1] = self.resources['raasi_str']
            _ndl_table[0][2] = self.resources['lord_str']
            _64th_navamsa = charts.get_64th_navamsa(planet_positions)
            for p_i,(p,(v1,v2)) in enumerate(_64th_navamsa.items()):
                pstr = self.resources['ascendant_str'] if p==const._ascendant_symbol else utils.PLANET_NAMES[p]
                _ndl_table[p_i+1][0] = pstr
                _ndl_table[p_i+1][1] = utils.RAASI_LIST[v1]
                _ndl_table[p_i+1][2] = utils.PLANET_NAMES[v2]
            _navamsa_drekkana_lord_menu_dict = {key:vl_chart}
            v_layout = QVBoxLayout()
            _widget = QWidget()
            _ndl_64_widget = LabelGrid(data=_ndl_table,has_header=False,set_labels_bold=False,colors=_colors)
            _method_str = self.resources['d' + str(dcf) + '_option' + str(chart_method) + '_str']
            lbl = QLabel(_method_str);lbl.setStyleSheet('font-weight:bold; color:black')
            v_layout.addWidget(_ndl_64_widget); v_layout.addWidget(lbl)
            _widget.setLayout(v_layout)
            _ndl_64_widgets = [_widget]
        _saham_menu_dict,_ = self._horo.get_sahams(planet_positions)
        _paachakaadi_dict = charts.get_pachakadi_sambhandha(planet_positions)
        _paachakaadi_info = ''
        ps = [self.resources[pr+'_str'] for pr in const.paachaadi_relations]
        for planet1,[index,(planet2,h,enemy)] in _paachakaadi_dict.items():
            p2_str = utils.PLANET_NAMES[planet2]; p1_str=utils.PLANET_NAMES[planet1]
            e_str = self.resources['inimical_str'] if enemy=='E' else ''
            p_str = ps[index]; h_str = self.resources['house_str']+'-'+str(h)
            _paachakaadi_info += p2_str+ ' '+ e_str + ' '+ p_str +' '+ p1_str+ ' '+ h_str +'<br>'
        _paachakadi_menu_dict = {}
        if _paachakaadi_info.strip() != '':
            _paachakadi_menu_dict = {self.resources['paachakaadi_sambhandha_str']:_paachakaadi_info}
        _,_drishti_table_widgets = self._get_drishti_table_widgets(chart_index, chart_method, 
                            divisional_chart_factor, base_rasi, count_from_end_of_sign, chart_index_1, chart_method_1,
                            chart_index_2, chart_method_2)
        _drishti_menu_dict = {self.resources['drishti_str']:vl_chart}
        _brahma = house.brahma(planet_positions); _rudra=house.rudra(planet_positions)
        _brahma_menu_dict = {}
        _maheshwara = house.maheshwara_from_planet_positions(planet_positions)
        if _brahma and _rudra and _maheshwara:
            _brahma_info = self.resources['brahma_str']+':'+utils.PLANET_NAMES[_brahma]+'<br>'
            _brahma_info += self.resources['rudra_str']+':'+utils.PLANET_NAMES[_rudra[0]]+' '+ \
                    self.resources['raasi_str']+':'+utils.RAASI_LIST[_rudra[1]]+ '<br>' + \
                    self.resources['trishoola_str']+' '+self.resources['raasi_str']+':'+ \
                    utils.RAASI_LIST[_rudra[2][0]]+','+utils.RAASI_LIST[_rudra[2][1]]+','+utils.RAASI_LIST[_rudra[2][2]] +'<br>'
            _brahma_info += self.resources['maheshwara_str']+':'+utils.PLANET_NAMES[_maheshwara]
            _brahma_menu_dict = {utils.resource_strings['brahma_str']+','+utils.resource_strings['rudra_str']+','+utils.resource_strings['maheshwara_str']:
                                 _brahma_info}
        
        _prasna_menu_dict = {self.resources['prasna_lagna_str']+'('+self.resources['prasna_lagna_short_str']+')':vl_chart}
        _planets_menu_dict = {self.resources['planets_str']:vl_chart}
        key = utils.resource_strings['planets_str']+' '+utils.resource_strings['speed_str']+', '+ \
                    utils.resource_strings['distance_str']+' '+ utils.resource_strings['information_str']
        _planets_info_dict = {key:vl_chart}
        _planets_info_table = QTableWidget(len(drik.planet_list),6)
        psi = drik.planets_speed_info(jd, place)
        _planets_info_table.setHorizontalHeaderItem(0,QTableWidgetItem(utils.resource_strings['longitude_str']))
        _planets_info_table.setHorizontalHeaderItem(1,QTableWidgetItem(utils.resource_strings['longitude_str']+'\n'+utils.resource_strings['speed_str']))
        _planets_info_table.setHorizontalHeaderItem(2,QTableWidgetItem(utils.resource_strings['latitude_str']))
        _planets_info_table.setHorizontalHeaderItem(3,QTableWidgetItem(utils.resource_strings['latitude_str']+'\n'+utils.resource_strings['speed_str']))
        _planets_info_table.setHorizontalHeaderItem(4,QTableWidgetItem(utils.resource_strings['distance_str']))
        _planets_info_table.setHorizontalHeaderItem(5,QTableWidgetItem(utils.resource_strings['distance_str']+'\n'+utils.resource_strings['speed_str']))
        for p,s_p in psi.items():
            p_i = p# drik.planet_list.index(p)
            s_p = [round(s_p_p,8) if i == len(psi)-1 else round(s_p_p,4) for i,s_p_p in enumerate(s_p) ]
            _planets_info_table.setVerticalHeaderItem(p,QTableWidgetItem(utils.PLANET_NAMES[p_i]))
            _planets_info_table.setItem(p,0,QTableWidgetItem(str(s_p[0])+' deg'))
            _planets_info_table.setItem(p,1,QTableWidgetItem(str(s_p[3])+' deg/day'))
            _planets_info_table.setItem(p,2,QTableWidgetItem(str(s_p[1])+' deg'))
            _planets_info_table.setItem(p,3,QTableWidgetItem(str(s_p[4])+' deg/day'))
            _planets_info_table.setItem(p,4,QTableWidgetItem(str(s_p[2])+' AU'))
            _planets_info_table.setItem(p,5,QTableWidgetItem(str(s_p[5])+' AU/day'))
            _planets_info_table.resizeRowToContents(p)
        _planets_info_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        #_yogi_menu_dict = {key:vl_chart for key,_ in _yogi_info.items()}
        _yogi_info = list(_yogi_info.values())[0]
        _yogi_menu_dict = {key:_yogi_info}
        pa,pb = charts.planets_in_pushkara_navamsa_bhaga(planet_positions)
        _pushkara_info = ''
        _pushkara_menu_dict = {}
        if len(pa)>0:
            _pushkara_info += utils.resource_strings['pushkara_amsa_str']+' '+utils.resource_strings['planets_str']+': <br>'
            for p in pa:
                _pushkara_info +=  utils.PLANET_NAMES[p]+'<br>'
        if len(pb)>0:
            _pushkara_info += '<br>'+utils.resource_strings['pushkara_bhaga_str']+' '+utils.resource_strings['planets_str']+':<br>'
            for p in pb:
                _pushkara_info +=  utils.PLANET_NAMES[p]+'<br'
        if _pushkara_info.strip() != '':
            key = utils.resource_strings['pushkara_amsa_str']+', '+utils.resource_strings['pushkara_bhaga_str']
            _pushkara_menu_dict = {key:_pushkara_info}
        planets_in_combustion = charts.planets_in_combustion(planet_positions)
        if len(planets_in_combustion)==0:
            _combustion_dict = {}; _combustion_info = ''
        else:
            key = self.resources['combustion_str']+' '+self.resources['planets_str']
            #_combustion_dict={key:vl_chart}
            _combustion_info = key
            for p in planets_in_combustion:
                _combustion_info += '<br>' + utils.PLANET_NAMES[p]
            _combustion_dict = {key:_combustion_info}
        _grahayudh_dict = {}
        _yudh_info = ''
        if chart_index==0:
            _yudh_planets = drik.planets_in_graha_yudh(jd, place)
            if len(_yudh_planets)>0:
                #_grahayudh_dict = {self.resources['graha_yudh_str']:vl_chart}
                yudh_types = [self.resources[gy+'_str'] for gy in ['bhed_yuti','ullekh_yuti','apasavya_yuti','anshumardan_yuti']]
                _yudh_info += self.resources['graha_yudh_str']+' '+self.resources['planets_str']+' :'
                for (planet1,planet2,gy_type) in _yudh_planets:
                    _yudh_info += '<br>' +utils.PLANET_NAMES[planet1]+' '+yudh_types[gy_type]+' '+utils.PLANET_NAMES[planet2]
                _grahayudh_dict = {self.resources['graha_yudh_str']:_yudh_info}
        _mrityu_info = ''; _mrityu_dict = {}
        _mrityu_planets = charts.planets_in_mrityu_bhaga(dob, tob, place, planet_positions)
        if len(_mrityu_planets) > 0:
            #_mrityu_dict = {self.resources['mrityu_bhaga_str']:vl_chart}
            _mrityu_info += self.resources['mrityu_bhaga_str']+' '+self.resources['planets_str']+' :'
            for p,r,l in _mrityu_planets:
                pstr = utils.PLANET_NAMES[p] if isinstance(p,int) else (self.resources['ascendant_str'] if p=='L' else self.resources['maandi_str'])
                _mrityu_info += '<br>'+pstr+' '+utils.RAASI_LIST[r]+' '+self.resources['balance_str']+' : ' + \
                                    utils.to_dms(l,is_lat_long='plong')
            _mrityu_dict = {self.resources['mrityu_bhaga_str']:_mrityu_info}
        _aspect_info = ''; include_houses = True; rows = 9
        _aspect_values = [[str(ele) for ele in row ] for row in strength.planet_aspect_relationship_table(planet_positions,include_houses=include_houses)]
        planets = ['']+utils.PLANET_SHORT_NAMES[:9]
        if include_houses:
            rows = 21
            planets += ['1st','2nd','3rd','4th','5th','6th','7th','8th','9th','10th','11th','12th']
        new_list = [planets]
        for i in range(len(_aspect_values)):
            new_list.append([planets[i + 1]] + _aspect_values[i])
        _aspect_values = new_list[:]
        crp = const.compound_planet_relations[:]; crp_i = 0
        #h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
        #crp = house._get_compound_relationships_of_planets(h_to_p); crp_i=1
        hsp = const.house_strengths_of_planets[:]
        _header_colors = ['black' for _ in range(rows+1)]
        _planet_relation_colors = ['black','red','orange','blue','lightgreen','darkgreen','black']
        _rasi_relation_colors = ['red','orange','cyan','blue','lightgreen','darkgreen']
        _aspect_colors = [[_planet_relation_colors[crp[p1][p2]+crp_i] if p1 < 9 \
                           else _rasi_relation_colors[hsp[p2][p1-9]] for p1 in range(rows)] for p2 in range(9)] #+1 to crp if h_to_p used
        new_list = [_header_colors]
        for i in range(len(_aspect_colors)):
            new_list.append([_header_colors[i + 1]] + _aspect_colors[i])
        _aspect_colors = new_list[:]
        _aspect_values = list(zip(*_aspect_values));_aspect_colors = list(zip(*_aspect_colors))
        _legends = [[self.resources['adhisathru_str']+' / '+self.resources['neecha_str'],self.resources['sathru_str'],
                    self.resources['sama_str']],[self.resources['sama_str'],
                    self.resources['mithra_str']+' / '+self.resources['uchcha_str'],self.resources['adhimitra_str'] +' / '+ self.resources['swagraha_str']]
                    ]
        v_layout = QVBoxLayout()
        gl = QGridLayout()
        clr = 0
        for r in range(2):
            for c in range(3):
                lbl = QLabel(_rasi_relation_colors[clr]+':'+_legends[r][c])
                lbl.setStyleSheet('font-weight:bold; color:'+_rasi_relation_colors[clr])
                gl.addWidget(lbl,r,c)
                clr+=1
        v_layout.addWidget(LabelGrid(data=_aspect_values,colors=_aspect_colors,label_font_size=12))
        _widget = QWidget()
        v_layout.addLayout(gl)
        _widget.setLayout(v_layout)
        _aspect_widgets = [_widget]
        #_aspect_widgets = [LabelGrid(data=_aspect_values,colors=_aspect_colors,label_font_size=12)]
        _aspect_dict = {self.resources['planet_aspects_relations_str']:vl_chart}
        # Marana Karaka Sthana
        mks_planets = charts.get_planets_in_marana_karaka_sthana(planet_positions, consider_ketu_4th_house=True)
        _mks_menu_dict = {}; _mks_info = ''
        if len(mks_planets) > 0:
            key = self.resources['marana_karaka_sthana_str'] +' '+self.resources['planets_str']
            _mks_info += key
            for p,h in mks_planets:
                _mks_info +='<br>'+utils.PLANET_NAMES[p]+' ' + self.resources['house_str']+'-'+str(h)
            _mks_menu_dict = {key:_mks_info}
        _rasi_entry_info = ''; _rasi_entry_menu_dict = {}
        key = self.resources['raasi_str']+' '+self.resources['entry_str']
        """
        if chart_index == _mixed_chart_index:
            for p in ['L']:#+[*range(9)]:
                print(chart_index,_mixed_chart_index,v1,v2,dcf)
                pstr = self.resources['ascendant_str'] if p=='L' else utils.PLANET_NAMES[p]
                ajd,al = charts.next_planet_entry_date_mixed_chart(jd, place, p, v1, chart_method_1, 
                                                    v2, chart_method_2)
                ay,am,ad,ah = utils.jd_to_gregorian(ajd)
                _rasi_entry_info += pstr+' '+ self.resources['next_str']+' '+ \
                    self.resources['raasi_str']+' ('+utils.RAASI_LIST[int(round(al/30,0))%12]+') '+self.resources['entry_str']+\
                    ' : (' + str(ay)+','+str(am)+','+str(ad) +') ' + utils.to_dms(ah)+'<br>'
                ajd,al = charts.previous_planet_entry_date_mixed_chart(jd, place, p, v1, chart_method_1, 
                                                    v2, chart_method_2)
                ay,am,ad,ah = utils.jd_to_gregorian(ajd)
                _rasi_entry_info += pstr+' '+ self.resources['previous_str']+' '+ \
                    self.resources['raasi_str']+' ('+utils.RAASI_LIST[int(round(al/30,0))%12]+') '+self.resources['entry_str']+\
                    ' : (' + str(ay)+','+str(am)+','+str(ad) +') ' + utils.to_dms(ah)+'<br><br>'
        else:
        """
        if chart_index != _mixed_chart_index:
            #import time
            #start_time = time.time()
            for p in ['L']:#+[*range(9)]:
                pstr = self.resources['ascendant_str'] if p=='L' else utils.PLANET_NAMES[p]
                ajd,al = charts.next_planet_entry_date_divisional_chart(jd, place, p, dcf, direction=1,
                                        chart_method=chart_method, base_rasi=base_rasi,
                                        count_from_end_of_sign=count_from_end_of_sign)
                ay,am,ad,ah = utils.jd_to_gregorian(ajd)
                _rasi_entry_info += pstr+' '+ self.resources['next_str']+' '+ \
                    self.resources['raasi_str']+' ('+utils.RAASI_LIST[int(round(al/30,0))%12]+') '+self.resources['entry_str']+\
                    ' : (' + str(ay)+','+str(am)+','+str(ad) +') ' + utils.to_dms(ah)+'<br>'
                ajd,al = charts.previous_planet_entry_date_divisional_chart(jd, place, p, dcf,
                                        chart_method=chart_method, base_rasi=base_rasi,
                                        count_from_end_of_sign=count_from_end_of_sign)
                ay,am,ad,ah = utils.jd_to_gregorian(ajd)
                _rasi_entry_info += pstr+' '+ self.resources['previous_str']+' '+ \
                    self.resources['raasi_str']+' ('+utils.RAASI_LIST[int(round(al/30,0))%12]+') '+self.resources['entry_str']+\
                    ' : (' + str(ay)+','+str(am)+','+str(ad) +') ' + utils.to_dms(ah)+'<br><br>'
            _rasi_entry_menu_dict = {key:_rasi_entry_info}
            #end_time = time.time(); print('cpu time planet entry',end_time-start_time,'seconds')
        _latta_info = ''; _latta_planets_stars = charts.lattha_stars_planets(planet_positions)
        #print('lattha_stars_planets',_latta_planets_stars)
        _star_list = [utils.NAKSHATRA_LIST[s] for s in const.abhijit_order_of_stars]
        #print([(s+1,_star_list[s]) for s in range(28)])
        for p,(p_star,l_star) in enumerate(_latta_planets_stars):
            _latta_info += utils.PLANET_NAMES[p]+' ( '+utils.NAKSHATRA_LIST[p_star-1]+' ) : '+_star_list[l_star-1]+'<br>'
        _latta_menu_dict = {self.resources['lattha_star_str']:_latta_info}
        _graha_drekkana_dict = {}; _graha_drekkana_widgets = None
        _nava_thaara_dict = {}; _nava_thaara_widgets = None
        _spl_thaara_dict = {}; _spl_thaara_widgets = None
        _special_thaara_dict = {}; _special_thaara_widgets = None
        if chart_index == 0: # Only for Raasi
            _drek_str = self.resources['drekkanam_str'].replace(' (D3)','')
            key = self.resources['planet_str']+' '+_drek_str
            _gd_info = [[utils.PLANET_NAMES[p],''] if gpt==0 else [utils.PLANET_NAMES[p],self.resources[const.graha_drekkana_types[gpt]+'_str']] \
                  for p,gpt in enumerate(drik.graha_drekkana(jd, place))]
            _gd_colors = [['brown','green'] for _ in range(len(drik.planet_list))]
            _graha_drekkana_widgets = [LabelGrid(data=_gd_info,colors=_gd_colors)]
            _graha_drekkana_dict = { key:vl_chart}
            
            key = self.resources['nava_thaara_str']
            _navas = ['janma_str','sampatha_str','vipatha_str','kshema_str','prathyaka_str','saadhana_str','naidhana_str','mithra_str','paramithra_str']
            v_layout = QVBoxLayout()
            v_layout.addWidget(QLabel(key+' ('+self.resources['ascendant_str']+')'))
            _star_list = utils.NAKSHATRA_LIST
            _nava_colors = [['green','brown','blue','blue','blue']for _ in range(len(_navas))]
            _ntl = drik.nava_thaara(jd, place, from_lagna_or_moon=0)
            _nava_info = [[self.resources[_navas[n]]]+[utils.PLANET_NAMES[lord]]+[_star_list[s] for s in st_list] for n,(lord,st_list) in enumerate(_ntl)]
            v_layout.addWidget(LabelGrid(data=_nava_info,colors=_nava_colors))
            v_layout.addWidget(QLabel(key+' ('+utils.PLANET_NAMES[1]+')'))
            _ntl = drik.nava_thaara(jd, place, from_lagna_or_moon=1)
            _nava_info = [[self.resources[_navas[n]]]+[utils.PLANET_NAMES[lord]]+[_star_list[s] for s in st_list] for n,(lord,st_list) in enumerate(_ntl)]
            v_layout.addWidget(LabelGrid(data=_nava_info,colors=_nava_colors))
            _widget = QWidget()
            _widget.setLayout(v_layout)
            _nava_thaara_widgets = [_widget]
            _nava_thaara_dict = {key:vl_chart}

            v_layout = QVBoxLayout()
            key = self.resources['special_thaara_str']
            _spls = ['janma_str','karma_str','samudayika_str','sangathika_str','jaathi_str','naidhana_str','desha_str','abhisheka_str','aadhaana_str','vainasika_str','maanasa_str']
            v_layout.addWidget(QLabel(key+' ('+self.resources['ascendant_str']+')'))
            _star_list = utils.get_nakshathra_list_with_abhijith()
            _spl_colors = [['green','brown','blue']for _ in range(len(_spls))]
            _ntl = drik.special_thaara(jd, place, from_lagna_or_moon=0)
            _spl_info = [[self.resources[_spls[s]]]+[utils.PLANET_NAMES[lord],_star_list[star]] for s,(lord,star) in enumerate(_ntl)]
            v_layout.addWidget(LabelGrid(data=_spl_info,colors=_spl_colors))
            v_layout.addWidget(QLabel(key+' ('+utils.PLANET_NAMES[1]+')'))
            _ntl = drik.special_thaara(jd, place, from_lagna_or_moon=1)
            _spl_info = [[self.resources[_spls[s]]]+[utils.PLANET_NAMES[lord],_star_list[star]] for s,(lord,star) in enumerate(_ntl)]
            v_layout.addWidget(LabelGrid(data=_spl_info,colors=_spl_colors))
            _widget = QWidget()
            _widget.setLayout(v_layout)
            _spl_thaara_widgets = [_widget]
            _spl_thaara_dict = {key:vl_chart}
        """ Construct final dictionary from above data """
        _arudha_menu_dict = {self.resources['arudhas_str']:self._horo._arudha_menu_dict}
        _special_menu_dict_1d_chart = {**_planets_menu_dict, **_arudha_menu_dict,**_varnada_menu_dict,**_karaka_menu_dict,
                                       **_special_lagna_menu_dict,**_special_planets_menu_dict,
                                       **_sphuta_menu_dict, **_prasna_menu_dict, **_saham_menu_dict,
                                       **_paachakadi_menu_dict, **_brahma_menu_dict, **_drishti_menu_dict,
                                       **_yogi_menu_dict,**_planets_info_dict, **_pushkara_menu_dict,
                                       **_combustion_dict,**_grahayudh_dict, **_mrityu_dict, **_aspect_dict,
                                       **_mks_menu_dict, **_rasi_entry_menu_dict, **_latta_menu_dict,
                                       **_navamsa_drekkana_lord_menu_dict,**_graha_drekkana_dict,
                                       **_nava_thaara_dict, **_spl_thaara_dict}
        return _special_menu_dict_1d_chart,_drishti_table_widgets,_planets_info_table,_aspect_widgets, \
                        _ndl_22_widgets, _ndl_64_widgets, _graha_drekkana_widgets,_nava_thaara_widgets, \
                        _spl_thaara_widgets
    def _update_tabs_with_divisional_charts(self,jd,place,chart_index=None,chart_method=None,divisional_chart_factor=None,
                                            base_rasi=None,count_from_end_of_sign=None,
                                    chart_index_1=None,chart_method_1=None,chart_index_2=None,chart_method_2=None):
        y,m,d,fh = utils.jd_to_gregorian(jd); dob = drik.Date(y,m,d); tob=(fh,0,0)
        tab_str,_chart_title_separator = self._get_tab_chart_prefix()
        format_str = '%-18s%-20s\n'
        t = chart_index
        if divisional_chart_factor==None:
            if chart_index < _custom_chart_index:
                dcf = const.division_chart_factors[chart_index]
            else:
                dcf = const.DEFAULT_CUSTOM_VARGA_FACTOR
        else:
            dcf = divisional_chart_factor
        if chart_index == _custom_chart_index:
            tab_name = tab_str + 'D'+str(dcf)
        elif chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[chart_index_1]; v2 = const.division_chart_factors[chart_index_2]
            dcf = v1*v2
            mds = ' D'+str(v1)+'('+str(chart_method_1)+')xD'+ str(v2)+'('+str(chart_method_2)+')'+' '
            tab_name = tab_str + mds
        else:
            tab_name = tab_str + self.resources[_chart_names[t]]
        if chart_index==_mixed_chart_index:
            self._kundali_info,self._kundali_chart,self._kundali_ascendant_house = \
                self._horo.get_horoscope_information_for_mixed_chart(chart_index_1=chart_index_1,
                                chart_method_1=chart_method_1,chart_index_2=chart_index_2,chart_method_2=chart_method_2,
                                varnada_method=self._varnada_method_index)
        else:
            self._kundali_info,self._kundali_chart,self._kundali_ascendant_house = \
                self._horo.get_horoscope_information_for_chart(chart_index=chart_index,chart_method=chart_method,
                                            divisional_chart_factor=dcf,
                                            base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
        """ Get Context Menu Dictionary and associated data """
        _special_menu_dict_1d_chart,_drishti_table_widgets,_planets_info_table,_aspect_widgets,\
                        _ndl_22_widgets,_ndl_64_widgets, _graha_drekkana_widgets, \
                        _nava_thaara_widgets, _spl_thaara_widgets = \
                    self._get_menu_dicts(jd, place, chart_index, chart_method,
                            divisional_chart_factor, base_rasi, count_from_end_of_sign, chart_index_1,
                            chart_method_1, chart_index_2, chart_method_2)
        _arudha_lagnas_count = len(_arudha_lagnas_included_in_chart.keys())
        planet_count = len(drik.planet_list) + 1 # Inlcuding Lagnam
        #print(drik.planet_list,planet_count)
        upagraha_count = len(const._solar_upagraha_list) + len(const._other_upagraha_list)
        special_lagna_count = len(const._special_lagna_list)
        total_row_count = _arudha_lagnas_count + planet_count + upagraha_count + special_lagna_count
        """ update the chart from horoscope charts """
        _chart_title = tab_name + _chart_title_separator+self._date_text_years + \
                        _chart_title_separator+self._time_text_years +_chart_title_separator + \
                        self._timezone_text + _chart_title_separator + self._place_name + _chart_title_separator + \
                        self._lat_chart_text + " , " + self._long_chart_text
        self.tabWidget.setTabText(_tabcount_before_chart_tab,tab_name.replace('\n','-'))
        i_start = 0#t*total_row_count
        # 26 #29 # 4 for special lagnas, 10 from lagnam and planets, 12 rows for upagraha details
        i_end = i_start + total_row_count
        chart_info = ''
        western_data = []
        _kundali_info = self._kundali_info.copy()
        if self._western_chart:
            i_start = i_start + special_lagna_count + _arudha_lagnas_count + 2 #2=>VL and Md
            i_end = i_start + planet_count
            _kundali_info = dict(list(self._kundali_info.items())[i_start:i_end])
        i_i = -1
        for (k,v) in _kundali_info.items():##list(self._horoscope_info.items())[i_start:i_end]:
            i_i += 1
            k1 = k.split('-')[-1]
            v1 = v.split('-')[0]
            if self._western_chart: # Remove Karaka strings starting from "("
                v1 = v1.split('(')[0]
            chart_info += format_str % (k1,v1)
            western_data.append(k1+' '+v1)
        if self._western_chart:
            i_end += upagraha_count-1# if const.include_maandhi_in_charts else upagraha_count
        chart_info_list = chart_info.split('\n')
        chart_info_count = len(chart_info_list); chart_info_count_half = int(chart_info_count/2)
        chart_info1 = '\n'.join(chart_info_list[:chart_info_count_half])
        chart_info2 = '\n'.join(chart_info_list[chart_info_count_half:])
        self._chart_info_label1.setText(chart_info1);self._chart_info_label1.adjustSize()
        self._chart_info_label1.setMaximumWidth(_chart_info_label_width)  # Fixed defect here in 1.0.2
        self._chart_info_label2.setText(chart_info2);self._chart_info_label2.adjustSize()
        self._chart_info_label2.setMaximumWidth(_chart_info_label_width)  # Fixed defect here in 1.0.2
        chart_data_1d = self._kundali_chart#self._horoscope_charts[t]
        chart_data_1d = [x.strip() for x in chart_data_1d] # remove \n from end of each element
        hl = self._horo._hora_lagna_data_kundali; gl = self._horo._ghati_lagna_data_kundali
        vl = self._horo._vighati_lagna_data_kundali; bl = self._horo._bhava_lagna_data_kundali;
        sl = self._horo._sree_lagna_data_kundali # V3.1.9
        if const.include_maandhi_in_charts and not self._western_chart:
            ml = self._horo._maandhi_data_kundali
            chart_data_1d[list(self._horo._maandhi_data_kundali.values())[0]]+='\n'+self.resources['maandi_str']
        adc = []
        if const.include_special_and_arudha_lagna_in_charts:
            for k,v in enumerate(self._horo._arudha_lagna_data_kundali):
                v1 = v
                if k in bl.values() and self.resources['bhava_lagna_short_str'] not in v1:
                    v1 += '\n' + self.resources['bhava_lagna_short_str'] # V3.1.9
                if k in sl.values() and self.resources['sree_lagna_short_str'] not in v1:
                    v1 += '\n' + self.resources['sree_lagna_short_str'] # V3.1.9
                if k in hl.values() and self.resources['hora_lagna_short_str'] not in v1:
                    v1 += '\n' + self.resources['hora_lagna_short_str']
                if k in gl.values() and self.resources['ghati_lagna_short_str'] not in v1:
                    v1 += '\n' + self.resources['ghati_lagna_short_str']
                if k in vl.values() and self.resources['vighati_lagna_short_str'] not in v1:
                    v1 += '\n' + self.resources['vighati_lagna_short_str']
                if not self._western_chart:
                    if const.include_maandhi_in_charts and k in ml.values() and self.resources['maandi_str'] not in v1:
                        v1 += '\n' + self.resources['maandi_str']
                adc.append(v1.strip())            
        self._horo._arudha_lagna_data_kundali = adc
        self._western_chart = False
        if 'north' in self._chart_type.lower():
            asc_house = self._kundali_ascendant_house#self._horoscope_ascendant_houses[t]+1
            self._kundali_charts[0]._asc_house = asc_house
            chart_data_north = chart_data_1d[asc_house-1:]+chart_data_1d[0:asc_house-1]
            ald_north = self._horo._arudha_lagna_data_kundali[:]
            ald_north = ald_north[asc_house-1:]+ald_north[0:asc_house-1]
            self._kundali_charts[0].setData(chart_data_north,chart_title=_chart_title,
                                            chart_title_font_size=north_chart_title_font_size,
                                            menu_dict=_special_menu_dict_1d_chart,varga_factor=dcf,
                                            drishti_table_widgets=_drishti_table_widgets,
                                            planet_info_widgets=[_planets_info_table],
                                            aspect_widgets=_aspect_widgets,
                                            ndl_22_widgets=_ndl_22_widgets,ndl_64_widgets=_ndl_64_widgets,
                                            graha_drekkana_widgets=_graha_drekkana_widgets,
                                            nava_thaara_widgets=_nava_thaara_widgets,
                                            spl_thaara_widgets=_spl_thaara_widgets)
        elif 'east' in self._chart_type.lower():
            chart_data_2d = utils._convert_1d_house_data_to_2d(chart_data_1d,self._chart_type)
            row,col = const._asc_house_row_col__chart_map[self._kundali_ascendant_house]
            arudha_lagna_data_2d = utils._convert_1d_house_data_to_2d(self._horo._arudha_lagna_data_kundali,self._chart_type)
            self._kundali_charts[0]._asc_house = row*self._kundali_charts[0].row_count+col
            self._kundali_charts[0].setData(chart_data_2d,chart_title=_chart_title,
                                            chart_title_font_size=east_chart_title_font_size,
                                            menu_dict=_special_menu_dict_1d_chart,varga_factor=dcf,
                                            drishti_table_widgets=_drishti_table_widgets,
                                            planet_info_widgets=[_planets_info_table],
                                            aspect_widgets=_aspect_widgets,
                                            ndl_22_widgets=_ndl_22_widgets,ndl_64_widgets=_ndl_64_widgets,
                                            graha_drekkana_widgets=_graha_drekkana_widgets,
                                            nava_thaara_widgets=_nava_thaara_widgets,
                                            spl_thaara_widgets=_spl_thaara_widgets)
        elif 'west' in self._chart_type.lower():
            self._western_chart = True
            self._kundali_charts[0].setData(western_data,chart_title=_chart_title,chart_title_font_size=west_chart_title_font_size)
            self._kundali_charts[0].update()                
        elif 'sudar' in self._chart_type.lower():
            dcf = const.division_chart_factors[t]
            chart_1d = sudharsana_chakra.sudharshana_chakra_chart(jd, place,self._date_of_birth,years_from_dob=0, divisional_chart_factor=dcf)
            data_1d = self._convert_1d_chart_with_planet_names(chart_1d)
            self._kundali_charts[0].setData(data_1d,chart_title=_chart_title,chart_title_font_size=sudarsana_chakra_chart_title_font_size)
            self._kundali_charts[0].update()                
        else: # south indian'
            chart_data_2d = utils._convert_1d_house_data_to_2d(chart_data_1d)
            row,col = const._asc_house_row_col__chart_map[self._kundali_ascendant_house]
            arudha_lagna_data_2d = utils._convert_1d_house_data_to_2d(self._horo._arudha_lagna_data_kundali)
            self._kundali_charts[0]._asc_house = (row,col)
            self._kundali_charts[0].setData(chart_data_2d,chart_title=_chart_title,
                                            chart_title_font_size=south_chart_title_font_size,
                                            menu_dict=_special_menu_dict_1d_chart,varga_factor=dcf,
                                            drishti_table_widgets=_drishti_table_widgets,
                                            planet_info_widgets=[_planets_info_table],
                                            aspect_widgets=_aspect_widgets,
                                            ndl_22_widgets=_ndl_22_widgets,ndl_64_widgets=_ndl_64_widgets,
                                            graha_drekkana_widgets=_graha_drekkana_widgets,
                                            nava_thaara_widgets=_nava_thaara_widgets,
                                            spl_thaara_widgets=_spl_thaara_widgets)
        self._kundali_charts[0].update()
    def _bhava_method_changed(self):
        _bhava_value_index = self._bhava_method_combo.currentIndex()
        self._bhaava_madhya_method = list(const.available_house_systems.keys())[_bhava_value_index] 
        self._update_bhava_chart_information()
    def _update_pps_tab_information(self):
        dob = self._horo.Date
        tob = self._horo.birth_time
        jd = self._horo.julian_day
        place = self._horo.Place
        bs = drik.nakshatra(jd, place)[0]
        paksha_index =  1 if drik.tithi(jd, place)[0] <= 15 else 2
        bird_index = pancha_paksha.pancha_pakshi_stars_birds_paksha[bs-1][paksha_index-1]
        dt = datetime.now().timetuple()
        dob = dt[0:3]; tob=dt[3:6]
        headers,top_level_list,child_level_list,parent_level_labels = pancha_paksha.construct_pancha_pakshi_information(dob, tob, place, nakshathra_bird_index=bird_index)
        self._pps_tree.bird_combo.clear()
        self._pps_tree.bird_combo.addItems([self.resources[b+'_str'] for b in pancha_paksha.pancha_pakshi_birds])
        self._pps_tree.bird_combo.setCurrentIndex(bird_index-1)
        self._pps_tree.populate_tree(bird_index,headers, top_level_list, child_level_list, hide_headers=False,
                                     parent_level_labels=parent_level_labels,
                                     tree_font_size=_pancha_pakshi_sastra_font_size)
        self.tabWidget.setTabText(_tabcount_before_chart_tab-1,self.resources['pancha_pakshi_sastra_str'])
    def _update_bhava_chart_information(self):
        jd = self._horo.julian_day ; place = self._horo.Place
        self._bhava_chart_data,self._bhava_chart_info = self._horo.get_bhava_chart_information(jd,place,self._bhaava_madhya_method)
        #self._bhava_chart_data,self._bhava_chart_info = self._horo.bhava_chart,self._horo.bhava_chart_info
        format_str = '%-18s%-20s\n'
        tab_str,_chart_title_separator = self._get_tab_chart_prefix()
        #_chart_title_separator = ' '
        tab_name = tab_str + self.resources['bhaava_str']
        if 'south' in self._chart_type.lower() or 'east' in self._chart_type.lower():
            _chart_title_separator = '\n'
        _house_str = self.resources['house_str']
        _starts_at_str = self.resources['starts_at_str']
        _middle_str = self.resources['middle_str']
        _ends_at_str = self.resources['ends_at_str']
        _planets_str = self.resources['planets_str']
        _label_str = ''
        _header_str = _house_str+'\t'+_starts_at_str+'\t\t'+_middle_str+'\t\t'+_ends_at_str+'\t\t'+_planets_str
        _label_str += _header_str
        data = [['' for _ in range(self._bhava_table_columns)] for _ in range(self._bhava_table_rows)]
        data[0] = [_house_str,_starts_at_str,_middle_str,_ends_at_str,_planets_str]
        for r in range(1,self._bhava_table_rows):
            for c in range(self._bhava_table_columns):
                data[r][c] = self._bhava_chart_info[r-1][c]
        self._bhava_table.setData(data)
        _chart_title = tab_name + _chart_title_separator+self._date_text_years + \
                        _chart_title_separator+self._time_text_years +_chart_title_separator + \
                        self._timezone_text + _chart_title_separator + self._place_name + _chart_title_separator + \
                        self._lat_chart_text + " , " + self._long_chart_text
        chart_data_1d = self._bhava_chart_data
        chart_data_1d = [x[:-1] for x in chart_data_1d] # remove ]n from end of each element
        #self._western_chart = False
        if 'north' in self._bhava_chart_type.lower():
            _ascendant = drik.ascendant(jd,place)
            asc_house = _ascendant[0]+1
            self._bhava_chart._asc_house = asc_house
            chart_data_north = chart_data_1d[asc_house-1:]+chart_data_1d[0:asc_house-1]
            self._bhava_chart.setData(chart_data_north,chart_title=_chart_title,chart_title_font_size=north_chart_title_font_size)
        elif 'east' in self._bhava_chart_type.lower():
            chart_data_2d = utils._convert_1d_house_data_to_2d(chart_data_1d,self._chart_type)
            #row,col = _get_row_col_string_match_from_2d_list(chart_data_2d,self.resources['ascendant_str'])
            row,col = const._asc_house_row_col__chart_map[self._kundali_ascendant_house]
            self._bhava_chart._asc_house = row*self._bhava_chart.row_count+col
            self._bhava_chart.setData(chart_data_2d,chart_title=_chart_title,chart_title_font_size=east_chart_title_font_size)
        elif 'west' in self._bhava_chart_type.lower():
            print('!!!! Why bhaava type set to WESTERN????')
            return; western_data = []
            #self._western_chart = True
            #print('western chart data',western_data)
            self._bhava_chart.setData(western_data,chart_title=_chart_title,chart_title_font_size=west_chart_title_font_size)
            self._bhava_chart.update()
        elif 'sudar' in self._bhava_chart_type.lower():
            chart_1d = sudharsana_chakra.sudharshana_chakra_chart(jd, place,self._date_of_birth,years_from_dob=0)
            data_1d = self._convert_1d_chart_with_planet_names(chart_1d)
            self._bhava_chart.setData(data_1d,chart_title=_chart_title,chart_title_font_size=sudarsana_chakra_chart_title_font_size)
            self._bhava_chart.update()                
        else: # south indian'
            chart_data_2d = utils._convert_1d_house_data_to_2d(chart_data_1d)
            #row,col = _get_row_col_string_match_from_2d_list(chart_data_2d,self.resources['ascendant_str'])
            row,col = const._asc_house_row_col__chart_map[self._kundali_ascendant_house]
            self._bhava_chart._asc_house = (row,col)
            self._bhava_chart.setData(chart_data_2d,chart_title=_chart_title,chart_title_font_size=south_chart_title_font_size)
        self._bhava_chart.update()
    def _update_tab_chart_information(self,chart_index=None,chart_method=None,divisional_chart_factor=None,
                                      base_rasi=None,count_from_end_of_sign=None,
                                      chart_index_1=None,chart_method_1=None,chart_index_2=None,chart_method_2=None):
        info_str = ''
        format_str = _KEY_VALUE_FORMAT_
        self._fill_panchangam_info(info_str, format_str)
        jd = self._horo.julian_day  # For ascendant and planetary positions, dasa bukthi - use birth time
        place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        self._update_tabs_with_divisional_charts(jd,place,chart_index=chart_index,chart_method=chart_method,
                                                 divisional_chart_factor=divisional_chart_factor,
                                                 base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign,
                                                 chart_index_1=chart_index_1,chart_method_1=chart_method_1,
                                                 chart_index_2=chart_index_2,chart_method_2=chart_method_2)
        self._kundali_charts[0].update()
    def _update_table_tab_information(self,tab_title_str,tab_start,tab_count,rows_per_table,tables_per_tab,
                                              table_info,db_tables,table_titles,dhasa_bhukti=True):#,app_check=True):
        self._show_hide_marriage_checkboxes(False)
        tab_title = tab_title_str
        if dhasa_bhukti:
            tab_title = tab_title_str+'-'+self.resources['dhasa_bhukthi_str']
        table_index = 0
        for db_tab in range(tab_count):
            p = db_tab*(rows_per_table)*tables_per_tab
            for col in range(tables_per_tab):
                i_start = p
                i_end = i_start + rows_per_table
                db_list = table_info[i_start:i_end]
                if not db_list:
                    continue
                if dhasa_bhukti:
                    db_str = db_list[0][0].split('-')[0]+' '+self.resources['dhasa_str']
                    db_tables[db_tab][col].setHorizontalHeaderItem(0,QTableWidgetItem(db_str+'\n'+self.resources['starts_at_str']))
                else:
                    db_tables[db_tab][col].setHorizontalHeaderItem(0,QTableWidgetItem(table_titles[table_index]))
                t_row = 0
                for k,v in db_list:
                    k1 = k
                    if dhasa_bhukti:
                        k1 = k.split('-')[-1]+' '+self.resources['bhukthi_str']
                    db_tables[db_tab][col].setVerticalHeaderItem(t_row,QTableWidgetItem(str(k1)))
                    db_tables[db_tab][col].setItem(t_row,0,QTableWidgetItem(str(v)))
                    t_row += 1
                p = i_end
                table_index += 1
                db_tables[db_tab][col].horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
                db_tables[db_tab][col].verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
                db_tables[db_tab][col].verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
                db_tables[db_tab][col].horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            tab_text = tab_title+'-'+str(db_tab+1) if tab_count > 1 else tab_title
            self.tabWidget.setTabText(tab_start+db_tab,tab_text)            
    def _update_amsa_ruler_tab_information(self,chart_index=1,chart_method=1,divisional_chart_factor=None,
                                            base_rasi=None,count_from_end_of_sign=None):
        tab_str,_chart_title_separator = self._get_tab_chart_prefix()
        self.tabWidget.setTabText(_amsa_ruler_tab_start,tab_str+self.resources['amsa_ruler_str'])
        _ar_keys = list(const.amsa_rulers.keys())
        self._amsa_ruler_dcf = _ar_keys[chart_index]
        _amsa_resources = charts.get_amsa_resources(const._DEFAULT_LANGUAGE)
        _amsa_planet_info,_amsa_special_info,_amsa_upagraha_info,_amsa_sphuta_info = \
                    charts._amsa(self._horo.julian_day, self._horo.Place,ayanamsa_mode=self._ayanamsa_mode,
                                 divisional_chart_factor=self._amsa_ruler_dcf,chart_method=chart_method,
                                  include_special_lagnas=_amsa_include_special_lagna,
                                  include_upagrahas=_amsa_include_upagraha,include_sphutas=_amsa_include_sphuta,
                                  base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
        for r,(p,ai) in enumerate(_amsa_planet_info.items()):
            am = _amsa_resources[str(self._amsa_ruler_dcf)][ai]
            planet = self.resources['ascendant_str'] if p == const._ascendant_symbol else utils.PLANET_NAMES[p]                
            self._amsa_ruler_table1.setItem(r,0,QTableWidgetItem(planet))
            self._amsa_ruler_table1.setItem(r,1,QTableWidgetItem(am))
        self._amsa_ruler_table1.resizeColumnsToContents()
        if _amsa_include_special_lagna: 
            for r,(p,ai) in enumerate(_amsa_special_info.items()):
                #am = const.amsa_rulers[self._amsa_ruler_dcf][ai]
                am = _amsa_resources[str(self._amsa_ruler_dcf)][ai]
                planet = self.resources[p]                
                self._amsa_ruler_table2.setItem(r,0,QTableWidgetItem(planet))
                self._amsa_ruler_table2.setItem(r,1,QTableWidgetItem(am))
            self._amsa_ruler_table2.resizeColumnsToContents()
        if _amsa_include_upagraha: 
            for r,(p,ai) in enumerate(_amsa_upagraha_info.items()):
                #am = const.amsa_rulers[self._amsa_ruler_dcf][ai]
                am = _amsa_resources[str(self._amsa_ruler_dcf)][ai]
                planet = self.resources[p]                
                self._amsa_ruler_table3.setItem(r,0,QTableWidgetItem(planet))
                self._amsa_ruler_table3.setItem(r,1,QTableWidgetItem(am))
                self._amsa_ruler_table3.resizeColumnsToContents()
        if _amsa_include_sphuta: 
            for r,(p,ai) in enumerate(_amsa_sphuta_info.items()):
                #am = const.amsa_rulers[self._amsa_ruler_dcf][ai]
                am = _amsa_resources[str(self._amsa_ruler_dcf)][ai]
                planet = self.resources[p] + ' ' + self.resources['sphuta_str']
                self._amsa_ruler_table4.setItem(r,0,QTableWidgetItem(planet))
                self._amsa_ruler_table4.setItem(r,1,QTableWidgetItem(am))
                self._amsa_ruler_table4.resizeColumnsToContents()
        return 
    def _update_chakra_tab_information(self,chart_index=None,chart_method=None,divisional_chart_factor=None,
                                            base_rasi=None,count_from_end_of_sign=None,
                                    chart_index_1=None,chart_method_1=None,chart_index_2=None,chart_method_2=None):
        if divisional_chart_factor==None:
            if chart_index < _custom_chart_index:
                dcf = const.division_chart_factors[chart_index]
            else:
                dcf = const.DEFAULT_CUSTOM_VARGA_FACTOR
        else:
            dcf = divisional_chart_factor
        tab_str,_chart_title_separator = self._get_tab_chart_prefix()
        tab_str += self.resources['chakra_str']
        if chart_index == _custom_chart_index:
            tab_title_str = tab_str + '-' + 'D'+str(dcf)
        elif chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[chart_index_1]; v2 = const.division_chart_factors[chart_index_2]
            mds = ' D'+str(v1)+'('+str(chart_method_1)+')xD'+ str(v2)+'('+str(chart_method_2)+')'+' '
            tab_title_str = tab_str + mds
        else:
            tab_title_str = tab_str+'-'+self._chakra_chart_combo.currentText()
        self.tabWidget.setTabText(_chakra_tab_start,tab_title_str)
        place = self._horo.Place
        dob = self._horo.Date
        tob = self._horo.birth_time
        jd =utils.julian_day_number(dob, tob)
        planets_in_retrograde = drik.planets_in_retrograde(jd, place)
        _chakra_type_index = self._chakra_options_group.checkedId()
        if chart_index==_mixed_chart_index: # Kota Chakra
            planet_positions = charts.mixed_chart(jd, place, varga_factor_1=v1, chart_method_1=chart_method_1,
                                                  varga_factor_2=v2, chart_method_2=chart_method_2)
        else:
            planet_positions = charts.divisional_chart(jd, place,divisional_chart_factor=dcf,
                                    chart_method=self._chakra_method_index,base_rasi=base_rasi,
                                    count_from_end_of_sign=count_from_end_of_sign)
        if _chakra_type_index==0:
            nak = drik.nakshatra(self._birth_julian_day, place)
            birth_star,birth_star_padha=nak[0],nak[1]
            widget = KotaChakra(birth_star=birth_star)
            widget.setData(planet_positions=planet_positions, birth_star=birth_star,
                                        birth_star_padha=birth_star_padha,planets_in_retrograde=planets_in_retrograde,
                                        label_font_size=_chakra_label_font_size)
            kota_lord = widget._kota_lord; kota_paala = widget._kota_paala
            self._chakra_info_label.setVisible(True)
            self._chakra_info_label.setText(self.resources['kota_swami_str']+' : '+kota_lord+' '+
                                            self.resources['kota_paala_str']+' : '+kota_paala)
        elif _chakra_type_index==1: # Kaala Chakra
            widget = KaalaChakra()
            if chart_index != None and chart_index==0:
                planet_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
            else:
                planet_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
            base_star,_,_ = drik.nakshatra_pada(planet_long)
            widget.setData(planet_positions=planet_positions, base_star=base_star,
                                        planets_in_retrograde=planets_in_retrograde,
                                        label_font_size=_chakra_label_font_size)
            self._chakra_info_label.setVisible(False)
        elif _chakra_type_index==2: # Sarvatobadra
            widget = Sarvatobadra()
            widget.setData(planet_positions=planet_positions,
                                        planets_in_retrograde=planets_in_retrograde,
                                        label_font_size=_chakra_label_font_size)
            self._chakra_info_label.setVisible(False)
        elif _chakra_type_index==3: # Surya Kalanala
            if chart_index != None and chart_index==0:
                planet_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
            else:
                planet_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
            base_star,_,_ = drik.nakshatra_pada(planet_long)
            widget = SuryaKalanala(base_star=base_star)
            widget.setData(planet_positions=planet_positions, base_star=base_star,
                                        planets_in_retrograde=planets_in_retrograde,
                                        label_font_size=_chakra_label_font_size)
            self._chakra_info_label.setVisible(False)
        elif _chakra_type_index==4: # Chandra Kalanala
            if chart_index != None and chart_index==0:
                planet_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
            else:
                planet_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
            base_star,_,_ = drik.nakshatra_pada(planet_long)
            widget = ChandraKalanala(base_star=base_star)
            widget.setData(planet_positions=planet_positions, base_star=base_star,
                                        planets_in_retrograde=planets_in_retrograde,
                                        label_font_size=_chakra_label_font_size)
            self._chakra_info_label.setVisible(False)
        elif _chakra_type_index==5: # Shoola
            if chart_index != None and chart_index==0:
                planet_long = planet_positions[1][1][0]*30+planet_positions[1][1][1]
            else:
                planet_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
            base_star,_,_ = drik.nakshatra_pada(planet_long)
            widget = Shoola(base_star=base_star)
            widget.setData(base_star=base_star,planet_positions=planet_positions,
                                        planets_in_retrograde=planets_in_retrograde,
                                        label_font_size=_chakra_label_font_size)
            self._chakra_info_label.setVisible(False)
        elif _chakra_type_index==6: # Tripataki
            widget = Tripataki()
            widget.setData(planet_positions=planet_positions,
                                        planets_in_retrograde=planets_in_retrograde,
                                        label_font_size=_chakra_label_font_size)
            self._chakra_info_label.setVisible(False)
        elif _chakra_type_index==7: # Saptha Shalaka / Rahu Kalanala
            widget = SapthaShalaka()
            widget.setData(planet_positions=planet_positions,
                                        planets_in_retrograde=planets_in_retrograde,
                                        label_font_size=_chakra_label_font_size)
            self._chakra_info_label.setVisible(False)
        elif _chakra_type_index==8: # Pancha Shalaka
            widget = PanchaShalaka()
            widget.setData(planet_positions=planet_positions,
                                        planets_in_retrograde=planets_in_retrograde,
                                        label_font_size=_chakra_label_font_size)
            self._chakra_info_label.setVisible(False)
        elif _chakra_type_index==9 and not _EXCLUDE_SAPTHA_NADI_CHARA: # Saptha Naadi
            widget = SapthaNaadi()
            widget.setData(planet_positions=planet_positions,
                                        planets_in_retrograde=planets_in_retrograde,
                                        label_font_size=_chakra_label_font_size)
            self._chakra_info_label.setVisible(False)
        if self._chakra_widget.count() > 1:
            self._chakra_widget.removeWidget(self._chakra_widget.widget(1))
        
        self._chakra_widget.addWidget(widget)
        self._chakra_widget.setCurrentIndex(1)
        #self._chakra_widget.update()

    def _update_kpinfo_information(self,chart_index=None,chart_method=None,
                                       divisional_chart_factor=None,
                                            base_rasi=None,count_from_end_of_sign=None,
                                    chart_index_1=None,chart_method_1=None,chart_index_2=None,chart_method_2=None):
        if divisional_chart_factor==None:
            if chart_index < _custom_chart_index:
                dcf = const.division_chart_factors[chart_index]
            else:
                dcf = const.DEFAULT_CUSTOM_VARGA_FACTOR
        else:
            dcf = divisional_chart_factor
        tab_str,_chart_title_separator = self._get_tab_chart_prefix()
        tab_str += 'KP-'+self.resources['lord_str']
        if chart_index == _custom_chart_index:
            tab_title_str = tab_str + '-' + 'D'+str(dcf)
        elif chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[chart_index_1]; v2 = const.division_chart_factors[chart_index_2]
            mds = ' D'+str(v1)+'('+str(chart_method_1)+')xD'+ str(v2)+'('+str(chart_method_2)+')'+' '
            tab_title_str = tab_str + mds
        else:
            tab_title_str = tab_str+'-'+self._kpinfo_chart_combo.currentText()
        self.tabWidget.setTabText(_kpinfo_tab_start,tab_title_str)
        _sphuta_count = len(const.sphuta_list)
        jd = utils.julian_day_number(self._horo.Date,self._horo.birth_time)
        place = self._horo.Place
        if chart_index==_mixed_chart_index: # Kota Chakra
            planet_positions = charts.mixed_chart(jd, place, varga_factor_1=v1, chart_method_1=chart_method_1,
                                                  varga_factor_2=v2, chart_method_2=chart_method_2)
        else:
            planet_positions = charts.divisional_chart(jd, place,divisional_chart_factor=dcf,
                                    chart_method=self._chakra_method_index,base_rasi=base_rasi,
                                    count_from_end_of_sign=count_from_end_of_sign)
        kp_info = charts.get_KP_lords_from_planet_positions(planet_positions)
        col_count = self._kpinfo_table.columnCount()
        self._kpinfo_table.horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._kpinfo_table.verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        for c,col_str in enumerate(['KP '+self.resources['number_str']]+[self.resources[r] for r in ['nakshatra_lord_str',
                        'sub_lord_str','prathyanthara_lord_str','sookshma_lord_str','praana_lord_str','deha_lord_str']]):
            self._kpinfo_table.setHorizontalHeaderItem(c,QTableWidgetItem(col_str))
        for r,(p,kp_details) in enumerate(kp_info.items()):
            pStr = self.resources['ascendant_str'] if p==const._ascendant_symbol else utils.PLANET_NAMES[p]
            self._kpinfo_table.setVerticalHeaderItem(r,QTableWidgetItem(pStr))
            for c in range(col_count):
                col_str = str(kp_details[c]) if c== 0 else utils.PLANET_NAMES[kp_details[c]]
                self._kpinfo_table.setItem(r,c,QTableWidgetItem(col_str))
                self._kpinfo_table.resizeColumnToContents(c)
            self._kpinfo_table.resizeRowToContents(r)
        #bhava_info = charts.bhava_chart(jd, place, bhava_madhya_method=4) # 4=>KP Method
        bhava_info = charts._bhaava_madhya_new(jd, place, planet_positions=planet_positions, bhava_madhya_method=1)
        h = 1
        for _,(_,bm,_),_ in bhava_info:
            bm1 = drik.dasavarga_from_long(bm)
            pStr = self.resources['house_str']+'-'+str(h)
            self._kpinfo_table.setVerticalHeaderItem(r+h,QTableWidgetItem(pStr))
            kp_info = charts._get_KP_lords_from_planet_longitude(pStr, bm1[0], bm1[1])
            for pStr,kp_details in kp_info.items():
                for c in range(col_count):
                    col_str = str(kp_details[c]) if c== 0 else utils.PLANET_NAMES[kp_details[c]]
                    self._kpinfo_table.setItem(r+h,c,QTableWidgetItem(col_str))
                    self._kpinfo_table.resizeColumnToContents(c)
                self._kpinfo_table.resizeRowToContents(r+h)
                h += 1
    def _update_sphuta_tab_information(self,chart_index=None,method_index=None,varnada_method_index=1,
                                       divisional_chart_factor=None,
                                            base_rasi=None,count_from_end_of_sign=None,
                                    chart_index_1=None,chart_method_1=None,chart_index_2=None,chart_method_2=None):
        if divisional_chart_factor==None:
            if chart_index < _custom_chart_index:
                dcf = const.division_chart_factors[chart_index]
                self._varnada_method_index = self._varnada_varga_dict[dcf]
            else:
                dcf = const.DEFAULT_CUSTOM_VARGA_FACTOR
                self._varnada_method_index = self._varnada_varga_dict[dcf]
        else:
            dcf = divisional_chart_factor
            self._varnada_method_index = self._varnada_varga_dict[dcf] if dcf in const.division_chart_factors \
                        else self._varnada_varga_dict[const.DEFAULT_CUSTOM_VARGA_FACTOR]
        tab_str,_chart_title_separator = self._get_tab_chart_prefix()
        tab_str += self.resources['sphuta_str']+'-'+self.resources['varnada_lagna_str']
        if chart_index == _custom_chart_index:
            tab_title_str = tab_str + '-' + 'D'+str(dcf)
        elif chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[chart_index_1]; v2 = const.division_chart_factors[chart_index_2]
            mds = ' D'+str(v1)+'('+str(chart_method_1)+')xD'+ str(v2)+'('+str(chart_method_2)+')'+' '
            tab_title_str = tab_str + mds
        else:
            tab_title_str = tab_str+'-'+self._sphuta_chart_combo.currentText()
        self.tabWidget.setTabText(_sphuta_tab_start,tab_title_str)
        self._varnada_option_button.setText(self.resources['varnada_lagna_str']+' '+self.resources['options_str'])
        self._varnada_option_info_label.setText(_varnada_method_options[self._varnada_method_index-1])
        _sphuta_count = len(const.sphuta_list)
        dob = self._horo.Date
        tob = self._horo.birth_time
        place = self._horo.Place
        if chart_index==_mixed_chart_index:
            _sphuta_values = self._horo._get_sphuta_mixed_chart(dob, tob, place, varga_factor_1=v1,
                                    chart_method_1=chart_method_1, varga_factor_2=v2, chart_method_2=chart_method_2)
        else:    
            _sphuta_values = self._horo._get_sphuta(dob, tob, place, divisional_chart_factor=dcf,
                                                    chart_method=method_index,
                                            base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
        _sphuta_values = list(_sphuta_values.items())
        self._sphuta_table.horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._sphuta_table.setHorizontalHeaderItem(0,QTableWidgetItem(self.resources['sphuta_str']))
        self._sphuta_table.setHorizontalHeaderItem(1,QTableWidgetItem(self.resources['raasi_str']))
        for r,(k,v) in enumerate(_sphuta_values):
            self._sphuta_table.setItem(r,0,QTableWidgetItem(str(k)))
            self._sphuta_table.setItem(r,1,QTableWidgetItem(str(v)))
        self._sphuta_table.resizeColumnToContents(0);self._sphuta_table.resizeColumnToContents(1)
        self._varnada_table.horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._varnada_table.setHorizontalHeaderItem(0,QTableWidgetItem(self.resources['varnada_lagna_str']))
        self._varnada_table.setHorizontalHeaderItem(1,QTableWidgetItem(self.resources['raasi_str']))
        for h in range(12):
            if chart_index==_mixed_chart_index:
                vl = charts.varnada_lagna_mixed_chart(dob, tob, place, house_index=h+1,
                            varga_factor_1=v1, chart_method_1=chart_method_1,
                            varga_factor_2=v2, chart_method_2=chart_method_2, varnada_method=varnada_method_index)
            else:
                vl = charts.varnada_lagna(dob, tob, place, divisional_chart_factor=dcf, chart_method=method_index, 
                                          house_index=h+1, varnada_method=varnada_method_index)
            self._varnada_table.setItem(h,0,QTableWidgetItem('V'+str(h+1)))
            _value = utils.RAASI_LIST[vl[0]]+' '+utils.to_dms(vl[1],is_lat_long='plong')
            self._varnada_table.setItem(h,1,QTableWidgetItem(_value))
        self._varnada_table.resizeColumnToContents(0);self._varnada_table.resizeColumnToContents(1)
        return 
    def _update_graha_arudha_tab_information(self,chart_index=None, chart_method=None,divisional_chart_factor=None,
                                            base_rasi=None,count_from_end_of_sign=None,chart_index_1=None,
                                            chart_method_1=None,chart_index_2=None,chart_method_2=None):
        _graha_arudha_count = 9
        dob = self._horo.Date; tob = self._horo.birth_time; place = self._horo.Place
        jd_at_dob = utils.julian_day_number(dob,tob)
        if divisional_chart_factor==None:
            if chart_index < _custom_chart_index:
                dcf = const.division_chart_factors[chart_index]
            else:
                dcf = const.DEFAULT_CUSTOM_VARGA_FACTOR
        else:
            dcf = divisional_chart_factor
        tab_str,_chart_title_separator = self._get_tab_chart_prefix()
        tab_str += self.resources['bhava_graha_arudha_str']
        if chart_index == _custom_chart_index:
            tab_title_str = tab_str+'-'+'D'+str(dcf)
        elif chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[chart_index_1]; v2 = const.division_chart_factors[chart_index_2]
            mds = ' D'+str(v1)+'('+str(chart_method_1)+')xD'+ str(v2)+'('+str(chart_method_2)+')'+' '
            tab_title_str = tab_str + mds
        else:
            tab_title_str = tab_str+'-'+self._arudha_chart_combo.currentText()
        self.tabWidget.setTabText(_graha_arudha_tab_start,tab_title_str)
        if chart_index == _mixed_chart_index:
            planet_positions = charts.mixed_chart(jd_at_dob, place, varga_factor_1=v1, chart_method_1=chart_method_1,
                                                  varga_factor_2=v2, chart_method_2=chart_method_2)
        else:    
            planet_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=dcf,
                                                       chart_method=chart_method,
                                            base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
        ga = arudhas.graha_arudhas_from_planet_positions(planet_positions)
        _graha_arudha_values = {}
        self._bhava_arudha_label1.setText('<b>'+self.resources['graha_arudha_str']+'</b>')
        _graha_arudha_values[self.resources['ascendant_str']]=utils.RAASI_LIST[ga[0]]
        for p in range(9):
            _graha_arudha_values[utils.PLANET_NAMES[p]]=utils.RAASI_LIST[ga[p+1]]
        _graha_arudha_values = list(_graha_arudha_values.items())
        for r,(k,v) in enumerate(_graha_arudha_values):
            self._graha_arudha_table.setItem(r,0,QTableWidgetItem(str(k)))
            self._graha_arudha_table.setItem(r,1,QTableWidgetItem(str(v)))
        self._graha_arudha_table.resizeColumnToContents(0);self._graha_arudha_table.resizeColumnToContents(1)
        self._bhava_arudha_label2.setText('<b>'+self.resources['bhava_arudha_str']+'</b>')
        _bhava_arudha_base_index = self._bhava_arudha_combo.currentIndex()
        ba = arudhas.bhava_arudhas_from_planet_positions(planet_positions, arudha_base=_bhava_arudha_base_index)
        for b in range(len(ba)):
            if _bhava_arudha_base_index==0:
                self._bhava_arudha_table.setItem(b,0,QTableWidgetItem(self.resources['bhava_arudha_a'+str(b+1)+'_str']))
            else:
                self._bhava_arudha_table.setItem(b,0,QTableWidgetItem(utils.PLANET_NAMES[_bhava_arudha_base_index-1]+'-' +str(b+1)))
            self._bhava_arudha_table.setItem(b,1,QTableWidgetItem(utils.RAASI_LIST[ba[b]]))
        self._bhava_arudha_table.resizeColumnToContents(0);self._bhava_arudha_table.resizeColumnToContents(1)
        return
    def _update_vimsopaka_bala_tab_information(self):
        #"""
        tab_str,_chart_title_separator = self._get_tab_chart_prefix()
        tab_title_str = tab_str +self.resources['vimsopaka_bala_str']
        tab_start = _vimsopaka_bala_tab_start
        tab_count = _vimsopaka_bala_tab_count
        tables_per_tab = self._vimsopaka_bala_tables_per_tab
        rows_per_table = self._vimsopaka_bala_rows_per_table
        table_info = [(k,v) for dbl in self._vimsopaka_bala_info for k,v in dbl.items() ]
        db_tables = self.vimsopaka_bala_db_tables
        table_titles = [self.resources[t]+'\n'+self.resources['vimsopaka_score_str'] for t in ['shadvarga_bala_str','sapthavarga_bala_str','dhasavarga_bala_str','shodhasavarga_bala_str']]
        self._update_table_tab_information(tab_title_str,tab_start,tab_count,rows_per_table,tables_per_tab,
                                              table_info,db_tables,table_titles,dhasa_bhukti=False)
        return
    def _update_vaiseshikamsa_bala_tab_information(self):
        #"""
        tab_str,_chart_title_separator = self._get_tab_chart_prefix()
        tab_title_str = tab_str+self.resources['vaiseshikamsa_bala_str']
        tab_start = _vaiseshikamsa_bala_tab_start
        tab_count = _vaiseshikamsa_bala_tab_count
        tables_per_tab = self._vaiseshikamsa_bala_tables_per_tab
        rows_per_table = self._vaiseshikamsa_bala_rows_per_table
        table_info = [(k,v) for dbl in self._vaiseshikamsa_bala_info for k,v in dbl.items() ]
        db_tables = self.vaiseshikamsa_bala_db_tables
        table_titles = [self.resources[t]+'\n'+self.resources['vaiseshikamsa_score_str'] for t in ['shadvarga_bala_str','sapthavarga_bala_str','dhasavarga_bala_str','shodhasavarga_bala_str']]
        self._update_table_tab_information(tab_title_str,tab_start,tab_count,rows_per_table,tables_per_tab,
                                              table_info,db_tables,table_titles,dhasa_bhukti=False)
        return
    def _update_other_bala_tab_information(self):
        tab_str,_chart_title_separator = self._get_tab_chart_prefix()
        tab_title_str = tab_str+self.resources['harsha_pancha_dwadhasa_vargeeya_bala_str']
        tab_start = _other_bala_tab_start
        tab_count = _other_bala_tab_count
        tables_per_tab = self._other_bala_tables_per_tab
        rows_per_table = self._other_bala_rows_per_table
        table_info = [(k,v) for dbl in self._other_bala_info for k,v in dbl.items() ]
        db_tables = self.other_bala_db_tables
        table_titles = [self.resources[t] for t in ['harsha_bala_str','pancha_vargeeya_bala_str','dwadhasa_vargeeya_bala_str']]
        self._update_table_tab_information(tab_title_str,tab_start,tab_count,rows_per_table,tables_per_tab,
                                              table_info,db_tables,table_titles,dhasa_bhukti=False)
        return
    def _update_dhasa_bhukthi_tab_information(self):
        if self._western_chart or self._horo==None: return
        """ TODO: Should we change dob,tob to birth date/time here """
        dob = self._horo.Date
        tob = self._horo.birth_time
        place = self._horo.Place
        dcf = const.division_chart_factors[self._current_dhasa_varga_index]
        if self._current_dhasa_type_index==0: #Graha Dhasa
            """
            from jhora.horoscope.dhasa.graha import applicability
            _applicable_conditional_dhasas = applicability.applicability_check(dob, tob, place, divisional_chart_factor=dcf)
            if len(_applicable_conditional_dhasas)>0:
                _applicable_conditional_dhasa_index = list(_graha_dhasa_dict.keys()).index(_applicable_conditional_dhasas[-1])
                self._current_dhasa_index = _applicable_conditional_dhasa_index
                #print('setting self._current_dhasa_index',self._current_dhasa_index)
            """
            if self._current_dhasa_index >= len(_graha_dhasa_dict): self._current_dhasa_index = 0
            self._dhasa_combo.setCurrentIndex(self._current_dhasa_index)
            tab_str, tab_values = list(_graha_dhasa_dict.items())[self._current_dhasa_index]
            #retval = eval('self._horo._get_'+tab_str+'_dhasa_bhukthi(dob, tob, place,divisional_chart_factor='+str(dcf)+')')
            option_str = self._dhasa_bhukthi_options_str[self._current_dhasa_index]
            if option_str.strip() != '': option_str = ','+option_str
            func_str = 'self._horo._get_'+tab_str+'_dhasa_bhukthi'
            arg_str = 'dob, tob, place'#,divisional_chart_factor='+str(dcf)
            eval_str = func_str+'('+arg_str+option_str+')'
            #print(self._dhasa_bhukthi_options_str,'_update_dhasa_bhukthi_tab_information',eval_str)
            retval = eval(eval_str)
            tab_values[7] = retval
            #self._dhasa_bhukthi_options_str[self._current_dhasa_index] = '' # RESET Argument Options
        elif self._current_dhasa_type_index==1: #Raasi Dhasa
            if self._current_dhasa_index >= len(_rasi_dhasa_dict): self._current_dhasa_index = 0
            tab_str, tab_values = list(_rasi_dhasa_dict.items())[self._current_dhasa_index]
            retval = eval('self._horo._get_'+tab_str+'_dhasa(dob, tob, place,divisional_chart_factor='+str(dcf)+')')
            tab_values[7] = retval
        else: # Annual Dhasa
            if self._current_dhasa_index >= len(_annual_dhasa_dict): self._current_dhasa_index = 0
            tab_str, tab_values = list(_annual_dhasa_dict.items())[self._current_dhasa_index]
            _db_info = self._horo._get_annual_dhasa_bhukthi(divisional_chart_factor=dcf)
            tab_values[7] = _db_info[self._current_dhasa_index]
        label_count = min(tab_values[0],_DB_LABEL_MAX); _label_font_size = tab_values[1]
        row_count = tab_values[2]*tab_values[3]
        db_values = [k.replace('\n','')+' ' + v.replace('\n','')+'\n' for k,v in tab_values[7]]
        db_row_count = len(db_values)
        if len(db_values)>0 and len(self._db_labels) > 0:
            [self._db_labels[lbl].setText('') for lbl in range(label_count)] 
            tab_str = self._dhasa_type_combo.currentText()+'-'+self._dhasa_combo.currentText()+'-'+\
                    self._dhasa_varga_combo.currentText()+'-'+self.resources['dhasa_str']+'-'+\
                    self.resources['bhukthi_str']
            self.tabWidget.setTabText(_dhasa_bhukthi_tab_index,tab_str)
            i_start = 0; i_end = row_count
            for lbl in range(label_count):
                self._db_labels[lbl].setVisible(True)
                i_end = i_start + row_count if (i_start + row_count)<=db_row_count else db_row_count
                #print('lbl,i_start,i_end',lbl,i_start,i_end)
                lv = ''.join(db_values[i_start:i_end])
                self._db_labels[lbl].setText(lv)
                self._db_labels[lbl].setStyleSheet('font-size:'+str(_label_font_size)+'pt')
                i_start += row_count
            for lbl in range(label_count,_DB_LABEL_MAX):
                self._db_labels[lbl].setText('')
                self._db_labels[lbl].setVisible(False)
        return
    def _show_hide_marriage_checkboxes(self,_show = True):
        self._mahendra_porutham_checkbox.setVisible(_show)
        self._vedha_porutham_checkbox.setVisible(_show)
        self._rajju_porutham_checkbox.setVisible(_show)
        self._sthree_dheerga_porutham_checkbox.setVisible(_show)
        self._min_score_label.setVisible(_show)
        self._min_score_combo.setVisible(_show)
    def _update_shad_bala_table_information(self):
        tab_str,_chart_title_separator = self._get_tab_chart_prefix()
        tab_name = tab_str+self.resources['shad_bala_str']
        self.tabWidget.setTabText(_shad_bala_tab_start,tab_name)
        column_names = utils.PLANET_NAMES[:7]
        row_names = ['sthaana_bala_str','kaala_bala_str','dig_bala_str','chesta_bala_str','naisargika_bala_str',
                     'drik_bala_str','shad_bala_str','shad_bala_rupas_str','shad_bala_strength_str']
        row_count = self._shad_bala_table[0].rowCount()
        col_count = self._shad_bala_table[0].columnCount()
        _sb_info = self._shad_bala_info
        for row in range(row_count):
            for col in range(col_count):
                cell_value = str(_sb_info[row][col])
                self._shad_bala_table[0].setItem(row,col,QTableWidgetItem(cell_value))
        for row in range(row_count):
            shad_str = self.resources[row_names[row]]
            self._shad_bala_table[0].setVerticalHeaderItem(row,QTableWidgetItem(shad_str))
            self._shad_bala_table[0].resizeRowToContents(row)
        for col in range(col_count):
            header = column_names[col]
            self._shad_bala_table[0].setHorizontalHeaderItem(col,QTableWidgetItem(header))
            self._shad_bala_table[0].resizeColumnToContents(col)
        self._shad_bala_table[0].horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._shad_bala_table[0].verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
    def _update_bhava_bala_table_information(self):
        tab_str,_chart_title_separator = self._get_tab_chart_prefix()
        tab_name = tab_str+self.resources['bhava_bala_str']
        self.tabWidget.setTabText(_bhava_bala_tab_start,tab_name)
        row_names = [self.resources['house_str']+'-'+str(h+1) for h in range(12)]
        column_names = ['bhava_bala_str','bhava_bala_rupas_str','bhava_bala_strength_str']
        row_count = self._bhava_bala_table[0].rowCount()
        col_count = self._bhava_bala_table[0].columnCount()
        _sb_info = self._bhava_bala_info
        for row in range(row_count):
            for col in range(col_count):
                cell_value = str(_sb_info[row][col])
                self._bhava_bala_table[0].setItem(row,col,QTableWidgetItem(cell_value))
        for row in range(row_count):
            bhava_str = row_names[row]
            self._bhava_bala_table[0].setVerticalHeaderItem(row,QTableWidgetItem(bhava_str))
            self._bhava_bala_table[0].resizeRowToContents(row)
        for col in range(col_count):
            header = self.resources[column_names[col]]
            self._bhava_bala_table[0].setHorizontalHeaderItem(col,QTableWidgetItem(header))
            self._bhava_bala_table[0].resizeColumnToContents(col)
        self._bhava_bala_table[0].horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._bhava_bala_table[0].verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
    def _update_argala_table_information(self,chart_index=None,chart_method=None,divisional_chart_factor=None,
                                    base_rasi=None,count_from_end_of_sign=None,
                                    chart_index_1=None,chart_method_1=None,chart_index_2=None,chart_method_2=None):
        planet_names = utils.PLANET_NAMES
        rasi_names_en = utils.RAASI_LIST
        if divisional_chart_factor==None:
            if chart_index < _custom_chart_index:
                dcf = const.division_chart_factors[chart_index]
            else:
                dcf = const.DEFAULT_CUSTOM_VARGA_FACTOR
        else:
            dcf = divisional_chart_factor
        tab_str,_chart_title_separator = self._get_tab_chart_prefix()
        tab_str += self.resources['argala_str']+'-'+self.resources['virodhargala_str']
        if chart_index == _custom_chart_index:
            tab_title_str = tab_str+'-'+'D'+str(dcf)
        elif chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[chart_index_1]; v2 = const.division_chart_factors[chart_index_2]
            mds = ' D'+str(v1)+'('+str(chart_method_1)+')xD'+ str(v2)+'('+str(chart_method_2)+')'+' '
            tab_title_str = tab_str + mds
        else:
            tab_title_str = self.resources[_chart_names[chart_index]]+'-'+tab_str
        self.tabWidget.setTabText(_argala_tab_start,tab_title_str)
        if chart_index==_mixed_chart_index:
            _,chart_1d,_ = self._horo.get_horoscope_information_for_mixed_chart(chart_index_1=chart_index_1,
                                chart_method_1=chart_method_1,chart_index_2=chart_index_2,chart_method_2=chart_method_2,
                                varnada_method=self._varnada_method_index)
        else:
            _,chart_1d,_ = self._horo.get_horoscope_information_for_chart(chart_index,chart_method,
                                                                          divisional_chart_factor=dcf,
                                               base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign,
                                               varnada_method=self._varnada_method_index)
        chart_1d_ind = self._convert_language_chart_to_indices(chart_1d)
        row_count_1 = self._argala_table1.rowCount()
        col_count = self._argala_table1.columnCount()
        argala,virodhargala = house.get_argala(chart_1d_ind)
        for row in range(row_count_1):
            for col in range(col_count):
                a_planets = argala[row][col].split('/')
                a_planets = '\n'.join(planet_names[int(p)] for p in a_planets if p.strip() !='' and p.strip() !=const._ascendant_symbol)
                self._argala_table1.setItem(row,col,QTableWidgetItem(a_planets))
                v_planets = virodhargala[row][col].split('/')
                v_planets = '\n'.join(planet_names[int(p)] for p in v_planets if p.strip() !='' and p.strip() !=const._ascendant_symbol)
                self._argala_table2.setItem(row,col,QTableWidgetItem(v_planets))
        for row in range(row_count_1):
            raasi = rasi_names_en[row]
            self._argala_table1.setVerticalHeaderItem(row,QTableWidgetItem(raasi))
            self._argala_table1.resizeRowToContents(row)
            self._argala_table2.setVerticalHeaderItem(row,QTableWidgetItem(raasi))
            self._argala_table2.resizeRowToContents(row)
        for col in range(col_count):
            header = const.argala_houses_str[col]
            self._argala_table1.setHorizontalHeaderItem(col,QTableWidgetItem(header))
            self._argala_table1.resizeColumnToContents(col)
            header = const.virodhargala_houses_str[col]
            self._argala_table2.setHorizontalHeaderItem(col,QTableWidgetItem(header))
            self._argala_table2.resizeColumnToContents(col)
        self._argala_table1.horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._argala_table2.horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._argala_table1.verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._argala_table2.verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
    def _update_drishti_table_information(self,chart_index=None,chart_method=None,divisional_chart_factor=None,
                                            base_rasi=None,count_from_end_of_sign=None,
                                        chart_index_1=None,chart_method_1=None,chart_index_2=None,chart_method_2=None):
        planet_names = utils.PLANET_NAMES
        rasi_names_en = utils.RAASI_LIST
        if divisional_chart_factor==None:
            if chart_index < _custom_chart_index:
                dcf = const.division_chart_factors[chart_index]
            else:
                dcf = const.DEFAULT_CUSTOM_VARGA_FACTOR
        else:
            dcf = divisional_chart_factor
        tab_str,_chart_title_separator = self._get_tab_chart_prefix()
        tab_str += self.resources['graha_str']+'-'+self.resources['drishti_str']
        if chart_index == _custom_chart_index:
            tab_title_str = tab_str+'-'+'D'+str(dcf)
        elif chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[chart_index_1]; v2 = const.division_chart_factors[chart_index_2]
            mds = ' D'+str(v1)+'('+str(chart_method_1)+')xD'+ str(v2)+'('+str(chart_method_2)+')'+' '
            tab_title_str = tab_str + mds
        else:
            tab_title_str = self.resources[_chart_names[chart_index]]+'-'+tab_str
        self.tabWidget.setTabText(_drishti_tab_start,tab_title_str)
        if chart_index==_mixed_chart_index:
            _,chart_1d,_ = self._horo.get_horoscope_information_for_mixed_chart(chart_index_1=chart_index_1,
                                chart_method_1=chart_method_1,chart_index_2=chart_index_2,chart_method_2=chart_method_2,
                                varnada_method=self._varnada_method_index)
        else:
            _,chart_1d,_ = self._horo.get_horoscope_information_for_chart(chart_index,chart_method,
                                                                          divisional_chart_factor=dcf,
                                               base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign,
                                               varnada_method=self._varnada_method_index)
        chart_1d_ind = self._convert_language_chart_to_indices(chart_1d)
        r_arp,r_ahp,r_app = house.raasi_drishti_from_chart(chart_1d_ind,'\n')
        g_arp,g_ahp,g_app = house.graha_drishti_from_chart(chart_1d_ind,'\n')
        row_count_1 = self._drishti_table1.rowCount()
        row_count_2 = self._drishti_table2.rowCount()
        col_count = self._drishti_table1.columnCount()
        join_str = '\n'
        for row in range(row_count_2):
            col1 = join_str.join([rasi_names_en[arp] for arp in r_arp[row]])
            self._drishti_table2.setItem(row,0,QTableWidgetItem(col1))
            col2 = join_str.join([const.houses_str[arp-1] for arp in r_ahp[row]])
            self._drishti_table2.setItem(row,1,QTableWidgetItem(col2))
            col3 = join_str.join([planet_names[int(pl)] for pl in r_app[row] if pl != '' and pl!=const._ascendant_symbol])
            self._drishti_table2.setItem(row,2,QTableWidgetItem(col3))
        for row in range(row_count_1):
            col1 = join_str.join([rasi_names_en[arp] for arp in g_arp[row]])
            self._drishti_table1.setItem(row,0,QTableWidgetItem(col1))
            col2 = join_str.join([const.houses_str[arp-1] for arp in g_ahp[row]])
            self._drishti_table1.setItem(row,1,QTableWidgetItem(col2))
            col3 = join_str.join([planet_names[int(pl)] for pl in g_app[row] if pl != '' and pl!=const._ascendant_symbol])
            self._drishti_table1.setItem(row,2,QTableWidgetItem(col3))
        for row in range(row_count_1):
            planet = planet_names[row]
            self._drishti_table1.setVerticalHeaderItem(row,QTableWidgetItem(planet))
            self._drishti_table1.resizeRowToContents(row)
        for row in range(row_count_2):
            planet = planet_names[row]
            self._drishti_table2.setVerticalHeaderItem(row,QTableWidgetItem(planet))
            self._drishti_table2.resizeRowToContents(row)
        headers = [self.resources['raasis_str'],self.resources['houses_str'],self.resources['planets_str']]
        for col in range(col_count):
            self._drishti_table1.setHorizontalHeaderItem(col,QTableWidgetItem(headers[col]))
            self._drishti_table2.setHorizontalHeaderItem(col,QTableWidgetItem(headers[col]))
            self._drishti_table1.resizeColumnToContents(col)
            self._drishti_table2.resizeColumnToContents(col)
        self._drishti_table1.horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._drishti_table2.horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._drishti_table1.verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._drishti_table2.verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
    def _get_drishti_table_widgets(self,chart_index=None,chart_method=None,divisional_chart_factor=None,
                                            base_rasi=None,count_from_end_of_sign=None,
                                        chart_index_1=None,chart_method_1=None,chart_index_2=None,chart_method_2=None):
        planet_names = utils.PLANET_NAMES
        rasi_names_en = utils.RAASI_LIST
        if divisional_chart_factor==None:
            if chart_index < _custom_chart_index:
                dcf = const.division_chart_factors[chart_index]
            else:
                dcf = const.DEFAULT_CUSTOM_VARGA_FACTOR
        else:
            dcf = divisional_chart_factor
        tab_str,_chart_title_separator = self._get_tab_chart_prefix()
        tab_str += self.resources['graha_str']+'-'+self.resources['drishti_str']
        if chart_index == _custom_chart_index:
            tab_title_str = tab_str+'-'+'D'+str(dcf)
        elif chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[chart_index_1]; v2 = const.division_chart_factors[chart_index_2]
            mds = ' D'+str(v1)+'('+str(chart_method_1)+')xD'+ str(v2)+'('+str(chart_method_2)+')'+' '
            tab_title_str = tab_str + mds
        else:
            tab_title_str = self.resources[_chart_names[chart_index]]+'-'+tab_str
        #self.tabWidget.setTabText(_drishti_tab_start,tab_title_str)
        if chart_index==_mixed_chart_index:
            _,chart_1d,_ = self._horo.get_horoscope_information_for_mixed_chart(chart_index_1=chart_index_1,
                                chart_method_1=chart_method_1,chart_index_2=chart_index_2,chart_method_2=chart_method_2,
                                varnada_method=self._varnada_method_index)
        else:
            _,chart_1d,_ = self._horo.get_horoscope_information_for_chart(chart_index,chart_method,
                                                                          divisional_chart_factor=dcf,
                                               base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign,
                                               varnada_method=self._varnada_method_index)
        chart_1d_ind = self._convert_language_chart_to_indices(chart_1d)
        r_arp,r_ahp,r_app = house.raasi_drishti_from_chart(chart_1d_ind,'\n')
        g_arp,g_ahp,g_app = house.graha_drishti_from_chart(chart_1d_ind,'\n')
        _drishti_table1 = QTableWidget(7, 3); _drishti_table2 = QTableWidget(9, 3)
        row_count_1 = _drishti_table1.rowCount()
        row_count_2 = _drishti_table2.rowCount()
        col_count = _drishti_table1.columnCount()
        join_str = '\n'
        for row in range(row_count_2):
            col1 = join_str.join([rasi_names_en[arp] for arp in r_arp[row]])
            _drishti_table2.setItem(row,0,QTableWidgetItem(col1))
            col2 = join_str.join([const.houses_str[arp-1] for arp in r_ahp[row]])
            _drishti_table2.setItem(row,1,QTableWidgetItem(col2))
            col3 = join_str.join([planet_names[int(pl)] for pl in r_app[row] if pl != '' and pl!=const._ascendant_symbol])
            _drishti_table2.setItem(row,2,QTableWidgetItem(col3))
        for row in range(row_count_1):
            col1 = join_str.join([rasi_names_en[arp] for arp in g_arp[row]])
            _drishti_table1.setItem(row,0,QTableWidgetItem(col1))
            col2 = join_str.join([const.houses_str[arp-1] for arp in g_ahp[row]])
            _drishti_table1.setItem(row,1,QTableWidgetItem(col2))
            col3 = join_str.join([planet_names[int(pl)] for pl in g_app[row] if pl != '' and pl!=const._ascendant_symbol])
            _drishti_table1.setItem(row,2,QTableWidgetItem(col3))
        for row in range(row_count_1):
            planet = planet_names[row]
            _drishti_table1.setVerticalHeaderItem(row,QTableWidgetItem(planet))
            _drishti_table1.resizeRowToContents(row)
        for row in range(row_count_2):
            planet = planet_names[row]
            _drishti_table2.setVerticalHeaderItem(row,QTableWidgetItem(planet))
            _drishti_table2.resizeRowToContents(row)
        headers = [self.resources['raasis_str'],self.resources['houses_str'],self.resources['planets_str']]
        for col in range(col_count):
            _drishti_table1.setHorizontalHeaderItem(col,QTableWidgetItem(headers[col]))
            _drishti_table2.setHorizontalHeaderItem(col,QTableWidgetItem(headers[col]))
            _drishti_table1.resizeColumnToContents(col)
            _drishti_table2.resizeColumnToContents(col)
        _drishti_table1.horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        _drishti_table2.horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        _drishti_table1.verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        _drishti_table2.verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        _drishti_table1.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        _drishti_table2.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        return tab_title_str,[_drishti_table1,_drishti_table2]
    def _update_saham_table_information(self,chart_index=None,chart_method=None,divisional_chart_factor=None,
                                            base_rasi=None,count_from_end_of_sign=None,
                                        chart_index_1=None,chart_method_1=None,chart_index_2=None,chart_method_2=None):
        planet_names = utils.PLANET_NAMES
        rasi_names_en = utils.RAASI_LIST
        if divisional_chart_factor==None:
            if chart_index < _custom_chart_index:
                dcf = const.division_chart_factors[chart_index]
            else:
                dcf = const.DEFAULT_CUSTOM_VARGA_FACTOR
        else:
            dcf = divisional_chart_factor
        tab_str,_chart_title_separator = self._get_tab_chart_prefix()
        tab_str += self.resources['saham_str']
        if chart_index == _custom_chart_index:
            tab_title_str = tab_str+'-'+'D'+str(dcf)
        elif chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[chart_index_1]; v2 = const.division_chart_factors[chart_index_2]
            mds = ' D'+str(v1)+'('+str(chart_method_1)+')xD'+ str(v2)+'('+str(chart_method_2)+')'+' '
            tab_title_str = tab_str + mds
        else:
            tab_title_str = self.resources[_chart_names[chart_index]]+'-'+tab_str
        self.tabWidget.setTabText(_saham_tab_start,tab_title_str)
        dob = self._horo.Date; tob = self._horo.birth_time; place = self._horo.Place
        jd_at_dob = utils.julian_day_number(dob,tob)
        if chart_index == _mixed_chart_index:
            planet_positions = charts.mixed_chart(jd_at_dob, place, varga_factor_1=v1, chart_method_1=chart_method_1,
                                                  varga_factor_2=v2, chart_method_2=chart_method_2)
        else:    
            planet_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=dcf,
                                                       chart_method=chart_method,
                                            base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
        _,_saham_info = self._horo.get_sahams(planet_positions)
        _saham_info1 = dict(list(_saham_info.items())[:18]);_saham_info2 = dict(list(_saham_info.items())[18:])
        row_count_1 = self._saham_table1.rowCount()
        row_count_2 = self._saham_table2.rowCount()
        col_count = self._saham_table1.columnCount()
        headers = [self.resources['saham_str'],self.resources['raasi_str']+' '+self.resources['longitude_str']]
        for col in range(col_count):
            self._saham_table1.setHorizontalHeaderItem(col,QTableWidgetItem(headers[col]))
            self._saham_table2.setHorizontalHeaderItem(col,QTableWidgetItem(headers[col]))
            self._saham_table1.resizeColumnToContents(col)
            self._saham_table2.resizeColumnToContents(col)
        for row, (s1,s2) in enumerate(_saham_info1.items()):
            self._saham_table1.setItem(row,0,QTableWidgetItem(s1))
            self._saham_table1.setItem(row,1,QTableWidgetItem(s2))
            self._saham_table1.resizeRowToContents(row)
            self._saham_table1.resizeColumnToContents(0);self._saham_table1.resizeColumnToContents(1)
        for row, (s1,s2) in enumerate(_saham_info2.items()):
            self._saham_table2.setItem(row,0,QTableWidgetItem(s1))
            self._saham_table2.setItem(row,1,QTableWidgetItem(s2))
            self._saham_table2.resizeRowToContents(row)        
            self._saham_table2.resizeColumnToContents(0);self._saham_table2.resizeColumnToContents(1)
        self._saham_table1.horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._saham_table2.horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._saham_table1.verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._saham_table2.verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._saham_table1.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._saham_table2.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    def _get_saham_table_widgets(self,chart_index=None,chart_method=None,divisional_chart_factor=None,
                                            base_rasi=None,count_from_end_of_sign=None,
                                        chart_index_1=None,chart_method_1=None,chart_index_2=None,chart_method_2=None):
        if divisional_chart_factor==None:
            if chart_index < _custom_chart_index:
                dcf = const.division_chart_factors[chart_index]
            else:
                dcf = const.DEFAULT_CUSTOM_VARGA_FACTOR
        else:
            dcf = divisional_chart_factor
        tab_str,_chart_title_separator = self._get_tab_chart_prefix()
        tab_str += self.resources['saham_str']
        if chart_index == _custom_chart_index:
            tab_title_str = tab_str+'-'+'D'+str(dcf)
        elif chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[chart_index_1]; v2 = const.division_chart_factors[chart_index_2]
            mds = ' D'+str(v1)+'('+str(chart_method_1)+')xD'+ str(v2)+'('+str(chart_method_2)+')'+' '
            tab_title_str = tab_str + mds
        else:
            tab_title_str = self.resources[_chart_names[chart_index]]+'-'+tab_str
        #self.tabWidget.setTabText(_saham_tab_start,tab_title_str)
        dob = self._horo.Date; tob = self._horo.birth_time; place = self._horo.Place
        jd_at_dob = utils.julian_day_number(dob,tob)
        if chart_index == _mixed_chart_index:
            planet_positions = charts.mixed_chart(jd_at_dob, place, varga_factor_1=v1, chart_method_1=chart_method_1,
                                                  varga_factor_2=v2, chart_method_2=chart_method_2)
        else:    
            planet_positions = charts.divisional_chart(jd_at_dob, place, divisional_chart_factor=dcf,
                                                       chart_method=chart_method,
                                            base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign)
        _,_saham_info = self._horo.get_sahams(planet_positions)
        _saham_info1 = dict(list(_saham_info.items())[:18]);_saham_info2 = dict(list(_saham_info.items())[18:])
        _saham_table1 = QTableWidget(18, 2);_saham_table2 = QTableWidget(18, 2)
        row_count_1 = _saham_table1.rowCount()
        row_count_2 = _saham_table2.rowCount()
        col_count = _saham_table1.columnCount()
        headers = [self.resources['saham_str'],self.resources['raasi_str']+' '+self.resources['longitude_str']]
        for col in range(col_count):
            _saham_table1.setHorizontalHeaderItem(col,QTableWidgetItem(headers[col]))
            _saham_table2.setHorizontalHeaderItem(col,QTableWidgetItem(headers[col]))
            _saham_table1.resizeColumnToContents(col)
            _saham_table2.resizeColumnToContents(col)
        for row, (s1,s2) in enumerate(_saham_info1.items()):
            _saham_table1.setItem(row,0,QTableWidgetItem(s1))
            _saham_table1.setItem(row,1,QTableWidgetItem(s2))
            _saham_table1.resizeRowToContents(row)
        for row, (s1,s2) in enumerate(_saham_info2.items()):
            _saham_table2.setItem(row,0,QTableWidgetItem(s1))
            _saham_table2.setItem(row,1,QTableWidgetItem(s2))
            _saham_table2.resizeRowToContents(row)
        _saham_table1.horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        _saham_table2.horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        _saham_table1.verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        _saham_table2.verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        return [_saham_table1,_saham_table2]
    def _update_shodhaya_table_information(self,chart_index=None, chart_method=None,divisional_chart_factor=None,
                            base_rasi=None,count_from_end_of_sign=None,
                            chart_index_1=None,chart_method_1=None,chart_index_2=None,chart_method_2=None):
        """ Following List should match _shodhaya_tab_count """
        label_title = self.resources['ashtaka_varga_str']+' ('+self.resources['trikona_str']+'-'+self.resources['ekadhipathya_str']+' )'
        self._shodhaya_table_label1.setText(label_title)
        self._shodhaya_table_label1.setStyleSheet("font-weight: bold")
        label_title = self.resources['shodhaya_pinda_str']
        self._shodhaya_table_label2.setText(label_title)
        self._shodhaya_table_label2.setStyleSheet("font-weight: bold")
        if divisional_chart_factor==None:
            if chart_index < _custom_chart_index:
                dcf = const.division_chart_factors[chart_index]
            else:
                dcf = const.DEFAULT_CUSTOM_VARGA_FACTOR
        else:
            dcf = divisional_chart_factor
        tab_str = self.resources['shodhaya_pinda_str']
        if chart_index == _custom_chart_index:
            tab_title_str = tab_str+'-'+'D-'+str(dcf)
        elif chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[chart_index_1]; v2 = const.division_chart_factors[chart_index_2]
            mds = ' D'+str(v1)+'('+str(chart_method_1)+')xD'+ str(v2)+'('+str(chart_method_2)+')'+' '
            tab_title_str = tab_str + mds
        else:
            tab_title_str = self.resources[_chart_names[chart_index]]+'-'+tab_str
        self.tabWidget.setTabText(_shodhaya_tab_start,tab_title_str)
        if chart_index==_mixed_chart_index:
            _,chart_1d,_ = self._horo.get_horoscope_information_for_mixed_chart(chart_index_1=chart_index_1,
                                chart_method_1=chart_method_1,chart_index_2=chart_index_2,chart_method_2=chart_method_2,
                                varnada_method=self._varnada_method_index)
        else:
            _,chart_1d,_ = self._horo.get_horoscope_information_for_chart(chart_index,chart_method,
                                                                          divisional_chart_factor=dcf,
                                               base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign,
                                varnada_method=self._varnada_method_index)
        #chart_1d = self._horoscope_charts[chart_counters[t]] #charts[t]
        chart_1d = self._convert_language_chart_to_indices(chart_1d)
        bav,_,_ = ashtakavarga.get_ashtaka_varga(chart_1d)#_en)
        tri = ashtakavarga._trikona_sodhana(bav)
        eka = ashtakavarga._ekadhipatya_sodhana(tri,chart_1d)#_en)
        sav = np.asarray(eka).sum(axis=0).tolist()
        raasi_pindas,graha_pindas,shodya_pindas = ashtakavarga._sodhya_pindas(eka,chart_1d)#_en)
        row_count = self._shodhaya_table1.rowCount()
        col_count = self._shodhaya_table1.columnCount()
        for r in range(col_count):
            for p in range(row_count-1):
                self._shodhaya_table1.setItem(p,r,QTableWidgetItem(str(eka[p][r])))
            self._shodhaya_table1.setItem(row_count-1,r,QTableWidgetItem(str(sav[r])))
        for p in range(row_count):
            if p==row_count-1:
                header = "SAV"
            elif p==row_count-2:
                header = self.resources['ascendant_str']
            else:
                header = utils.PLANET_NAMES[p]#self._horo._get_planet_list()[0][p]
            self._shodhaya_table1.setVerticalHeaderItem(p,QTableWidgetItem(header))
            self._shodhaya_table1.resizeRowToContents(p)
        for r in range(col_count):
            header = utils.RAASI_LIST[r]#self._horo._get_raasi_list()[0][r]
            self._shodhaya_table1.setHorizontalHeaderItem(r,QTableWidgetItem(header))
            self._shodhaya_table1.resizeColumnToContents(r)                
        self._shodhaya_table1.horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._shodhaya_table1.verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._shodhaya_table1.update()
        row_count = self._shodhaya_table2.rowCount()
        col_count = self._shodhaya_table2.columnCount()
        row_names = [self.resources['graha_pinda_str'],self.resources['raasi_pinda_str'],self.resources['shodhaya_pinda_str']]
        for p in range(col_count):
            self._shodhaya_table2.setItem(0,p,QTableWidgetItem(str(raasi_pindas[p])))
            self._shodhaya_table2.setItem(1,p,QTableWidgetItem(str(graha_pindas[p])))
            self._shodhaya_table2.setItem(2,p,QTableWidgetItem(str(shodya_pindas[p])))
        for row in range(row_count):
            self._shodhaya_table2.setVerticalHeaderItem(row,QTableWidgetItem(row_names[row]))
            self._shodhaya_table2.resizeRowToContents(row)
        for p in range(col_count):
            self._shodhaya_table2.setHorizontalHeaderItem(p,QTableWidgetItem(self._horo._get_planet_list()[0][p]))
            self._shodhaya_table2.resizeColumnToContents(p)
        self._shodhaya_table2.horizontalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._shodhaya_table2.verticalHeader().setStyleSheet("QHeaderView { font-weight: bold }")
        self._shodhaya_table2.update()
    def _update_ashtaka_varga_tab_information(self,chart_index=None,chart_method=None,divisional_chart_factor=None,
                                base_rasi=None,count_from_end_of_sign=None,
                                chart_index_1=None,chart_method_1=None,chart_index_2=None,chart_method_2=None):
        #print('_update_ashtaka_varga_tab_information',chart_index)
        """ TODO: Should this be julian day, julian_years or birth-julian-day? """
        #jd = self._horo.julian_day  # For ascendant and planetary positions, dasa bukthi - use birth time
        jd = self._birth_julian_day
        place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        tab_names = [self.resources[tab] for tab in _chart_names]#self.tabNames[_tabcount_before_chart_tab:_chart_tab_end]]#_vimsottari_dhasa_tab_start]]
        if divisional_chart_factor==None:
            if chart_index < _custom_chart_index:
                dcf = const.division_chart_factors[chart_index]
            else:
                dcf = const.DEFAULT_CUSTOM_VARGA_FACTOR
        else:
            dcf = divisional_chart_factor
        tab_str=self.resources['ashtaka_varga_str']
        if chart_index == _custom_chart_index:
            tab_title_str = tab_str+'-'+'D'+str(dcf)
        elif chart_index == _mixed_chart_index:
            v1 = const.division_chart_factors[chart_index_1]; v2 = const.division_chart_factors[chart_index_2]
            mds = ' D'+str(v1)+'('+str(chart_method_1)+')xD'+ str(v2)+'('+str(chart_method_2)+')'+' '
            tab_title_str = tab_str + mds
        else:
            tab_title_str = self.resources[_chart_names[chart_index]]+'-'+tab_str
        self.tabWidget.setTabText(_ashtaka_varga_tab_start,tab_title_str)
        if chart_index==_mixed_chart_index:
            _,self._ashtaka_chart,self._ashtaka_ascendant_house = \
                self._horo.get_horoscope_information_for_mixed_chart(chart_index_1=chart_index_1,
                                chart_method_1=chart_method_1,chart_index_2=chart_index_2,chart_method_2=chart_method_2,
                                varnada_method=self._varnada_method_index)
        else:
            _,self._ashtaka_chart,self._ashtaka_ascendant_house = \
                self._horo.get_horoscope_information_for_chart(chart_index,chart_method,
                                                               divisional_chart_factor=dcf,
                                               base_rasi=base_rasi,count_from_end_of_sign=count_from_end_of_sign,
                                varnada_method=self._varnada_method_index)
        chart_1d = self._ashtaka_chart#self._horoscope_charts[t] #charts[t]
        chart_1d = self._convert_language_chart_to_indices(chart_1d)
        bav,sav, _ = ashtakavarga.get_ashtaka_varga(chart_1d)#_en)
        ac = 0
        for _ in range(3):
            for _ in range(3):
                if ac ==0:
                    chart_data_1d = sav
                    chart_title = 'SAV'
                else:
                    chart_data_1d = bav[ac-1]
                    # Last value is Lagnam not Raghu
                    chart_title = self.resources['ascendant_str'] if ac==8 else self._horo._get_planet_list()[0][ac-1]
                if 'north' in self._chart_type.lower() or 'sudar' in self._chart_type.lower():
                    #_ascendant = drik.ascendant(jd,place)
                    asc_house = self._ashtaka_ascendant_house+1 # _ascendant[0]+1
                    chart_data_north = chart_data_1d[asc_house-1:]+chart_data_1d[0:asc_house-1]
                    self._ashtaka_charts[ac].setData(chart_data_north,chart_title=chart_title,chart_title_font_size=ashtaka_chart_title_font_size)
                elif 'east' in self._chart_type.lower():
                    chart_data_2d = utils._convert_1d_house_data_to_2d(chart_data_1d,self._chart_type)
                    row,col = const._asc_house_row_col__chart_map[self._ashtaka_ascendant_house]
                    self._ashtaka_charts[ac]._asc_house = row*self._ashtaka_charts[ac].row_count+col
                    self._ashtaka_charts[ac].setData(chart_data_2d,chart_title=chart_title,chart_title_font_size=ashtaka_chart_title_font_size)
                else: # south indian
                    chart_data_2d = utils._convert_1d_house_data_to_2d(chart_data_1d)
                    row,col = const._asc_house_row_col__chart_map[self._ashtaka_ascendant_house]
                    self._ashtaka_charts[ac]._asc_house = (row,col)
                    self._ashtaka_charts[ac].setData(chart_data_2d,chart_title=chart_title,chart_title_font_size=ashtaka_chart_title_font_size)
                self._ashtaka_charts[ac].parent().layout().setSpacing(0)
                self._ashtaka_charts[ac].update()
                ac += 1        
    def _update_prediction_table(self):
        cur_row = self._prediction_list.currentRow()
        if cur_row == -1:
            cur_row = 0
            self._prediction_list.setCurrentRow(cur_row)
        cur_item = self._prediction_list.currentItem()
        if cur_item:
            if 'matching' in cur_item.text():
                return
        """ Show the selected dosha information in the dosha edit box """
        sy = cur_item.text()
        sy = sy.split('\n')
        sy_len = len(sy)
        prediction_results_text = ''
        list_count = _predictions_per_list_item
        list_len = self._prediction_count-1
        if cur_row < self._prediction_count:
            list_count = _predictions_per_list_item
            list_len = 0
        prediction_keys = list(self._prediction_results.keys())
        for k in range(list_count):
            if sy_len > k:
                yk = prediction_keys[(cur_row-list_len) * list_count + k] 
                #prediction_results_text += "<b><u>"+yk+"</u></b><br>"
                prediction_results_text += self._prediction_results[yk]+"<br>"
        prediction_results_text = prediction_results_text[:-len("<br>")]
        self._prediction_text.setHtml(prediction_results_text)
        self._prediction_text.setReadOnly(True) #setDisabled(True)
        
    def _update_prediction_tab_information(self):
        self.tabWidget.setTabText(_prediction_tab_start,self.resources['general_prediction_str'])
        """ TODO: Should this be julian day, julian_years or birth-julian-day? """
        #jd = self._horo.julian_day  # For ascendant and planetary positions, dasa bukthi - use birth time
        jd = self._birth_julian_day
        place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        self._prediction_results = general.get_prediction_details(jd,place,language=available_languages[self._language])
        self._prediction_list.clear()
        self._prediction_count = len(self._prediction_results)
        for k in range(0,self._prediction_count,_predictions_per_list_item):
            key = ''
            for kk in range(_predictions_per_list_item):
                if k+kk<=self._prediction_count-kk:
                    key = key+'\n'+''.join(list(self._prediction_results.keys())[k+kk])
            key = key[1:]
            self._prediction_list.addItem(QListWidgetItem(key))
        self._prediction_list.setCurrentRow(0)
        return 
    def _update_dosha_table(self):
        cur_row = self._dosha_list.currentRow()
        if cur_row == -1:
            cur_row = 0
            self._dosha_list.setCurrentRow(cur_row)
        cur_item = self._dosha_list.currentItem()
        if cur_item:
            if 'matching' in cur_item.text():
                return
        """ Show the selected dosha information in the dosha edit box """
        sy = cur_item.text()
        sy = sy.split('\n')
        sy_len = len(sy)
        dosha_results_text = ''
        list_count = _doshas_per_list_item
        list_len = self._dosha_count-1
        if cur_row < self._dosha_count:
            list_count = _doshas_per_list_item
            list_len = 0
        dosha_keys = list(self._dosha_results.keys())
        for k in range(list_count):
            if sy_len > k:
                yk = dosha_keys[(cur_row-list_len) * list_count + k] 
                dosha_results_text += "<b><u>"+yk+"</u></b><br>"
                dosha_results_text += self._dosha_results[yk]+"<br>"
        dosha_results_text = dosha_results_text[:-len("<br>")]
        self._dosha_text.setHtml(dosha_results_text)
        self._dosha_text.setReadOnly(True) #setDisabled(True)
        
    def _update_dosha_tab_information(self):
        self.tabWidget.setTabText(_dosha_tab_start,self.resources['dosha_str'])
        """ TODO: Should this be julian day, julian_years or birth-julian-day? """
        #jd = self._horo.julian_day  # For ascendant and planetary positions, dasa bukthi - use birth time
        jd = self._birth_julian_day
        place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        self._dosha_results = dosha.get_dosha_details(jd,place,language=available_languages[self._language])
        self._dosha_list.clear()
        self._dosha_count = len(self._dosha_results)
        for k in range(0,self._dosha_count,_doshas_per_list_item):
            key = ''
            for kk in range(_doshas_per_list_item):
                if k+kk<=self._dosha_count-kk:
                    key = key+'\n'+''.join(list(self._dosha_results.keys())[k+kk])
            key = key[1:]
            self._dosha_list.addItem(QListWidgetItem(key))
        self._dosha_list.setCurrentRow(0)
        return 
    def _update_yoga_table(self):
        cur_row = self._yoga_list.currentRow()
        if cur_row == -1:
            cur_row = 0
            self._yoga_list.setCurrentRow(cur_row)
        cur_item = self._yoga_list.currentItem()
        if cur_item:
            if 'matching' in cur_item.text():
                return
        """ Show the selected yoga information in the yoga edit box """
        sy = cur_item.text()
        sy = sy.split('\n')
        sy_len = len(sy)
        yoga_results_text = ''
        list_count = _yogas_per_list_item
        list_len = self._raja_yoga_count-1 if self._raja_yoga_count>0 else 0
        if self._raja_yoga_count>0 and cur_row < self._raja_yoga_count:
            list_count = _raja_yogas_per_list_item
            list_len = 0
        yoga_keys = list(self._yoga_results.keys())
        for k in range(list_count):
            if sy_len > k:
                yki = (cur_row-list_len) * list_count + k
                yk = yoga_keys[yki] 
                yoga_chart,yoga_name, yoga_description, yoga_predictions = self._yoga_results[yk]
                yoga_results_text += "<b><u>"+yoga_name+" ("+yoga_chart+")</u></b><br>"
                yoga_results_text += "<b>"+self.resources['description_str']+"</b> "+yoga_description+"<br>"
                yoga_results_text += "<b>"+self.resources['prediction_str']+"</b> " +yoga_predictions+"<br><br>"
        yoga_results_text = yoga_results_text[:-len("<br>")]
        self._yoga_text.setHtml(yoga_results_text)
        self._yoga_text.setReadOnly(True) #setDisabled(True)
        
    def _update_yoga_tab_information(self):
        self.tabWidget.setTabText(_yoga_tab_start,self.resources['yoga_str'])
        """ TODO: Should this be julian day, julian_years or birth-julian-day? """
        #jd = self._horo.julian_day  # For ascendant and planetary positions, dasa bukthi - use birth time
        jd = self._birth_julian_day
        place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        self._raja_yoga_results,_,_ = raja_yoga.get_raja_yoga_details_for_all_charts(jd,place,
                                    language=available_languages[self._language],divisional_chart_factor=_yoga_chart_option)
        self._yoga_results,_,_ = yoga.get_yoga_details_for_all_charts(jd,place,
                                    language=available_languages[self._language],divisional_chart_factor=_yoga_chart_option)
        self._yoga_list.clear()
        self._raja_yoga_count = len(self._raja_yoga_results)#; print('found raja yogas',self._raja_yoga_count)
        if self._raja_yoga_count>0:#self._raja_yoga_results:
            yoga_count = len(self._raja_yoga_results)
            for k in range(0,yoga_count,_raja_yogas_per_list_item):
                key = ''
                for kk in range(_raja_yogas_per_list_item):
                    if k+kk<=yoga_count-kk:
                        key = key+'\n'+''.join(list(self._raja_yoga_results.values())[k+kk][1].split()[0:-1])
                key = key[1:]
                self._yoga_list.addItem(QListWidgetItem(key))
            #self._yoga_list.setCurrentRow(0)
        yoga_count = len(self._yoga_results)#; print('found yogas',yoga_count)
        for k in range(0,yoga_count,_yogas_per_list_item):
            key = ''
            for kk in range(_yogas_per_list_item):
                if k+kk<=yoga_count-kk:
                    key = key+'\n'+''.join(list(self._yoga_results.values())[k+kk][1].split()[0:-1])
            key = key[1:]
            self._yoga_list.addItem(QListWidgetItem(key))
        if self._raja_yoga_count>0: self._yoga_results = {**self._raja_yoga_results, **self._yoga_results}
        self._yoga_list.setCurrentRow(0)
        return 
    def _update_compatibility_tab_information(self):
        self.tabWidget.setTabText(_compatibility_tab_start,self.resources['compatibility_str'])
        bn=None
        bp=None
        gn=None
        gp=None
        self._mahendra_porutham = self._mahendra_porutham_checkbox.isChecked()
        self._vedha_porutham = self._vedha_porutham_checkbox.isChecked()
        self._rajju_porutham = self._rajju_porutham_checkbox.isChecked()
        self._sthree_dheerga_porutham = self._sthree_dheerga_porutham_checkbox.isChecked()
        if 'south' in self._chart_type.lower():
            self._min_score_combo.setRange(0.0,const.compatibility_maximum_score_south)
            self._min_score_combo.setSingleStep(1.0)
            self._min_score_combo.setValue(const.compatibility_minimum_score_south)
        else:
            """ NOTE: setValue works only when used after setting range """ 
            self._min_score_combo.setRange(0.0,const.compatibility_maximum_score_north)
            self._min_score_combo.setSingleStep(0.5)
            self._min_score_combo.setValue(const.compatibility_minimum_score_north)
        self._minimum_score = float(self._min_score_combo.text())
        nak = drik.nakshatra(self._birth_julian_day, self._horo.Place)
        _nakshatra_number = nak[0]; _paadha_number = nak[1]
        if self._gender_combo.currentIndex()==0: # self._gender.lower() == 'male':
            bn = _nakshatra_number # self._horo._nakshatra_number
            bp = _paadha_number# self._horo._paadha_number
        else:
            gn = _nakshatra_number # self._horo._nakshatra_number
            gp = _paadha_number # self._horo._paadha_number
        comp = compatibility.Match(boy_nakshatra_number=bn,boy_paadham_number=bp,girl_nakshatra_number=gn,girl_paadham_number=gp,\
                   check_for_mahendra_porutham=self._mahendra_porutham,check_for_vedha_porutham=self._vedha_porutham,\
                   check_for_rajju_porutham=self._rajju_porutham,check_for_shreedheerga_porutham=self._sthree_dheerga_porutham,\
                   minimum_score=self._minimum_score,method=self._chart_type)
        self._matching_stars_tuple = utils.sort_tuple(comp.get_matching_partners(),3,reverse=True)
        matching_stars_count = len(self._matching_stars_tuple)
        if not self._matching_stars_tuple:
            self._matching_star_list.clear()
            self._matching_star_list.addItems(['No matching found'])
        else:
            self._matching_star_list.clear()
            matching_stars = []
            for k in range(0,matching_stars_count,_comp_results_per_list_item):
                key = ''
                for kk in range(_comp_results_per_list_item):
                    if k+kk<=matching_stars_count-kk:
                        m_s_tup = self._matching_stars_tuple[k+kk]
                        nakshatra = utils.NAKSHATRA_LIST[m_s_tup[0]-1]
                        paadham = str(m_s_tup[1])
                        key += '\n'+nakshatra+'-'+paadham
                key = key[1:]
                matching_stars.append(key)
            self._matching_star_list.addItems(matching_stars)
            self._matching_star_list.setCurrentRow(0)
    def _update_compatibility_table(self):
        cur_item = self._matching_star_list.currentItem()
        if cur_item:
            if 'matching' in cur_item.text():
                return
        """ Show the selected item in the results table """
        sy = cur_item.text()
        sy = sy.split('\n')
        sy_len = len(sy)
        selected_list_index = self._matching_star_list.currentRow()
        for k in range(_comp_results_per_list_item):
            if sy_len > k:
                self._comp_results_table[k].setVisible(True)
                results_table = self._comp_results_table[k]
                sel_index = selected_list_index*_comp_results_per_list_item+k
                self._update_compatibility_table_tmp(results_table,sel_index)
            else:
                self._comp_results_table[k].setVisible(False)
    def _update_compatibility_table_tmp(self,results_table,selected_list_index):
        selected_matching_star_tuple = self._matching_stars_tuple[selected_list_index]
        ettu_poruthham_list = [self.resources[p] for p in compatibility.compatibility_list_north]
        if 'south' in self._chart_type.lower():
            ettu_poruthham_list = [self.resources[p] for p in compatibility.compatibility_list_south]            
        ettu_porutham_max_score = [compatibility.varna_max_score,compatibility.vasiya_max_score,compatibility.gana_max_score,\
                                    compatibility.nakshathra_max_score,compatibility.yoni_max_score,compatibility.raasi_adhipathi_max_score, \
                                    compatibility.raasi_max_score, compatibility.naadi_max_score]
        naalu_porutham_list = [self.resources[p] for p in compatibility.naalu_porutham_list]
        ettu_porutham_results = selected_matching_star_tuple[2]
        compatibility_score = selected_matching_star_tuple[3]
        naalu_porutham_results = selected_matching_star_tuple[4]
        minimum_tamil_porutham = naalu_porutham_results[-1]
        if 'south' in self._chart_type.lower():
            ettu_porutham_results = ettu_porutham_results[1:-1]
            #minimum_tamil_porutham = all([ettu_porutham_results[t] for t in const.mandatory_compatibility_south_list]) and naalu_porutham_results[2]          
        nakshatra = utils.NAKSHATRA_LIST[selected_matching_star_tuple[0]-1]
        paadham = self.resources['paadham_str']+' '+str(selected_matching_star_tuple[1])
        results_table.setHorizontalHeaderItem(0,QTableWidgetItem(nakshatra+'-'+paadham))
        results_table.setHorizontalHeaderItem(1,QTableWidgetItem(''))
        results_table.setHorizontalHeaderItem(2,QTableWidgetItem(''))
        results_table.setHorizontalHeaderItem(3,QTableWidgetItem(''))
        row = 0
        for p,porutham in enumerate(ettu_poruthham_list):
            if 'south' in self._chart_type.lower():
                results_table.setItem(row,0,QTableWidgetItem(porutham))
                results_table.setItem(row,1,QTableWidgetItem(str(ettu_porutham_results[p])))
                results_table.setItem(row,2,QTableWidgetItem('True'))
                if ettu_porutham_results[p]:
                    results_table.setItem(row,3,QTableWidgetItem(str(const._GREEN_CHECK)))
                else:
                    results_table.setItem(row,3,QTableWidgetItem(str(const._RED_CROSS)))                
            else:
                results_table.setItem(row,0,QTableWidgetItem(porutham))
                results_table.setItem(row,1,QTableWidgetItem(str(ettu_porutham_results[p])))
                results_table.setItem(row,2,QTableWidgetItem(str(ettu_porutham_max_score[p])))
                perc = '{:3.0f}%'.format(ettu_porutham_results[p]/ettu_porutham_max_score[p]*100)
                results_table.setItem(row,3,QTableWidgetItem(str(perc)))
            row += 1
        for p,porutham in enumerate(naalu_porutham_list):
            results_table.setItem(row,0,QTableWidgetItem(porutham))
            results_table.setItem(row,1,QTableWidgetItem(str(naalu_porutham_results[p])))
            results_table.setItem(row,2,QTableWidgetItem('True'))
            if naalu_porutham_results[p]:
                results_table.setItem(row,3,QTableWidgetItem(str(const._GREEN_CHECK)))
            else:
                results_table.setItem(row,3,QTableWidgetItem(str(const._RED_CROSS)))
            row += 1
        results_table.setItem(row,0,QTableWidgetItem(self.resources['overall_match_str']))
        results_table.setItem(row,1,QTableWidgetItem(str(compatibility_score)))
        if 'south' in self._chart_type.lower():
            results_table.setItem(row,2,QTableWidgetItem(str(compatibility.max_compatibility_score_south)))
            if minimum_tamil_porutham:
                results_table.setItem(row,3,QTableWidgetItem(str(const._GREEN_CHECK)))
            else:
                results_table.setItem(row,3,QTableWidgetItem(str(const._RED_CROSS)))
        else:
            results_table.setItem(row,2,QTableWidgetItem(str(compatibility.max_compatibility_score)))
            perc = '{:3.0f}%'.format(compatibility_score/compatibility.max_compatibility_score*100)
            results_table.setItem(row,3,QTableWidgetItem(str(perc)))
        results_table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        results_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        for c in range(4):
            results_table.resizeColumnToContents(c)
        for r in range(14):
            results_table.resizeRowToContents(r)
    def _update_chart_ui_with_info(self):
        self._update_bhava_chart_information()
        self._update_pps_tab_information()
        # Update Panchanga and Bhava tab names here
        for t in range(_tabcount_before_chart_tab):
            self.tabWidget.setTabText(t,self.resources[_tab_names[t]])
        self._current_kundali_chart_index = self._kundali_chart_combo.currentIndex()
        self._update_tab_chart_information(chart_index=self._current_kundali_chart_index,chart_method=self._kundali_method_index)
        _chart_tab_name = self._kundali_chart_combo.currentText()
        #self.tabWidget.setTabText(_tabcount_before_chart_tab,_chart_tab_name)
        if not self._western_chart:
            self._update_kpinfo_information(chart_index=self._current_kpinfo_chart_index,chart_method=self._kpinfo_method_index)
            self._update_chakra_tab_information(chart_index=self._current_chakra_chart_index,chart_method=self._chakra_method_index)
            self._update_amsa_ruler_tab_information(self._current_amsa_chart_index,self._amsa_method_index)
            self._update_sphuta_tab_information(chart_index=self._current_sphuta_chart_index,method_index=self._sphuta_method_index)
            self._update_saham_table_information(self._current_saham_chart_index,self._saham_method_index)
            self._update_drishti_table_information(self._current_drishti_chart_index,self._drishti_method_index)
            self._update_graha_arudha_tab_information(self._current_arudha_chart_index,self._arudha_method_index)
            self._update_vimsopaka_bala_tab_information()
            self._update_vaiseshikamsa_bala_tab_information()
            self._update_other_bala_tab_information()
            self._update_shad_bala_table_information()
            self._update_bhava_bala_table_information()
            self._update_dhasa_bhukthi_tab_information()
            self._current_ashtaka_chart_index = self._ashtaka_chart_combo.currentIndex()
            self._update_ashtaka_varga_tab_information(self._current_ashtaka_chart_index,self._ashtaka_method_index)
            self._update_argala_table_information(self._current_argala_chart_index,self._argala_method_index)
            self._update_shodhaya_table_information(self._current_shodhaya_chart_index,self._shodhaya_method_index)
            self._update_yoga_tab_information()
            self._update_dosha_tab_information()
            self._show_compatibility = self._gender_combo.currentIndex() in [0,1]
            if  self._show_compatibility:
                self._update_compatibility_tab_information()
            self._update_prediction_tab_information()
        self.update()
    def _reset_place_text_size(self):
        pt = 'Chennai'#self._place_text.text().split(',')[0]
        f = QFont("",0)
        fm = QFontMetrics(f)
        pw = fm.boundingRect(pt).width()
        ph = fm.height()
        self._place_text.setFixedSize(pw,ph)
        self._place_text.adjustSize()
        self._place_text.selectionStart()
        self._place_text.setCursorPosition(0)
    def _resize_place_text_size(self):
        pt = self._place_text.text()
        f = QFont("",0)
        fm = QFontMetrics(f)
        pw = fm.boundingRect(pt).width()
        ph = fm.height()
        self._place_text.setFixedSize(pw,ph)
        self._place_text.adjustSize()       
    def _get_location(self,place_name):
        result = utils.get_location(place_name)
        print('RESULT',result)
        if result:
            self._place_name,self._latitude,self._longitude,self._time_zone = result
            self._place_text.setText(self._place_name)
            self._lat_text.setText(str(self._latitude))
            self._long_text.setText(str(self._longitude))
            self._tz_text.setText(str(self._time_zone))
            print(self._place_name,self._latitude,self._longitude,self._time_zone)
        else:
            msg = place_name+" could not be found in OpenStreetMap.\nTry entering latitude and longitude manually.\nOr try entering nearest big city"
            print(msg)
            QMessageBox.about(self,"City not found",msg)
            self._lat_text.setText('')
            self._long_text.setText('')
        self._reset_place_text_size()
            
    def _save_city_to_database(self):
        if self._validate_ui():
            " add this data to csv file "
            tmp_arr = self._place_name.split(',')
            country = 'N/A'
            city = tmp_arr[0]
            if len(tmp_arr) > 1:
                country = tmp_arr[1:]
            location_data = [country,city,self._latitude,self._longitude,country,self._time_zone]
            utils.save_location_to_database(location_data)
        return          
    def save_as_pdf(self,pdf_file_name=None):
        """
            Save the displayed chart as a pdf
            Choose a file from file save dialog displayed
        """
        image_prefix = 'pdf_grb_'
        image_ext = '.png'
        if pdf_file_name==None:
            path = QFileDialog.getSaveFileName(self, 'Choose folder and file to save as PDF file', './output', 'PDF files (*.pdf)')#)
            pdf_file_name = path[0]
        image_files = []
        combined_image_files = []
        image_id = 1
        def __save_scrollable_list_widget_as_image(widget:QWidget,image_id, image_files,_row_steps=1,widget_is_combo=False,row_count_size=None):
            """ TODO: Annual Dhasa count is not coming correct. Annual Dhasa is repeatedly printed by rasi/graha dhasa count times """
            _sleep_time = 0.01
            scroll_tab_count = 0
            import time; 
            row_count = widget.count() if row_count_size==None else row_count_size
            for row in range(0,row_count,_row_steps):
                self._hide_show_even_odd_pages(image_id)
                if widget_is_combo:
                    widget.setCurrentIndex(row)
                    if widget == self._dhasa_combo:
                        self._dhasa_type_selection_changed()                 
                else:
                    widget.setCurrentRow(row)
                image_file = _images_path+image_prefix+str(image_id)+image_ext
                time.sleep(_sleep_time)
                im = self.grab()
                im.save(image_file) 
                image_files.append(image_file)
                image_id +=1
                scroll_tab_count += 1
            return image_id
        if not self._western_chart:
            self._matching_star_list.setVisible(False)
            self._matching_star_list.setMaximumWidth(0)
            self._yoga_list.setVisible(False)
            self._yoga_list.setMaximumWidth(0)
            self._dosha_list.setVisible(False)
            self._dosha_list.setMaximumWidth(0)
            if self._gender in [0,1]:
                for c in range(_comp_results_per_list_item):
                    self._comp_results_table[c].update()
            self._prediction_list.setVisible(False)
            self._prediction_list.setMaximumWidth(0)
            self._yoga_text.update()
            self._dosha_text.update()
            self._prediction_text.update()
        if pdf_file_name:
            self._hide_show_layout_widgets(self._row3_h_layout, False)
            for t in range(self.tabCount):
                self._hide_show_even_odd_pages(image_id)
                self.tabWidget.setCurrentIndex(t)
                self._show_only_tab(t)
                #"""
                if t==_chart_tab_end-1: image_id = __save_scrollable_list_widget_as_image(self._kundali_chart_combo,image_id, image_files,widget_is_combo=True)
                elif t==_amsa_ruler_tab_start: image_id = __save_scrollable_list_widget_as_image(self._amsa_chart_combo,image_id, image_files,widget_is_combo=True)
                elif t==_sphuta_tab_start: image_id = __save_scrollable_list_widget_as_image(self._sphuta_chart_combo,image_id, image_files,widget_is_combo=True)
                elif t==_graha_arudha_tab_start: image_id = __save_scrollable_list_widget_as_image(self._arudha_chart_combo,image_id, image_files,widget_is_combo=True)
                elif t==_dhasa_bhukthi_tab_index:
                    self._dhasa_type_combo.setCurrentIndex(0)
                    image_id = __save_scrollable_list_widget_as_image(self._dhasa_combo,image_id, image_files,widget_is_combo=True,row_count_size=len(_graha_dhasa_dict))
                    self._dhasa_type_combo.setCurrentIndex(1)
                    image_id = __save_scrollable_list_widget_as_image(self._dhasa_combo,image_id, image_files,widget_is_combo=True,row_count_size=len(_rasi_dhasa_dict))
                    self._dhasa_type_combo.setCurrentIndex(2)
                    image_id = __save_scrollable_list_widget_as_image(self._dhasa_combo,image_id, image_files,widget_is_combo=True,row_count_size=len(_annual_dhasa_dict))
                elif t==_ashtaka_varga_tab_start: image_id = __save_scrollable_list_widget_as_image(self._ashtaka_chart_combo,image_id, image_files,widget_is_combo=True)
                elif t==_argala_tab_start: image_id = __save_scrollable_list_widget_as_image(self._argala_chart_combo,image_id, image_files,widget_is_combo=True)
                elif t==_yoga_tab_start: image_id = __save_scrollable_list_widget_as_image(self._yoga_list,image_id, image_files)
                elif t==_dosha_tab_start:image_id = __save_scrollable_list_widget_as_image(self._dosha_list,image_id, image_files)
                elif t==_compatibility_tab_start:image_id = __save_scrollable_list_widget_as_image(self._matching_star_list,image_id, image_files,_comp_results_per_list_item)
                elif t==_prediction_tab_start:image_id = __save_scrollable_list_widget_as_image(self._prediction_list,image_id, image_files)
                else:
                    image_file = _images_path+image_prefix+str(image_id)+image_ext
                    image_files.append(image_file)
                    im = self.grab()
                    im.save(image_file) 
                    image_id +=1
                #"""
            self._reset_all_ui()
            ci = 1
            for i in range(0,len(image_files),_IMAGES_PER_PDF_PAGE):
                combined_image_file = _images_path+'combined_'+str(ci)+image_ext
                _combine_multiple_images(image_files[i:i+2],combined_image_file)
                combined_image_files.append(combined_image_file)
                ci += 1
            with open(pdf_file_name,"wb") as f:
                f.write(img2pdf.convert(combined_image_files))
            f.close()
        for image_file in image_files+combined_image_files:
            if os.path.exists(image_file):
                os.remove(image_file)
    def _reset_all_ui(self):
        self._hide_show_layout_widgets(self._row1_h_layout, True)
        self._hide_show_layout_widgets(self._row2_h_layout, True)
        self._hide_show_layout_widgets(self._row3_h_layout, True)
        self._hide_show_layout_widgets(self._comp_h_layout, True)
        self._footer_label.show()
        if not self._western_chart:
            self._matching_star_list.setVisible(True)
            self._matching_star_list.setMaximumWidth(_compatability_list_width)
            self._yoga_list.setVisible(True)
            self._yoga_list.setMaximumWidth(_yoga_list_box_width)
            self._dosha_list.setVisible(True)
            self._dosha_list.setMaximumWidth(_dosha_list_box_width)
            self._prediction_list.setVisible(True)
            self._prediction_list.setMaximumWidth(_prediction_list_box_width)
            for c in range(_comp_results_per_list_item):
                self._comp_results_table[c].update()
            self._yoga_text.update()
            self._dosha_text.update()
            self._prediction_text.update()
        for t in range(self.tabCount): # reset all tabs to visible
            self.tabWidget.setTabVisible(t,True)
        
    def _hide_show_even_odd_pages(self,image_id):
        if image_id % 2 == 0: # Even Page
            self._hide_show_layout_widgets(self._row1_h_layout, False)
            self._hide_show_layout_widgets(self._row2_h_layout, False)
            self._hide_show_layout_widgets(self._comp_h_layout, False)
            self._footer_label.show()
        else:
            self._hide_show_layout_widgets(self._row1_h_layout, True)
            if image_id==1:
                self._hide_show_layout_widgets(self._row2_h_layout, True)
                self._hide_show_layout_widgets(self._comp_h_layout, True)
            self._footer_label.hide()        
    def _hide_show_layout_widgets(self,layout,show):
        for index in range(layout.count()):
            myWidget = layout.itemAt(index).widget()
            if show:
                myWidget.show()
            else:
                myWidget.hide()
            index -=1            
    def exit(self):
        self.close()
        QApplication.quit()
        print('Application Closed')
    def _show_only_tab(self,t): #set onlt tab t to be visible
        for ti in range(self.tabCount):
            self.tabWidget.setTabVisible(ti,False)
            if t==ti:
                self.tabWidget.setTabVisible(ti,True)
    def _convert_language_chart_to_english(self,rasi_1d_lang):
        rasi_1d_en = rasi_1d_lang[:]
        #utils.PLANET_NAMES = self.resources['PLANET_NAMES'].split(',')
        #utils.RAASI_LIST = self.resources['RAASI_LIST'].split(',')
        #print(utils.PLANET_NAMES,self.resources['ascendant_str'])
        planet_list_lang = utils.PLANET_NAMES+[self.resources['ascendant_str']]
        planet_list_en = ['Sun☉','Moon☾','Mars♂','Mercury☿','Jupiter♃','Venus♀','Saturn♄','Raagu☊','Kethu☋','Uranus','Neptune','Pluto','Lagnam']
        planet_lang_dict = {planet_list_lang[i]:planet_list_en[i] for i in range(len(planet_list_en))}
        for k,v in planet_lang_dict.items():
            for i,house in enumerate(rasi_1d_en):
                if k in house:
                    rasi_1d_en[i] = rasi_1d_en[i].replace(k,v)
        return rasi_1d_en
    def _convert_language_chart_to_indices(self,rasi_1d_lang):
        rasi_1d_en = self._convert_language_chart_to_english(rasi_1d_lang)
        planet_list_en = ['Sun☉','Moon☾','Mars♂','Mercury☿','Jupiter♃','Venus♀','Saturn♄','Raagu☊','Kethu☋','Uranus','Neptune','Pluto']+['Lagnam']
        planet_lang_dict = {planet_list_en[i]:str(i) for i in range(len(planet_list_en))}
        last_key = list(planet_lang_dict)[-1]
        planet_lang_dict[last_key] = const._ascendant_symbol
        for k,v in planet_lang_dict.items():
            for i,house in enumerate(rasi_1d_en):
                if k in house:
                    rasi_1d_en[i] = rasi_1d_en[i].replace(k,v).replace(const._retrogade_symbol,'')
        return rasi_1d_en
def show_horoscope(data):
    """
        Same as class method show() to display the horoscope
        @param data - last chance to pass the data to the class
    """
    app=QApplication(sys.argv)
    window=ChartTabbed(data)
    window.show()
    app.exec_()
def _index_containing_substring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
            return i
    return -1
def _convert_1d_house_data_to_2d(rasi_1d,chart_type='south_indian'):
    separator = '/'
    if 'south' in chart_type.lower():
        row_count = 4
        col_count = 4
        map_to_2d = [ [11,0,1,2], [10,"","",3], [9,"","",4], [8,7,6,5] ]
    elif 'east' in chart_type.lower():
        row_count = 3
        col_count = 3
        map_to_2d = [['2'+separator+'1','0','11'+separator+'10'], ['3', "",'9' ], ['4'+separator+'5','6','7'+separator+'8']]
    rasi_2d = [['X']*row_count for _ in range(col_count)]
    for p,val in enumerate(rasi_1d):
        for index, row in enumerate(map_to_2d):
            if 'south' in chart_type.lower():
                i,j = [(index, row.index(p)) for index, row in enumerate(map_to_2d) if p in row][0]
                rasi_2d[i][j] = str(val)
            elif 'east' in chart_type.lower():
                p_index = _index_containing_substring(row,str(p))
                if p_index != -1:
                    i,j = (index, p_index)
                    if rasi_2d[i][j] != 'X':
                        if index > 0:
                            rasi_2d[i][j] += separator + str(val)
                        else:
                            rasi_2d[i][j] = str(val) + separator + rasi_2d[i][j]
                    else:
                        rasi_2d[i][j] = str(val)
    for i in range(row_count):
        for j in range(col_count):
            if rasi_2d[i][j] == 'X':
                rasi_2d[i][j] = ''
    return rasi_2d
def _get_row_col_string_match_from_2d_list(list_2d,match_string):
    for row in range(len(list_2d)):
        for col in range(len(list_2d[0])):
            if match_string in list_2d[row][col]:
                return (row,col)
def _get_date_difference(then, now = datetime.now(), interval = "default"):
    from dateutil import relativedelta
    diff = relativedelta.relativedelta(now,then)
    years = abs(diff.years)
    months = abs(diff.months)
    days = abs(diff.days)
    return [years,months,days]
def _dhasa_balance(date_of_birth,dhasa_end_date):
    return utils.panchanga_date_diff(date_of_birth,dhasa_end_date)
def _combine_multiple_images(image_list,output_image,combine_mode='vertical',image_quality_in_pixels=100):
    total_width = 0
    total_height = 0
    max_width = 0
    max_height = 0
    ix =[]
    for img in image_list:
        im = Image.open(img)
        size = im.size
        w = size[0]
        h = size[1]
        total_width += w 
        total_height += h
        
        if h > max_height:
            max_height = h
        if w > max_width:
            max_width = w
        ix.append(im) 
    if combine_mode.lower()=='vertical':
        target = Image.new('RGB', (max_width, total_height))
    else:
        target = Image.new('RGB', (total_width, max_height))
    pre_w = 0
    pre_h = 0
    for img in ix:
        if combine_mode.lower()=='vertical':
            target.paste(img, (pre_w, pre_h, pre_w+max_width, pre_h + img.size[1]))
            pre_h += img.size[1]
        else:
            target.paste(img, (pre_w, pre_h, pre_w+img.size[0], pre_h + img.size[1]))
            pre_w += img.size[0]            
    target.save(output_image, quality=image_quality_in_pixels)
if __name__ == "__main__":
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    App = QApplication(sys.argv)
    chart = ChartTabbed()
    chart.language('Tamil')
    """
    chart.name('XXX')#'('Rama')
    chart.gender(1) #(0)
    ### TODO: STRANGELY Date('-3101,2,1'), Time('2:34:00') - hangs  
    chart.date_of_birth('-5114,1,9')#('-3101,1,22')#('1996,12,7')#
    chart.time_of_birth('12:10:00')#('10:34:00')#
    chart.place('Ayodhya, India',26.7991,82.2047,5.5)#('Ujjain,India',23.18,75.77,5.5)#('Chennai,India',13.0878,80.2785,5.5)#
    """
    chart.compute_horoscope()
    chart.show()
    sys.exit(App.exec())
