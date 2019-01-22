import sys, os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
import design
from Auxledsdata import *
from Commondata import *
from profiledata import *
import Mediator
import assistant
import palitra

from loguru import logger

logger.start("logfile.log", rotation="1 week", format="{time} {level} {message}", level="DEBUG", enqueue=True)

auxleds = 'AUXLEDs'
common = 'Common'
profiletab = 'Profiles'
tabnames = [auxleds, common, profiletab]


def initiate_exception_logging():
    # generating our hook
    # Back up the reference to the exceptionhook
    sys._excepthook = sys.excepthook

    def my_exception_hook(exctype, value, traceback):
        # Print the error and traceback
        logger.exception(f"{exctype}, {value}, {traceback}")
        # Call the normal Exception hook after
        sys._excepthook(exctype, value, traceback)
        #sys.exit(1)

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook


# from PyQt5.QtGui import QIcon


class StepTreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, name):
        super().__init__([name])

class RepeatTreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, name):
        super().__init__([name])


class SequencerTreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, name):
        super().__init__([name])


class ProfileEditor(QtWidgets.QMainWindow, design.Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.auxdata = AuxEffects()
        self.commondata = CommonData()
        self.profiledata = Profiles()
        self.data = [self.auxdata, self.commondata, self.profiledata]
        self.saved = [True, True, True]
        self.filename = ["", "", ""]
        self.default_names = ["Auxleds.ini", "Common.ini", "Profiles.ini"]
        self.savefunctions = [self.auxdata.save_to_file, self.commondata.save_to_file, self.profiledata.save_to_file]
        self.openfunctions = [Mediator.translate_json_to_tree_structure, Mediator.get_common_data, Mediator.load_profiles]
        self.statusfields = [self.TxtAuxStatus, self.TxtCommonStatus, self.TxtProfileStatus]
        self.loadfunctions = [self.LoadAuxleds, self.LoadCommon, self.LoadProfiles]
        self.initAuxUI()
        self.CommonUI()
        self.ProfileUI()

        # add menu triggers
        self.actionExit.triggered.connect(self.close)
        self.actionExit.setShortcut('Ctrl+Q')
        self.actionSave.triggered.connect(self.SavePressed)
        self.actionSave.setShortcut('Ctrl+S')
        self.actionSave_As.triggered.connect(self.SaveAsPressed)
        self.actionSave_As.setShortcut('Ctrl+Shift+S')
        self.actionNew.triggered.connect(self.NewPressed)
        self.actionSave_All.setShortcut('Ctrl+Alt+S')
        self.actionSave_All.triggered.connect(self.SaveAllPressed)
        self.actionNew.setShortcut('Ctrl+N')
        self.actionOpen.triggered.connect(self.OpenPressed)
        self.actionOpen.setShortcut('Ctrl+O')
        self.actionAuxLeds_Editor_Help.triggered.connect(assistant.auxleds_help)
        self.actionCommon_Editor_Help.triggered.connect(assistant.common_help)
        self.actionProfiles_Edtor_Help.triggered.connect(assistant.profile_help)
        self.actionAbout.triggered.connect(assistant.about_help)
        self.actionOpenAll.triggered.connect(self.OpenAllPressed)

    # init part
    ####################################################################################################################
    def initAuxUI(self):
        # useful lists of items
        self.leds_combo_list = [self.CBLed1, self.CBLed2, self.CBLed3, self.CBLed4, self.CBLed5, self.CBLed6,
                                self.CBLed7, self.CBLed8]
        self.leds = dict(list(zip(Mediator.leds_list, self.leds_combo_list)))
        self.leds_cb_str = dict(list(zip(self.leds_combo_list, Mediator.leds_list)))
        self.step_leds_brightnesses = [self.SpinBrightness1, self.SpinBrightness2, self.SpinBrightness3,
                                       self.SpinBrightness4, self.SpinBrightness5, self.SpinBrightness6,
                                       self.SpinBrightness7, self.SpinBrightness8]
        self.step_channels = [self.CBChannel1, self.CBChannel2, self.CBChannel3, self.CBChannel4, self.CBChannel5,
                              self.CBChannel6, self.CBChannel7, self.CBChannel8]
        self.step_brightness_dict = dict(list(zip(Mediator.leds_list, self.step_leds_brightnesses)))
        self.step_channels_dict = dict(list(zip(Mediator.leds_list, self.step_channels)))

        # add Logo
        # self.ImgLogo = QPixmap('Logo.jpg')
        # self.LblLogo = QtWidgets.QLabel(self)
        # self.LblLogo.setPixmap(self.ImgLogo)
        # self.gridLayout.addWidget(self.LblLogo, 2, 0, 12, 1)

        # add button clicks
        self.BtnAddGroup.clicked.connect(self.AddGroup)
        self.BtnAddSequencer.clicked.connect(self.AddSequencer)
        self.BtnCopySeq.clicked.connect(self.CopySequencer)
        self.BtnDeleteGroup.clicked.connect(self.DeleteGroup)
        self.BtnAddStep.clicked.connect(self.AddStep)
        self.BtnEditStep.clicked.connect(self.EditStep)
        self.BtnDeleteSeq.clicked.connect(self.DeleteItem)
        self.BtnDeleteStep.clicked.connect(self.DeleteItem)
        self.BtnAddRepeat.clicked.connect(self.AddRepeatStep)
        self.BtnDeleteRepeat.clicked.connect(self.DeleteItem)
        self.BtnEditRepeat.clicked.connect(self.EditRepeater)
        self.BtnUpdate.clicked.connect(self.UpdateGroup)
        self.BtnChange.clicked.connect(self.ChangePressed)

        self.CBGroup.currentTextChanged.connect(self.GroupChanged)

        self.TxtGroup.textChanged[str].connect(self.GroupNameChanged)

        #for led in self.step_leds_brightnesses:
        #    led.valueChanged.connect(self.BrightnessChanged)
        self.LstGroup.itemPressed.connect(self.GroupClicked)
        self.TrStructure.itemPressed.connect(self.TreeItemChanged)

        for CB in self.leds_combo_list:
            CB.stateChanged.connect(self.LedClicked)
        self.preload_auxes()

    def preload_auxes(self):
        """
        load Auxleds.ini file if it exists in current directory
        :return:
        """
        filename = assistant.find_file("Auxleds.ini")
        if filename != None:
            text = open(filename, encoding='utf-8').read()
            gui_data, error, warning = self.openfunctions[0](text)
            if error == "":
                if warning:
                    self.statusfields[0].setText("Try to open %s...\n %s" % (filename, warning))
                else:
                    self.statusfields[0].setText("%s successfully loaded" % filename)
                self.LoadAuxleds(gui_data)
                self.filename[0] = filename
                self.ChangeTabTitle(auxleds, 0)

    def CommonUI(self):
        # list of common items
        self.blade1_controls = [self.SpinBand, self.SpinPixPerBand, self.SpinStartFlash]
        self.blade2_controls = [self.SpinBandNumber, self.SpinPixPerBand2, self.SpinStartFlash_2]
        self.volume_controls = [self.SpinCommon, self.SpinCoarseLow, self.SpinCoarseMid, self.SpinCoarseHigh]
        self.deadtime_controls = [self.SpinAfterPowerOn, self.SpinAfterBlaster, self.SpinAfterClash]
        self.other_ccntrols = [self.SpinPowerOffTimeout]
        self.swing_controls = [self.SpinSwingHighW, self.SpinSwingPercent, self.SpinSwingCircle, self.SpinSwingCircleW]
        self.spin_controls = [self.CBSpinEnabled, self.SpinSpinCounter, self.SpinSpinW, self.SpinSpinCircle,
                              self.SpinSpinWLow]
        self.clash_controls = [self.SpinClashHighA, self.SpinClashLength, self.SpinClashHitLevel, self.SpinClashLowW]
        self.stab_controls = [self.CBStabEnabled, self.SpinStabHighA, self.SpinStabLowW, self.SpinStabHitLevel,
                              self.SpinStabLength, self.SpinStabPercent]
        self.screw_controls = [self.CBScrewEnabled, self.SpinScrewHighW, self.SpinScrewLowW]
        self.common_controls = [self.blade1_controls, self.blade2_controls, self.volume_controls,
                                self.deadtime_controls, self.other_ccntrols]
        self.motion_controls = [self.swing_controls, self.spin_controls, self.clash_controls, self.stab_controls,
                                self.screw_controls]

        # common_controls_connect_maps
        self.common_dict = {}
        for i in range(len(self.common_controls)):
            keys_list = [[Mediator.main_sections[i], key] for key in Mediator.main_list[i]]
            self.common_dict.update(dict(list(zip(self.common_controls[i], keys_list))))
        self.motion_dict = {}
        for i in range(len(self.motion_controls)):
            keys_list = [[Mediator.motion_key, Mediator.motion_keys[i], key] for key in Mediator.motion_list[i]]
            self.motion_dict.update((dict(list(zip(self.motion_controls[i], keys_list)))))

        # common controls init
        for control_list in self.common_controls + self.motion_controls:
            for control in control_list:
                if control in (self.CBBlade2Enabled, self.CBSpinEnabled, self.CBStabEnabled, self.CBScrewEnabled):
                    control.stateChanged.connect(self.CBClicked)
                else:
                    control.valueChanged.connect(self.SpinChanged)

        self.SetDefaultCommon()
        self.BtnSave.clicked.connect(self.SavePressed)
        self.BtnDefault.clicked.connect(self.SetDefaultCommon)
        self.CBBlade2Enabled.stateChanged.connect(self.Blade2Clicked)
        self.preload_common()
        self.saved[1] = True
        self.ChangeTabTitle(common, 1)

    def preload_common(self):
        """
        loaas file Commom.ini if any
        :return:
        """
        filename = assistant.find_file("Common.ini")
        if filename != None:
            text = open(filename, encoding='utf-8').read()
            gui_data, error, warning = self.openfunctions[1](text)
            if error == "":
                if warning:
                    self.statusfields[1].setText("Try to open %s...\n %s" % (filename, warning))
                else:
                    self.statusfields[1].setText("%s successfully loaded" % filename)
                self.LoadCommon(gui_data)
                self.filename[1] = filename
                self.ChangeTabTitle(common, 1)

    def ProfileUI(self):
        # list of controls
        self.poweron = [self.SpinBladeSpeedOn]
        self.poweroff = [self.SpinPowerOffSpeed, self.CBMoveForward]
        self.working = [self.TxtWorkingColor, self.CBFlaming, self.CBFlickering]
        self.flaming = [self.SpinFlamingSizeMin, self.SpinFlamingSizeMax, self.SpinFlamingSpeedMin,
                        self.SpinFlamingSpeedMax,
                        self.SpinFlamingDelayMin, self.SpinFlamingDelayMax]
        self.flickering = [self.SpinFlickeringTimeMin, self.SpinFlickeringTimeMax, self.SpinFlickeringBrMin,
                           self.SpinFlickeringBrMax]
        self.blaster = [self.TxtBlasterColor, self.SpinBlasterDuration, self.SpinBlasterSizePix]
        self.clash = [self.TxtClashColor, self.SpinClashDuration, self.SpinClashSizePix]
        self.stab = [self.TxtStabColor, self.SpinStabDuration, self.SpinStabSizePix]
        self.lockup = [self.TxtLockupFlickerColor, self.SpinLockupTimeMin, self.SpinLockupTimeMax,
                       self.SpinLockupBrightnessMin, self.SpinLockupBrightnessMax, self.SpinLockupPeriodMin,
                       self.SpinLockupPeriodMax, self.TxtLockupFlashesColor, self.SpinLockupDuration,
                       self.SpinLockupSizepix]
        # map of tabs and their controls
        self.control_tab_dict = {1: self.poweron, 2: self.working, 3: self.poweroff, 4: self.flaming, 5: self.flickering,
                             6: self.blaster, 7: self.clash, 8: self.stab, 9: self.lockup}
        # map of color change data to their text field
        self.color_dict = {self.BtnBlasterColor: self.TxtBlasterColor, self.BtnClashColor: self.TxtClashColor,
                           self.BtnStabColor: self.TxtStabColor, self.BtnWorkingColor: self.TxtWorkingColor,
                           self.BtnLockupFlashesColor: self.TxtLockupFlashesColor,
                           self.BtnLockupFlickerColor: self.TxtLockupFlickerColor}
        self.selected_color_dict = {self.TxtBlasterColor: self.BlasterColor, self.TxtClashColor: self.ClashColor,
                                    self.TxtStabColor: self.StabColor, self.TxtWorkingColor: self.WorkingColor,
                                    self.TxtLockupFlashesColor: self.LockupFlashesColor,
                                    self.TxtLockupFlickerColor: self.LockupFlickerColor}
        # list of color text fields
        self.color_list = [self.TxtClashColor, self.TxtWorkingColor, self.TxtStabColor, self.TxtBlasterColor,
                           self.TxtLockupFlickerColor, self.TxtLockupFlashesColor]
        # map of min to max values in min max pairs
        self.min_max_dict = {self.SpinLockupTimeMin: self.SpinLockupTimeMax,
                             self.SpinLockupPeriodMin: self.SpinLockupPeriodMax,
                             self.SpinLockupBrightnessMin: self.SpinLockupBrightnessMax,
                             self.SpinFlickeringTimeMin: self.SpinFlickeringTimeMax,
                             self.SpinFlickeringBrMin: self.SpinFlickeringBrMax,
                             self.SpinFlamingSpeedMin: self.SpinFlamingSpeedMax,
                             self.SpinFlamingSizeMin: self.SpinFlamingSizeMax,
                             self.SpinFlamingDelayMin: self.SpinFlamingDelayMax}
        # lists of checkboxes
        self.CB_list = [self.CBFlickering, self.CBFlaming, self.CBMoveForward]
        self.extra_blade_CB_dict = {self.CBIndicate: Mediator.indicate_path, self.CBFlickeringAlwaysOn:
                                    Mediator.flickering_on_path, self.CBFlamingAlwaysOn: Mediator.flaming_on_path}
        self.CB_single_dict = {self.CBFlickering: self.CBFlaming, self.CBFlaming: self.CBFlickering,
                               self.CBFlamingAlwaysOn: self.CBFlickeringAlwaysOn,
                               self.CBFlickeringAlwaysOn:self.CBFlamingAlwaysOn}
        # reverse of min max dict - map max value to min
        self.max_min_dict = dict([(self.min_max_dict[key], key) for key in self.min_max_dict.keys()])

        #create map of controls to key path in data dictionary (path lists from Mediator file)
        self.profile_dict = {}
        for i in self.control_tab_dict.keys():
            keys_list = []
            for key in Mediator.profile_list[i - 1]:
                keys_list.append([Mediator.tab_list[i - 1]] + key)
            self.profile_dict.update(dict(list(zip(self.control_tab_dict[i], keys_list))))
        #set data change handlers
        for control in self.profile_dict.keys():
            if control in self.CB_list:
                control.stateChanged.connect(self.ProfileCBClicked)
            else:
                if control in self.color_list:
                    control.textChanged.connect(self.ProfileTextChanged)
                else:
                    control.valueChanged.connect(self.ProfileSpinChanged)

        for color_button in self.color_dict.keys():
            color_button.clicked.connect(self.ColorChanged)

        for CB in self.extra_blade_CB_dict.keys():
            CB.clicked.connect(self.ExtraBladeCBlicked)

        self.BtnProfile.clicked.connect(self.AddProfile)
        self.BtnDeleteProfile.clicked.connect(self.DeleteProfile)
        self.BtnAddColor.clicked.connect(self.AddColor)
        self.BtnDeleteColor.clicked.connect(self.DeleteColor)
        self.BtnCReateAux.clicked.connect(self.ProfileAddAux)
        self.BtnAuxDelete.clicked.connect(self.DeleteAux)
        self.BtnEditProfile.clicked.connect(self.ProfileEditPressed)
        self.BtnUp.clicked.connect(self.MoveUp)
        self.BtnDown.clicked.connect(self.MoveDown)

        self.TabEffects.currentChanged.connect(self.EffectTabChanged)
        self.TxtAddProfile.textChanged[str].connect(self.ProfileNameChanged)
        self.LstProfile.itemPressed.connect(self.ProfileClicked)
        self.LstFlamingColor.itemPressed.connect(self.ColorClicked)
        self.LstAuxProfile.itemPressed.connect(self.AuxClicked)
        self.CBBlade.currentIndexChanged.connect(self.BladeChanged)
        self.SpinDelayBeforeOn.valueChanged.connect(self.DelayChanged)


        self.preload_profiles()

    def preload_profiles(self):
        """
        load Profiles.ini file if it exists in current directory
        :return:
        """
        filename = assistant.find_file("Profiles.ini")
        if filename != None:
            text = open(filename, encoding='utf-8').read()
            gui_data, error, warning = self.openfunctions[2](text)
            if error == "":
                if warning:
                    self.statusfields[2].setText("Try to open %s...\n %s" % (filename, warning))
                else:
                    self.statusfields[2].setText("%s successfully loaded" % filename)
                self.LoadProfiles(gui_data)
                self.filename[2] = filename
                self.ChangeTabTitle(profiletab, 2)

    # auxleds part
    ####################################################################################################################
    def AddGroup(self):
        """
        Adds group to UI and data if name is correct
        disables used leds
        """
        name: str = self.TxtGroup.text()
        # get clicked leds and create new group
        leds_clicked: List[QtWidgets.QComboBox] = [CB for CB in self.leds_combo_list if CB.isChecked() and CB.isEnabled()]
        leds_list: List[str] = [self.leds_cb_str[CB] for CB in leds_clicked]
        group_to_add, error = self.auxdata.add_group(name, leds_list)
        if group_to_add is None:
            self.ErrorMessage(error)
        else:
            # add group to group liat and sequencer, disable its leds
            self.LstGroup.addItem(str(group_to_add))
            self.LstGroup.setCurrentRow(self.auxdata.LedGroups.index(group_to_add))
            self.GroupClicked()
            self.CBGroup.addItem(group_to_add.Name)
            for led in leds_clicked:
                led.setEnabled(False)
            self.BtnAddGroup.setEnabled(False)
            # leds are now available for change
            leds_to_add = ["LED"+self.leds_cb_str[led] for led in leds_clicked]
            self.CBFirstLED.addItems(leds_to_add)
            self.CBSecondLED.addItems(leds_to_add)
            self.BtnChange.setEnabled(True)
            # data is unsaved now
            self.saved[0] = False
            self.ChangeTabTitle(auxleds, self.tabWidget.currentIndex())

    def UpdateGroup(self):
        """
        changes group name on gui and data
        :return:
        """
        # get group with new name
        new = self.TxtGroup.text()
        old = self.LstGroup.currentItem().text()
        group, error = self.auxdata.rename_group(old, new)
        if error:
            self.ErrorMessage(error)
        else:
            # reload group list
            self.LstGroup.clear()
            self.CBGroup.clear()
            for group in self.auxdata.LedGroups:
                self.LstGroup.addItem(str(group))
                self.CBGroup.addItem(group.Name)
            # reload tree with sequencers with new groups
            self.TrStructure.clear()
            for seq in self.auxdata.Sequencers:
                item = SequencerTreeItem(str(seq))
                self.TrStructure.addTopLevelItem(item)
                for step in seq.Sequence:
                    if isinstance(step, Step):
                        step_item = StepTreeItem(str(step))
                        item.addChild(step_item)
                    elif isinstance(step, Repeater):
                        step_item = RepeatTreeItem(str(step))
                        item.addChild(step_item)
            self.StepControlsDisable()
            self.RepeatControlDisable()
            self.BtnUpdate.setEnabled(False)
            # data is unsaved now
            self.saved[0] = False
            self.ChangeTabTitle(auxleds, 0)

    def GroupNameChanged(self, name):
        """
        enables add group button if name is not empty and some leds are checked
        :param name:
        :return:
        """
        enabled = True if name and any([CB.isChecked() and CB.isEnabled() for CB in self.leds_combo_list]) else False
        self.BtnAddGroup.setEnabled(enabled)

    def LedClicked(self):
        """
        changes status of add group button if some leds are selected/are not selected
        :return:
        """
        name = self.TxtGroup.text()
        enabled = True if name and any([CB.isChecked() and CB.isEnabled() for CB in self.leds_combo_list]) else False
        self.BtnAddGroup.setEnabled(enabled)

    def ChangePressed(self):
        """
        exchanges two leds in groups
        :return:
        """
        led1 = self.CBFirstLED.currentText().replace("LED", "")
        led2 = self.CBSecondLED.currentText().replace("LED", "")
        error = self.auxdata.change_leds(led1, led2)
        if error:
            self.ErrorMessage(error)
        else:
            self.LstGroup.clear()
            self.LstGroup.addItems([str(group) for group in self.auxdata.LedGroups])
            self.BtnAddGroup.setEnabled(False)
            self.BtnUpdate.setEnabled(False)
            self.BtnDeleteGroup.setEnabled(False)
            self.saved[0] = False
            self.ChangeTabTitle(auxleds, 0)
        current = self.TrStructure.currentItem()
        if current and isinstance(current, StepTreeItem):
            self.TreeItemChanged(current)


    def GroupClicked(self):
        """
        enables Sequence controls and Delete Button
        :return:
        """
        self.BtnDeleteGroup.setEnabled(True)
        self.BtnUpdate.setEnabled(True)

    def DeleteGroup(self):
        """
        deletes group if it is not used in any Sequencer
        :return:
        """
        group = self.LstGroup.currentItem().text()
        leds_to_free = self.auxdata.delete_group_and_enable_leds(group)
        if not leds_to_free:
            self.ErrorMessage("This group is used un sequencers, remove or edit them first")
        else:
            # enabled freed leds
            for led in leds_to_free:
                self.leds[led].setEnabled(True)
                self.leds[led].setChecked(False)
            #reload leds to change list
            leds = self.auxdata.get_leds_used()
            self.CBFirstLED.clear()
            self.CBSecondLED.clear()
            if leds:
                leds_to_add = [("LED" + led) for led in leds]
                self.CBFirstLED.addItems(leds_to_add)
                self.CBSecondLED.addItems(leds_to_add)
            self.BtnChange.setEnabled(bool(leds))

            # reload group list
            self.LstGroup.clear()
            self.CBGroup.clear()
            for group in self.auxdata.LedGroups:
                self.LstGroup.addItem(str(group))
                self.CBGroup.addItem(group.Name)
            # disable delete button and sequencer controls
            self.BtnDeleteGroup.setEnabled(False)
            self.SequenceControlsDisable()
            #data is unsaved now
            self.saved[0] = False
            self.ChangeTabTitle(auxleds, 0)

    def GroupControlsClear(self):
        """
        clears all group controls
        :return:
        """
        self.TxtGroup.clear()
        # check and disable used leds
        leds_used = self.auxdata.get_leds_used()
        for led in self.leds_cb_str.keys():
            if self.leds_cb_str[led] in leds_used:
                led.setEnabled(False)
                led.setChecked(True)
            else:
                led.setChecked(False)
                led.setEnabled(True)
        # reload leds for change
        self.CBFirstLED.clear()
        self.CBSecondLED.clear()
        if leds_used:
            leds_to_add = ["LED" + led for led in leds_used]
            self.CBFirstLED.addItems(leds_to_add)
            self.CBSecondLED.addItems(leds_to_add)
            self.BtnChange.setEnabled(True)
        else:
            self.BtnChange.setEnabled(False)
        # disable group buttons
        self.BtnAddGroup.setEnabled(False)
        self.BtnDeleteGroup.setEnabled(False)
        self.BtnUpdate.setEnabled(False)
        self.CBGroup.clear()
        # reload group list
        for group in self.auxdata.LedGroups:
            self.CBGroup.addItem(group.Name)

    def SequenceControlsEnable(self):
        """
        enables all sequencer controls
        :return:
        """
        self.TxtSeqName.setEnabled(True)
        self.BtnAddSequencer.setEnabled(True)
        self.CBSeqList.setEnabled(True)
        if self.CBSeqList.count() > 0:
            self.BtnCopySeq.setEnabled(True)

    def SequenceControlsDisable(self):
        """
        disables all sequencer controls
        :return:
        """
        self.TxtSeqName.setEnabled(False)
        self.BtnAddSequencer.setEnabled(False)
        self.CBSeqList.setEnabled(False)
        self.BtnCopySeq.setEnabled(False)

    def GroupChanged(self):
        """
        if there are items in gropu comboobox, Sequencer fata is enabled, otherwise disabled
        :return:
        """
        if self.CBGroup.count() > 0:
            self.SequenceControlsEnable()
            seqs = self.auxdata.get_corresponding_seqs(self.CBGroup.currentText())
            self.CBSeqList.clear()
            self.CBSeqList.addItems(seqs)
            if not seqs:
                self.BtnCopySeq.setEnabled(False)
            else:
                self.BtnCopySeq.setEnabled(True)
        else:
            self.SequenceControlsDisable()


    def AddSequencer(self):
        """
        Adds new Sequencer to gui and data
        :return:
        """
        seq_name = self.TxtSeqName.text()
        group_name = self.CBGroup.currentText()
        seq, error = self.auxdata.create_sequence(group_name, seq_name)
        if not seq:
            self.ErrorMessage(error)
        else:
            seq_item = SequencerTreeItem(str(seq))
            self.TrStructure.addTopLevelItem(seq_item)
            self.saved[0] = False
            self.ChangeTabTitle(auxleds, self.tabWidget.currentIndex())
            self.CBAuxList.addItem(seq_name)  # add sequencer to aux section on profile tab
            self.CBSeqList.addItem(seq_name)  # add sequencer to copy sequencer section
            self.BtnCopySeq.setEnabled(True)
            self.TrStructure.setCurrentItem(seq_item)
            self.TreeItemChanged(seq_item)

    def StepControlsDisable(self):
        """
        disable all step controls
        :return:
        """
        self.TxtStepName.setEnabled(False)
        self.SpinWait.setEnabled(False)
        self.SpinSmooth.setEnabled(False)
        self.BtnAddStep.setEnabled(False)
        self.BtnDeleteStep.setEnabled(False)
        self.BtnEditStep.setEnabled(False)
        self.BtnEditRepeat.setEnabled(False)
        for brightness in self.step_leds_brightnesses:
            brightness.setEnabled(False)
        for channel in self.step_channels:
            channel.setEnabled(False)

    def RepeatControlDisable(self):
        """
        disables all repeat controls
        :return:
        """
        self.CBStartrom.setEnabled(False)
        self.SpinCount.setEnabled(False)
        self.CBForever.setEnabled(False)
        self.BtnAddRepeat.setEnabled(False)
        self.BtnDeleteRepeat.setEnabled(False)

    def StepControlsEnable(self):
        """
        enable step controls, enable only used in tis sequencer led group led brightness and channels
        :return:
        """
        self.TxtStepName.setEnabled(True)
        self.SpinWait.setEnabled(True)
        self.SpinSmooth.setEnabled(True)
        self.BtnAddStep.setEnabled(True)
        self.TxtNewName.setEnabled(True)
        # get leds for tis sequencer led group and enable its brightnesses and channels
        current = self.TrStructure.currentItem()
        if isinstance(current, SequencerTreeItem):
            leds_list = self.auxdata.get_led_list(current.text(0))
        else:
            leds_list = self.auxdata.get_led_list(current.parent().text(0))

        for brightness in self.step_brightness_dict.keys():
            if brightness in leds_list:
                self.step_brightness_dict[brightness].setEnabled(True)
            else:
                self.step_brightness_dict[brightness].setEnabled(False)
        for channel in self.step_channels_dict.keys():
            if channel in leds_list:
                self.step_channels_dict[channel].setEnabled(True)
            else:
                self.step_channels_dict[channel].setEnabled(False)

    def RepeatControlsEnable(self):
        """
        enable repeat controls
        :return:
        """
        if self.CBStartrom.count() > 0:
            self.CBStartrom.setEnabled(True)
            self.SpinCount.setEnabled(True)
            self.BtnAddRepeat.setEnabled(True)
            self.CBForever.setEnabled(True)
        else:
            self.RepeatControlDisable()

    def ClearStepControls(self):
        """
        load new data for step controls
        :return:
        """
        current = self.TrStructure.currentItem()
        if current:
            if isinstance(current, SequencerTreeItem):
                seq = self.auxdata.get_seq_by_name(Sequencer.get_name(current.text(0)))
            else:
                seq = self.auxdata.get_seq_by_name(Sequencer.get_name(current.parent().text(0)))

            max_step = seq.get_max_step_number()
            self.TxtStepName.setText("Step" + str(max_step+1))
            self.CBStartrom.clear()
            self.CBStartrom.addItems(seq.get_steps_names())
        else:
            self.TxtStepName.clear()
        for led in self.step_leds_brightnesses:
            led.setValue(0)
        for channel in self.step_channels:
            channel.setCurrentIndex(0)
        self.SpinWait.setValue(0)
        self.SpinSmooth.setValue(0)

    def ClearRepeatControls(self):
        """
        clears repeat controls
        :return:
        """
        self.CBForever.setChecked(False)
        self.CBStartrom.setCurrentIndex(0)
        self.SpinCount.setValue(0)
        self.CBStartrom.clear()
        current = self.TrStructure.currentItem()
        if current:
            if isinstance(current, SequencerTreeItem):
                seq = self.auxdata.get_seq_by_name(Sequencer.get_name(current.text(0)))
            elif isinstance(current, StepTreeItem) or isinstance(current, RepeatTreeItem):
                seq = self.auxdata.get_seq_by_name(Sequencer.get_name(current.parent().text(0)))
            steps_used = seq.get_steps_names()
            self.CBStartrom.addItems(steps_used)

    def LoadStepControls(self):
        """
        load data for selected step
        :return:
        """
        current = self.TrStructure.currentItem()
        name = Step.get_name(current.text(0))
        self.TxtNewName.setText(name)
        parent = current.parent()
        seq_descr = parent.text(0)
        seq = self.auxdata.get_seq_by_name(Sequencer.get_name(seq_descr))
        self.TxtStepName.setText("Step"+str(seq.get_max_step_number()+1))
        index = self.GetItemId(current)
        brightnesses, wait, smooth = self.auxdata.get_step_info(parent.text(0), index)
        self.SpinWait.setValue(wait)
        self.SpinSmooth.setValue(smooth)
        leds = self.auxdata.get_led_list(parent.text(0))
        for i in range(len(leds)):
            if isinstance(brightnesses[i], int):
                self.step_brightness_dict[leds[i]].setValue(brightnesses[i])
                self.step_channels_dict[leds[i]].setCurrentText('None')
            else:
                self.step_channels_dict[leds[i]].setCurrentText(Mediator.get_color_text(brightnesses[i]))
        for led in Mediator.leds_list:
            if led not in leds:
                self.step_channels_dict[led].setCurrentText('None')
                self.step_brightness_dict[led].setValue(0)

    def LoadRepeatControls(self):
        """
        load data for selected repeat
        :return:
        """
        current = self.TrStructure.currentItem()
        id = self.GetItemId(current)
        repeat_info = self.auxdata.get_repeat_info(current.parent().text(0), id)
        if repeat_info:
            self.CBStartrom.setCurrentText(repeat_info[0])
            if isinstance(repeat_info[1], str) and repeat_info[1].lower() == 'forever':
                self.CBForever.setChecked(True)
            elif isinstance(repeat_info[1], int):
                self.CBForever.setChecked(False)
                self.SpinCount.setValue(int(repeat_info[1]))
            else:
                self.ErrorMessage("Wrong repeat count")

    def TreeItemChanged(self, current):
        self.BtnAddStep.setEnabled(False)  # for not top-level items sequencer and leds are not available
        if isinstance(current, SequencerTreeItem):
            self.ClearStepControls()
            self.ClearRepeatControls()
            self.StepControlsEnable()
            self.RepeatControlsEnable()
            self.BtnDeleteSeq.setEnabled(True)
            self.BtnDeleteStep.setEnabled(False)
            self.BtnEditStep.setEnabled(False)
        if isinstance(current, StepTreeItem):
            self.BtnDeleteStep.setEnabled(True)
            self.BtnDeleteSeq.setEnabled(False)
            self.LoadStepControls()
            self.ClearRepeatControls()
            self.BtnEditStep.setEnabled(True)
            self.StepControlsEnable()
            self.RepeatControlsEnable()
            self.BtnEditRepeat.setEnabled(False)
            self.BtnDeleteRepeat.setEnabled(False)
        if isinstance(current, RepeatTreeItem):
            self.ClearStepControls()
            self.StepControlsEnable()
            self.RepeatControlsEnable()
            self.LoadRepeatControls()
            self.BtnEditStep.setEnabled(False)
            self.BtnDeleteStep.setEnabled(False)
            self.BtnEditRepeat.setEnabled(True)
            self.BtnDeleteRepeat.setEnabled(True)

    def GetItemId(self, item):
        parent = self.TrStructure.invisibleRootItem() if type(item) == SequencerTreeItem else item.parent()
        for i in range(parent.childCount()):
            if parent.child(i) == item:
                return i

    def AddStep(self):
        current = self.TrStructure.currentItem()
        name = self.TxtStepName.text()
        brightnesses = list()
        # for led in Mediator.leds_list:
        #     if self.step_channels_dict[led].isEnabled() and self.step_channels_dict[led].currentIndex() != 0:
        #         brightnesses.append(self.step_channels_dict[led].currentText())
        #     elif self.step_brightness_dict[led].isEnabled():
        #         brightnesses.append(self.step_brightness_dict[led].value())
        # wait = self.SpinWait.value()
        # smooth = self.SpinSmooth.value()
        if isinstance(current, SequencerTreeItem):
            seq_name = current.text(0)
            for i in range(len(self.auxdata.get_group_by_name(self.auxdata.get_seq_by_name(Sequencer.get_name(seq_name)).Group).Leds)):
                brightnesses.append(0)
            step, error = self.auxdata.create_step(seq_name, -1, name, brightnesses, 0, 0)
        else:
            seq_name = current.parent().text(0)
            index = self.GetItemId(current)
            for i in range(len(self.auxdata.get_group_by_name(self.auxdata.get_seq_by_name(Sequencer.get_name(seq_name)).Group).Leds)):
                brightnesses.append(0)
            step, error = self.auxdata.create_step(seq_name, index, name, brightnesses, 0, 0)
        if error:
            self.ErrorMessage(error)
            return
        step_item = StepTreeItem(str(step))
        if isinstance(current, SequencerTreeItem):
            current.addChild(step_item)
        else:
            current.parent().insertChild(index+1, step_item)
        self.saved[0] = False
        self.ChangeTabTitle(auxleds, self.tabWidget.currentIndex())
        self.TrStructure.expandItem(current)
        if name:
            self.CBStartrom.addItem(name)
            self.BtnAddRepeat.setEnabled(True)
            self.CBStartrom.setEnabled(True)
            self.SpinCount.setEnabled(True)
            self.CBForever.setEnabled(True)
        self.TrStructure.setCurrentItem(step_item)
        self.TreeItemChanged(step_item)

    def EditStep(self):
        """
        edit step in data
        :return:
        """
        current = self.TrStructure.currentItem()
        seq_name = current.parent().text(0)
        name = self.TxtNewName.text()
        brightnesses = list()
        for led in Mediator.leds_list:
            if self.step_channels_dict[led].isEnabled() and self.step_channels_dict[led].currentIndex() != 0:
                brightnesses.append(self.step_channels_dict[led].currentText())
            elif self.step_brightness_dict[led].isEnabled():
                brightnesses.append(self.step_brightness_dict[led].value())
        wait = self.SpinWait.value()
        smooth = self.SpinSmooth.value()
        id = self.GetItemId(current)
        step, old_step, changed = self.auxdata.update_step(seq_name, id, name, brightnesses, wait, smooth)
        if old_step:
            # to do update repeat steps
            self.CBStartrom.clear()
            seq = self.auxdata.get_seq_by_name(Sequencer.get_name(seq_name))
            step_names = seq.get_steps_names()
            for name in step_names:
                self.CBStartrom.addItem(name)
        # edit item in tree
        current.setText(0, str(step))
        # update repeat items
        for i in changed:
            item = current.parent().child(i)
            current_text: str = item.text(0)
            item.setText(0, current_text.replace(old_step, self.TxtStepName.text()))
        # profile is not saved now
        self.saved[0] = False
        self.ChangeTabTitle(auxleds, 0)

    def AddRepeatStep(self):
        current = self.TrStructure.currentItem()
        startstep: str = self.CBStartrom.currentText()
        if self.CBForever.isChecked():
            count: Union[str, int] = 'forever'
        else:
            count = self.SpinCount.value()
        if isinstance(current, SequencerTreeItem):
            repeat, error = self.auxdata.add_repeat(current.text(0), -1, startstep, count)
        else:
            parent = current.parent()
            id = self.GetItemId(current)
            repeat, error = self.auxdata.add_repeat(parent.text(0), id, startstep, count)
        if error:
            self.ErrorMessage(error)
        else:
            repeat_item = RepeatTreeItem(str(repeat))
            if isinstance(current, SequencerTreeItem):
                current.addChild(repeat_item)
            else:
                current.parent().insertChild(id+1, repeat_item)
            self.TrStructure.setCurrentItem(repeat_item)
            self.TreeItemChanged(repeat_item)
            self.saved[0] = False
            self.ChangeTabTitle(auxleds, self.tabWidget.currentIndex())


    def EditRepeater(self):
        """
        update gui and data for repeater
        :return:
        """
        current = self.TrStructure.currentItem()
        seq_name: str = current.parent().text(0)
        id = self.GetItemId(current)
        new_start = self.CBStartrom.currentText()
        if self.CBForever.isChecked():
            new_count = 'Forever'
        else:
            new_count = self.SpinCount.value()
        repeat, error = self.auxdata.update_repeat(seq_name, id, new_start, new_count)
        if error:
            self.ErrorMessage(error)
            return
        current.setText(0, str(repeat))
        self.saved[0] = False
        self.ChangeTabTitle(auxleds, 0)

    def DeleteItem(self):
        current = self.TrStructure.currentItem()
        current_name = current.text(0)
        if current.childCount() > 0:
            reply = QMessageBox.question(self, 'Message', "This sequencer has steps, do you really want to delete it?",
                                         QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        self.ChangeTabTitle(auxleds, self.tabWidget.currentIndex())
        if isinstance(current, SequencerTreeItem):
            parent = self.TrStructure.invisibleRootItem()
            parent.removeChild(current)
            self.auxdata.delete_sequence(current_name)
            #delete seq from copy sequncer block and aux block in profile tab
            self.CBSeqList.clear()
            self.CBAuxList.clear()
            for sequencer in self.auxdata.Sequencers:
                self.CBSeqList.addItem(sequencer.Name)
                self.CBAuxList.addItem(sequencer.Name)
            if self.CBSeqList.count() == 0:
                self.BtnCopySeq.setEnabled(False)
            self.ClearStepControls()
            self.StepControlsDisable()
            self.RepeatControlDisable()

        if isinstance(current, StepTreeItem):
            index = self.GetItemId(current)
            parent = current.parent()
            seq_name = parent.text(0)
            step_name = Step.get_name(current_name)

            seq = self.auxdata.get_seq_by_name(Sequencer.get_name(seq_name))
            used_repeat_steps = seq.get_repeat_steps_names()
            if step_name in used_repeat_steps:
                self.ErrorMessage("This step is used in repeat step, first delete repeat step")
                return
            self.auxdata.delete_step(current_name, seq_name)
            parent.removeChild(current)
            #reload steps for repeat
            used_steps = seq.get_steps_names()
            if not used_steps:
                self.CBForever.setEnabled(False)
                self.CBStartrom.setEnabled(False)
                self.SpinCount.setEnabled(False)
                self.BtnAddRepeat.setEnabled(False)
            else:
                self.CBStartrom.clear()
                for step in used_steps:
                    self.CBStartrom.addItem(step)
        if isinstance(current, RepeatTreeItem):
            parent: SequencerTreeItem = current.parent()
            seq_name: str = parent.text(0)
            index = self.GetItemId(current)
            error = self.auxdata.delete_repeat(seq_name, index)
            if error:
                self.ErrorMessage(error)
                return
            parent.removeChild(current)
        # select next step if any, or previous, or none if there are no steps
        if not isinstance(current, SequencerTreeItem):
            if index < parent.childCount():
                self.TrStructure.setCurrentItem(parent.child(index))
                self.TreeItemChanged(self.TrStructure.currentItem())
            elif parent.childCount() > 0:
                self.TrStructure.setCurrentItem(parent.child(index - 1))
            else:
                # disable step controls
                self.ClearStepControls()
                self.ClearRepeatControls()
                self.StepControlsDisable()
                self.RepeatControlDisable()
                self.BtnEditStep.setEnabled(False)
                self.BtnEditRepeat.setEnabled(False)
                self.BtnDeleteRepeat.setEnabled(False)
        # data is unsaved now
        self.saved[0] = False
        self.ChangeTabTitle(auxleds, self.tabWidget.currentIndex())

    def CopySequencer(self):

        """
        Adds new Sequencer with steps of selected to gui and data
        :return:
        """
        seq_name = self.TxtSeqName.text()
        group_name = self.CBGroup.currentText()
        seq, error = self.auxdata.create_sequence(group_name, seq_name)
        if not seq:
            self.ErrorMessage(error)
        else:
            seq_item = SequencerTreeItem(str(seq))
            self.TrStructure.addTopLevelItem(seq_item)
            seq_old = self.auxdata.get_seq_by_name(self.CBSeqList.currentText())
            for step in seq_old.Sequence:
                if (isinstance(step, Step)):
                    self.auxdata.create_step(str(seq), -1, step.Name, step.Brightness, step.Smooth, step.Wait)
                    step_item = StepTreeItem(str(step))
                    seq_item.addChild(step_item)
                elif (isinstance(step, Repeater)):
                    self.auxdata.add_repeat(str(seq), -1,  step.StartingFrom, step.Count)
                    step_item = RepeatTreeItem(str(step))
                    seq_item.addChild(step_item)

            self.saved[0] = False
            self.ChangeTabTitle(auxleds, self.tabWidget.currentIndex())
            self.CBAuxList.addItem(seq_name)  # add sequencer to aux section on profile tab
            self.CBSeqList.addItem(seq_name)  # add sequencer to copy sequencer section

    def LoadDataToTree(self):
        self.TrStructure.clear()
        self.LstGroup.clear()
        self.CBStartrom.clear()
        self.CBAuxList.clear()
        self.CBSeqList.clear()
        self.CBGroup.clear()
        for group in self.auxdata.LedGroups:
            self.LstGroup.addItem(str(group))
            self.CBGroup.addItem(group.Name)
        for seq in self.auxdata.Sequencers:
            item = SequencerTreeItem(str(seq))
            self.TrStructure.addTopLevelItem(item)
            self.CBAuxList.addItem(seq.get_name(str(seq)))
            self.CBSeqList.addItem(seq.get_name(str(seq)))
            for step in seq.Sequence:
                if isinstance(step, Step):
                    step_item = StepTreeItem(str(step))
                    item.addChild(step_item)
                elif isinstance(step, Repeater):
                    step_item = RepeatTreeItem(str(step))
                    item.addChild(step_item)
        self.ClearStepControls()
        self.ClearRepeatControls()
        self.RepeatControlDisable()
        self.StepControlsDisable()
        # self.SequenceControlsDisable()
        self.TxtSeqName.clear()
        self.GroupControlsClear()
        if self.CBSeqList.count() > 0:
            self.BtnCopySeq.setEnabled(True)

    # common tab part
    ####################################################################################################################
    def CBClicked(self):
        CB = self.sender()
        if CB in self.common_dict.keys():
            key_list = self.common_dict[CB]
        else:
            key_list = self.motion_dict[CB]
        if CB.isChecked():
            self.commondata.update_value(key_list, 1)
        else:
            self.commondata.update_value(key_list, 0)
        if self.saved[1]:
            self.saved[1] = False
            self.ChangeTabTitle(common, self.tabWidget.currentIndex())
        self.BtnSave.setEnabled(True)
        self.BtnDefault.setEnabled(True)

    def SpinChanged(self):
        Spin = self.sender()
        if Spin in self.common_dict.keys():
            key_list = Mediator.change_keylist(self.common_dict[Spin])
        else:
            key_list = self.motion_dict[Spin]
        self.commondata.update_value(key_list, Spin.value())
        if self.saved[1]:
            self.saved[1] = False
            self.ChangeTabTitle(common, 1)
        self.BtnSave.setEnabled(True)
        self.BtnDefault.setEnabled(True)

    def SetDefaultCommon(self):
        for key in self.common_dict.keys():
            value = self.commondata.get_default_value(Mediator.change_keylist(self.common_dict[key]))
            if key == self.CBBlade2Enabled:
                key.setChecked(value)
            else:
                key.setValue(value)
        for key in self.motion_dict.keys():
            value = self.commondata.get_default_value(Mediator.change_keylist(self.motion_dict[key]))
            if key in [self.CBStabEnabled, self.CBScrewEnabled, self.CBSpinEnabled]:
                key.setChecked(value)
            else:
                key.setValue(value)

    def LoadCommonData(self, data):
        try:
            for key in self.common_dict.keys():
                path = Mediator.change_keylist(self.common_dict[key])
                value = data
                for path_key in path:
                    value = value[path_key]
                if key == self.CBBlade2Enabled:
                    key.setChecked(value)
                else:
                    key.setValue(value)
            for key in self.motion_dict.keys():
                path = Mediator.change_keylist(self.motion_dict[key])
                value = data
                for path_key in path:
                    value = value[path_key]
                if key in [self.CBStabEnabled, self.CBScrewEnabled, self.CBSpinEnabled]:
                    key.setChecked(value)
                else:
                    key.setValue(value)
            self.CBBlade2Enabled.setChecked(data[Mediator.blade2_key[0]]['Enabled'])
        except Exception:
            e = sys.exc_info()[1]
            self.ErrorMessage(e.args[0])

    def Blade2Clicked(self):
        """
        writes 0 or 1 to corresponding data field
        :return:
        """
        if self.CBBlade2Enabled.isChecked():
            self.commondata.update_value(Mediator.blade2_enabled_keys, 1)
            self.SpinPixPerBand2.setEnabled(True)
            self.SpinBandNumber.setEnabled(True)
        else:
            self.commondata.update_value(Mediator.blade2_enabled_keys, 0)
            self.SpinPixPerBand2.setEnabled(False)
            self.SpinBandNumber.setEnabled(False)
        self.saved[1] = False
        self.ChangeTabTitle(common, 1)

    # profiles tab
    ###################################################################################################################
    def EffectTabChanged(self):
        """
        changes group and button label for auxleds group when tab changes
        :return:
        """
        current = self.TabEffects.currentIndex()
        text = self.TabEffects.tabText(current)
        self.GBAuxLeds.setTitle("Select AuxLeds Effects for %s Effect" % text)
        self.BtnCReateAux.setText("Add effect to %s" % text)
        # load data or current tab if profile is selected
        if self.BtnCReateAux.isEnabled():
            profile = self.LstProfile.currentItem().text()
            auxeffects = self.profiledata.get_aux_effects(text, profile)
            self.LstAuxProfile.clear()
            for aux in auxeffects:
                self.LstAuxProfile.addItem(aux)

    def MinChanged(self, min_control):
        """
        when min data changes corresponding max border changes too
        :param min_control: control that changes
        :return:
        """
        max_control = self.min_max_dict[min_control]
        max_control.setMinimum(min_control.value())

    def MaxChanged(self, max_control):
        """
        when max data changes corresponding min border changes too
        :param max_control: control that changes
        :return:
        """
        min_control = self.max_min_dict[max_control]
        min_control.setMaximum(max_control.value())

    def ProfileNameChanged(self, name):
        """
        if text in profile field changed and this name is not used yet and it is valid make add profile button enabled
        :param name:
        :return:
        """
        effects = self.profiledata.get_profiles_list()
        has_symbol = any([ch.isalpha() for ch in name])
        valid = all(ch.isalpha() or ch.isdigit() or ch == "_" for ch in name)
        enabled = True if name and name not in effects and valid and has_symbol else False
        self.BtnProfile.setEnabled(enabled)
        self.BtnEditProfile.setEnabled(enabled)

    def AddProfile(self):
        """
        adds new profile with current name to Profile List and profile data
        :return:
        """
        name = self.TxtAddProfile.text()
        self.profiledata.add_profile(name)
        self.BtnProfile.setEnabled(False)
        self.LstProfile.addItem(name)
        # data is unsaved now
        self.saved[2] = False
        self.ChangeTabTitle(profiletab, self.tabWidget.currentIndex())

    def ProfileCBClicked(self):
        """
        any check box in profile controls clicked. we get key path for it and save to data to current profile
        (checked = 1, otherwise 0)
        :return:
        """
        CB = self.sender()
        if CB.isEnabled():
            key_list = self.profile_dict[CB]
            profile = self.LstProfile.currentItem().text()
            if CB.isChecked():
                self.profiledata.update_value(key_list, profile, 1)
                # disable coupled checkbox
                self.CB_single_dict[CB].setEnabled(False)
            else:
                self.profiledata.update_value(key_list, profile, 0)
                # enable coupled checkbox
                self.CB_single_dict[CB].setEnabled(True)
            # data now is unsaved
            if self.saved[2]:
                self.saved[2] = False
                self.ChangeTabTitle(profiletab, self.tabWidget.currentIndex())

    def LoadProfileControls(self, profile):
        """
        enables all neeeded controls for selected profile
        load data for selected profile to profile controls (Main Blade section)
        :param profile:
        :return:
        """
        # enable all control for all tabs
        for key in self.control_tab_dict.keys():
            for control in self.control_tab_dict[key]:
                control.setEnabled(True)
        for key in self.color_dict.keys():
            key.setEnabled(True)
        self.BtnAddColor.setEnabled(True)
        self.CBBlade.setEnabled(True)
        #aux block enable
        self.TxtCreateAux.setEnabled(True)
        self.BtnCReateAux.setEnabled(True)
        self.CBAuxList.setEnabled(True)

        # loads data for main blade
        for control in self.profile_dict.keys():
            value = self.profiledata.get_value(self.profile_dict[control], profile)
            # Combo Box
            if control in self.CB_list:
                control.setChecked(value)
            else:
                # color text
                if control in self.color_list:
                    text = Mediator.color_data_to_str(value)
                    control.setText(text)
                else:
                    # spin box
                    control.setValue(value)

        # controls under Blade selection loaded
        value = self.profiledata.get_value(Mediator.indicate_path, profile)
        self.CBIndicate.setChecked(value)
        value = self.profiledata.get_value(Mediator.delay_path, profile)
        self.SpinDelayBeforeOn.setValue(value)

        # flaming colors lis loaded
        self.LstFlamingColor.clear()
        flaming_colors = self.profiledata.get_colors(Mediator.flaming_color_path, self.LstProfile.currentItem().text())
        for color in flaming_colors:
            item = Mediator.color_data_to_str(color)
            self.LstFlamingColor.addItem(item)

        #auxleds section
        index = self.TabEffects.currentIndex()
        effect = self.TabEffects.tabText(index)
        auxeffects = self.profiledata.get_aux_effects(effect, profile)
        self.LstAuxProfile.clear()
        for aux in auxeffects:
            self.LstAuxProfile.addItem(aux)

        # you may delete profile now
        self.BtnDeleteProfile.setEnabled(True)

    def ProfileClicked(self, item):
        """
        profile item in Profile List clicked. All neseccary data loaded, controls enabled
        :param item:
        :return:
        """
        profile = item.text()
        print(profile)
        self.CBBlade.setCurrentIndex(0)
        self.LoadProfileControls(profile)
        i = self.LstProfile.currentRow()
        print(i)
        enabled = True if i > 0 else False
        self.BtnUp.setEnabled(enabled)
        enabled = True if (i < self.LstProfile.count() - 1) else False
        self.BtnDown.setEnabled(enabled)
        has_symbol = any([s.isalpha() for s in self.TxtAddProfile.text()])
        valid = all(s.isalpha() or s.isdigit() or s == "_" for s in self.TxtAddProfile.text())
        if valid and has_symbol and self.TxtAddProfile.text() != "" and self.TxtAddProfile.text() not in self.profiledata.get_profiles_list():
            self.BtnEditProfile.setEnabled(True)

    def DeleteProfile(self):
        """
        delete profile from data and UI with question, disables delete button, loads default data to all controls
        :return:
        """
        name = self.LstProfile.currentItem().text()
        # warning message
        reply = QMessageBox.question(self, 'Message', "Do you realy want to delete this profile?",
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.profiledata.delete_profile(name)
            self.LstProfile.clear()
            for profile in self.profiledata.get_profiles_list():
                self.LstProfile.addItem(profile)
            self.ProfileControlsDisable()
            #file is unsaved now
            self.saved[2] = False
            self.ChangeTabTitle(profiletab, self.tabWidget.currentIndex())

    def ProfileControlsDisable(self):
        """
        desables and loads default for all profile controls
        :return:
        """
        self.BtnDeleteProfile.setEnabled(False)

        # disable all profile controls
        for key in self.control_tab_dict.keys():
            for control in self.control_tab_dict[key]:
                control.setEnabled(False)
        for key in self.color_dict.keys():
            key.setEnabled(False)
        self.BtnAddColor.setEnabled(False)
        self.CBBlade.setEnabled(False)
        self.SpinDelayBeforeOn.setEnabled(False)
        self.CBIndicate.setEnabled(False)
        # and auxleds group
        self.BtnAuxDelete.setEnabled(False)
        self.BtnCReateAux.setEnabled(False)
        self.CBAuxList.setEnabled(False)
        self.TxtCreateAux.setEnabled(False)

        # load default data
        for key in self.profile_dict.keys():
            value = self.profiledata.get_default(self.profile_dict[key])
            if key in self.CB_list:
                key.setChecked(value)
            else:
                if key in self.color_list:
                    text = Mediator.color_data_to_str(value)
                    key.setText(text)
                else:
                    key.setValue(value)
        self.LstFlamingColor.clear()
        value = self.profiledata.get_default(Mediator.indicate_path)
        self.CBIndicate.setChecked(value)
        value = self.profiledata.get_default(Mediator.delay_path)
        self.SpinDelayBeforeOn.setValue(value)
        self.TxtAddProfile.clear()
        self.BtnEditProfile.setEnabled(False)
        self.BtnUp.setEnabled(False)
        self.BtnDown.setEnabled(False)

    def ProfileSpinChanged(self):
        """
        saves new value of any profile spin control to corresponding data using path of keys, changes min/max controls
        borders if nesessary
        :return:
        """
        spin = self.sender()
        if spin.isEnabled():
            blade = self.CBBlade.currentIndex()
            key_list = self.profile_dict[spin]
            # for second blade Blade2 key added to key path
            if blade == 1:
                key_list = Mediator.blade2_key + key_list
            text = self.LstProfile.currentItem().text()
            self.profiledata.update_value(key_list, text, spin.value())
            # data may be unsaved now
            if self.saved[2]:
                self.saved[2] = False
                self.ChangeTabTitle(profiletab, self.tabWidget.currentIndex())
            # update min and max controls
            if spin in self.min_max_dict.keys():
                self.MinChanged(spin)
            if spin in self.max_min_dict.keys():
                self.MaxChanged(spin)

    def ProfileTextChanged(self):
        """
        saves data if text changed
        :return:
        """
        text = self.sender()
        label = text.text()
        label = Mediator.str_to_color_data(label)
        # not save id control is disabled (may occur when we load default settings if no profile is selected
        if text.isEnabled():
            if label:
                key_list = self.profile_dict[text]
                # add blade2 key to path for second blade
                blade = self.CBBlade.currentIndex()
                if blade == 1:
                    key_list = Mediator.blade2_key + key_list
                profile = self.LstProfile.currentItem().text()
                self.profiledata.update_value(key_list, profile, label)
                #profile is not saved now
                if self.saved[2]:
                    self.saved[2] = False
                    self.ChangeTabTitle(profiletab, self.tabWidget.currentIndex())
        color_widget = self.selected_color_dict[text]
        color_widget.setAutoFillBackground(True)
        if label != 'random':
            try:
                color = QtGui.QColor(label[0], label[1], label[2])
            except IndexError:
                color = QtGui.QColor(215, 215, 215)
        else:
            color = QtGui.QColor(215, 215, 215)
        color_widget.setStyleSheet("QWidget { background-color: %s }" % color.name())

    def ProfileEditPressed(self):
        """
        edit profile name
        :return:
        """
        result, i = self.profiledata.change_key_order(self.LstProfile.currentItem().text(), self.TxtAddProfile.text())
        if result != "":
            self.ErrorMessage(result)
        else:
            self.LoadProfileList()
            self.LstProfile.setCurrentRow(i)
            self.ProfileClicked(self.LstProfile.currentItem())

    def ColorChanged(self):
        """
        adds new color selected with color dialog to control
        :return:
        """
        color_button = self.sender()
        color_input = self.color_dict[color_button]
        color_data = palitra.ColorDialog.getColor()
        if color_data[1]:
            color_input.setText(color_data[0][0])
            color_widget = self.selected_color_dict[color_input]
            color_widget.setAutoFillBackground(True)
            rgb_shifted = ",".join(str(color) for color in color_data[0][1])
            color_widget.setStyleSheet("QWidget { background-color: rgb(%s); }" % rgb_shifted)

        # color = QtWidgets.QColorDialog.getColor()
        # if color.isValid():
        #     rgb = [color.red(), color.green(), color.blue()]
        #     color_text = Mediator.color_data_to_str(rgb)
        #     color_input = self.color_dict[color_button]
        #     color_input.setText(color_text)

    def AddColor(self):
        """
        adds color to flaming color list and saves color data to profile
        :return:
        """
        color_data = palitra.ColorDialog.getColor()
        if color_data[1]:
            self.LstFlamingColor.addItem(color_data[0][0])
            # save to profile adding Blade2 key if Blade2 selected
            profile = self.LstProfile.currentItem().text()
            path = Mediator.flaming_color_path
            index = self.CBBlade.currentIndex()
            if index == 1:
                path = Mediator.blade2_key + path
            rgb = list(map(int, color_data[0][0].split(', ')))
            self.profiledata.save_color(path, rgb, profile)
        #profile is unsaved now
        self.saved[2] = False
        self.ChangeTabTitle(profiletab, self.tabWidget.currentIndex())

    def ColorClicked(self):
        """
        if any color selected we may delete it
        :return:
        """
        self.BtnDeleteColor.setEnabled(True)

    def DeleteColor(self):
        current_color = self.LstFlamingColor.currentItem().text()
        current_index = self.LstFlamingColor.currentIndex()
        current_color = Mediator.str_to_color_data(current_color)
        path = Mediator.flaming_color_path
        index = self.CBBlade.currentIndex()
        if index == 1:
            path = Mediator.blade2_key + path
        self.profiledata.delete_color(path, current_color, self.LstProfile.currentItem().text())
        self.LstFlamingColor.clear()
        flaming_colors = self.profiledata.get_colors(path, self.LstProfile.currentItem().text())
        for color in flaming_colors:
            item = Mediator.color_data_to_str(color)
            self.LstFlamingColor.addItem(item)
        self.saved[2] = False
        self.ChangeTabTitle(profiletab, self.tabWidget.currentIndex())
        #select next color (previous if the color is last) or disable delete button if there are no colors
        count = self.LstFlamingColor.count()
        if current_index.row() < count:
            self.LstFlamingColor.setCurrentIndex(current_index)
        elif count > 0:
            self.LstFlamingColor.setCurrentRow(current_index.row()-1)
        else:
            self.BtnDeleteColor.setEnabled(False)

    def BladeChanged(self, index):
        """
        enable necessary controls for selected blade and disable unnecessary and loads data
        :param index: index of blade
        :return:
        """
        profile = self.LstProfile.currentItem().text()
        if index == 0:
            # main blade
            # all tabs enabled
            self.TabPowerOn.setEnabled(True)
            self.TabPowerOff.setEnabled(True)
            self.TabClash.setEnabled(True)
            self.TabStab.setEnabled(True)
            self.TabLockup.setEnabled(True)
            self.TabBlaster.setEnabled(True)
            # enables and loads all tab controls for main blade
            self.LoadProfileControls(profile)
            # disable extra blade2 comboboxes
            self.CBFlickeringAlwaysOn.setEnabled(False)
            self.CBFlamingAlwaysOn.setEnabled(False)
            # disables controls for blade2
            self.CBIndicate.setEnabled(False)
            self.SpinDelayBeforeOn.setEnabled(False)
        else:
            # blade2
            # disables unused tabs
            self.TabPowerOn.setEnabled(False)
            self.TabPowerOff.setEnabled(False)
            self.TabClash.setEnabled(False)
            self.TabStab.setEnabled(False)
            self.TabLockup.setEnabled(False)
            self.TabBlaster.setEnabled(False)
            # enables special Blade2 Comboboxes
            self.CBFlamingAlwaysOn.setEnabled(True)
            self.CBFlickeringAlwaysOn.setEnabled(True)
            # enables blade2 settings
            self.CBIndicate.setEnabled(True)
            self.SpinDelayBeforeOn.setEnabled(True)
            # disables AuxEffects section
            self.BtnCReateAux.setEnabled(False)
            self.TxtCreateAux.setEnabled(False)
            self.CBAuxList.setEnabled(False)
            self.BtnAuxDelete.setEnabled(False)
            self.LstAuxProfile.clear()
            # disable unused comboboxes
            self.CBFlaming.setEnabled(False)
            self.CBFlickering.setEnabled(False)
            # load data for blade2
            self.LoadBlade2Controls()

    def LoadBlade2Controls(self):
        """
        loads data for blade2 for selected profile
        :return:
        """
        # all paths must start with Mediator.blade2_keys.
        # Done automatically for self.extra_blade_CB and self.spinDelayBeforeOn
        profile = self.LstProfile.currentItem().text()
        # flickering and flaming tabs
        controls = self.flickering + self.flaming
        for spin in controls:
            path = self.profile_dict[spin]
            path = Mediator.blade2_key + path
            value = self.profiledata.get_value(path, profile)
            spin.setValue(value)
        # color for working mode
        path = self.profile_dict[self.TxtWorkingColor]
        color = self.profiledata.get_value(Mediator.blade2_key + path, profile)
        text = Mediator.color_data_to_str(color)
        self.TxtWorkingColor.setText(text)
        # extrs Blade2 comboboxes
        for CB in self.extra_blade_CB_dict.keys():
            value = self.profiledata.get_value(self.extra_blade_CB_dict[CB], profile)
            CB.setChecked(value)
        # dalay before blade2
        delay = self.profiledata.get_value(Mediator.delay_path, profile)
        self.SpinDelayBeforeOn.setValue(delay)
        # flaming colors fpr blade2
        self.LstFlamingColor.clear()
        flaming_colors = self.profiledata.get_colors(Mediator.blade2_key + Mediator.flaming_color_path, self.LstProfile.currentItem().text())
        for color in flaming_colors:
            item = Mediator.color_data_to_str(color)
            self.LstFlamingColor.addItem(item)

    def ExtraBladeCBlicked(self):
        """
        handlers for extra comboboxes for blade2, saves to profile data
        :return:
        """
        CB = self.sender()
        path = self.extra_blade_CB_dict[CB]
        profile = self.LstProfile.currentItem().text()
        if CB.isChecked():
            value = 1
            #disable coupled checkbox
            self.CB_single_dict[CB].setEnabled(False)
        else:
            value = 0
            #enable coupled checkbox
            self.CB_single_dict[CB].setEnabled(True)
        #data is unsaved now
        self.profiledata.update_value(path, profile, value)
        self.saved[2] = False

    def DelayChanged(self):
        """
        delay before handler, saves to profile data
        :return:
        """
        if self.SpinDelayBeforeOn.isEnabled():
            path = Mediator.delay_path
            value = self.SpinDelayBeforeOn.value()
            profile = self.LstProfile.currentItem().text()
            self.profiledata.update_value(path, profile, value)

    def ProfileAddAux(self):
        """
        adds aux effect from test field if it is correcty filled or from auxlist
        :return:
        """
        current = self.TabEffects.currentIndex()
        effect = self.TabEffects.tabText(current)
        profile = self.LstProfile.currentItem().text()
        auxeffect = self.TxtCreateAux.text()
        valid = [ch.isalpha() or ch.isdigit() or ch == '_' for ch in auxeffect]
        existing = [seq.lower() for seq in self.profiledata.get_aux_effects(effect, profile)]
        if auxeffect != "" and all(valid) and auxeffect.lower() not in existing:
            self.LstAuxProfile.addItem(auxeffect)
            self.TxtCreateAux.clear()
            self.profiledata.save_aux(auxeffect, effect, profile)
        else:
            auxeffect = self.CBAuxList.currentText()
            groups_used = list()
            for sequencer in existing:
                seq = self.auxdata.get_seq_by_name(sequencer)
                if seq:
                    groups_used.append(seq.Group)
            group_selected = self.auxdata.get_seq_by_name(auxeffect).Group
            if group_selected.lower() in groups_used:
                self.ErrorMessage("Effect for this LED group already added")
                return
            if auxeffect and auxeffect.lower() not in existing:
                self.LstAuxProfile.addItem(auxeffect)
                self.profiledata.save_aux(auxeffect, effect, profile)
            else:
                self.ErrorMessage("Effect does not exiss or is already used")

    def AuxClicked(self):
        """
        button Delete AuxEffect activated
        :return:
        """
        self.BtnAuxDelete.setEnabled(True)

    def DeleteAux(self):
        """
        delete selected aux from UI and profile data for tos effect. AuxSetion is cleared if it was last effect
        :return:
        """
        current = self.LstAuxProfile.currentItem().text()
        current_tab = self.TabEffects.currentIndex()
        effect = self.TabEffects.tabText(current_tab)
        profile = self.LstProfile.currentItem().text()
        self.profiledata.delete_aux(current, effect, profile)
        auxeffects = self.profiledata.get_aux_effects(effect, profile)
        self.LstAuxProfile.clear()
        for aux in auxeffects:
            self.LstAuxProfile.addItem(aux)
        self.BtnAuxDelete.setEnabled(False)

    def LoadProfileList(self):
        """
        loads from data all profiles to list
        :return:
        """
        self.LstProfile.clear()
        for profile in self.profiledata.order:
            self.LstProfile.addItem(profile)
        self.BtnDeleteProfile.setEnabled(False)

        # disable all profile controls
        for key in self.control_tab_dict.keys():
            for control in self.control_tab_dict[key]:
                control.setEnabled(False)
        for key in self.color_dict.keys():
            key.setEnabled(False)
        self.BtnAddColor.setEnabled(False)
        self.CBBlade.setEnabled(False)
        self.SpinDelayBeforeOn.setEnabled(False)
        self.CBIndicate.setEnabled(False)
        # and auxleds group
        self.BtnAuxDelete.setEnabled(False)
        self.BtnCReateAux.setEnabled(False)
        self.CBAuxList.setEnabled(False)
        self.TxtCreateAux.setEnabled(False)

        # load default data
        for key in self.profile_dict.keys():
            value = self.profiledata.get_default(self.profile_dict[key])
            if key in self.CB_list:
                key.setChecked(value)
            else:
                if key in self.color_list:
                    text = Mediator.color_data_to_str(value)
                    key.setText(text)
                else:
                    key.setValue(value)
        self.LstFlamingColor.clear()
        value = self.profiledata.get_default(Mediator.indicate_path)
        self.CBIndicate.setChecked(value)
        value = self.profiledata.get_default(Mediator.delay_path)
        self.SpinDelayBeforeOn.setValue(value)
        self.TxtAddProfile.clear()

    def MoveUp(self):
        """
        moves selected profile upper in order
        :return:
        """
        i = self.profiledata.order_changed(self.LstProfile.currentItem().text(), "Up")
        self.LoadProfileList()
        self.LstProfile.setCurrentRow(i-1)
        self.ProfileClicked(self.LstProfile.currentItem())

    def MoveDown(self):
        """
        moves selected profile down in order
        :return:
        """
        i = self.profiledata.order_changed(self.LstProfile.currentItem().text(), "Down")
        self.LoadProfileList()
        self.LstProfile.setCurrentRow(i+1)
        self.ProfileClicked(self.LstProfile.currentItem())


    def SavePressed(self):
        self.Save(False)

    def Save(self, save_as: bool):
        index = self.tabWidget.currentIndex()
        if save_as or not self.filename[index]:
            new_filename = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", "")[0]
            if new_filename:
                self.filename[index] = new_filename
            else:
                return
        if index < 2:
            self.savefunctions[index](self.filename[index])
        else:
            self.profiledata.save_to_file(self.profiledata.data, self.filename[2])
        self.saved[index] = True
        self.ChangeTabTitle(tabnames[index], self.tabWidget.currentIndex())
        if index == 1:
            self.BtnSave.setEnabled(False)
        self.statusfields[index].setText('File %s successfully saved' % self.filename[index])

    def NewPressed(self):
        """
        clears all gui data for profile and auxleds
        :return:
        """
        i = self.tabWidget.currentIndex()
        if not self.saved[i]:
            quit_msg = "You have unsaved %s file. Do you want to save?" % tabnames[i]
            reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.SavePressed()
        if i == 0:
            self.auxdata = AuxEffects()
            self.TrStructure.clear()
            self.LstGroup.clear()
            self.CBAuxList.clear()
            self.GroupControlsClear()
            self.RepeatControlDisable()
            self.ClearRepeatControls()
            self.ClearStepControls()
            self.StepControlsDisable()
            self.SequenceControlsDisable()
            self.BtnDeleteSeq.setEnabled(False)
            for led in self.leds_combo_list:
                led.setChecked(False)
                led.setEnabled(True)
        if i == 2:
            self.profiledata = Profiles()
            self.LstProfile.clear()
            self.LstProfile.clear()
            self.ProfileControlsDisable()
            self.TxtAddProfile.clear()
            self.TxtAddProfile.setEnabled(True)
            self.BtnProfile.setEnabled(False)
            self.BtnDeleteProfile.setEnabled(False)
            self.BtnEditProfile.setEnabled(False)
            self.BtnUp.setEnabled(False)
            self.BtnDown.setEnabled(False)
            # file is saved now
        self.saved[i] = True
        self.filename[i] = ""
        self.statusfields[i].clear()
        self.ChangeTabTitle(tabnames[i], i)

    def SaveAsPressed(self):
        self.Save(True)

    def SaveAllPressed(self):
        """
        saves files from all three tabs
        :return:
        """
        for i in range(3):
            self.tabWidget.setCurrentIndex(i)
            self.Save(False)
        self.tabWidget.setCurrentIndex(0)

    def OpenPressed(self):
        index = self.tabWidget.currentIndex()
        openfilename = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "")[0]
        if openfilename:
            if "auxleds" in openfilename.lower():
                index = 0
            if "common" in openfilename.lower():
                index = 1
            if "profile" in openfilename.lower():
                index = 2
            if not self.saved[index]:
                save_msg = "You have unsaved %s settings. Do you want to save?" % tabnames[index]
                reply = QMessageBox.question(self, 'Message', save_msg, QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.SavePressed()
            openfile = open(openfilename, encoding='utf-8')
            text = openfile.read()
            self.tabWidget.setCurrentIndex(index)
            gui_data, error, warning = self.openfunctions[index](text)
            if error:
                self.ErrorMessage("Could not load file % s: % s" % (openfilename, error))
            else:
                if warning:
                    self.statusfields[index].setText("Try to open %s...\n %s" % (openfilename, warning))
                else:
                    self.statusfields[index].setText("%s successfully loaded" % openfilename)
                self.loadfunctions[index](gui_data)
                self.filename[index] = openfilename
                self.saved[index] = True
                self.ChangeTabTitle(tabnames[index], self.tabWidget.currentIndex())

    def OpenAllPressed(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        dialog.exec_()
        openfiledir = dialog.selectedFiles()[0]
        # openfiledir = dialog.getOpenFileName(self, "Open File")[0]
        if openfiledir:
            for i in range(3):
                filename = assistant.find_file(self.default_names[i], openfiledir)
                if filename:
                    filename = openfiledir+r'/'+filename
                    openfile = open(filename, encoding='utf-8')
                    text = openfile.read()
                    if not self.saved[i]:
                        save_msg = "You have unsaved %s settings. Do you want to save?" % tabnames[i]
                        reply = QMessageBox.question(self, 'Message', save_msg, QMessageBox.Yes, QMessageBox.No)
                        if reply == QMessageBox.Yes:
                            self.SavePressed()
                    gui_data, error, warning = self.openfunctions[i](text)
                    if error:
                        self.ErrorMessage("Could not load file % s: % s" % (filename, error))
                        self.statusfields[i].setText("Could not load file % s: % s" % (filename, error))
                    else:
                        if warning:
                            self.statusfields[i].setText("Try to open %s...\n %s" % (filename, warning))
                        else:
                            self.statusfields[i].setText("%s successfully loaded" % filename)
                        self.loadfunctions[i](gui_data)
                        self.filename[i] = filename
                        self.saved[i] = True
                        self.ChangeTabTitle(tabnames[i], i)
                else:
                    self.statusfields[i].setText("No %s file in %s directory" % (self.default_names[i], openfiledir))

    def LoadAuxleds(self, gui_data):
        """
        load auxleds data to tree
        :param gui_data: data
        :return:
        """
        self.auxdata.LedGroups = list()
        self.auxdata.Sequencers = list()
        for group in gui_data.LedGroups:
            self.auxdata.LedGroups.append(group)
        for sequencer in gui_data.Sequencers:
            self.auxdata.Sequencers.append(sequencer)
        self.LoadDataToTree()

    def LoadCommon(self, gui_data):
        """
        load common data to tab
        :param gui_data: data
        :return:
        """
        self.LoadCommonData(gui_data)
        self.BtnSave.setEnabled(False)

    def LoadProfiles(self, gui_data):
        """
        Load profile data to tree
        :param gui_data: data
        :return:
        """
        self.profiledata.data = gui_data
        self.profiledata.order = list(gui_data.keys())
        self.LoadProfileList()

    def ErrorMessage(self, text):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText(text)
        error.setWindowTitle("Error")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()

    def ChangeTabTitle(self, filetype, index):
        if self.filename[index]:
            text = "%s - %s" % (filetype, self.filename[index].split(r'/')[-1])
        else:
            text = filetype
        if not self.saved[index]:
            text += "*"
        self.tabWidget.setTabText(index, text)
        # self.tabWidget.setTabText(index,
        #                          QtCore.QCoreApplication.translate("MainWindow", text))

    def closeEvent(self, event):
        for i in range(3):
            if not self.saved[i]:
                quit_msg = "You have unsaved %s file. Do you want to save?" % tabnames[i]
                reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.SavePressed()
        event.accept()

@logger.catch
def main():
    initiate_exception_logging()
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ProfileEditor()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
