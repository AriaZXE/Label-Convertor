import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import xml.etree.ElementTree as ET
import shutil

# Function to convert Pascal VOC label to YOLO format
def convert_pascal_to_yolo(xml_file, output_dir, classes):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    for obj in root.findall('object'):
        bbox = obj.find('bndbox')
        xmin = int(bbox.find('xmin').text)
        ymin = int(bbox.find('ymin').text)
        xmax = int(bbox.find('xmax').text)
        ymax = int(bbox.find('ymax').text)

        img_width = int(root.find('size').find('width').text)
        img_height = int(root.find('size').find('height').text)

        x_center = (xmin + xmax) / 2.0 / img_width
        y_center = (ymin + ymax) / 2.0 / img_height
        width = (xmax - xmin) / img_width
        height = (ymax - ymin) / img_height

        class_name = obj.find('name').text
        try:
            class_id = classes.index(class_name)  # Find the class ID from the list
        except ValueError:
            messagebox.showwarning("Warning", f"Class '{class_name}' not found in classes.txt!")
            continue  # Skip this object if class not found

        yolo_label = f"{class_id} {x_center} {y_center} {width} {height}\n"

        output_file = os.path.join(output_dir, os.path.basename(xml_file).replace('.xml', '.txt'))
        with open(output_file, 'a') as f:
            f.write(yolo_label)

# GUI Application
class PascalToYoloConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Pascal to YOLO Converter")
        self.geometry("400x300")

        # Folder selection button for input
        self.select_input_folder_button = ctk.CTkButton(self, text="Select Input Folder", command=self.select_input_folder)
        self.select_input_folder_button.pack(pady=10)

        # Display selected input folder
        self.input_folder_label = ctk.CTkLabel(self, text="")
        self.input_folder_label.pack(pady=10)

        # Folder selection button for output
        self.select_output_folder_button = ctk.CTkButton(self, text="Select Output Folder", command=self.select_output_folder)
        self.select_output_folder_button.pack(pady=10)

        # Display selected output folder
        self.output_folder_label = ctk.CTkLabel(self, text="")
        self.output_folder_label.pack(pady=10)

        # Convert button
        self.convert_button = ctk.CTkButton(self, text="Convert", command=self.convert_labels)
        self.convert_button.pack(pady=20)

        self.selected_input_folder = ""
        self.selected_output_folder = ""
        self.classes = []

        # Check for 'data' folder and 'predefined_classes.txt' file
        self.check_data_folder()

    def check_data_folder(self):
        data_folder = 'data'
        classes_file = 'predefined_classes.txt'

        if not os.path.exists(data_folder):
            messagebox.showerror("Error", f"The folder '{data_folder}' does not exist!")
            self.destroy()

        if not os.path.exists(os.path.join(data_folder, classes_file)):
            messagebox.showerror("Error", f"The file '{classes_file}' does not exist in '{data_folder}'!")
            self.destroy()

        # Load classes from predefined_classes.txt
        with open(os.path.join(data_folder, classes_file), 'r') as file:
            self.classes = [line.strip() for line in file.readlines()]

    def select_input_folder(self):
        self.selected_input_folder = filedialog.askdirectory()
        self.input_folder_label.configure(text=self.selected_input_folder)

    def select_output_folder(self):
        self.selected_output_folder = filedialog.askdirectory()
        self.output_folder_label.configure(text=self.selected_output_folder)

        # Copy predefined_classes.txt to selected output folder as classes.txt
        if self.selected_output_folder:
            shutil.copy(os.path.join('data', 'predefined_classes.txt'),
                        os.path.join(self.selected_output_folder, 'classes.txt'))

    def convert_labels(self):
        if not self.selected_input_folder:
            messagebox.showwarning("Warning", "Please select an input folder first!")
            return

        if not self.selected_output_folder:
            messagebox.showwarning("Warning", "Please select an output folder first!")
            return

        for file in os.listdir(self.selected_input_folder):
            if file.endswith('.xml'):
                convert_pascal_to_yolo(os.path.join(self.selected_input_folder, file), self.selected_output_folder, self.classes)

        messagebox.showinfo("Success", f"Conversion completed! YOLO labels saved in {self.selected_output_folder}")

if __name__ == "__main__":
    app = PascalToYoloConverterApp()
    app.mainloop()
