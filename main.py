"""
Audio Transcription Desktop Application
A PySide6 application for playing audio files and transcribing them using Deepgram API
"""
import sys
import os
from pathlib import Path
import threading
import subprocess

# Suppress FFmpeg warnings at the C library level
os.environ['QT_LOGGING_RULES'] = 'qt.multimedia.ffmpeg*=false'
os.environ['FFREPORT'] = 'level=fatal'
os.environ['AV_LOG_FORCE_NOCOLOR'] = '1'


def filter_stderr():
    """Filter stderr in a separate thread to suppress FFmpeg warnings"""
    import select
    while True:
        try:
            # This won't work for C-level stderr, but worth trying
            pass
        except:
            break


# Create a pipe to filter stderr
def setup_stderr_filter():
    """Redirect stderr through a filter to suppress FFmpeg warnings"""
    # Save original stderr
    original_stderr = sys.stderr
    stderr_fd = sys.stderr.fileno()

    # Create a pipe
    read_fd, write_fd = os.pipe()

    # Duplicate stderr
    stderr_copy = os.dup(stderr_fd)

    # Redirect stderr to write end of pipe
    os.dup2(write_fd, stderr_fd)
    os.close(write_fd)

    # Create thread to read from pipe and filter
    def filter_thread():
        with os.fdopen(read_fd, 'r', buffering=1) as pipe_read:
            for line in pipe_read:
                # Filter out FFmpeg warnings
                if "Could not update timestamps for skipped samples" not in line:
                    # Write to original stderr
                    os.write(stderr_copy, line.encode())

    thread = threading.Thread(target=filter_thread, daemon=True)
    thread.start()


# Setup stderr filtering before importing Qt
setup_stderr_filter()
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QFileDialog, QTabWidget, QLineEdit,
    QMessageBox, QProgressBar, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt, QUrl, QThread, Signal, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from deepgram import DeepgramClient
from deepgram_utils import (
    transcribe_audio_file,
    extract_response_dict,
    save_transcription
)
from clean_audio import clean_audio, check_ffmpeg_installed
from audio_splitter import split_audio_file, get_audio_duration
from config_utils import load_api_key, save_api_key, get_env_file_path


class TranscriptionWorker(QThread):
    """Worker thread for handling transcription without blocking UI"""
    finished = Signal(bool, str)
    progress = Signal(str)

    def __init__(self, api_key, audio_file, output_dir, model="whisper-large", language="it", save_json=False):
        super().__init__()
        self.api_key = api_key
        self.audio_file = audio_file
        self.output_dir = output_dir
        self.model = model
        self.language = language
        self.save_json = save_json

    def run(self):
        try:
            self.progress.emit("Initializing Deepgram client...")
            deepgram = DeepgramClient(api_key=self.api_key)

            self.progress.emit(f"Transcribing audio file with {self.model}...")
            response = transcribe_audio_file(
                deepgram,
                self.audio_file,
                model=self.model,
                language=self.language
            )

            self.progress.emit("Processing transcription...")
            response_dict = extract_response_dict(response)

            # Create output filename
            audio_filename = Path(self.audio_file).stem
            base_filename = os.path.join(self.output_dir, f"{audio_filename}_transcript")

            self.progress.emit("Saving transcription...")
            json_path, txt_path, _ = save_transcription(
                response_dict,
                base_filename=base_filename,
                save_json=self.save_json
            )

            # Build success message
            if json_path:
                message = f"Transcription saved:\n{txt_path}\n{json_path}"
            else:
                message = f"Transcription saved:\n{txt_path}"

            self.finished.emit(True, message)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.finished.emit(False, f"Error during transcription:\n{str(e)}\n\nDetails:\n{error_details}")


