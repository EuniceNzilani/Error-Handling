import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import traceback
import re
import json
import threading
import time
from datetime import datetime

class FileProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced File Processor")
        self.root.geometry("800x600")
        self.root.minsize(600, 500)
        
        # Set theme colors
        self.bg_color = "#f0f0f0"
        self.accent_color = "#4a6ea9"
        self.text_color = "#333333"
        self.error_color = "#e74c3c"
        self.success_color = "#2ecc71"
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 10), background=self.accent_color)
        self.style.configure('TLabel', font=('Arial', 11), background=self.bg_color)
        self.style.configure('TFrame', background=self.bg_color)
        
        self.root.configure(bg=self.bg_color)
        
        # Variables
        self.input_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.status_message = tk.StringVar(value="Ready")
        self.processing_option = tk.StringVar(value="Convert to uppercase")
        self.is_processing = False
        self.progress_value = tk.DoubleVar(value=0.0)
        self.search_pattern = tk.StringVar()
        self.replace_text = tk.StringVar()
        
        # Create and place widgets
        self.create_widgets()
        
        # Log
        self.log("Application started")
        
    def create_widgets(self):
        # Main layout frames
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Advanced File Processor", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Input file selection
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(file_frame, text="Input File:").grid(row=0, column=0, padx=5, sticky=tk.W)
        ttk.Entry(file_frame, textvariable=self.input_file_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_input_file).grid(row=0, column=2, padx=5)
        
        # Output file selection
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="Output File:").grid(row=0, column=0, padx=5, sticky=tk.W)
        ttk.Entry(output_frame, textvariable=self.output_file_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output_file).grid(row=0, column=2, padx=5)
        
        # Processing options
        options_frame = ttk.LabelFrame(main_frame, text="Processing Options", padding=10)
        options_frame.pack(fill=tk.X, pady=10)
        
        ttk.Radiobutton(options_frame, text="Convert to uppercase", 
                       variable=self.processing_option, value="Convert to uppercase").pack(anchor=tk.W)
        ttk.Radiobutton(options_frame, text="Convert to lowercase", 
                       variable=self.processing_option, value="Convert to lowercase").pack(anchor=tk.W)
        ttk.Radiobutton(options_frame, text="Add line numbers", 
                       variable=self.processing_option, value="Add line numbers").pack(anchor=tk.W)
        ttk.Radiobutton(options_frame, text="Remove empty lines", 
                       variable=self.processing_option, value="Remove empty lines").pack(anchor=tk.W)
        ttk.Radiobutton(options_frame, text="Find and replace", 
                       variable=self.processing_option, value="Find and replace").pack(anchor=tk.W)
        
        # Find and replace options
        find_replace_frame = ttk.Frame(options_frame)
        find_replace_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(find_replace_frame, text="Find:").grid(row=0, column=0, padx=5, sticky=tk.W)
        ttk.Entry(find_replace_frame, textvariable=self.search_pattern, width=25).grid(row=0, column=1, padx=5)
        
        ttk.Label(find_replace_frame, text="Replace:").grid(row=1, column=0, padx=5, sticky=tk.W)
        ttk.Entry(find_replace_frame, textvariable=self.replace_text, width=25).grid(row=1, column=1, padx=5)
        
        # Process button
        process_frame = ttk.Frame(main_frame)
        process_frame.pack(fill=tk.X, pady=10)
        
        self.process_button = ttk.Button(process_frame, text="Process File", command=self.start_processing)
        self.process_button.pack(side=tk.RIGHT, padx=5)
        
        # Progress bar
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT, padx=5)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_value, length=400, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(status_frame, textvariable=self.status_message)
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Input File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.input_file_path.set(file_path)
            self.log(f"Selected input file: {file_path}")
            
            # Suggest output file name based on input file
            if not self.output_file_path.get():
                base_name = os.path.basename(file_path)
                name, ext = os.path.splitext(base_name)
                self.output_file_path.set(f"{os.path.dirname(file_path)}/{name}_processed{ext}")
    
    def browse_output_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Select Output File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.output_file_path.set(file_path)
            self.log(f"Selected output file: {file_path}")
    
    def start_processing(self):
        # Validate input file exists
        input_file = self.input_file_path.get()
        if not input_file:
            self.show_error("Please select an input file.")
            return
            
        if not os.path.exists(input_file):
            self.show_error(f"Input file does not exist: {input_file}")
            return
            
        # Validate output path
        output_file = self.output_file_path.get()
        if not output_file:
            self.show_error("Please specify an output file.")
            return
            
        # Check if output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            self.show_error(f"Output directory does not exist: {output_dir}")
            return
            
        # Check if output file exists and confirm overwrite
        if os.path.exists(output_file):
            confirm = messagebox.askyesno(
                "Confirm Overwrite", 
                f"The output file already exists:\n{output_file}\n\nDo you want to overwrite it?"
            )
            if not confirm:
                return
        
        # Start processing in a separate thread to keep UI responsive
        self.is_processing = True
        self.process_button.config(state=tk.DISABLED)
        self.status_message.set("Processing...")
        self.progress_value.set(0)
        
        processing_thread = threading.Thread(target=self.process_file)
        processing_thread.daemon = True
        processing_thread.start()
    
    def process_file(self):
        try:
            input_file = self.input_file_path.get()
            output_file = self.output_file_path.get()
            option = self.processing_option.get()
            
            self.log(f"Processing file: {input_file}")
            self.log(f"Processing option: {option}")
            
            # Get file size to track progress
            file_size = os.path.getsize(input_file)
            
            # Process based on selected option
            with open(input_file, 'r', encoding='utf-8') as infile:
                # First, read all lines for processing
                lines = infile.readlines()
                total_lines = len(lines)
                
                processed_lines = []
                
                for i, line in enumerate(lines):
                    # Update progress
                    progress = (i + 1) / total_lines * 100
                    self.root.after(0, lambda p=progress: self.progress_value.set(p))
                    
                    # Add small delay to show progress better
                    time.sleep(0.01)
                    
                    # Process the line based on selected option
                    if option == "Convert to uppercase":
                        processed_line = line.upper()
                    elif option == "Convert to lowercase":
                        processed_line = line.lower()
                    elif option == "Add line numbers":
                        processed_line = f"{i+1}: {line}"
                    elif option == "Remove empty lines":
                        if line.strip():
                            processed_line = line
                        else:
                            processed_line = None  # Skip this line
                    elif option == "Find and replace":
                        search = self.search_pattern.get()
                        replace = self.replace_text.get()
                        if search:
                            processed_line = line.replace(search, replace)
                        else:
                            processed_line = line
                    else:
                        processed_line = line
                    
                    if processed_line is not None:
                        processed_lines.append(processed_line)
            
            # Write to output file
            with open(output_file, 'w', encoding='utf-8') as outfile:
                outfile.writelines(processed_lines)
            
            # Show success message
            self.root.after(0, lambda: self.show_success(
                f"File processed successfully!\n\n"
                f"Input file: {input_file}\n"
                f"Output file: {output_file}\n"
                f"Process: {option}\n"
                f"Lines processed: {total_lines}\n"
                f"Output lines: {len(processed_lines)}"
            ))
            
        except Exception as e:
            error_msg = f"Error during file processing: {str(e)}"
            self.log(error_msg)
            self.log(traceback.format_exc())
            self.root.after(0, lambda: self.show_error(error_msg))
        finally:
            self.root.after(0, self.reset_ui)
    
    def reset_ui(self):
        self.is_processing = False
        self.process_button.config(state=tk.NORMAL)
        self.status_message.set("Ready")
        self.progress_value.set(100)  # Show complete
    
    def show_error(self, message):
        self.log(f"ERROR: {message}")
        messagebox.showerror("Error", message)
    
    def show_success(self, message):
        self.log(f"SUCCESS: File processed successfully")
        messagebox.showinfo("Success", message)
    
    def log(self, message):
        now = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{now}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileProcessorApp(root)
    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()