import codecs
import os
import sys
import tempfile
import time
from pathlib import Path

import cv2
import kivy
import numpy
import PIL.Image
import qrcode
from kivy.app import App
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image as kiImage
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.utils import platform
from plyer import notification, storagepath
from pyzbar.pyzbar import decode as qr_decode

if platform == "android":
    from android.permissions import Permission, request_permissions
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE, Permission.CAMERA])

# from kivy.logger import Logger
# import logging
# Logger.setLevel(logging.TRACE)

# from kivy.config import Config
# Config.set('kivy', 'log_level', 'debug')
# Config.set('kivy', 'log_dir', 'logs')
# Config.set('kivy', 'log_name', 'kivy_%y-%m-%d_%_.txt')
# Config.set('kivy', 'log_enable', 1)
# Config.write()
# Logger.debug("DEBUG: primary_external_storage_path")
# Logger.debug("DEBUG: %s", primary_external_storage_path())

kivy.require('2.0.0')
ui = Builder.load_file('app.kv')


class QrCamScreen(Screen):
    camera = ObjectProperty(None)
    # detector = cv2.QRCodeDetector()

    def try_detect_go(self, *args):
        result = try_detect(img=self.generate_pic_in_memory())
        print(f'RESULT: {str(result)}')

    def create_detect_task(self, interval=1.0, *args):
        self.detect_task = Clock.schedule_interval(try_detect(img=self.generate_pic_in_memory()), 1.0 / 60.0)

    def detect_click(self, state, pic_name='pic', *args):
        if state == 'down':
            print('Starting Scan')
            Clock.unschedule(self.try_detect_go())
            Clock.schedule_interval(self.try_detect_go(), 1.0 / 60.0)
            # self.trigger()
        else:
            print('Stopping Scan')
            # self.detect_task.stop()
            Clock.unschedule(self.try_detect_go())
        # self.camera.export_to_png(f'./{pic_name}.png')
        # img = self.generate_pic_in_memory()
        # print('pic taken')
        # self.detect_schedule_once(1)

    def generate_pic_in_memory(self, *args):
        print('attempting pic generation')
        try:
            pixels_data = self.camera.texture.pixels
            image = PIL.Image.frombytes(mode="RGBA", size=(int(self.camera.resolution[0]),
                                                           int(self.camera.resolution[1])), data=pixels_data)
        # print('pixel image')
        # print(type(image))
        # print('camera image')
        # print(type(self.camera.export_as_image()))
            print('pic generated')
            return image
            # return self.camera.export_as_image()
        except AttributeError as e:
            print(e)
            pass

    def detect_schedule_once(self, interval=1.0):
        Clock.schedule_once(try_detect(img=self.generate_pic_in_memory()), interval)


class QrCreatorScreen(Screen):
    qr_image = ObjectProperty(None)
    qr_data = ObjectProperty(None)

    def generate_qr_image(self, *args):
        data = str(self.qr_data.text)
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make()
        img = qr.make_image(fill_color="black", back_color="white")
        timestr = time.strftime("%Y%m%d_%H%M%S")
        if platform == "android":
            img_name = str(Path.joinpath(Path(storagepath.get_pictures_dir()), 'qrgenread', f'QR_{timestr}.png'))
            try:
                os.mkdir(Path.joinpath(Path(storagepath.get_pictures_dir()), 'qrgenread'))
            except Exception:
                pass
            # if Path.exists(img_name):
            #     img_name = img_name.split('.')[-1]
        else:
            img_name = str(Path.joinpath(Path('qrgenread'), f'QR_{timestr}.png'))
            try:
                os.mkdir(Path('qrgenread'))
            except Exception:
                pass
        print(img_name)
        self.display_qr_image(img, img_name)
        return img, img_name

    def save_qr_image(self, *args):
        img, img_name = self.generate_qr_image()
        img.save(img_name)
        notification.notify(title="image saved", message=f"{img_name} saved", toast=False)
        notification.notify(message=f"{img_name} saved", timeout=4, toast=True)
        print(f'{img_name} saved')
        return img_name

    def display_qr_image(self, img, img_name, *args_):
        with tempfile.NamedTemporaryFile() as temp:
            img.save(temp, format=img_name.split('.')[-1])
            self.qr_image.source = temp.name

    def clear_image(self, *args):
        self.qr_image.source = ''
        self.qr_data.text = ''


class QrReaderScreen(Screen):
    qr_image = ObjectProperty(None)
    qr_data = ObjectProperty(None)
    files = ObjectProperty(None)

    def scan_image(self, *args):
        try:
            if len(self.files) > 0:
                print(f"FILE SELECTED: {self.files}")
                with PIL.Image.open(self.files[0], 'r') as img:
                    result = try_detect(img=img)
                    # print(result)
                    return result, img
        except PIL.UnidentifiedImageError:
            print("NO VALID IMAGE SELECTED")
            # TODO: throw error popup
        return None

    def show_popup(self, *args):
        popup = FileChooserPopup()
        popup.bind(on_dismiss=lambda e: self.popup_callback(e))
        popup.open()

    def popup_callback(self, instance):
        self.files = instance.chooser.selection
        result, img = self.scan_image()
        self.qr_data.text = codecs.decode(result)
        with tempfile.NamedTemporaryFile() as temp:
            img.save(temp, format='png')
            self.qr_image.source = temp.name
        # self.qr_image.source = img


class FileChooserPopup(Popup):
    chooser = ObjectProperty(None)
    path = StringProperty('')

    def get_path(self):
        if platform == "android":
            self.path = str(Path.joinpath(Path(storagepath.get_pictures_dir()), 'qrgenread'))
        else:
            # self.path = Path('qrgenread')
            self.path = str(Path(''))
        return self.path

    def dismiss_popup(self, *args):
        print(self.chooser.selection)
        self.dismiss()


class QrApp(App):
    def build(self):
        self.sm = ScreenManager()

        # cam_screen = QrCamScreen(name='camera')
        creator_screen = QrCreatorScreen(name='creator')
        reader_screen = QrReaderScreen(name='reader')

        # self.sm.add_widget(cam_screen)
        self.sm.add_widget(creator_screen)
        self.sm.add_widget(reader_screen)

        self.sm.current = 'creator'
        # self.sm.current = 'camera'
        # cam_screen.create_detect_task()
        # cam_screen.trigger = Clock.create_trigger(cam_screen.try_detect_go())

        # cam_screen.detect_schedule_once(interval=4)
        # cam_screen.camera.on_texture(cam_screen.detect_schedule_once(1.0))

        return self.sm


def try_detect(img, *args):
    try:
        result = qr_decode(img)
        print('try detect img')
        # self.camera.texture_update()
        if len(result) > 0:
            # print('QR Code detected -->', result[0][0].decode('utf-8'))
            print('QR Code detected -->', result[0][0])
            # self.on_camera_click('qrdetect')
            # self.detect_task.stop()
            return result[0][0]
        # self.detect_schedule_once(interval=.5)
    except Exception as e:
        raise e
    return None


def main():
    QrApp().run()


if __name__ == '__main__':
    main()
