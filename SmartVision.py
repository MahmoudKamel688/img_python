import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.image import Image as KivyImage
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.core.text import LabelBase
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import os
import arabic_reshaper
from bidi.algorithm import get_display

# تسجيل خط يدعم العربية
LabelBase.register(name='Arabic', fn_regular='arial.ttf')

def fix_arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

class ImageProcessor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        
        self.file_chooser = FileChooserListView()
        self.file_chooser.bind(on_selection=self.load_files)
        self.add_widget(self.file_chooser)
        
        self.image_display = KivyImage()
        self.add_widget(self.image_display)
        
        self.controls = BoxLayout(orientation='vertical')
        
        self.checkbox_ai = CheckBox()
        self.label_ai = Label(text=fix_arabic_text('تحسين باستخدام الذكاء الاصطناعي'), font_name='Arabic')
        self.controls.add_widget(self.label_ai)
        self.controls.add_widget(self.checkbox_ai)
        
        self.checkbox_resize = CheckBox()
        self.label_resize = Label(text=fix_arabic_text('إعادة الحجم الأصلي'), font_name='Arabic')
        self.controls.add_widget(self.label_resize)
        self.controls.add_widget(self.checkbox_resize)
        
        self.checkbox_remove_duplicates = CheckBox()
        self.label_remove_duplicates = Label(text=fix_arabic_text('حذف الصور المكررة'), font_name='Arabic')
        self.controls.add_widget(self.label_remove_duplicates)
        self.controls.add_widget(self.checkbox_remove_duplicates)
        
        self.checkbox_video_processing = CheckBox()
        self.label_video_processing = Label(text=fix_arabic_text('معالجة الفيديو'), font_name='Arabic')
        self.controls.add_widget(self.label_video_processing)
        self.controls.add_widget(self.checkbox_video_processing)
        
        self.process_button = Button(text=fix_arabic_text('معالجة الملفات'), font_name='Arabic')
        self.process_button.bind(on_press=self.process_files)
        self.controls.add_widget(self.process_button)
        
        self.add_widget(self.controls)
        
        self.file_paths = []
    
    def load_files(self, instance, selection):
        self.file_paths = selection
        if selection and selection[0].lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'tiff')):
            self.image_display.source = selection[0]
    
    def process_files(self, instance):
        for file_path in self.file_paths:
            if file_path.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'tiff')):
                self.process_image(file_path)
            elif file_path.lower().endswith(('mp4', 'avi', 'mov')):
                if self.checkbox_video_processing.active:
                    self.process_video(file_path)
        
        if self.checkbox_remove_duplicates.active:
            self.remove_duplicates()
    
    def process_image(self, image_path):
        img = Image.open(image_path)
        
        if self.checkbox_ai.active:
            img = img.filter(ImageFilter.DETAIL)
        
        if self.checkbox_resize.active:
            img = img.resize((img.width, img.height))
        
        img.save(f"processed_{os.path.basename(image_path)}")
    
    def process_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(f'processed_{os.path.basename(video_path)}', fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if self.checkbox_ai.active:
                frame = cv2.detailEnhance(frame, sigma_s=10, sigma_r=0.15)
            
            out.write(frame)
        
        cap.release()
        out.release()
    
    def remove_duplicates(self):
        unique_images = {}
        for image_path in self.file_paths:
            if image_path.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'tiff')):
                img = cv2.imread(image_path)
                img_hash = hash(img.tobytes())
                if img_hash not in unique_images:
                    unique_images[img_hash] = image_path
        
        for image_path in self.file_paths:
            if image_path not in unique_images.values() and image_path.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'tiff')):
                os.remove(image_path)
                
class ImageProcessingApp(App):
    def build(self):
        return ImageProcessor()

if __name__ == '__main__':
    ImageProcessingApp().run()
