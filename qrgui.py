import numpy
import qrcode
import cv2
import PIL.Image
import kivy
from kivy.app import App

if platform == "android":
    from android.permissions import request_permissions, Permission
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

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, ScreenManager

kivy.require('1.11.1')
ui = Builder.load_file('app.kv')


class QrCamScreen(Screen):
    camera = ObjectProperty(None)
    detector = cv2.QRCodeDetector()

    def onCameraClick(self, pic_name='pic', *args):
        # self.cameraObject.export_to_png('/storage/emulated/0/test.png')
        self.camera.export_to_png(f'./{pic_name}.png')
        # self.cameraObject.take_picture('./test.png', None)

    def generate_pic_in_memory(self, *args):
        pixels_data = self.camera.texture.get_region(x=self.camera.x, y=self.camera.y,
                                                     width=self.camera.resolution[0],
                                                     height=self.camera.resolution[1]).pixels
        image = PIL.Image.frombytes(mode="RGBA", size=(int(self.camera.resolution[0]),
                                                       int(self.camera.resolution[1])),
                                    data=pixels_data)
        return image

    def detect_schedule_once(self, interval=1.0):
        Clock.schedule_once(self.tryDetect, interval)

    def tryDetect(self, *args):
        img = cv2.cvtColor(numpy.array(self.generate_pic_in_memory()), cv2.COLOR_RGBA2BGRA)
        data, bbox, straight_qrcode = self.detector.detectAndDecode(img)
        if data:
            print('QR Code detected -->', data)
            self.onCameraClick('qrdetect')
            return
        self.detect_schedule_once(interval=.5)


class QrApp(App):
    def build(self):
        self.sm = ScreenManager()

        cam_screen = QrCamScreen(name='cam')
        self.sm.add_widget(cam_screen)

        # layout = BoxLayout(orientation='vertical')

        # self.cam = cv2.VideoCapture()
        # self.detector = cv2.QRCodeDetector()

        # self.cameraObject = Camera(resolution=(1280, 720), play=True, index=0)
        # self.cameraObject.size_hint_y = 8

        # self.camaraClick = Button(text="Take Photo")
        # self.camaraClick.size_hint = (.5, .2)
        # self.camaraClick.pos_hint = {'x': .25, 'y': .75}
        # self.camaraClick.bind(on_press=self.onCameraClick)

        # layout.add_widget(self.cameraObject)
        # layout.add_widget(self.camaraClick)

        cam_screen.detect_schedule_once(interval=.5)

        return self.sm

    # def onCameraClick(self, *args):
    #     # self.cameraObject.export_to_png('/storage/emulated/0/test.png')
    #     self.cameraObject.export_to_png('./test.png')
    #     # self.cameraObject.take_picture('./test.png', None)
    #
    # def generate_pic_in_memory(self, *args):
    #     pixels_data = self.cameraObject.texture.get_region(x=self.cameraObject.x, y=self.cameraObject.y,
    #                                                        width=self.cameraObject.resolution[0],
    #                                                        height=self.cameraObject.resolution[1]).pixels
    #     image = PIL.Image.frombytes(mode="RGBA", size=(int(self.cameraObject.resolution[0]),
    #                                                    int(self.cameraObject.resolution[1])),
    #                                 data=pixels_data)
    #     # image.save('./out.png')
    #     return image
    #
    # def tryDetect(self, *args):
    #     img = cv2.cvtColor(numpy.array(self.generate_pic_in_memory()), cv2.COLOR_RGBA2BGRA)
    #     data, bbox, straight_qrcode = self.detector.detectAndDecode(img)
    #     if data:
    #         print('QR Code detected -->', data)
    #         return
    #     Clock.schedule_once(self.tryDetect, .5)


def main():
    QrApp().run()


if __name__ == '__main__':
    main()
