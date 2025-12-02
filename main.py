"""
GiffyDrop - Discord GIF Optimizer
A desktop application to convert MP4 videos into high-quality GIFs optimized for Discord.
Target: < 9.9MB file size with maximum visual quality.
"""

import os
import shutil
import subprocess
import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

import customtkinter as ctk


# ============================================================================
# BACKEND LOGIC: FFmpeg Conversion Engine
# ============================================================================

class GiffyConverter:
    """
    Handles the conversion logic from MP4 to GIF using FFmpeg's two-pass palette method.
    This class is UI-agnostic and focuses purely on file operations and subprocess management.
    """
    
    def __init__(self, input_path: str, width: str, fps: int):
        """
        Initialize the converter with input parameters.
        
        Args:
            input_path: Full path to the source MP4 file.
            width: Target width in pixels or "Original".
            fps: Target frames per second.
        """
        self.input_path = Path(input_path)
        self.width = width
        self.fps = fps
        
        # Create output folder if it doesn't exist
        output_folder = self.input_path.parent / "output"
        output_folder.mkdir(exist_ok=True)
        
        # Generate output path in the output folder
        self.output_path = output_folder / f"{self.input_path.stem}_optimized.gif"
        self.palette_path = output_folder / "palette.png"
    
    def build_scale_filter(self) -> str:
        """
        Build the FFmpeg scale filter based on width selection.
        
        Returns:
            FFmpeg scale filter string.
        """
        if self.width == "Original":
            return f"fps={self.fps}"
        else:
            # Extract numeric width from strings like "320px (Standard)"
            width_value = self.width.split("px")[0]
            return f"fps={self.fps},scale={width_value}:-1:flags=lanczos"
    
    def generate_palette(self, log_callback) -> bool:
        """
        Execute FFmpeg pass 1: Generate optimized color palette.
        
        Args:
            log_callback: Function to call with output messages.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            scale_filter = self.build_scale_filter()
            cmd = [
                "ffmpeg",
                "-i", str(self.input_path),
                "-vf", f"{scale_filter},palettegen",
                "-y",  # Overwrite without asking
                str(self.palette_path)
            ]
            
            log_callback(f"[Pass 1/2] Generating color palette...\n")
            log_callback(f"Command: {' '.join(cmd)}\n\n")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Stream output to log
            for line in process.stdout:
                log_callback(line)
            
            process.wait()
            
            if process.returncode != 0:
                log_callback(f"\n❌ Error: Palette generation failed (exit code {process.returncode})\n")
                return False
            
            log_callback("\n✓ Palette generated successfully\n\n")
            return True
            
        except FileNotFoundError:
            log_callback("\n❌ Error: FFmpeg not found in PATH\n")
            return False
        except Exception as e:
            log_callback(f"\n❌ Error: {str(e)}\n")
            return False
    
    def generate_gif(self, log_callback) -> bool:
        """
        Execute FFmpeg pass 2: Generate final GIF using the palette.
        
        Args:
            log_callback: Function to call with output messages.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            scale_filter = self.build_scale_filter()
            cmd = [
                "ffmpeg",
                "-i", str(self.input_path),
                "-i", str(self.palette_path),
                "-lavfi", f"{scale_filter} [x]; [x][1:v] paletteuse",
                "-y",
                str(self.output_path)
            ]
            
            log_callback(f"[Pass 2/2] Converting to GIF...\n")
            log_callback(f"Command: {' '.join(cmd)}\n\n")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Stream output to log
            for line in process.stdout:
                log_callback(line)
            
            process.wait()
            
            if process.returncode != 0:
                log_callback(f"\n❌ Error: GIF conversion failed (exit code {process.returncode})\n")
                return False
            
            log_callback("\n✓ GIF generated successfully\n\n")
            return True
            
        except Exception as e:
            log_callback(f"\n❌ Error: {str(e)}\n")
            return False
    
    def cleanup_temp_files(self, log_callback):
        """Remove temporary palette file."""
        try:
            if self.palette_path.exists():
                self.palette_path.unlink()
                log_callback("✓ Temporary files cleaned up\n")
        except Exception as e:
            log_callback(f"⚠ Warning: Could not remove temporary files: {str(e)}\n")
    
    def check_file_size(self, log_callback) -> float:
        """
        Check the final GIF size and log warnings if needed.
        Discord's limit is 10MB for regular users, 50MB for nitro+ users.
        We use 10MB as the safe threshold.
        
        Args:
            log_callback: Function to call with output messages.
            
        Returns:
            File size in megabytes.
        """
        if not self.output_path.exists():
            return 0.0
        
        size_bytes = self.output_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        
        log_callback(f"\n📊 Final size: {size_mb:.2f} MB\n")
        
        if size_mb > 10.0:
            log_callback("\n⚠ WARNING: File exceeds Discord limit (10MB).\n")
            log_callback("   Try lowering FPS or Width for a smaller file.\n")
        else:
            log_callback("✓ File size is within Discord limits!\n")
        
        return size_mb
    
    def convert(self, log_callback) -> bool:
        """
        Execute the full conversion pipeline.
        
        Args:
            log_callback: Function to call with output messages.
            
        Returns:
            True if successful, False otherwise.
        """
        log_callback("=" * 60 + "\n")
        log_callback("Starting conversion process...\n")
        log_callback("=" * 60 + "\n\n")
        
        # Pass 1: Generate palette
        if not self.generate_palette(log_callback):
            self.cleanup_temp_files(log_callback)
            return False
        
        # Pass 2: Generate GIF
        if not self.generate_gif(log_callback):
            self.cleanup_temp_files(log_callback)
            return False
        
        # Check file size
        self.check_file_size(log_callback)
        
        # Cleanup
        self.cleanup_temp_files(log_callback)
        
        log_callback("\n" + "=" * 60 + "\n")
        log_callback(f"✓ Conversion complete!\n")
        log_callback(f"Output: {self.output_path}\n")
        log_callback("=" * 60 + "\n")
        
        return True


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def check_ffmpeg() -> bool:
    """
    Check if FFmpeg is available in the system PATH.
    
    Returns:
        True if FFmpeg is found, False otherwise.
    """
    return shutil.which("ffmpeg") is not None