class AudioSplittingWorker(QThread):
    """Worker thread for handling audio splitting without blocking UI"""
    finished = Signal(bool, str, list)  # success, message, output_files
    progress = Signal(str)

    def __init__(self, input_file, output_dir):
        super().__init__()
        self.input_file = input_file
        self.output_dir = output_dir

    def run(self):
        try:
            def emit_progress(msg):
                self.progress.emit(msg)

            output_files = split_audio_file(
                self.input_file,
                output_dir=self.output_dir,
                segment_length=1800,  # 30 minutes
                overlap=30,  # 30 seconds
                output_format="mp3",
                progress_callback=emit_progress
            )

            message = f"Successfully split into {len(output_files)} segments"
            self.finished.emit(True, message, output_files)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.finished.emit(False, f"Error splitting audio:\n{str(e)}\n\nDetails:\n{error_details}", [])


class AudioCleaningWorker(QThread):
    """Worker thread for handling audio cleaning without blocking UI"""
    finished = Signal(bool, str, str)  # success, message, output_file_path
    progress = Signal(str)

    def __init__(self, input_file, output_file, sex="male", remove_keyboard_noise=False, voice_isolation=False):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.sex = sex
        self.remove_keyboard_noise = remove_keyboard_noise
        self.voice_isolation = voice_isolation

    def run(self):
        try:
            def emit_progress(msg):
                self.progress.emit(msg)

            output_path = clean_audio(
                self.input_file,
                self.output_file,
                sex=self.sex,
                remove_keyboard_noise=self.remove_keyboard_noise,
                voice_isolation=self.voice_isolation,
                progress_callback=emit_progress
            )

            self.finished.emit(True, "Audio enhancement completed successfully!", output_path)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.finished.emit(False, f"Error during audio enhancement:\n{str(e)}\n\nDetails:\n{error_details}", "")


