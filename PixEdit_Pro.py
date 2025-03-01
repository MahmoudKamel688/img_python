import os
import cv2
import numpy as np
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.image import Image as KivyImage
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.graphics.texture import Texture
from kivy.core.text import LabelBase
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from matplotlib import font_manager

# 🔹 Find an available system font
def find_available_font():
    font_paths = [f.fname for f in font_manager.fontManager.ttflist]
    return font_paths[:10]  # Get 10 fonts for selection

available_fonts = find_available_font()
default_font = available_fonts[0] if available_fonts else None

# 🔹 Main App Class
class ImageEditor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        # 📂 File chooser
        self.file_chooser = FileChooserListView(filters=['*.png', '*.jpg', '*.jpeg', '*.bmp'])
        self.file_chooser.bind(on_selection=self.load_image)
        self.add_widget(self.file_chooser)

        # 🖼️ Image Display
        self.image_display = KivyImage(allow_stretch=True, size_hint=(1, 2))
        self.add_widget(self.image_display)

        # ✏️ Editing Controls
        control_layout = BoxLayout(size_hint=(1, 0.3))
        
        self.brightness = Button(text="Brightness")
        self.brightness.bind(on_press=self.adjust_brightness)
        control_layout.add_widget(self.brightness)

        self.contrast = Button(text="Contrast")
        self.contrast.bind(on_press=self.adjust_contrast)
        control_layout.add_widget(self.contrast)

        self.resize = Button(text="Resize")
        self.resize.bind(on_press=self.resize_image)
        control_layout.add_widget(self.resize)

        self.add_text = Button(text="Add Text")
        self.add_text.bind(on_press=self.add_text_to_image)
        control_layout.add_widget(self.add_text)

        self.save_btn = Button(text="Save")
        self.save_btn.bind(on_press=self.save_image)
        control_layout.add_widget(self.save_btn)

        self.add_widget(control_layout)

        # 🎨 Text Input & Font Selection
        self.text_input = TextInput(hint_text="Enter text", size_hint=(1, 0.1))
        self.add_widget(self.text_input)

        self.font_selector = Spinner(text="Select Font", values=[os.path.basename(f) for f in available_fonts] if available_fonts else ["Default"])
        self.add_widget(self.font_selector)

        self.image_path = None
        self.pil_image = None

    # 📌 Load Selected Image
    def load_image(self, instance, selection):
        if selection:
            self.image_path = selection[0]
            self.pil_image = Image.open(self.image_path)
            self.display_image(self.pil_image)

    # 🔹 Display Image in Kivy
    def display_image(self, img):
        img = img.convert("RGB")
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        buffer = cv2.flip(img, 0).tobytes()
        texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        
        self.image_display.texture = texture

    # 🎨 Adjust Brightness
    def adjust_brightness(self, instance):
        if self.pil_image:
            enhancer = ImageEnhance.Brightness(self.pil_image)
            self.pil_image = enhancer.enhance(1.2)
            self.display_image(self.pil_image)

    # 🎨 Adjust Contrast
    def adjust_contrast(self, instance):
        if self.pil_image:
            enhancer = ImageEnhance.Contrast(self.pil_image)
            self.pil_image = enhancer.enhance(1.5)
            self.display_image(self.pil_image)

    # 📏 Resize Image
    def resize_image(self, instance):
        if self.pil_image:
            new_size = (self.pil_image.width // 2, self.pil_image.height // 2)
            self.pil_image = self.pil_image.resize(new_size)
            self.display_image(self.pil_image)

    # ✏️ Add Text to Image
    def add_text_to_image(self, instance):
        if self.pil_image and self.text_input.text:
            draw = ImageDraw.Draw(self.pil_image)
            selected_font_path = available_fonts[self.font_selector.values.index(self.font_selector.text)] if available_fonts else None
            
            font = ImageFont.truetype(selected_font_path, 40) if selected_font_path else ImageFont.load_default()
            draw.text((50, 50), self.text_input.text, fill=(255, 0, 0), font=font)
            self.display_image(self.pil_image)

    # 💾 Save Image
    def save_image(self, instance):
        if self.pil_image:
            save_path = os.path.join(os.path.dirname(self.image_path), "edited_" + os.path.basename(self.image_path))
            self.pil_image.save(save_path)
            print(f"✅ Image saved at: {save_path}")

# 🔹 Run the App
class ImageEditorApp(App):
    def build(self):
        return ImageEditor()

if __name__ == "__main__":
    ImageEditorApp().run()