# ============================================================================
# GUI APPLICATION
# ============================================================================

class App(ctk.CTk):
    """
    Main GUI application for GiffyDrop.
    Uses CustomTkinter for a modern, dark-mode interface.
    """
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("GiffyDrop - Discord GIF Optimizer")
        self.geometry("700x750")
        self.resizable(False, False)
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # State variables
        self.selected_file: Optional[str] = None
        self.is_converting: bool = False
        
        # Initialize UI
        self.setup_ui()
        
        # Check FFmpeg on startup
        self.after(100, self.check_ffmpeg_availability)
    
    def setup_ui(self):
        """Build the complete user interface."""
        
        # Main container with padding
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ===== HEADER =====
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🎬 GiffyDrop",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack()
        
        instruction_label = ctk.CTkLabel(
            header_frame,
            text="Select your edited MP4 file",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        instruction_label.pack(pady=(5, 0))
        
        # ===== INPUT AREA =====
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="x", pady=(0, 20))
        
        self.select_button = ctk.CTkButton(
            input_frame,
            text="📁 Select video file...",
            command=self.select_file,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.select_button.pack(pady=15, padx=15)
        
        self.file_label = ctk.CTkLabel(
            input_frame,
            text="No file selected",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        self.file_label.pack(pady=(0, 15), padx=15)
        
        # ===== TABVIEW: "The Ezgif Control Module" =====
        self.tabview = ctk.CTkTabview(main_frame, height=180)
        self.tabview.pack(fill="x", pady=(0, 20))
        
        # Tab 1: Profile avatar
        self.tab_avatar = self.tabview.add("Profile avatar")
        self.setup_avatar_tab()
        
        # Tab 2: Profile banner
        self.tab_banner = self.tabview.add("Profile banner")
        self.setup_banner_tab()
        
        # Set default tab
        self.tabview.set("Profile avatar")
        
        # ===== ACTION AREA =====
        action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        action_frame.pack(fill="both", expand=True)
        
        self.convert_button = ctk.CTkButton(
            action_frame,
            text="🎯 Convert to GIF",
            command=self.start_conversion,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2b8a3e",
            hover_color="#237a33"
        )
        self.convert_button.pack(fill="x", pady=(0, 15))
        
        # Status log label
        log_label = ctk.CTkLabel(
            action_frame,
            text="Status log",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        log_label.pack(fill="x", pady=(0, 5))
        
        # Status log textbox
        self.status_log = ctk.CTkTextbox(
            action_frame,
            height=250,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word"
        )
        self.status_log.pack(fill="both", expand=True)
        self.status_log.insert("1.0", "Ready to convert. Select a video file to begin.\n")
        self.status_log.configure(state="disabled")
    
    def setup_avatar_tab(self):
        """Setup the Profile avatar tab with fixed 320px width and FPS controls."""
        
        # Resolution info (fixed)
        info_label = ctk.CTkLabel(
            self.tab_avatar,
            text="Resolution: 320 × Auto",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        info_label.pack(fill="x", padx=20, pady=(15, 10))
        
        info_desc = ctk.CTkLabel(
            self.tab_avatar,
            text="Optimized for Discord profile pictures",
            font=ctk.CTkFont(size=11),
            text_color="gray70",
            anchor="w"
        )
        info_desc.pack(fill="x", padx=20, pady=(0, 15))
        
        # FPS selection
        fps_label = ctk.CTkLabel(
            self.tab_avatar,
            text="Frame rate",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        fps_label.pack(fill="x", padx=20, pady=(0, 5))
        
        self.avatar_fps_var = ctk.StringVar(value="20 fps (Balanced)")
        self.avatar_fps_dropdown = ctk.CTkOptionMenu(
            self.tab_avatar,
            variable=self.avatar_fps_var,
            values=[
                "30 fps (Fluid)",
                "24 fps (Cinema)",
                "20 fps (Balanced)",
                "15 fps (Compact)",
                "10 fps (Low weight)"
            ],
            font=ctk.CTkFont(size=12)
        )
        self.avatar_fps_dropdown.pack(fill="x", padx=20, pady=(0, 15))
    
    def setup_banner_tab(self):
        """Setup the Profile banner tab with fixed 600px width and FPS controls."""
        
        # Resolution info (fixed)
        info_label = ctk.CTkLabel(
            self.tab_banner,
            text="Resolution: 600 × Auto",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        info_label.pack(fill="x", padx=20, pady=(15, 10))
        
        info_desc = ctk.CTkLabel(
            self.tab_banner,
            text="Optimized for Discord profile banners",
            font=ctk.CTkFont(size=11),
            text_color="gray70",
            anchor="w"
        )
        info_desc.pack(fill="x", padx=20, pady=(0, 15))
        
        # FPS selection
        fps_label = ctk.CTkLabel(
            self.tab_banner,
            text="Frame rate",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        fps_label.pack(fill="x", padx=20, pady=(0, 5))
        
        self.banner_fps_var = ctk.StringVar(value="15 fps (Compact)")
        self.banner_fps_dropdown = ctk.CTkOptionMenu(
            self.tab_banner,
            variable=self.banner_fps_var,
            values=[
                "30 fps (Fluid)",
                "24 fps (Cinema)",
                "20 fps (Balanced)",
                "15 fps (Compact)",
                "10 fps (Low weight)"
            ],
            font=ctk.CTkFont(size=12)
        )
        self.banner_fps_dropdown.pack(fill="x", padx=20, pady=(0, 15))
    
    def check_ffmpeg_availability(self):
        """Check if FFmpeg is installed and warn the user if not."""
        if not check_ffmpeg():
            self.log_message("\n⚠ WARNING: FFmpeg not found in PATH!\n")
            self.log_message("Please install FFmpeg and add it to your system PATH.\n")
            self.log_message("Download: https://ffmpeg.org/download.html\n\n")
            
            messagebox.showwarning(
                "FFmpeg not found",
                "FFmpeg is required for this application.\n\n"
                "Please install FFmpeg and add it to your system PATH.\n"
                "Download: https://ffmpeg.org/download.html"
            )
    
    def select_file(self):
        """Open file dialog to select an MP4 file."""
        file_path = filedialog.askopenfilename(
            title="Select MP4 video file",
            filetypes=[
                ("MP4 files", "*.mp4"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.selected_file = file_path
            # Show shortened path if too long
            display_path = file_path
            if len(display_path) > 60:
                display_path = "..." + display_path[-57:]
            
            self.file_label.configure(text=display_path, text_color="white")
            self.log_message(f"\n✓ File selected: {file_path}\n")
    
    def get_current_settings(self) -> tuple[str, int]:
        """
        Get the current FPS and fixed width settings based on active tab.
        Profile avatar: 320px fixed width (auto height)
        Profile banner: 600px fixed width (auto height)
        
        Returns:
            Tuple of (width_px, fps_int).
        """
        current_tab = self.tabview.get()
        
        # Set fixed widths based on profile type
        if current_tab == "Profile avatar":
            width = "320"
            fps_str = self.avatar_fps_var.get()
        else:  # Profile banner
            width = "600"
            fps_str = self.banner_fps_var.get()
        
        # Extract numeric FPS value from strings like "20 fps (Balanced)"
        fps = int(fps_str.split(" ")[0])
        
        return width, fps
    
    def log_message(self, message: str):
        """
        Add a message to the status log.
        
        Args:
            message: Text to append to the log.
        """
        self.status_log.configure(state="normal")
        self.status_log.insert("end", message)
        self.status_log.see("end")
        self.status_log.configure(state="disabled")
        self.update_idletasks()
    
    def clear_log(self):
        """Clear the status log."""
        self.status_log.configure(state="normal")
        self.status_log.delete("1.0", "end")
        self.status_log.configure(state="disabled")
    
    def start_conversion(self):
        """Validate inputs and start the conversion process in a separate thread."""
        
        # Validation
        if not self.selected_file:
            messagebox.showerror("No file selected", "Please select a video file first.")
            return
        
        if not Path(self.selected_file).exists():
            messagebox.showerror("File not found", "The selected file no longer exists.")
            return
        
        if self.is_converting:
            messagebox.showinfo("Conversion in progress", "Please wait for the current conversion to finish.")
            return
        
        if not check_ffmpeg():
            messagebox.showerror(
                "FFmpeg not found",
                "FFmpeg is not installed or not in PATH.\n"
                "Please install FFmpeg to continue."
            )
            return
        
        # Disable UI during conversion
        self.is_converting = True
        self.convert_button.configure(state="disabled", text="Converting...")
        self.select_button.configure(state="disabled")
        
        # Clear previous log
        self.clear_log()
        
        # Start conversion in separate thread
        conversion_thread = threading.Thread(target=self.run_conversion, daemon=True)
        conversion_thread.start()
    
    def run_conversion(self):
        """
        Execute the conversion process in a background thread.
        This keeps the GUI responsive during long operations.
        """
        try:
            # Get current settings
            width, fps = self.get_current_settings()
            
            # Create converter instance
            converter = GiffyConverter(self.selected_file, width, fps)
            
            # Run conversion with log callback
            success = converter.convert(self.log_message)
            
            # Show completion message
            if success:
                self.after(0, lambda: messagebox.showinfo(
                    "Conversion complete",
                    f"GIF saved successfully!\n\n{converter.output_path}"
                ))
            else:
                self.after(0, lambda: messagebox.showerror(
                    "Conversion failed",
                    "An error occurred during conversion.\nCheck the status log for details."
                ))
        
        except Exception as e:
            self.log_message(f"\n❌ Unexpected error: {str(e)}\n")
            self.after(0, lambda: messagebox.showerror(
                "Error",
                f"An unexpected error occurred:\n{str(e)}"
            ))
        
        finally:
            # Re-enable UI
            self.is_converting = False
            self.after(0, lambda: self.convert_button.configure(state="normal", text="🎯 Convert to GIF"))
            self.after(0, lambda: self.select_button.configure(state="normal"))


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Initialize and run the application."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