class AudioPlayerTab(QWidget):
    """Main tab containing audio player and transcription controls"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_file = None
        self.api_key = None
        self.transcription_worker = None

        # Initialize media player
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.init_ui()
        self.load_api_key()

    def init_ui(self):
        layout = QVBoxLayout()

        # File selection section
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setWordWrap(True)
        select_file_btn = QPushButton("Select Audio File")
        select_file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label, 1)
        file_layout.addWidget(select_file_btn)
        layout.addLayout(file_layout)

        # Improve Audio button
        self.improve_audio_btn = QPushButton("Improve Audio Quality")
        self.improve_audio_btn.clicked.connect(self.open_audio_enhancement)
        self.improve_audio_btn.setEnabled(False)
        self.improve_audio_btn.setToolTip("Select an audio file first")
        layout.addWidget(self.improve_audio_btn)

        # Audio controls section
        controls_layout = QHBoxLayout()
        self.play_pause_btn = QPushButton("Play")
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        self.play_pause_btn.setEnabled(False)

        self.time_label = QLabel("00:00 / 00:00")
        controls_layout.addWidget(self.play_pause_btn)
        controls_layout.addWidget(self.time_label)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Audio slider
        self.audio_slider = QSlider(Qt.Horizontal)
        self.audio_slider.setEnabled(False)
        self.audio_slider.sliderMoved.connect(self.seek_position)
        layout.addWidget(self.audio_slider)

        # Progress bar for transcription
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)

        # Model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Transcription Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["nova-3", "nova-2", "whisper-large"])
        self.model_combo.setCurrentText("nova-3")
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch()
        layout.addLayout(model_layout)

        # Language selection
        language_layout = QHBoxLayout()
        language_layout.addWidget(QLabel("Audio Language:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Italian (it)", "English (en)"])
        self.language_combo.setCurrentIndex(0)  # Default to Italian
        language_layout.addWidget(self.language_combo)

        # Save JSON checkbox
        self.save_json_checkbox = QCheckBox("Save JSON (debug)")
        self.save_json_checkbox.setChecked(False)
        self.save_json_checkbox.setToolTip("Save detailed JSON transcription file (for debugging)")
        language_layout.addWidget(self.save_json_checkbox)

        language_layout.addStretch()
        layout.addLayout(language_layout)

        # Transcription button
        self.transcribe_btn = QPushButton("Transcribe Audio")
        self.transcribe_btn.clicked.connect(self.start_transcription)
        self.transcribe_btn.setEnabled(False)
        layout.addWidget(self.transcribe_btn)

        layout.addStretch()
        self.setLayout(layout)

        # Connect player signals
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)
        self.player.playbackStateChanged.connect(self.handle_playback_state_changed)

    def load_api_key(self):
        """Load API key from configuration file"""
        self.api_key = load_api_key()
        self.update_transcribe_button_state()

        # Check if API key is missing and show warning after UI is ready
        if not self.api_key or self.api_key.strip() == "":
            QTimer.singleShot(500, self.show_missing_api_key_warning)

    def show_missing_api_key_warning(self):
        """Show warning dialog when API key is missing"""
        QMessageBox.warning(
            self,
            "API Key Required",
            "No Deepgram API key found.\n\n"
            "Please go to the Settings tab to configure your API key.\n"
            "Get your API key from: https://console.deepgram.com/"
        )

    def select_file(self):
        """Open file dialog to select audio file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            str(Path.home()),
            "Audio Files (*.mp3 *.wav *.m4a *.ogg *.flac *.mp4);;All Files (*)"
        )

        if file_path:
            self.audio_file = file_path
            self.file_label.setText(f"File: {Path(file_path).name}")

            # Load audio file into player
            self.player.setSource(QUrl.fromLocalFile(file_path))
            self.play_pause_btn.setEnabled(True)
            self.audio_slider.setEnabled(True)

            # Enable improve audio button if ffmpeg is installed
            if check_ffmpeg_installed():
                self.improve_audio_btn.setEnabled(True)
                self.improve_audio_btn.setToolTip("")
            else:
                self.improve_audio_btn.setEnabled(False)
                self.improve_audio_btn.setToolTip("FFmpeg is not installed")

            # Check audio duration and warn if > 30 minutes
            self.check_audio_duration(file_path)

            self.update_transcribe_button_state()

    def check_audio_duration(self, file_path):
        """Check audio duration and warn if longer than 30 minutes"""
        try:
            duration_seconds = get_audio_duration(file_path)

            if duration_seconds is None:
                return  # Could not get duration

            duration_minutes = duration_seconds / 60

            # Warn if longer than 30 minutes (with buffer to avoid warning on exactly 30 min segments)
            if duration_minutes > 30.5:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Long Audio File")
                msg_box.setText(
                    f"This audio file is {duration_minutes:.1f} minutes long.\n\n"
                    "Deepgram may truncate or timeout on very long files."
                )
                msg_box.setInformativeText(
                    "Would you like to split it into shorter segments?\n\n"
                    "The file will be split into ~30-minute segments with 30-second overlap "
                    "for better transcription results."
                )

                # Add custom buttons
                split_button = msg_box.addButton("Split Audio", QMessageBox.ActionRole)
                cancel_button = msg_box.addButton("Continue Anyway", QMessageBox.RejectRole)

                msg_box.exec()

                if msg_box.clickedButton() == split_button:
                    self.split_current_audio()

        except Exception:
            # Silently fail if errors occur
            pass

    def split_current_audio(self):
        """Split current audio file into segments"""
        if not self.audio_file:
            return

        # Ask user to select destination folder
        desktop_dir = str(Path.home() / "Desktop")
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Folder for Audio Segments",
            desktop_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        # If user cancelled the dialog, return
        if not output_dir:
            return

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Create progress dialog
        self.split_progress_dialog = QMessageBox(self)
        self.split_progress_dialog.setIcon(QMessageBox.Information)
        self.split_progress_dialog.setWindowTitle("Splitting Audio")
        self.split_progress_dialog.setText("Splitting audio file into segments...")
        self.split_progress_dialog.setStandardButtons(QMessageBox.NoButton)
        self.split_progress_dialog.show()

        # Start worker thread
        self.splitting_worker = AudioSplittingWorker(self.audio_file, output_dir)
        self.splitting_worker.finished.connect(self.splitting_finished)
        self.splitting_worker.progress.connect(self.splitting_progress)
        self.splitting_worker.start()

    def splitting_progress(self, message):
        """Update splitting progress"""
        if hasattr(self, 'split_progress_dialog'):
            self.split_progress_dialog.setInformativeText(message)

    def splitting_finished(self, success, message, output_files):
        """Handle splitting completion"""
        # Close and delete progress dialog
        if hasattr(self, 'split_progress_dialog'):
            self.split_progress_dialog.close()
            self.split_progress_dialog.deleteLater()
            delattr(self, 'split_progress_dialog')

        # Process events to ensure dialog is closed
        from PySide6.QtCore import QCoreApplication
        QCoreApplication.processEvents()

        if success:
            # Show success message with file list
            files_list = "\n".join([f"  • {Path(f).name}" for f in output_files])
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Audio Split Complete")
            msg_box.setText(f"{message}")
            msg_box.setInformativeText(
                f"Created segments:\n{files_list}\n\n"
                f"Location: {Path(output_files[0]).parent}\n\n"
                "You can now transcribe each segment separately."
            )
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
        else:
            QMessageBox.critical(
                self,
                "Splitting Failed",
                message
            )

    def toggle_play_pause(self):
        """Toggle between play and pause"""
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def handle_playback_state_changed(self, state):
        """Update play/pause button text based on playback state"""
        if state == QMediaPlayer.PlayingState:
            self.play_pause_btn.setText("Pause")
        else:
            self.play_pause_btn.setText("Play")

    def update_position(self, position):
        """Update slider position and time label"""
        self.audio_slider.setValue(position)
        self.update_time_label(position, self.player.duration())

    def update_duration(self, duration):
        """Update slider range when duration is known"""
        self.audio_slider.setRange(0, duration)
        self.update_time_label(self.player.position(), duration)

    def seek_position(self, position):
        """Seek to specific position in audio"""
        self.player.setPosition(position)

    def update_time_label(self, position, duration):
        """Update time label with current position and duration"""
        def format_time(ms):
            seconds = int(ms / 1000)
            minutes = int(seconds / 60)
            seconds = seconds % 60
            return f"{minutes:02d}:{seconds:02d}"

        self.time_label.setText(f"{format_time(position)} / {format_time(duration)}")

    def update_transcribe_button_state(self):
        """Enable/disable transcribe button based on API key and file selection"""
        has_api_key = self.api_key is not None and self.api_key.strip() != ""
        has_file = self.audio_file is not None

        if not has_api_key:
            self.transcribe_btn.setEnabled(False)
            self.transcribe_btn.setToolTip("Please set your Deepgram API key in Settings")
        elif not has_file:
            self.transcribe_btn.setEnabled(False)
            self.transcribe_btn.setToolTip("Please select an audio file first")
        else:
            self.transcribe_btn.setEnabled(True)
            self.transcribe_btn.setToolTip("")

    def start_transcription(self):
        """Start transcription process in background thread"""
        if not self.audio_file or not self.api_key:
            QMessageBox.warning(
                self,
                "Cannot Transcribe",
                "Please ensure both an API key is set and an audio file is selected."
            )
            return

        # Ask user to select destination folder
        desktop_dir = str(Path.home() / "Desktop")
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Destination Folder for Transcription",
            desktop_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        # If user cancelled the dialog, return
        if not output_dir:
            return

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Get selected model, language, and save options
        selected_model = self.model_combo.currentText()
        # Extract language code from "Language (code)" format
        language_text = self.language_combo.currentText()
        language_code = language_text.split("(")[1].rstrip(")")  # Extract "it" from "Italian (it)"
        save_json = self.save_json_checkbox.isChecked()

        # Disable button during transcription
        self.transcribe_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)

        # Start worker thread
        self.transcription_worker = TranscriptionWorker(
            self.api_key,
            self.audio_file,
            output_dir,
            selected_model,
            language_code,
            save_json
        )
        self.transcription_worker.finished.connect(self.transcription_finished)
        self.transcription_worker.progress.connect(self.transcription_progress)
        self.transcription_worker.start()

    def transcription_progress(self, message):
        """Update progress label with current status"""
        self.progress_label.setText(message)

    def transcription_finished(self, success, message):
        """Handle transcription completion"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.update_transcribe_button_state()

        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)

    def open_audio_enhancement(self):
        """Open audio enhancement tab"""
        # Get the main window and switch to enhancement tab
        main_window = self.window()
        if hasattr(main_window, 'open_enhancement_tab'):
            main_window.open_enhancement_tab(self.audio_file)


class AudioEnhancementTab(QWidget):
    """Tab for audio enhancement/cleaning"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_file = None
        self.output_file = None
        self.cleaning_worker = None

        # Initialize media player for preview
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Input file section
        layout.addWidget(QLabel("Input Audio File:"))
        self.input_path_edit = QLineEdit()
        self.input_path_edit.setReadOnly(True)
        layout.addWidget(self.input_path_edit)

        # Output file section
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output File:"))
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("Default: input_filename_clean.ext")
        browse_output_btn = QPushButton("Browse...")
        browse_output_btn.clicked.connect(self.browse_output_file)
        output_layout.addWidget(self.output_path_edit, 1)
        output_layout.addWidget(browse_output_btn)
        layout.addLayout(output_layout)

        # Sex/voice selection
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("Speaker Voice:"))
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["male", "female", "mixed"])
        voice_layout.addWidget(self.voice_combo)
        voice_layout.addStretch()
        layout.addLayout(voice_layout)

        # Enhancement options checkboxes
        self.keyboard_noise_checkbox = QCheckBox("Remove keyboard typing noise (aggressive filtering)")
        self.keyboard_noise_checkbox.setToolTip("Apply aggressive filters to remove keyboard typing sounds. Use only if keyboard noise is present.")
        layout.addWidget(self.keyboard_noise_checkbox)

        self.voice_isolation_checkbox = QCheckBox("Enhance voice isolation (reduce background noise)")
        self.voice_isolation_checkbox.setToolTip("Use AI-powered dialogue enhancement to isolate voice and reduce background noise.")
        layout.addWidget(self.voice_isolation_checkbox)

        # Process button
        self.process_btn = QPushButton("Start Audio Enhancement")
        self.process_btn.clicked.connect(self.start_cleaning)
        self.process_btn.setEnabled(True)
        layout.addWidget(self.process_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)

        # Preview section (shown after processing)
        layout.addWidget(QLabel("Preview Enhanced Audio:"))

        preview_controls_layout = QHBoxLayout()
        self.preview_play_btn = QPushButton("Play Preview")
        self.preview_play_btn.clicked.connect(self.toggle_preview_play_pause)
        self.preview_play_btn.setEnabled(False)

        self.preview_time_label = QLabel("00:00 / 00:00")
        preview_controls_layout.addWidget(self.preview_play_btn)
        preview_controls_layout.addWidget(self.preview_time_label)
        preview_controls_layout.addStretch()
        layout.addLayout(preview_controls_layout)

        # Preview slider
        self.preview_slider = QSlider(Qt.Horizontal)
        self.preview_slider.setEnabled(False)
        self.preview_slider.sliderMoved.connect(self.seek_preview_position)
        layout.addWidget(self.preview_slider)

        # Accept button
        self.accept_btn = QPushButton("Accept Enhancement and Return")
        self.accept_btn.clicked.connect(self.accept_enhancement)
        self.accept_btn.setEnabled(False)
        layout.addWidget(self.accept_btn)

        layout.addStretch()
        self.setLayout(layout)

        # Connect player signals
        self.player.positionChanged.connect(self.update_preview_position)
        self.player.durationChanged.connect(self.update_preview_duration)
        self.player.playbackStateChanged.connect(self.handle_preview_playback_state_changed)

    def set_input_file(self, file_path):
        """Set the input file path"""
        self.input_file = file_path
        self.input_path_edit.setText(file_path)

        # Generate default output path - always use .mp3 extension
        p = Path(file_path)
        default_output = str(p.with_name(p.stem + "_clean.mp3"))
        self.output_path_edit.setPlaceholderText(f"Default: {Path(default_output).name}")

        # Reset state
        self.output_file = None
        self.accept_btn.setEnabled(False)
        self.preview_play_btn.setEnabled(False)
        self.preview_slider.setEnabled(False)

    def browse_output_file(self):
        """Browse for output file location"""
        if not self.input_file:
            return

        p = Path(self.input_file)
        default_name = p.stem + "_clean.mp3"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Enhanced Audio As (MP3)",
            str(p.parent / default_name),
            "MP3 Audio Files (*.mp3)"
        )

        if file_path:
            # Ensure the file has .mp3 extension
            file_path_obj = Path(file_path)
            if file_path_obj.suffix.lower() != '.mp3':
                file_path = str(file_path_obj.with_suffix('.mp3'))
            self.output_path_edit.setText(file_path)

    def start_cleaning(self):
        """Start the audio cleaning process"""
        if not self.input_file:
            QMessageBox.warning(self, "No Input File", "Please select an input file first.")
            return

        # Check if ffmpeg is installed
        if not check_ffmpeg_installed():
            result = QMessageBox.question(
                self,
                "FFmpeg Not Found",
                "FFmpeg is required for audio enhancement but was not found on your system.\n\n"
                "Would you like to install it?\n\n"
                "On Ubuntu/Debian: sudo apt install ffmpeg\n"
                "On macOS: brew install ffmpeg",
                QMessageBox.Yes | QMessageBox.No
            )
            return

        # Get output path - always use .mp3 extension
        output_path = self.output_path_edit.text().strip()
        if not output_path:
            p = Path(self.input_file)
            output_path = str(p.with_name(p.stem + "_clean.mp3"))
        else:
            # Ensure the output path has .mp3 extension
            output_path_obj = Path(output_path)
            if output_path_obj.suffix.lower() != '.mp3':
                output_path = str(output_path_obj.with_suffix('.mp3'))

        # Get voice type and enhancement settings
        sex = self.voice_combo.currentText()
        remove_keyboard_noise = self.keyboard_noise_checkbox.isChecked()
        voice_isolation = self.voice_isolation_checkbox.isChecked()

        # Disable button during processing
        self.process_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)

        # Start worker thread
        self.cleaning_worker = AudioCleaningWorker(
            self.input_file,
            output_path,
            sex=sex,
            remove_keyboard_noise=remove_keyboard_noise,
            voice_isolation=voice_isolation
        )
        self.cleaning_worker.finished.connect(self.cleaning_finished)
        self.cleaning_worker.progress.connect(self.cleaning_progress)
        self.cleaning_worker.start()

    def cleaning_progress(self, message):
        """Update progress label"""
        self.progress_label.setText(message)

    def cleaning_finished(self, success, message, output_path):
        """Handle cleaning completion"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.process_btn.setEnabled(True)

        if success:
            self.output_file = output_path

            # Enable preview controls
            self.player.setSource(QUrl.fromLocalFile(output_path))
            self.preview_play_btn.setEnabled(True)
            self.preview_slider.setEnabled(True)

            # Enable accept button
            self.accept_btn.setEnabled(True)

            QMessageBox.information(self, "Success", f"{message}\n\nYou can now preview the enhanced audio.")
        else:
            QMessageBox.critical(self, "Error", message)

    def toggle_preview_play_pause(self):
        """Toggle preview playback"""
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def handle_preview_playback_state_changed(self, state):
        """Update play/pause button text"""
        if state == QMediaPlayer.PlayingState:
            self.preview_play_btn.setText("Pause Preview")
        else:
            self.preview_play_btn.setText("Play Preview")

    def update_preview_position(self, position):
        """Update slider position and time label"""
        self.preview_slider.setValue(position)
        self.update_preview_time_label(position, self.player.duration())

    def update_preview_duration(self, duration):
        """Update slider range"""
        self.preview_slider.setRange(0, duration)
        self.update_preview_time_label(self.player.position(), duration)

    def seek_preview_position(self, position):
        """Seek to specific position"""
        self.player.setPosition(position)

    def update_preview_time_label(self, position, duration):
        """Update time label"""
        def format_time(ms):
            seconds = int(ms / 1000)
            minutes = int(seconds / 60)
            seconds = seconds % 60
            return f"{minutes:02d}:{seconds:02d}"

        self.preview_time_label.setText(f"{format_time(position)} / {format_time(duration)}")

    def accept_enhancement(self):
        """Accept the enhancement and return to main tab with new file"""
        if not self.output_file:
            return

        # Stop playback
        self.player.stop()

        # Get the main window and update the audio file
        main_window = self.window()
        if hasattr(main_window, 'accept_enhanced_audio'):
            main_window.accept_enhanced_audio(self.output_file)


class SettingsTab(QWidget):
    """Settings tab for API key management"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # API Key section
        layout.addWidget(QLabel("Deepgram API Key:"))

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter your Deepgram API key")

        # Load current API key
        current_key = load_api_key() or ""
        self.api_key_input.setText(current_key)

        layout.addWidget(self.api_key_input)

        # Save button
        save_btn = QPushButton("Save API Key")
        save_btn.clicked.connect(self.save_api_key)
        layout.addWidget(save_btn)

        # Info label
        env_file_path = get_env_file_path()
        info_label = QLabel(
            "Get your API key from: https://console.deepgram.com/\n\n"
            f"The API key will be saved securely to:\n{env_file_path}"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        layout.addStretch()
        self.setLayout(layout)

    def save_api_key(self):
        """Save API key to configuration file"""
        api_key_value = self.api_key_input.text().strip()

        if not api_key_value:
            QMessageBox.warning(self, "Warning", "Please enter an API key")
            return

        try:
            save_api_key(api_key_value)
            QMessageBox.information(self, "Success", "API key saved successfully!")

            # Notify parent window to update
            if isinstance(self.parent().parent(), MainWindow):
                self.parent().parent().reload_api_key()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save API key: {str(e)}")


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Transcription App")
        self.setMinimumSize(600, 400)

        # Create tab widget
        self.tabs = QTabWidget()

        # Create tabs
        self.audio_tab = AudioPlayerTab()
        self.enhancement_tab = AudioEnhancementTab()
        self.settings_tab = SettingsTab()

        # Add tabs in order
        self.tabs.addTab(self.audio_tab, "Audio Player")
        self.tabs.addTab(self.enhancement_tab, "Audio Enhancement")
        self.tabs.addTab(self.settings_tab, "Settings")

        # Disable enhancement tab by default
        self.tabs.setTabEnabled(1, False)

        self.setCentralWidget(self.tabs)

    def reload_api_key(self):
        """Reload API key in audio player tab after settings update"""
        self.audio_tab.load_api_key()

    def open_enhancement_tab(self, audio_file):
        """Open the enhancement tab with the specified audio file"""
        # Enable the enhancement tab
        self.tabs.setTabEnabled(1, True)

        # Set the input file in the enhancement tab
        self.enhancement_tab.set_input_file(audio_file)

        # Switch to the enhancement tab
        self.tabs.setCurrentIndex(1)

    def accept_enhanced_audio(self, enhanced_file):
        """Accept the enhanced audio and update the main tab"""
        # Update the audio file in the main tab
        self.audio_tab.audio_file = enhanced_file
        self.audio_tab.file_label.setText(f"File: {Path(enhanced_file).name}")

        # Load the enhanced audio into the player
        self.audio_tab.player.setSource(QUrl.fromLocalFile(enhanced_file))

        # Disable the enhancement tab
        self.tabs.setTabEnabled(1, False)

        # Switch back to the audio player tab
        self.tabs.setCurrentIndex(0)

        # Show success message
        QMessageBox.information(
            self,
            "Enhancement Applied",
            f"The enhanced audio file has been loaded:\n{Path(enhanced_file).name}"
        )


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
